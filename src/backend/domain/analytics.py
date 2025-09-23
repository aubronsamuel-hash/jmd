"""Domain models and services dedicated to analytics dashboards."""

from __future__ import annotations

from collections import defaultdict
from datetime import date as dt_date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Iterable
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from backend.models import (
    AnalyticsEquipmentIncident as EquipmentIncidentModel,
    AnalyticsMissionEvent as MissionEventModel,
    AnalyticsPayrollRecord as PayrollRecordModel,
)


class AnalyticsFilter(BaseModel):
    """Filtering options exposed on analytics endpoints."""

    model_config = ConfigDict(extra="forbid")

    project: str | None = Field(default=None, description="Filtre projet")
    location: str | None = Field(default=None, description="Filtre lieu")
    team: str | None = Field(default=None, description="Filtre equipe")
    start_date: dt_date | None = Field(default=None, description="Date debut (incluse)")
    end_date: dt_date | None = Field(default=None, description="Date fin (incluse)")


class AnalyticsKpi(BaseModel):
    """Key performance indicators summarizing the filtered dataset."""

    model_config = ConfigDict(extra="forbid")

    missions_count: int = Field(..., description="Nombre de missions validees")
    scheduled_hours: float = Field(..., description="Heures planifiees")
    realized_hours: float = Field(..., description="Heures realisees")
    coverage_rate: float = Field(..., description="Taux de couverture horaire")
    payroll_total: float = Field(..., description="Masse salariale")
    average_hourly_cost: float = Field(..., description="Cout horaire moyen")
    equipment_incidents: int = Field(..., description="Incidents materiel")


class AnalyticsHeatmapCell(BaseModel):
    """Single cell of the workload heatmap."""

    model_config = ConfigDict(extra="forbid")

    date: dt_date = Field(..., description="Jour concerne")
    hour: int = Field(..., description="Heure de la journee (0-23)")
    planned_hours: float = Field(..., description="Charge planifiee sur le slot")
    realized_hours: float = Field(..., description="Charge realisee sur le slot")


class AnalyticsComparisonPoint(BaseModel):
    """Aggregated metrics used for comparative curves."""

    model_config = ConfigDict(extra="forbid")

    date: dt_date = Field(..., description="Jour d'agregation")
    scheduled_hours: float = Field(..., description="Heures planifiees sur la journee")
    realized_hours: float = Field(..., description="Heures realisees sur la journee")
    payroll_total: float = Field(..., description="Masse salariale sur la journee")


class AnalyticsDatasetLatency(BaseModel):
    """Monitoring information about dataset refresh delays."""

    model_config = ConfigDict(extra="forbid")

    dataset: str = Field(..., description="Nom du dataset")
    latency_minutes: float | None = Field(
        default=None, description="Delai depuis la derniere mise a jour"
    )
    last_updated_at: datetime | None = Field(
        default=None, description="Horodatage de la derniere mise a jour"
    )


class AnalyticsDashboard(BaseModel):
    """Full payload returned by the dashboard endpoint."""

    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsFilter = Field(..., description="Filtres appliques")
    kpis: AnalyticsKpi = Field(..., description="KPIs aggregates")
    heatmap: list[AnalyticsHeatmapCell] = Field(
        default_factory=list, description="Heatmap heures planifiees"
    )
    comparisons: list[AnalyticsComparisonPoint] = Field(
        default_factory=list, description="Courbes comparatives"
    )
    dataset_latencies: list[AnalyticsDatasetLatency] = Field(
        default_factory=list, description="Delais de refresh des datasets"
    )


class AnalyticsExportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"
    PNG = "png"
    PDF = "pdf"


class AnalyticsExport(BaseModel):
    """Response returned when generating an export."""

    model_config = ConfigDict(extra="forbid")

    format: AnalyticsExportFormat = Field(..., description="Format demande")
    filename: str = Field(..., description="Nom du fichier exporte")
    content_type: str = Field(..., description="MIME type")
    generated_at: datetime = Field(..., description="Date de generation")
    metadata: dict[str, str] = Field(default_factory=dict, description="Metadonnees")
    data_base64: str = Field(..., description="Contenu encode en base64")
    signature: str = Field(..., description="Empreinte SHA-256 du contenu")


