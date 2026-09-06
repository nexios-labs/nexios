"""A `BaseResponse`-shaped editor over one outgoing ASGI message.

Every built-in middleware that needs to add a header or a cookie to a
response it didn't build itself -- a `Set-Cookie`, a CORS header, an
`X-RateLimit-*` -- does it the same way: intercept the one
`http.response.start` message as it passes through `send`, and edit its
headers list in place before forwarding it. :class:`ResponseHeaders` is that
edit, wrapped in the same `set_header`/`set_cookie`/`delete_cookie` surface a
real response object offers, so that code reads exactly like it would
against one.

This is a small shared *utility*, not a shared middleware base class: each
middleware still writes its own `__call__` and wraps `send` on its own terms
-- what counts as "before" and "after" the downstream app, and what its
methods are named, differs from one middleware to the next. This is only
here so none of them re-derive cookie serialisation (`SameSite` validation,
the `__Host-`/`__Secure-` `Secure` requirement, ...) by hand.
"""

from __future__ import annotations

from sillo.core.http.response import BaseResponse
from sillo.objects import MutableHeaders
from sillo.types import Message


class ResponseHeaders:
    """Edits the headers of one `http.response.start` ASGI message.

    `set_header`, `set_cookie`, `delete_cookie` and the rest are
    `BaseResponse`'s own methods, bound here instead -- they only ever touch
    `self.raw_headers`, so pointing that at the ASGI message's own headers
    list is all that's needed for them to edit it directly, with none of a
    response object's other machinery (a body, a status code, ...) along for
    the ride.
    """

    set_header = BaseResponse.set_header
    set_headers = BaseResponse.set_headers
    remove_header = BaseResponse.remove_header
    remove_headers = BaseResponse.remove_headers
    set_cookie = BaseResponse.set_cookie
    delete_cookie = BaseResponse.delete_cookie

    def __init__(self, message: Message) -> None:
        self.raw_headers: list[tuple[bytes, bytes]] = message["headers"]

    @property
    def headers(self) -> MutableHeaders:
        if not hasattr(self, "_headers"):
            self._headers = MutableHeaders(raw=self.raw_headers)
        return self._headers
