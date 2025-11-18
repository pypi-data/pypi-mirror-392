"""Lightweight helpers for the DUME public procurement API.

The real application is a JavaScript single-page app that posts JSON
payloads to https://dume.chorus-pro.gouv.fr/dumes/donneesEssentielles.
This module mirrors those requests so scripts can search or fetch
contracts without reverse-engineering the UI every time.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from datetime import date, timedelta
import time
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

import requests

API_URL = "https://dume.chorus-pro.gouv.fr/dumes/donneesEssentielles"

# These are the identifiers shipped by the official SPA and work for
# unauthenticated read access.
DEFAULT_PLATFORM = {
    "idPlateforme": "12345678901011",
    "idTechniquePlateforme": "AAA001",
}
DEFAULT_REQUESTER_ID = "12345698765445"
DEFAULT_REQUESTER_NAME = "AIFE"

# The API version header is required.
DEFAULT_HEADERS = {"X-Api-Version": "2"}

# Observed hard limit enforced by the API.
MAX_RESULTS_PER_QUERY = 100
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

TypeDE = Literal["MP", "CC"]
TYPE_ALIASES = {
    "MP": "MP",
    "MARCHE": "MP",
    "MARCHE PUBLIC": "MP",
    "MARCHÉ PUBLIC": "MP",
    "MARCHE PUBLICS": "MP",
    "CC": "CC",
    "CONCESSION": "CC",
    "CONTRAT DE CONCESSION": "CC",
}

# Default partitions to try when we hit the 100-result ceiling.
DEFAULT_PARTITIONS: Mapping[str, Sequence[str]] = {
    "type_de": ("MP", "CC"),
}


@dataclass
class SearchFilters:
    """Representation of the search form exposed on the website.

    All fields are optional; omit whatever you do not want to filter on.

    Attributes:
        reference_unique: Exact ``REF`` such as ``AIFEDUME-daoxup8c``.
        date_start: Publication date lower bound (``YYYY-MM-DD``).
        date_end: Publication date upper bound (``YYYY-MM-DD``).
        internal_id: The platform's internal identifier (``id`` column).
        nature: Human readable nature label (``Marché``, ``Délégation``, ...).
        procedure: Procedure label exactly as displayed on the site.
        cpv_code: CPV code (full string, e.g. ``45210000``).
        type_de: Either ``MP``/``MARCHE PUBLIC`` or ``CC``/``CONTRAT DE CONCESSION``.
        acheteur_id: SIRET of the buyer/autorité concédante selected from autocomplete.
        titulaire_id: SIRET of the titulaire/concessionnaire selected from autocomplete.
    """

    reference_unique: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    internal_id: Optional[str] = None
    nature: Optional[str] = None
    procedure: Optional[str] = None
    cpv_code: Optional[str] = None
    type_de: Optional[str] = None
    acheteur_id: Optional[str] = None
    titulaire_id: Optional[str] = None

    def clone(self, **changes: Optional[str]) -> "SearchFilters":
        """Return a copy with the provided attribute overrides."""
        return replace(self, **changes)

    def _normalize_type(self) -> Optional[TypeDE]:
        if not self.type_de:
            return None
        key = self.type_de.strip().upper()
        normalized = TYPE_ALIASES.get(key)
        if not normalized:
            raise ValueError(
                f"Unknown type_de '{self.type_de}'. Use one of: {', '.join(sorted(TYPE_ALIASES))}"
            )
        return normalized  # type: ignore[return-value]

    def to_payload(self) -> Dict[str, Any]:
        """Serialize the filters into what the API expects."""
        payload: Dict[str, Any] = {}

        if self.reference_unique:
            payload["referenceUnique"] = self.reference_unique
        if self.date_start:
            payload["dateDebutPublication"] = self.date_start
        if self.date_end:
            payload["dateFinPublication"] = self.date_end
        if self.internal_id:
            payload["id"] = self.internal_id
        if self.nature:
            payload["nature"] = self.nature
        if self.procedure:
            payload["procedure"] = self.procedure
        if self.cpv_code:
            payload["codeCPV"] = self.cpv_code

        normalized_type = self._normalize_type()
        if normalized_type:
            payload["typeDE"] = normalized_type

        if self.acheteur_id:
            if normalized_type == "CC":
                payload["idAutoriteConcedante"] = self.acheteur_id
            else:
                payload["idAcheteur"] = self.acheteur_id

        if self.titulaire_id:
            if normalized_type == "CC":
                payload["idConcessionnaire"] = self.titulaire_id
            else:
                payload["idTitulaire"] = self.titulaire_id

        return payload


def _split_filters_by_date(
    filters: SearchFilters,
) -> Optional[Tuple[SearchFilters, SearchFilters]]:
    """Split a filter object into two halves based on its date range."""
    if not filters.date_start or not filters.date_end:
        return None

    start = date.fromisoformat(filters.date_start)
    end = date.fromisoformat(filters.date_end)
    if start >= end:
        return None

    delta_days = (end - start).days
    midpoint = start + timedelta(days=delta_days // 2)
    second_start = midpoint + timedelta(days=1)

    first = filters.clone(
        date_start=start.isoformat(),
        date_end=midpoint.isoformat(),
    )
    second = filters.clone(
        date_start=second_start.isoformat(),
        date_end=end.isoformat(),
    )
    return first, second


class DumeApiClient:
    """Minimal API client that mirrors the calls performed by the SPA."""

    def __init__(
        self,
        *,
        base_url: str = API_URL,
        plateforme: Optional[Dict[str, str]] = None,
        requester_id: str = DEFAULT_REQUESTER_ID,
        requester_name: str = DEFAULT_REQUESTER_NAME,
        session: Optional[requests.Session] = None,
        timeout: int = 30,
        pause: float = 0.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url
        self.plateforme = plateforme or DEFAULT_PLATFORM
        self.requester_id = requester_id
        self.requester_name = requester_name
        self.timeout = timeout
        self.pause = max(0.0, pause)
        self.max_retries = max_retries if max_retries >= 1 else 1

        self.session = session or requests.Session()
        # Merge headers without mutating caller-provided session state unexpectedly.
        for key, value in DEFAULT_HEADERS.items():
            if key not in self.session.headers:
                self.session.headers[key] = value

    def _wrap_operation(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = {
            "operation": operation,
            "plateforme": self.plateforme,
            "idDemandeur": self.requester_id,
            "rsDemandeur": self.requester_name,
        }
        body.update(payload)
        return body

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        attempt = 0
        while True:
            resp = self.session.post(self.base_url, json=payload, timeout=self.timeout)
            try:
                resp.raise_for_status()
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response else None
                should_retry = (
                    status in RETRYABLE_STATUS_CODES and attempt < self.max_retries - 1
                )
                if should_retry:
                    wait_time = min(2 ** attempt, 30)
                    time.sleep(wait_time)
                    attempt += 1
                    continue
                raise

            data = resp.json()
            if self.pause:
                time.sleep(self.pause)
            break
        message_list = data.get("response", {}).get("messageList") or []
        errors = [
            f"{m.get('code')}:{m.get('message')}"
            for m in message_list
            if m.get("type") == "ERREUR"
        ]
        if errors:
            raise RuntimeError(f"API returned error(s): {', '.join(errors)}")
        return data

    def search_contracts(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """Search contracts via the ``recupererDEV2`` operation."""
        payload = filters.to_payload()
        envelope = self._wrap_operation("recupererDEV2", payload)
        data = self._post(envelope)
        return data.get("response", {}).get("donneesEssentielles", [])

    def exhaustive_search(
        self,
        filters: SearchFilters,
        *,
        partition_map: Optional[Mapping[str, Sequence[str]]] = None,
        max_results: int = MAX_RESULTS_PER_QUERY,
    ) -> List[Dict[str, Any]]:
        """Recursively split the search to work around the 100-result cap.

        Args:
            filters: Base filters to apply.
            partition_map: Additional fields to partition when a request hits the
                ``max_results`` ceiling. The dict maps a SearchFilters attribute
                (``procedure``, ``cpv_code``, ...) to the list of values to iterate over.
                Values should match what the frontend expects (use the exact labels).
            max_results: Cap reported by the API (exposed mainly for testing).

        Returns:
            A combined list of all rows fetched across every partition.

        Raises:
            RuntimeError: if the query cannot be split any further but still returns
                ``max_results`` entries. Provide more granular filters/partitions.
        """

        partitions: Dict[str, List[str]] = {
            field: list(values) for field, values in DEFAULT_PARTITIONS.items()
        }
        if partition_map:
            for field, values in partition_map.items():
                partitions[field] = list(values)

        queue: deque[SearchFilters] = deque([filters])
        combined: List[Dict[str, Any]] = []

        while queue:
            current = queue.popleft()
            rows = self.search_contracts(current)
            if len(rows) < max_results:
                combined.extend(rows)
                continue

            date_split = _split_filters_by_date(current)
            if date_split:
                queue.extendleft(date_split)
                continue

            partitioned = False
            for field, options in partitions.items():
                if getattr(current, field):
                    continue
                if not options:
                    continue

                queue.extendleft(current.clone(**{field: option}) for option in options)
                partitioned = True
                break

            if partitioned:
                continue

            raise RuntimeError(
                f"Query hit the {max_results}-result cap and no more partitions are "
                "available. Provide a ``partition_map`` for fields such as "
                f"'procedure' or narrow down the search filters ({current})."
            )

        return combined

    def contracts_on(self, iso_date: str) -> List[Dict[str, Any]]:
        """Convenience helper mirroring the original fetch_date function (single day)."""
        filters = SearchFilters(date_start=iso_date, date_end=iso_date)
        return self.search_contracts(filters)

    def get_contract(self, reference_unique: str) -> Dict[str, Any]:
        """Return the detailed record for a single contract."""
        filters = SearchFilters(reference_unique=reference_unique)
        results = self.search_contracts(filters)
        if not results:
            raise LookupError(f"No contract found for reference '{reference_unique}'")
        if len(results) > 1:
            # The API can technically return multiple versions; expose everything.
            return {"referenceUnique": reference_unique, "versions": results}
        return results[0]

    def iter_contracts(self, dates: Iterable[str]) -> Iterable[Dict[str, Any]]:
        """Yield contracts for each date string in ``dates``."""
        for day in dates:
            for entry in self.contracts_on(day):
                yield entry


_CLIENT: Optional[DumeApiClient] = None


def _client() -> DumeApiClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = DumeApiClient()
    return _CLIENT


def configure_client(**kwargs: Any) -> None:
    """Replace the global client used by helper functions.

    Example:
        >>> dume_api.configure_client(pause=0.5, max_retries=5)
    """

    global _CLIENT
    _CLIENT = DumeApiClient(**kwargs)


def _filters_from_kwargs(kwargs: Dict[str, Any]) -> SearchFilters:
    data = dict(kwargs)  # shallow copy to avoid modifying caller dict

    reference = data.pop("reference", None) or data.pop("reference_unique", None)
    date_value = data.pop("date", None)
    date_start = data.pop("date_start", None) or date_value
    date_end = data.pop("date_end", None) or date_value

    allowed = {
        "internal_id",
        "nature",
        "procedure",
        "cpv_code",
        "type_de",
        "acheteur_id",
        "titulaire_id",
    }
    unknown = set(data.keys()) - allowed
    if unknown:
        raise ValueError(f"Unknown filter argument(s): {', '.join(sorted(unknown))}")

    return SearchFilters(
        reference_unique=reference,
        date_start=date_start,
        date_end=date_end,
        internal_id=data.get("internal_id"),
        nature=data.get("nature"),
        procedure=data.get("procedure"),
        cpv_code=data.get("cpv_code"),
        type_de=data.get("type_de"),
        acheteur_id=data.get("acheteur_id"),
        titulaire_id=data.get("titulaire_id"),
    )


def _dedupe_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique_rows = []
    for row in rows:
        ref = row.get("referenceUnique")
        if ref and ref in seen:
            continue
        if ref:
            seen.add(ref)
        unique_rows.append(row)
    return unique_rows


def get_contracts(
    *,
    complete: bool = False,
    partition_map: Optional[Mapping[str, Sequence[str]]] = None,
    **filters: Any,
) -> List[Dict[str, Any]]:
    """Retrieve contracts matching the provided filters.

    Args:
        complete: When True, fetch the detailed record for each contract (one
            request per reference) instead of returning the list version.
        partition_map: Extra partition definitions to help the exhaustive search
            when a single day still returns 100 rows. Keys must match the keyword
            arguments above (e.g. ``procedure`` or ``cpv_code``).
        **filters: Any combination of ``date``, ``date_start``, ``date_end``,
            ``reference``, ``nature``, ``procedure``, ``cpv_code``, ``type_de``,
            ``acheteur_id``, ``titulaire_id``, ``internal_id``.

    Returns:
        A list of contracts. When ``complete`` is False you get the same payload
        as the website result table; when True you get the detailed record for
        each ``referenceUnique``.
    """

    client = _client()
    filter_obj = _filters_from_kwargs(filters)
    rows = client.exhaustive_search(filter_obj, partition_map=partition_map)
    rows = _dedupe_rows(rows)

    if not complete:
        return rows

    detailed: List[Dict[str, Any]] = []
    for row in rows:
        ref = row.get("referenceUnique")
        if not ref:
            continue
        detailed.append(client.get_contract(ref))
    return detailed


def get_contract(reference_unique: str) -> Dict[str, Any]:
    """Fetch a single contract by its reference."""
    return _client().get_contract(reference_unique)