def _apply_common_filters(
    stmt: Select, filters: AnalyticsFilter
) -> Select:
    """Apply the dimension filters to a SQLAlchemy statement."""

    if filters.project:
        stmt = stmt.where(MissionEventModel.project_code == filters.project)
    if filters.location:
        stmt = stmt.where(MissionEventModel.location_code == filters.location)
    if filters.team:
        stmt = stmt.where(MissionEventModel.team_name == filters.team)
    if filters.start_date:
        stmt = stmt.where(
            MissionEventModel.start_time
            >= datetime.combine(filters.start_date, time.min)
        )
    if filters.end_date:
        stmt = stmt.where(
            MissionEventModel.end_time <= datetime.combine(filters.end_date, time.max)
        )
    return stmt


def _apply_equipment_filters(
    stmt: Select, filters: AnalyticsFilter
) -> Select:
    """Apply dimension filters to equipment queries."""

    if filters.project:
        stmt = stmt.where(EquipmentIncidentModel.project_code == filters.project)
    if filters.location:
        stmt = stmt.where(EquipmentIncidentModel.location_code == filters.location)
    if filters.team:
        stmt = stmt.where(EquipmentIncidentModel.team_name == filters.team)
    if filters.start_date:
        stmt = stmt.where(
            EquipmentIncidentModel.occurred_at
            >= datetime.combine(filters.start_date, time.min)
        )
    if filters.end_date:
        stmt = stmt.where(
            EquipmentIncidentModel.occurred_at
            <= datetime.combine(filters.end_date, time.max)
        )
    return stmt


def _decimal_to_float(value: Decimal | float | None) -> float:
    """Convert decimal values to floats for serialization."""

    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _planned_hours(event: MissionEventModel) -> float:
    """Compute planned hours for the mission."""

    duration = event.end_time - event.start_time
    return max(duration.total_seconds() / 3600.0, 0.0)


def _realized_hours(event: MissionEventModel) -> float:
    """Compute realized hours for the mission."""

    if event.actual_hours is not None:
        return _decimal_to_float(event.actual_hours)
    if event.actual_start_time and event.actual_end_time:
        duration = event.actual_end_time - event.actual_start_time
        return max(duration.total_seconds() / 3600.0, 0.0)
    return _planned_hours(event)


def _heatmap_cells(events: Iterable[MissionEventModel]) -> list[AnalyticsHeatmapCell]:
    """Transform mission events into heatmap cells aggregated by hour."""

    buckets: dict[tuple[dt_date, int], dict[str, float]] = defaultdict(
        lambda: {"planned": 0.0, "realized": 0.0}
    )
    for event in events:
        planned = _planned_hours(event)
        realized = _realized_hours(event)
        ratio = realized / planned if planned > 0 else 0.0
        current = event.start_time
        while current < event.end_time:
            bucket_start = current.replace(minute=0, second=0, microsecond=0)
            bucket_end = min(
                event.end_time,
                bucket_start + timedelta(hours=1),
            )
            portion = max((bucket_end - current).total_seconds() / 3600.0, 0.0)
            key = (bucket_start.date(), bucket_start.hour)
            buckets[key]["planned"] += portion
            buckets[key]["realized"] += portion * ratio
            current = bucket_end
    cells = [
        AnalyticsHeatmapCell(
            date=item[0][0],
            hour=item[0][1],
            planned_hours=round(item[1]["planned"], 2),
            realized_hours=round(item[1]["realized"], 2),
        )
        for item in sorted(buckets.items(), key=lambda elem: (elem[0][0], elem[0][1]))
    ]
    return cells


