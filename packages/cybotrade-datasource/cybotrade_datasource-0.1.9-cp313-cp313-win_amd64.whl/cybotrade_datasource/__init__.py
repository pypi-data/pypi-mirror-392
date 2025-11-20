# import the contents of the Rust library into the Python extension
from .cybotrade_datasource import (
    query as _query,
    query_paginated as _query_paginated,
    stream as _stream,
)

from datetime import datetime, timezone
from typing import Literal, Optional, TypedDict, AsyncIterator, cast


class Data(TypedDict):
    start_time: datetime


PaginationMode = Literal["start_time_end_time", "start_time_limit", "end_time_limit"]


class Pagination(TypedDict):
    start_time: datetime
    end_time: datetime
    limit: int
    mode: PaginationMode


class Response(TypedDict):
    data: list[Data]
    page: Pagination


class SubscriptionResponse(TypedDict):
    conn_id: str
    success: bool
    message: str


CollectedDataType = Literal["snapshot", "delta"]


class CollectedData(TypedDict):
    topic: str
    data: list[Data]
    local_timestamp_ms: int
    type: CollectedDataType


Message = SubscriptionResponse | CollectedData


def _transform_data_from_timestamp_ms(data: list[Data]) -> list[Data]:
    return list(
        map(
            lambda d: {
                **d,
                "start_time": datetime.fromtimestamp(
                    cast(int, d["start_time"]) / 1000, tz=timezone.utc
                ),
            },
            data,
        )
    )


async def query_paginated(
    api_key: str,
    topic: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = None,
    flatten: Optional[bool] = None,
    api_url: Optional[str] = None,
) -> list[Data]:
    """
    Query Datasource API in a paginated manner.
    This function might call the server several times until it completes collecting data according to the
    parameters specified.

    You can only specify parameters in the combination of (start_time, end_time) or (limit).
    """
    return _transform_data_from_timestamp_ms(
        await _query_paginated(
            api_key=api_key,
            topic=topic,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            flatten=flatten,
            api_url=api_url,
        )
    )


async def query(
    api_key: str,
    topic: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = None,
    flatten: Optional[bool] = None,
    api_url: Optional[str] = None,
) -> Response:
    """
    Query Datasource API without pagination.
    This function will always make only one call to the server.

    You can only specify parameters in the combination of (start_time, end_time), (start_time, limit) or (end_time, limit).
    """
    resp = await _query(
        api_key=api_key,
        topic=topic,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        flatten=flatten,
        api_url=api_url,
    )
    resp["data"] = _transform_data_from_timestamp_ms(resp["data"])
    return resp


async def stream(
    api_key: str, topics: list[str], url: Optional[str] = None
) -> AsyncIterator[Message]:
    """
    Connect to the websocket server with the provided topics to listen for live updates.
    """
    stream = await _stream(api_key=api_key, topics=topics, url=url)

    class Wrapper:
        def __aiter__(self):
            return self

        async def __anext__(self):
            msg = await stream.__anext__()
            if "data" in msg:
                msg["data"] = _transform_data_from_timestamp_ms(msg["data"])
            return msg

    return Wrapper()
