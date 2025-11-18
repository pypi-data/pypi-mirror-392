import io
import traceback
from collections import OrderedDict

from pydantic import BaseModel


class ErrorData(BaseModel):
    code: int
    type: str
    cause: list[str]
    message: str
    call_stack: str


def throwable_traceback_to_string(ex: Exception, limit=None) -> str:
    buffer = io.StringIO()
    traceback.print_exception(ex, limit=limit, file=buffer)
    return buffer.getvalue()


def get_all_causes(exception: Exception) -> list[str]:
    causes = OrderedDict()
    current_cause = exception
    while current_cause is not None and current_cause not in causes:
        if str(current_cause) != "":
            # Emulating https://docs.oracle.com/en/java/javase/23/docs/api/java.base/java/util/LinkedHashSet.html
            causes[str(current_cause)] = None
        current_cause = current_cause.__cause__
    return list(causes.keys())


def throwable_to_error_data(
    ex: Exception,
    include_call_stack: bool = False,
) -> ErrorData:
    return ErrorData(
        code=500,
        type=ex.__class__.__name__,
        #  If str() is called on an instance of this class,
        #  the representation of the argument(s) to the instance are returned,
        #  or the empty string when there were no arguments.
        message=str(ex),
        cause=get_all_causes(ex),
        call_stack=throwable_traceback_to_string(ex) if include_call_stack else "",
    )
