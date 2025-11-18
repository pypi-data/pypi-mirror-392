import abc
import datetime
import time
from typing import TypeVar

from kong.common.app_logger import app_logger
from kong.common.env import env_flag
from kong.common.guard import check_deadline
from kong.common.timed import Timed
from pydantic import BaseModel

logger = app_logger(__name__)

InputData = TypeVar("InputData", bound=BaseModel)
OutputData = TypeVar("OutputData", bound=BaseModel)


class KongFunction(abc.ABC):
    def __init__(
        self,
        class_of_input_data: type[BaseModel],
    ):
        self.__class_of_input_data = class_of_input_data

    @abc.abstractmethod
    async def handle(self, data: InputData) -> OutputData:
        raise NotImplementedError

    @Timed(
        value="kong_sdk_function",
        extra_tags=["method", "call", "package", "kong-sdk-python"],
        percentiles=(0.5, 0.75, 0.9, 0.95, 0.99),
    )
    async def call(self, input_json: str, deadline: datetime.datetime):
        start_time = time.perf_counter()
        logger.info("call function")

        try:
            check_deadline(deadline)

            data = self.__class_of_input_data.model_validate_json(
                input_json,
                strict=env_flag("KONG_SDK_INPUT_CHECK_STRICT", default=True),
            )

            result = await self.handle(data)

            logger.info(
                "have call function result",
                lambda: dict(elapsed=start_time - time.perf_counter()),
            )

            return result
        except Exception as ex:
            logger.error(
                "call function failed",
                lambda: dict(
                    reason="an unexpected problem occurred",
                    data=input_json,
                    deadline=deadline,
                    elapsed=start_time - time.perf_counter(),
                ),
                ex,
            )
            raise ex
