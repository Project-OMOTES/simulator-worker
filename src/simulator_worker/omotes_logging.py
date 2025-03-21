import logging

from omotes_sdk.internal.orchestrator_worker_events.esdl_messages import (
    EsdlMessage,
    MessageSeverity,
)

logger = logging.getLogger(__name__)

SEVERITY_MAP = {
    logging.CRITICAL: MessageSeverity.ERROR,
    logging.ERROR: MessageSeverity.ERROR,
    logging.WARNING: MessageSeverity.WARNING,
    logging.INFO: MessageSeverity.INFO,
    logging.DEBUG: MessageSeverity.DEBUG,
}


class OmotesEsdlMessageHandler(logging.Handler):
    """Custom logging handler for simulator messages."""

    esdl_msgs: list[EsdlMessage] = []  # ClassVariable for shared storage (.append is threadsafe).

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        esdl_object_id = record.__dict__.get("esdl_object_id", None)
        self.esdl_msgs.append(
            EsdlMessage(
                esdl_object_id=esdl_object_id,
                severity=SEVERITY_MAP.get(record.levelno, MessageSeverity.INFO),
                technical_message=record.getMessage(),
            )
        )


def setup_logging(debug: bool = True) -> OmotesEsdlMessageHandler:
    """Setup logging for the simulator."""
    level = logging.DEBUG if debug else logging.INFO
    root = logging.getLogger()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s]:%(name)s - %(message)s")
    esdl_handler = OmotesEsdlMessageHandler()
    esdl_handler.setLevel(level)
    esdl_handler.setFormatter(formatter)
    root.addHandler(esdl_handler)
    return esdl_handler
