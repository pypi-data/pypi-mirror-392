#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3


class Error(Exception):
    pass


class RequestError(Error):
    pass


class TimeoutError(Error):
    pass
