"""Structured logging helpers adding trace metadata to log records."""

from __future__ import annotations

import logging

from .context import current_span_id, get_attribute, get_context


class ObservabilityLogFilter(logging.Filter):
    """Inject observability metadata on every log record."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - exercised indirectly
        context = get_context()
        record.trace_id = context.trace_id or "-"
        record.span_id = current_span_id() or "-"
        record.organization_id = get_attribute("organization_id", "-")
        record.request_id = get_attribute("request_id", record.trace_id)
        record.user_id = get_attribute("user_id", "-")
        record.rgpd_subject = get_attribute("rgpd_subject", "-")
        record.audit_event = get_attribute("audit_event", "-")
        return True


def configure_structured_logging() -> None:
    """Configure the root logger once to emit contextualised records."""

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s %(levelname)s %(name)s "
                "trace_id=%(trace_id)s span_id=%(span_id)s "
                "org=%(organization_id)s user=%(user_id)s rgpd=%(rgpd_subject)s "
                "audit=%(audit_event)s %(message)s"
            ),
        )
    root_logger.addFilter(ObservabilityLogFilter())


__all__ = ["configure_structured_logging", "ObservabilityLogFilter"]
