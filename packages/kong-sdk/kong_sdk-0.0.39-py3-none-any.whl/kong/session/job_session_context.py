from contextlib import contextmanager

from kong.common.app_logger import AppLogger
from kong.proto.service_pb2 import JobSession
from session_context import _session_as_dict


@contextmanager
def job_session_context(logger: AppLogger, session: JobSession):
    with logger.context(**_session_as_dict(session)):
        yield
