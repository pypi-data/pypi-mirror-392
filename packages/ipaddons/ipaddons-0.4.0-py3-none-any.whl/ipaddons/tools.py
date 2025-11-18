from __future__ import annotations

import ipaddress
from abc import ABC, abstractmethod
from threading import RLock
from typing import TYPE_CHECKING, Generic, TypeVar

_N = TypeVar("_N", ipaddress.IPv4Network, ipaddress.IPv6Network)

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from typing import TypeAlias, TypeGuard

    IPNetwork: TypeAlias = ipaddress.IPv4Network | ipaddress.IPv6Network
    UnSpecNet: TypeAlias = str | IPNetwork
    UnspecNetSeq: TypeAlias = Sequence[UnSpecNet]
    NetworkRange: TypeAlias = tuple[int, int]


class IPAllocationError(Exception):
    """General Error in an IPAllocation object."""


def ip_allocation(
    supernet: UnSpecNet, used_networks: UnspecNetSeq | None = None, ignore_invalid_subnets: bool = True
) -> IPv4Allocation | IPv6Allocation:
    """
    Create an IP allocation.

    Creates and returns an IP allocation object.

    :param supernet: An IPv4 or IPv6 network, either as a string or as an :doc:`ipaddress <python:library/ipaddress>`
        network object.
    :param used_networks: A list of subnets of the :py:attr:`supernet` that are already in use in this allocation,
        either as a string or an :doc:`ipaddress <python:library/ipaddress>` network object.
    :return: An :class:`IPv4Allocation` or :class:`IPv6Allocation` instance, depending on the passed
        :py:attr:`supernet` argument. Same principle as :py:func:`python:ipaddress.ip_network`.
    :param ignore_invalid_subnets: If set to False, used subnets that do not overlap with the supernet will raise
        a ValueError.
    """
    if used_networks is None:
        used_networks = []
    supernet = ipaddress.ip_network(supernet) if isinstance(supernet, str) else supernet
    if supernet.version == 4:
        assert isinstance(supernet, ipaddress.IPv4Network)
        return IPv4Allocation(supernet, used_networks, ignore_invalid_subnets)
    if supernet.version == 6:
        assert isinstance(supernet, ipaddress.IPv6Network)
        return IPv6Allocation(supernet, used_networks, ignore_invalid_subnets)
    msg = f"IP Version of Supernet is unknown: {supernet.version}"
    raise ValueError(msg)


