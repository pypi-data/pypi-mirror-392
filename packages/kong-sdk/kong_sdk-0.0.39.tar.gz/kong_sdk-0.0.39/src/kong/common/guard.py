import datetime

from kong.common.app_logger import app_logger
from kong.common.exceptions import DeadlineException

logger = app_logger(__name__)


def check_deadline(value: datetime.datetime):
    now = datetime.datetime.now()

    if value <= now:
        logger.warning(
            "provided deadline has passed", lambda: dict(deadline=value, now=now)
        )

        raise DeadlineException(f"The provided deadline {value} was reached at {now}")
