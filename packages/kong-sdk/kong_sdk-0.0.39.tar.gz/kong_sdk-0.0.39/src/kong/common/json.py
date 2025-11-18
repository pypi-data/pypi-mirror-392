import json
from datetime import datetime
from uuid import UUID


class JsonEncoder(json.JSONEncoder):
    def default(self, value: any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)

        return json.JSONEncoder.default(self, value)