def _ceildiv(a: int, b: int) -> int:
    return -(a // -b)


def range_overlap(a: NetworkRange, b: NetworkRange) -> bool:
    """
    Network Range Overlap Check.

    :param a: a network range
    :param b:  a network range
    :return: True if ranges overlap, otherwise false
    """
    return max(a[0], b[0]) < min(a[1], b[1])


def range_overlaps(a: NetworkRange, b: list[NetworkRange]) -> NetworkRange | None:
    """
    Overlap between a network range and a list of other network ranges.

    :param a: Network range to check against.
    :param b: List of network ranges that could overlap.
    :return: The first range from b that overlaps with a.
    """
    for x in b:
        if range_overlap(a, x):
            return x
    return None


def netrange(network: IPNetwork) -> NetworkRange:
    """
    Create a network range from an :doc:python:`ipaddress <library/ipaddress>` object.

    A network range is the integer presentation of the first and last IP address of the network as a tuple.
    :param network: An :doc:`ipaddress <python:library/ipaddress>` network object.
    :return: A network range tuple.
    """
    return int(network[0]), int(network[-1])


def free_ranges(superrange: NetworkRange, used_ranges: list[NetworkRange]) -> Generator[NetworkRange, None, None]:
    """
    Get free ranges from a supernet with provided used ranges.

    :param superrange: Covering range from where free subranges should be returned.
    :param used_ranges: List of used network ranges.
    :return: An interator for free ranges.
    """
    remaining_superrange = superrange
    # Make values unique and sort them. This is crucial when interating over them.
    used_ranges = list(dict.fromkeys(used_ranges))
    used_ranges = sorted(used_ranges, key=lambda x: (x[0], -x[1]))
    for used_range in used_ranges:
        if not range_overlap(superrange, used_range):
            msg = f"{used_range} does not overlap with {remaining_superrange}"
            raise ValueError(msg)
        if used_range[0] <= remaining_superrange[0] and used_range[1] >= remaining_superrange[1]:
            # Subrange is as large or larger than the remaining superrange so we have no more free ranges.
            return
        if used_range[1] <= remaining_superrange[0] or used_range[0] >= remaining_superrange[1]:
            # Subrange ends below or begins above remaining superrange, ignore.
            continue
        if remaining_superrange[0] == used_range[0]:
            # Used range is at the beginning of remaining superrange, shrink it.
            remaining_superrange = used_range[1] + 1, remaining_superrange[1]
            continue
        # There is a free range between the beginning of the remaining superrange and the current used range.
        free_range = remaining_superrange[0], used_range[0] - 1
        # Adjust remaining free superrange to begin after current used range.
        remaining_superrange = used_range[1] + 1, remaining_superrange[1]
        assert free_range[0] < free_range[1]
        yield free_range
    # The rest of the superrange is free when there are no more used ranges left
    assert remaining_superrange[0] < remaining_superrange[1]
    yield remaining_superrange


def merge_ranges(ranges: list[NetworkRange]) -> list[NetworkRange]:
    """
    Merge network ranges that overlap.

    :param ranges: A list of network ranges.
    :return: A list of network ranges with overlapping ranges merged into one.
    """
    if not len(ranges):
        # Empty range
        return []
    sorted_ranges = sorted(ranges, reverse=True)
    merged_ranges = []
    base = sorted_ranges.pop()
    while len(sorted_ranges):
        range = sorted_ranges.pop()
        if range_overlap(base, range):
            base = min(base[0], range[0]), max(base[1], range[1])
        else:
            merged_ranges.append(base)
            base = range
    merged_ranges.append(base)
    return merged_ranges


def net_size_iterator(
    supernet: IPNetwork, cidr: int, used_ranges: list[NetworkRange] | None = None
) -> Generator[NetworkRange, None, None]:
    """
    Iterate over an ipaddr network object and return subnet network ranges of the specified cidr size.

    :param supernet: An ipaddr network object.
    :param cidr: CIDR size of the subnets.
    :param used_ranges: A list of used network ranges.
    :return: An interator over all subnets in the network in the specified CIDR size.
    """
    cidr_size = 2 ** (supernet.max_prefixlen - cidr)
    supernet_range = int(supernet[0]), int(supernet[-1])
    if used_ranges is None:
        used_ranges = []
    for free_range in free_ranges(supernet_range, used_ranges):
        free_range_boundary = (
            # Large IPv6 integers are tricky...
            _ceildiv(free_range[0], cidr_size) * cidr_size,
            free_range[1] // cidr_size * cidr_size - 1,
        )
        for s in range(free_range_boundary[0], free_range_boundary[1] + cidr_size, cidr_size):
            yield s, s + cidr_size - 1


class _BaseIPAllocation(ABC, Generic[_N]):
    """
    An IP allocation.

    The object represents a supernet (the allocation) with an optional list of used (assigned) subnets. You can also
    request an iterator for free subnets of a specific size.

    :param supernet: An IPv4 or IPv6 network, either as a string or as an :doc:`ipaddress <python:library/ipaddress>`
        network object.
    :param used_subnets: A list of subnets of the :py:attr:`supernet` that are already in use in this allocation,
        either as string or an :doc:`ipaddress <python:library/ipaddress>` network object.
    :param ignore_invalid_subnets: If set to False, used subnets that do not overlap with the supernet will raise
        a ValueError.
    """

    def __init__(
        self, supernet: UnSpecNet, used_subnets: UnspecNetSeq | None = None, ignore_invalid_subnets: bool = True
    ):
        self.lock = RLock()
        self.ignore_invalid_subnets = ignore_invalid_subnets
        self.supernet: _N = self._normalize_network(supernet)
        if used_subnets is None:
            used_subnets = []
        self._used_network_ranges: list[NetworkRange] = []
        self._used_subnets: list[_N] = []
        self.used_subnets: list[_N] = used_subnets

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {getattr(self, 'supernet', 'INIT')}>"

    @property
    @abstractmethod
    def _network_class(self) -> type[_N]:
        raise NotImplementedError

    @property
    @abstractmethod
    def _version(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def _max_prefixlen(self) -> int:
        raise NotImplementedError

    def _normalize_network(self, _network: UnSpecNet) -> _N:
        network = ipaddress.ip_network(_network) if isinstance(_network, str) else _network
        if not self._version_compatible(network):
            msg = f"IP Version missmatch. Cannot use {network} in {self}"
            raise ValueError(msg)
        return network

    def _normalize_networks(self, input_networks: UnspecNetSeq) -> list[_N]:
        return [self._normalize_network(n) for n in input_networks]

    def _version_compatible(self, network: IPNetwork) -> TypeGuard[_N]:
        return self._version == network.version

    def _check_subnet(self, subnet: _N) -> bool:
        if not range_overlap(netrange(self.supernet), netrange(subnet)):
            if not self.ignore_invalid_subnets:
                msg = f"Subnet {subnet} does not overlap with {self.supernet}"
                raise ValueError(msg)
            return False
        return True

    @property
    def used_subnets(self) -> Generator[_N, None, None]:
        """
        Used subnets in this allocation.

        :getter: An iterator for used networks in this allocation.
        :setter: Sets the list of used networks.
        :type: List of networks either as string or :doc:`ipaddress <python:library/ipaddress>` network objects.
        """
        yield from self._used_subnets

    @used_subnets.setter
    def used_subnets(self, subnets: UnspecNetSeq) -> None:
        with self.lock:
            self._used_subnets = []
            self.add_used_subnets(subnets)

    def add_used_subnets(self, subnets: UnspecNetSeq) -> None:
        """
        Add additional subnets to the list of used networks in this allocation.

        :param subnets: A list of networks that are added to the in-use networks of this allocation, either as a string
            or :doc:`ipaddress <python:library/ipaddress>` network objects.
        """
        with self.lock:
            for _subnet in subnets:
                subnet = self._normalize_network(_subnet)
                if not self._check_subnet(subnet):
                    continue
                self._used_subnets.append(subnet)
                self._used_subnets.sort()
            self._update_used_subnet_ranges()

    def _update_used_subnet_ranges(self, merge: bool = True) -> None:
        with self.lock:
            ranges = [netrange(n) for n in self._used_subnets]
            if merge:
                ranges = merge_ranges(ranges)
            self._used_network_ranges = ranges

    def get_free_subnets(self, prefixlen: int) -> Generator[_N, None, None]:
        """
        List free subnets of a specific size.

        :param prefixlen: Size of the free subnets returned in CIDR notation.
        :return: An iterator for free subnets of :py:attr:`prefixlen` size.
        """
        for n in net_size_iterator(self.supernet, prefixlen, self._used_network_ranges):
            if range_overlaps(n, self._used_network_ranges):
                msg = "This should never happen! A free range cannot overlap with a used range."
                raise IPAllocationError(msg)
            yield self._network_class((n[0], prefixlen))


class IPv4Allocation(_BaseIPAllocation[ipaddress.IPv4Network]):  # noqa: D101
    __doc__ = _BaseIPAllocation.__doc__
    _version = 4
    _max_prefixlen = ipaddress.IPV4LENGTH
    _network_class = ipaddress.IPv4Network


class IPv6Allocation(_BaseIPAllocation[ipaddress.IPv6Network]):  # noqa: D101
    __doc__ = _BaseIPAllocation.__doc__
    _version = 6
    _max_prefixlen = ipaddress.IPV6LENGTH
    _network_class = ipaddress.IPv6Network
