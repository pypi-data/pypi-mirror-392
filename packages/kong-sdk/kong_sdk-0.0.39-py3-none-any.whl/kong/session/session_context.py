from contextlib import contextmanager

from kong.common.app_logger import app_logger
from kong.proto.service_pb2 import JobSession

logger = app_logger(__name__)


@contextmanager
def session_context(session: JobSession):

    def on_open():
        logger.debug("open session", lambda: __as_dict(session))

    def on_close():
        logger.debug("close session", lambda: __as_dict(session))

    def on_error():
        logger.error("close session", lambda: __as_dict(session))

    with logger.context(**__as_dict(session)):
        on_open()
        try:
            yield
        except Exception as ex:
            on_error()
            raise ex
        on_close()


def __as_dict(session: JobSession) -> dict:
    context = {
        "sessionId": session.id,
        "sessionRootId": session.rootId,
        "sessionParentId": session.parentId,
        "sessionTenant": session.tenant,
        "sessionSource": session.source,
        "sessionTopic": session.topic,
        "sessionBusinessKey": session.businessKey,
        "sessionExecutionMode": session.executionMode,
        "sessionPriority": session.priority,
        "sessionDeadline": session.deadline.ToDatetime(),
        "sessionRootCreated": session.rootCreated.ToDatetime(),
        "sessionCreated": session.created.ToDatetime(),
        "sessionMetadata": session.metadata,
    }

    return context
