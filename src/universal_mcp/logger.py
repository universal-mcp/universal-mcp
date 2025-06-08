import sys
from datetime import datetime
from pathlib import Path
import logging

from loguru import logger
from opentelemetry import trace
from opentelemetry import _logs as otel_logs # Renamed to avoid conflict
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LogRecord as OpenTelemetryLogRecord
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter # Corrected import
from opentelemetry._logs import set_logger_provider, SeverityNumber # Renamed to avoid conflict


def get_log_file_path(app_name: str = "universal-mcp") -> Path:
    """Get a standardized log file path for an application.

    Args:
        app_name: Name of the application.

    Returns:
        Path to the log file in the format: logs/{app_name}/{app_name}_{date}.log
    """
    date_str = datetime.now().strftime("%Y%m%d")
    home = Path.home()
    log_dir = home / ".universal-mcp" / "logs"
    return log_dir / f"{app_name}_{date_str}.log"


def setup_logger(
    log_file: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    compression: str = "zip",
    level: str = "INFO",
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    otel_exporter_otlp_endpoint: str | None = None,
    app_name: str = "universal-mcp",
) -> None:
    """Setup the logger with both stderr and optional file logging with rotation.

    Args:
        log_file: Optional path to log file. If None, only stderr logging is enabled.
        rotation: When to rotate the log file. Can be size (e.g., "10 MB") or time (e.g., "1 day").
        retention: How long to keep rotated log files (e.g., "1 week").
        compression: Compression format for rotated logs ("zip", "gz", or None).
        level: Minimum logging level.
        format: Log message format string.
        otel_exporter_otlp_endpoint: Optional OTLP endpoint for OpenTelemetry.
        app_name: Name of the application, used for OpenTelemetry service.name.
    """
    # Remove default handler
    logger.remove()

    if otel_exporter_otlp_endpoint:
        resource = Resource(attributes={"service.name": app_name})

        # Setup Tracing
        tracer_provider = TracerProvider(resource=resource)
        span_exporter = OTLPSpanExporter(endpoint=otel_exporter_otlp_endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
        set_tracer_provider(tracer_provider)

        # Setup Logging
        logger_provider = LoggerProvider(resource=resource)
        log_exporter = OTLPLogExporter(endpoint=otel_exporter_otlp_endpoint)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
        set_logger_provider(logger_provider) # Use the imported set_logger_provider

        # Custom Loguru Sink for OpenTelemetry
        class OtelLoguruSink:
            def __init__(self, otel_logger_provider: LoggerProvider, app_name: str):
                self.otel_logger = otel_logger_provider.get_logger(app_name)
                # Mapping Loguru levels to OpenTelemetry SeverityNumber
                self.level_mapping = {
                    "TRACE": SeverityNumber.TRACE,
                    "DEBUG": SeverityNumber.DEBUG,
                    "INFO": SeverityNumber.INFO,
                    "SUCCESS": SeverityNumber.INFO2, # Or map to INFO
                    "WARNING": SeverityNumber.WARN,
                    "ERROR": SeverityNumber.ERROR,
                    "CRITICAL": SeverityNumber.FATAL,
                }

            def write(self, message):
                record = message.record
                severity_number = self.level_mapping.get(record["level"].name, SeverityNumber.UNSPECIFIED)

                log_record = OpenTelemetryLogRecord(
                    timestamp=int(record["time"].timestamp() * 1e9), # nanoseconds
                    observed_timestamp=int(datetime.now().timestamp() * 1e9), # nanoseconds
                    severity_text=record["level"].name,
                    severity_number=severity_number,
                    body=record["message"],
                    resource=resource, # Associate with the same resource
                    attributes={
                        "loguru.file.name": record["file"].name,
                        "loguru.file.path": str(record["file"].path),
                        "loguru.function": record["function"],
                        "loguru.line": record["line"],
                        "loguru.module": record["module"],
                        "loguru.name": record["name"],
                        "loguru.thread.id": record["thread"].id,
                        "loguru.thread.name": record["thread"].name,
                        "loguru.process.id": record["process"].id,
                        "loguru.process.name": record["process"].name,
                        **record.get("extra", {}), # Include any extra data
                    }
                )
                self.otel_logger.emit(log_record)

        logger.add(OtelLoguruSink(logger_provider, app_name), level=level, format=format, enqueue=True)



    # Add stderr handler
    logger.add(
        sink=sys.stderr,
        level=level,
        format=format,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    if not log_file:
        log_file = get_log_file_path()

    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        sink=str(log_file),
        rotation=rotation,
        retention=retention,
        compression=compression,
        level=level,
        format=format,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    logger.info(f"Logging to {log_file}")
