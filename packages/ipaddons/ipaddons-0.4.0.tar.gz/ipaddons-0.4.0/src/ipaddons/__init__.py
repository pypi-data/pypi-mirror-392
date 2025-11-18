"""Various addons for the :doc:`ipaddress <python:library/ipaddress>` standard library module."""

from __future__ import annotations

from ._version import __version__, __version_tuple__  # noqa: F401
from .tools import IPv4Allocation, IPv6Allocation, ip_allocation

__all__ = ["IPv4Allocation", "IPv6Allocation", "ip_allocation"]
