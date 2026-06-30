from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


RISK_RANK = {
    "P3": 0,
    "P2": 1,
    "P1": 2,
    "P0": 3,
}


@dataclass(frozen=True)
class RouteRecord:
    route: str
    risk: str
    changed: bool
    seconds: float
    owner: str


@dataclass(frozen=True)
class RouteSummary:
    route: str
    total: int
    changed: int
    max_risk: str
    total_seconds: float
    owners: tuple[str, ...]
    validation_mode: str


def parse_route_line(line: str) -> RouteRecord:
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 5:
        raise ValueError(f"expected 5 fields, got {len(parts)}")

    route, risk, changed_text, seconds_text, owner = parts
    if not route:
        raise ValueError("route is required")
    if risk not in RISK_RANK:
        raise ValueError(f"unknown risk: {risk}")
    if changed_text not in {"0", "1", "false", "true"}:
        raise ValueError(f"unknown changed flag: {changed_text}")

    return RouteRecord(
        route=route,
        risk=risk,
        changed=changed_text in {"1", "true"},
        seconds=float(seconds_text),
        owner=owner or "unassigned",
    )


def parse_routes(lines: Iterable[str]) -> list[RouteRecord]:
    records = []
    for line in lines:
        clean = line.strip()
        if clean and not clean.startswith("#"):
            records.append(parse_route_line(clean))
    return records


def summarize_routes(records: Iterable[RouteRecord]) -> list[RouteSummary]:
    grouped: dict[str, dict[str, object]] = {}
    for record in records:
        bucket = grouped.setdefault(
            record.route,
            {
                "total": 0,
                "changed": 0,
                "max_risk": record.risk,
                "total_seconds": 0.0,
                "owners": set(),
            },
        )
        bucket["total"] = int(bucket["total"]) + 1
        bucket["changed"] = int(bucket["changed"]) + int(record.changed)
        bucket["total_seconds"] = float(bucket["total_seconds"]) + record.seconds
        bucket["owners"].add(record.owner)
        if RISK_RANK[record.risk] > RISK_RANK[str(bucket["max_risk"])]:
            bucket["max_risk"] = record.risk

    summaries = []
    for route, bucket in grouped.items():
        total = int(bucket["total"])
        changed = int(bucket["changed"])
        max_risk = str(bucket["max_risk"])
        if max_risk in {"P0", "P1"} or changed:
            validation_mode = "boundary"
        elif total >= 1000:
            validation_mode = "sampled"
        else:
            validation_mode = "fast"
        summaries.append(
            RouteSummary(
                route=route,
                total=total,
                changed=changed,
                max_risk=max_risk,
                total_seconds=round(float(bucket["total_seconds"]), 3),
                owners=tuple(sorted(bucket["owners"])),
                validation_mode=validation_mode,
            )
        )

    return sorted(summaries, key=lambda summary: (-RISK_RANK[summary.max_risk], summary.route))
