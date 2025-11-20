from typing import Optional

from tortoise import BaseDBAsyncClient, connections, transactions
from tortoise.exceptions import ParamsError


def _get_connection(connection_name: Optional[str]) -> BaseDBAsyncClient:
    # tortoise-orm==0.25.1
    # if connection_name:
    #     connection = connections.get(connection_name)
    # elif len(connections.db_config) == 1:
    #     connection_name = next(iter(connections.db_config.keys()))
    #     connection = connections.get(connection_name)
    # else:
    #     raise ParamsError(
    #         "You are running with multiple databases, so you should specify"
    #         f" connection_name: {list(connections.db_config)}"
    #     )
    # 修改后
    if connection_name:
        connection = connections.get(connection_name)
    elif len(connections.db_config) >= 1:
        # 默认选排序第一个
        connection_name = next(iter(connections.db_config.keys()))
        connection = connections.get(connection_name)
    else:
        raise ParamsError(
            "You are running with multiple databases, so you should specify"
            f" connection_name: {list(connections.db_config)}"
        )
    return connection


transactions._get_connection = _get_connection