def _comparison_points(
    events: Iterable[MissionEventModel],
    payroll_by_event: dict[UUID, float],
) -> list[AnalyticsComparisonPoint]:
    """Aggregate metrics per day for comparison charts."""

    per_day: dict[dt_date, dict[str, float]] = defaultdict(
        lambda: {"scheduled": 0.0, "realized": 0.0, "payroll": 0.0}
    )
    for event in events:
        day = event.start_time.date()
        per_day[day]["scheduled"] += _planned_hours(event)
        per_day[day]["realized"] += _realized_hours(event)
        per_day[day]["payroll"] += payroll_by_event.get(event.id, 0.0)
    points = [
        AnalyticsComparisonPoint(
            date=day,
            scheduled_hours=round(values["scheduled"], 2),
            realized_hours=round(values["realized"], 2),
            payroll_total=round(values["payroll"], 2),
        )
        for day, values in sorted(per_day.items(), key=lambda elem: elem[0])
    ]
    return points


def _latency(now: datetime, timestamp: datetime | None) -> float:
    """Compute latency in minutes from the provided timestamp."""

    if timestamp is None:
        return float("inf")
    delta = now - timestamp
    return max(delta.total_seconds() / 60.0, 0.0)


def get_analytics_dashboard(
    session: Session, filters: AnalyticsFilter
) -> AnalyticsDashboard:
    """Return analytics KPIs and visualizations according to filters."""

    mission_stmt = _apply_common_filters(select(MissionEventModel), filters)
    mission_stmt = mission_stmt.order_by(MissionEventModel.start_time)
    mission_events = session.execute(mission_stmt).scalars().all()

    payroll_by_event: dict[UUID, float] = {}
    payroll_records: list[PayrollRecordModel] = []
    if mission_events:
        event_ids = [event.id for event in mission_events]
        payroll_stmt = select(PayrollRecordModel).where(
            PayrollRecordModel.mission_event_id.in_(event_ids)
        )
        payroll_records = session.execute(payroll_stmt).scalars().all()
        for record in payroll_records:
            payroll_by_event.setdefault(record.mission_event_id, 0.0)
            payroll_by_event[record.mission_event_id] += _decimal_to_float(record.amount)
    total_payroll = sum(payroll_by_event.values())

    planned_total = sum(_planned_hours(event) for event in mission_events)
    realized_total = sum(_realized_hours(event) for event in mission_events)

    coverage = realized_total / planned_total if planned_total > 0 else 0.0
    avg_cost = total_payroll / realized_total if realized_total > 0 else 0.0

    equipment_stmt = _apply_equipment_filters(select(EquipmentIncidentModel), filters)
    equipment_records = session.execute(equipment_stmt).scalars().all()

    heatmap = _heatmap_cells(mission_events)
    comparisons = _comparison_points(mission_events, payroll_by_event)

    now = datetime.utcnow()
    mission_last_update = max((event.updated_at for event in mission_events), default=None)
    payroll_last_update = max(
        (record.recorded_at for record in payroll_records), default=None
    ) if mission_events else None
    equipment_last_update = max(
        (incident.occurred_at for incident in equipment_records), default=None
    )

    latencies = [
        AnalyticsDatasetLatency(
            dataset="missions",
            latency_minutes=round(_latency(now, mission_last_update), 2)
            if mission_last_update
            else None,
            last_updated_at=mission_last_update,
        ),
        AnalyticsDatasetLatency(
            dataset="payroll",
            latency_minutes=round(_latency(now, payroll_last_update), 2)
            if payroll_last_update
            else None,
            last_updated_at=payroll_last_update,
        ),
        AnalyticsDatasetLatency(
            dataset="equipment",
            latency_minutes=round(_latency(now, equipment_last_update), 2)
            if equipment_last_update
            else None,
            last_updated_at=equipment_last_update,
        ),
    ]

    dashboard = AnalyticsDashboard(
        filters=filters,
        kpis=AnalyticsKpi(
            missions_count=len(mission_events),
            scheduled_hours=round(planned_total, 2),
            realized_hours=round(realized_total, 2),
            coverage_rate=round(coverage, 4),
            payroll_total=round(total_payroll, 2),
            average_hourly_cost=round(avg_cost, 2),
            equipment_incidents=len(equipment_records),
        ),
        heatmap=heatmap,
        comparisons=comparisons,
        dataset_latencies=latencies,
    )
    return dashboard


