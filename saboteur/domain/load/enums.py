from enum import StrEnum
from aiohttp import hdrs


class HTTPMethod(StrEnum):
    GET = hdrs.METH_GET
    POST = hdrs.METH_POST
    PUT = hdrs.METH_PUT
    PATCH = hdrs.METH_PATCH
    DELETE = hdrs.METH_DELETE
