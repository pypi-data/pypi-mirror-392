# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025, 2ps all rights reserved.

import logging
from starlette.requests import Request
from starlette.responses import PlainTextResponse


class HealthFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


# Filter out /health
def add_logging_health_filter():
    """
    adds a logging filter to filter out /health requests from uvicorn
    access logs.
    """
    logging.getLogger("uvicorn.access").addFilter(HealthFilter())


def add_health_endpoint(mcp):
    """
    adds a very basic health endpoint that can be used with load balancers
    or services like aws ecs to test whether the server is up.
    """
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    pass