def generate_analytics_export(
    session: Session, filters: AnalyticsFilter, export_format: AnalyticsExportFormat
) -> AnalyticsExport:
    """Generate encoded exports for the requested format."""

    dashboard = get_analytics_dashboard(session=session, filters=filters)

    if export_format is AnalyticsExportFormat.CSV:
        content_type = "text/csv"
        payload = _build_csv_payload(dashboard)
    elif export_format is AnalyticsExportFormat.PNG:
        content_type = "image/png"
        payload = _build_png_payload(dashboard)
    else:
        content_type = "application/pdf"
        payload = _build_pdf_payload(dashboard)

    import base64
    import hashlib

    generated_at = datetime.utcnow()
    filename = (
        f"analytics_{generated_at.strftime('%Y%m%dT%H%M%S')}.{export_format.value}"
    )
    encoded = base64.b64encode(payload).decode("ascii")
    signature = hashlib.sha256(payload).hexdigest()

    metadata = {
        "project": filters.project or "*",
        "location": filters.location or "*",
        "team": filters.team or "*",
        "start_date": filters.start_date.isoformat()
        if filters.start_date
        else "*",
        "end_date": filters.end_date.isoformat() if filters.end_date else "*",
        "missions_count": str(dashboard.kpis.missions_count),
        "payroll_total": str(dashboard.kpis.payroll_total),
    }

    return AnalyticsExport(
        format=export_format,
        filename=filename,
        content_type=content_type,
        generated_at=generated_at,
        metadata=metadata,
        data_base64=encoded,
        signature=signature,
    )


def _build_csv_payload(dashboard: AnalyticsDashboard) -> bytes:
    """Serialize dashboard comparisons and KPIs to CSV."""

    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["date", "scheduled_hours", "realized_hours", "payroll_total"])
    for point in dashboard.comparisons:
        writer.writerow(
            [
                point.date.isoformat(),
                f"{point.scheduled_hours:.2f}",
                f"{point.realized_hours:.2f}",
                f"{point.payroll_total:.2f}",
            ]
        )
    writer.writerow([])
    writer.writerow(["missions_count", dashboard.kpis.missions_count])
    writer.writerow(["scheduled_hours", f"{dashboard.kpis.scheduled_hours:.2f}"])
    writer.writerow(["realized_hours", f"{dashboard.kpis.realized_hours:.2f}"])
    writer.writerow(["payroll_total", f"{dashboard.kpis.payroll_total:.2f}"])
    writer.writerow(["coverage_rate", f"{dashboard.kpis.coverage_rate:.4f}"])
    return buffer.getvalue().encode("utf-8")


def _build_png_payload(dashboard: AnalyticsDashboard) -> bytes:
    """Return a deterministic PNG placeholder embedding KPI data length."""

    import base64

    # 1x1 transparent PNG as base, embed metrics length in trailing bytes.
    base_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Yp2t7sAAAAASUVORK5CYII="
    )
    kpi_summary = (
        f"missions={dashboard.kpis.missions_count};"
        f"hours={dashboard.kpis.scheduled_hours:.2f};"
        f"payroll={dashboard.kpis.payroll_total:.2f}"
    ).encode("utf-8")
    return base_png + kpi_summary


def _build_pdf_payload(dashboard: AnalyticsDashboard) -> bytes:
    """Produce a minimal PDF document summarizing KPIs."""

    summary_lines = [
        f"Missions: {dashboard.kpis.missions_count}",
        f"Heures planifiees: {dashboard.kpis.scheduled_hours:.2f}",
        f"Heures realisees: {dashboard.kpis.realized_hours:.2f}",
        f"Masse salariale: {dashboard.kpis.payroll_total:.2f}",
    ]
    text = "\\n".join(summary_lines)
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1", "ignore")
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        + f"4 0 obj << /Length {len(stream)} >> stream\n".encode("ascii")
        + stream
        + b"\nendstream endobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"trailer << /Root 1 0 R >>\n%%EOF"
    )
    return pdf_content


__all__ = [
    "AnalyticsDashboard",
    "AnalyticsDatasetLatency",
    "AnalyticsExport",
    "AnalyticsExportFormat",
    "AnalyticsFilter",
    "AnalyticsHeatmapCell",
    "AnalyticsKpi",
    "AnalyticsComparisonPoint",
    "generate_analytics_export",
    "get_analytics_dashboard",
]
