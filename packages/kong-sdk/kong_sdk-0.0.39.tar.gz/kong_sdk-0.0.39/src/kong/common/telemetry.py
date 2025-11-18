from collections.abc import Callable
from contextlib import contextmanager
from logging import Logger
from uuid import UUID

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Tracer, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.span import SpanContext

from kong.sdk.config import config

BuildInstrument = Callable[[str], None]
TracerAndGetCurrentCtx = tuple[Tracer, Callable[[], SpanContext]]


def _install_once():
    completed = False

    def setup(name: str, builders: tuple[BuildInstrument]) -> None:
        nonlocal completed
        if completed:
            return

        completed = True

        if not config.app.use_telemetry:
            return

        resource = Resource(attributes={"service.name": name})
        trace.set_tracer_provider(TracerProvider(resource=resource))
        otlp_exporter = OTLPSpanExporter(
            endpoint=config.otel.agent_url,
            insecure=True,
        )

        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )

        for create_instrument in builders:
            create_instrument(name)

    return setup


_INSTALL = _install_once()


def telemetry(name: str, *builders: tuple[BuildInstrument]) -> TracerAndGetCurrentCtx:
    if len(builders) > 0:
        _INSTALL(name, builders)

    def get_current_ctx():
        return trace.get_current_span().get_span_context()

    return (trace.get_tracer(name), get_current_ctx)


def trace_stamp() -> str:
    context = trace.get_current_span().get_span_context()
    return f"00-{context.trace_id}-{context.span_id}-01"


class TraceLogger:
    def __init__(self, log: Logger):
        self.__log = log
        self.id = str(UUID(int=trace.get_current_span().get_span_context().trace_id))

    def info(self, msg: str):
        self.__log.info(self.__format(msg))

    def exception(self, e: BaseException):
        self.__log.exception(self.__format(str(e)))

    def __format(self, msg: str):
        if config.app.use_telemetry:
            return f"{msg} trace={self.id}"
        else:
            return msg


@contextmanager
def keep_trace(log: Logger):
    logger = TraceLogger(log)
    try:
        yield logger
    except BaseException as e:
        logger.exception(e)
        raise e
