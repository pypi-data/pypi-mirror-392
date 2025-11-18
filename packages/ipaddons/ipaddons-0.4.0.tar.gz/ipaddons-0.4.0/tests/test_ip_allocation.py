from __future__ import annotations

import ipaddress
from typing import Any, NamedTuple

import pytest

from ipaddons import IPv4Allocation, IPv6Allocation, ip_allocation, tools


class Net(NamedTuple):
    str: str
    ipa: ipaddress.IPv4Network | ipaddress.IPv6Network
    range: tuple[int, int]


def make_nets(input_str: str | list[str]) -> Net | list[Net]:
    if isinstance(input_str, str):
        single = True
        input_str = [input_str]
    else:
        single = False

    ret = []
    for input_net in input_str:
        net = ipaddress.ip_network(input_net, strict=True)
        ret.append(Net(str(net), net, (int(net[0]), int(net[-1]))))

    if single:
        return ret[0]
    return ret


def net_attr(nets: Net | list[Net], attribute: str) -> Any | list[Any]:
    if isinstance(nets, Net):
        return getattr(nets, attribute)
    return [getattr(n, attribute) for n in nets]


v4_supernet = make_nets("10.0.0.0/8")

v4_subnets = make_nets(
    [
        "10.0.0.0/16",
        "10.1.1.0/24",
        "10.1.1.16/29",
        "10.1.2.0/25",
        "10.1.2.0/24",
        "10.1.3.0/25",
        "10.1.3.64/26",
        "10.1.3.128/26",
    ]
)

v6_supernet = make_nets("fc00::/32")

v6_subnets = make_nets(
    [
        "fc00::/48",
        "fc00:0:a::/56",
        "fc00:0:b::/56",
        "fc00:0:b:100::/56",
        "fc00:0:b:200::/64",
        "fc00:0:b:100::/56",
    ]
)


mergeable_subnets = [
    [
        (int(ipaddress.IPv4Network(n)[0]), int(ipaddress.IPv4Network(n)[-1]))
        for n in ["192.168.0.0/24", "192.168.0.0/25", "192.168.0.128/25", "192.168.0.64/29"]
    ],
    [
        (int(ipaddress.IPv6Network(n)[0]), int(ipaddress.IPv6Network(n)[-1]))
        for n in ["fc01::/32", "fc01::/64", "fc01:0:ffff::/48", "fc01:0:cafe::/64"]
    ],
]


@pytest.mark.parametrize(
    ("supernet", "subnets", "allocation_class", "network_class"),
    [
        (net_attr(v4_supernet, "ipa"), net_attr(v4_subnets, "ipa"), IPv4Allocation, ipaddress.IPv4Network),
        (net_attr(v4_supernet, "str"), net_attr(v4_subnets, "str"), IPv4Allocation, ipaddress.IPv4Network),
        (net_attr(v6_supernet, "ipa"), net_attr(v6_subnets, "ipa"), IPv6Allocation, ipaddress.IPv6Network),
        (net_attr(v6_supernet, "str"), net_attr(v6_subnets, "str"), IPv6Allocation, ipaddress.IPv6Network),
        (net_attr(v4_supernet, "ipa"), net_attr(v4_subnets[:1], "ipa"), IPv4Allocation, ipaddress.IPv4Network),
        (net_attr(v6_supernet, "ipa"), net_attr(v6_subnets[:1], "ipa"), IPv6Allocation, ipaddress.IPv6Network),
        (net_attr(v4_supernet, "ipa"), [], IPv4Allocation, ipaddress.IPv4Network),
        (net_attr(v6_supernet, "ipa"), [], IPv6Allocation, ipaddress.IPv6Network),
    ],
)
def test_allocation_classes(supernet, subnets, allocation_class, network_class):
    a = ip_allocation(supernet, used_networks=subnets)
    assert isinstance(a, allocation_class)
    assert all(isinstance(n, network_class) for n in a.used_subnets)


def test_base_abstract_methods():
    class TestAllocation(tools._BaseIPAllocation):
        pass

    with pytest.raises(
        TypeError,
        match=r"Can't instantiate abstract class TestAllocation without an implementation for abstract methods '_max_prefixlen', '_network_class', '_version'",
    ):
        TestAllocation()


@pytest.mark.parametrize(
    ("supernet", "used_nets", "cidr", "first_free", "last_free", "num_subnets"),
    [
        ("10.0.0.0/8", ["10.0.0.0/16", "10.1.0.0/24"], 16, "10.2.0.0/16", "10.255.0.0/16", 254),
        ("2001:db8::/32", ["2001:db8::/48", "2001:db8:1::/120"], 48, "2001:db8:2::/48", "2001:db8:ffff::/48", 65534),
        ("10.0.0.0/8", ["10.5.0.0/16", "10.193.0.0/24"], 16, "10.0.0.0/16", "10.255.0.0/16", 254),
        ("2001:db8::/32", ["2001:db8:4::/48", "2001:db8:fca::/120"], 48, "2001:db8::/48", "2001:db8:ffff::/48", 65534),
        ("10.0.0.0/8", ["10.5.0.0/16", "10.255.0.0/24"], 16, "10.0.0.0/16", "10.254.0.0/16", 254),
        ("2001:db8::/32", ["2001:db8:4::/48", "2001:db8:ffff::/120"], 48, "2001:db8::/48", "2001:db8:fffe::/48", 65534),
    ],
)
def test_free_networks(supernet, used_nets, cidr, first_free, last_free, num_subnets):
    allocation = ip_allocation(supernet, used_nets)
    free_nets = list(allocation.get_free_subnets(cidr))
    assert first_free == str(free_nets[0])
    assert last_free == str(free_nets[-1])
    assert num_subnets == len(free_nets)


@pytest.mark.parametrize(
    ("subnet", "subnet_range"),
    zip(
        net_attr(v4_subnets, "ipa") + net_attr(v6_subnets, "ipa"),
        net_attr(v4_subnets, "range") + net_attr(v6_subnets, "range"),
        strict=True,
    ),
)
def test_netrange(subnet, subnet_range):
    assert tools.netrange(subnet) == subnet_range


@pytest.mark.parametrize(
    ("supernet", "subnets", "subnet_ranges"),
    [
        (net_attr(v4_supernet, "ipa"), net_attr(v4_subnets, "ipa"), net_attr(v4_subnets, "range")),
        (net_attr(v6_supernet, "ipa"), net_attr(v6_subnets, "ipa"), net_attr(v6_subnets, "range")),
    ],
)
def test_allocation_ranges(supernet, subnets, subnet_ranges):
    a = ip_allocation(supernet, used_networks=subnets, ignore_invalid_subnets=False)
    a._update_used_subnet_ranges(merge=False)
    assert sorted(a._used_network_ranges) == sorted(subnet_ranges)


@pytest.mark.parametrize(
    ("supernet_range", "subnet_ranges"),
    [
        (net_attr(v4_supernet, "range"), net_attr(v4_subnets, "range")),
        (net_attr(v6_supernet, "range"), net_attr(v6_subnets, "range")),
    ],
)
def test_range_overlaps(supernet_range, subnet_ranges):
    assert tools.range_overlaps(supernet_range, subnet_ranges) == subnet_ranges[0]


@pytest.mark.parametrize(
    ("supernet_range", "subnet_ranges"),
    [
        (net_attr(v4_supernet, "range"), net_attr(v6_subnets, "range")),
        (net_attr(v6_supernet, "range"), net_attr(v4_subnets, "range")),
    ],
)
def test_range_no_overlaps(supernet_range, subnet_ranges):
    assert tools.range_overlaps(supernet_range, subnet_ranges) is None


@pytest.mark.parametrize(
    ("supernet", "subnets"),
    [
        (net_attr(v4_supernet, "ipa"), net_attr(v4_subnets, "ipa")),
        (net_attr(v6_supernet, "ipa"), net_attr(v6_subnets, "ipa")),
    ],
)
def test_add_used_subnets(supernet, subnets):
    a = ip_allocation(supernet, ignore_invalid_subnets=False)
    a.add_used_subnets([subnets[0]])
    a.add_used_subnets(subnets[1:])
    assert sorted(a.used_subnets) == sorted(subnets)


@pytest.mark.parametrize(
    "subnets",
    mergeable_subnets,
)
def test_merge(subnets):
    covering_prefix = subnets[0]
    assert tools.merge_ranges(subnets) == [covering_prefix]


@pytest.mark.parametrize(
    "subnets",
    mergeable_subnets,
)
def test_merge_one(subnets):
    assert subnets[:1] == tools.merge_ranges(subnets[:1])


def test_merge_empty():
    assert tools.merge_ranges([]) == []


@pytest.mark.parametrize(
    ("supernet", "used_nets", "cidr", "first_free"),
    [
        ("2001:db8::/32", ["2001:db8::/48", "2001:db8:1::/120"], 64, "2001:db8:1:1::/64"),
        ("10.0.0.0/8", ["10.0.0.0/16", "10.1.0.0/24"], 16, "10.2.0.0/16"),
    ],
)
def test_netsize_iterator(supernet, used_nets, cidr, first_free):
    supernet = ipaddress.ip_network(supernet)
    used_nets = [(int(ipaddress.ip_network(n)[0]), int(ipaddress.ip_network(n)[-1])) for n in used_nets]
    i = tools.net_size_iterator(supernet, cidr, used_nets)
    first_ip, last_ip = next(i)
    net = next(ipaddress.summarize_address_range(ipaddress.ip_address(first_ip), ipaddress.ip_address(last_ip)))
    assert first_free == str(net)


@pytest.mark.parametrize(
    ("supernet", "used_nets", "cidr", "last_free"),
    [
        ("10.0.0.0/24", ["10.0.0.0/29", "10.0.0.96/30"], 30, "10.0.0.252/30"),
        ("2001:db8::/32", ["2001:db8::/48", "2001:db8:1::/120"], 48, "2001:db8:ffff::/48"),
    ],
)
def test_netsize_iterator_last(supernet, used_nets, cidr, last_free):
    supernet = ipaddress.ip_network(supernet)
    used_nets = [(int(ipaddress.ip_network(n)[0]), int(ipaddress.ip_network(n)[-1])) for n in used_nets]
    i = tools.net_size_iterator(supernet, cidr, used_nets)
    first_ip, last_ip = list(i)[-1]
    net = next(ipaddress.summarize_address_range(ipaddress.ip_address(first_ip), ipaddress.ip_address(last_ip)))
    assert last_free == str(net)


@pytest.mark.parametrize(
    ("supernet", "subnets", "used_networks"),
    [
        ("10.0.0.0/24", ["192.168.1.0/30", "10.0.0.0/25"], ["10.0.0.0/25"]),
        ("fc00::/32", ["fd00::/64", "fc00::/64"], ["fc00::/64"]),
    ],
)
def test_outside_networks(supernet, subnets, used_networks):
    allocation = ip_allocation(supernet, subnets)
    assert sorted([str(s) for s in allocation.used_subnets]) == sorted(used_networks)


@pytest.mark.parametrize(
    ("supernet", "subnets", "used_networks"),
    [
        ("10.0.0.0/24", ["192.168.1.0/30", "10.0.0.0/25"], ["10.0.0.0/25"]),
        ("fc00::/32", ["fd00::/64", "fc00::/64"], ["fc00::/64"]),
    ],
)
def test_outside_networks_added(supernet, subnets, used_networks):
    allocation = ip_allocation(supernet)
    allocation.add_used_subnets(subnets)
    assert sorted([str(s) for s in allocation.used_subnets]) == sorted(used_networks)


@pytest.mark.parametrize(
    ("supernet", "subnets"),
    [
        ("10.0.0.0/24", ["192.168.1.0/30", "10.0.0.0/25"]),
        ("fc00::/32", ["fd00::/64", "fc00::/64"]),
    ],
)
def test_outside_networks_exception(supernet, subnets):
    with pytest.raises(ValueError, match=r"Subnet .*? does not overlap with .*?"):
        _ = ip_allocation(supernet, subnets, ignore_invalid_subnets=False)


@pytest.mark.parametrize(
    ("supernet", "subnets"),
    [
        ("10.0.0.0/24", ["192.168.1.0/30", "10.0.0.0/25"]),
        ("fc00::/32", ["fd00::/64", "fc00::/64"]),
    ],
)
def test_outside_networks_added_exception(supernet, subnets):
    allocation = ip_allocation(supernet, ignore_invalid_subnets=False)
    with pytest.raises(ValueError, match=r" does not overlap with "):
        allocation.add_used_subnets(subnets)


@pytest.mark.parametrize(
    ("supernet_range", "subnet_ranges"),
    [
        (net_attr(v4_supernet, "range"), net_attr(v6_subnets, "range")),
        (net_attr(v6_supernet, "range"), net_attr(v4_subnets, "range")),
    ],
)
def test_free_ranges_mismatch(supernet_range, subnet_ranges):
    range_iterator = tools.free_ranges(supernet_range, subnet_ranges)
    with pytest.raises(ValueError, match=r" does not overlap with "):
        next(range_iterator)


@pytest.mark.parametrize(
    ("supernet", "subnets", "free_size"),
    [
        (make_nets("10.0.0.0/16"), make_nets(["10.0.0.0/8"]), 29),
        (make_nets("fc00::/32"), make_nets(["fc00::/16"]), 64),
        (make_nets("10.0.0.0/16"), make_nets(["10.0.0.0/17", "10.0.128.0/17"]), 29),
        (make_nets("fc00::/32"), make_nets(["fc00::/33", "fc00:0:8000::/33"]), 64),
        (make_nets("10.0.0.0/16"), make_nets(["10.0.0.0/17", "10.0.0.0/8"]), 29),
        (make_nets("fc00::/32"), make_nets(["fc00::/33", "fc00::/16"]), 64),
        (make_nets("10.0.0.0/16"), make_nets(["10.0.0.0/17", "10.0.0.0/17", "10.0.128.0/17"]), 29),
        (make_nets("fc00::/32"), make_nets(["fc00::/33", "fc00::/33", "fc00:0:8000::/33"]), 64),
        (make_nets("10.0.0.0/16"), make_nets(["10.0.0.0/17", "10.0.128.0/17", "10.0.128.0/17"]), 29),
        (make_nets("fc00::/32"), make_nets(["fc00::/33", "fc00:0:8000::/33", "fc00:0:8000::/33"]), 64),
        (make_nets("10.0.0.0/16"), make_nets(["10.0.0.0/17", "10.0.0.0/24", "10.0.128.0/17"]), 29),
        (make_nets("fc00::/32"), make_nets(["fc00::/33", "fc00::/64", "fc00:0:8000::/33"]), 64),
    ],
)
class TestNoFreeRanges:
    def test_no_free_ranges(self, supernet, subnets, free_size):
        range_iterator = tools.free_ranges(supernet.range, net_attr(subnets, "range"))
        with pytest.raises(StopIteration):
            next(range_iterator)

    def test_no_free_subnets(self, supernet, subnets, free_size):
        allocation = ip_allocation(supernet.ipa, net_attr(subnets, "ipa"))
        with pytest.raises(StopIteration):
            next(allocation.get_free_subnets(free_size))


@pytest.mark.parametrize(
    ("supernet", "subnets"),
    [
        (net_attr(v4_supernet, "str"), net_attr(v6_subnets, "str")),
        (net_attr(v6_supernet, "str"), net_attr(v4_subnets, "str")),
    ],
)
def test_version_mismatch(supernet, subnets):
    with pytest.raises(ValueError, match=r"IP Version missmatch"):
        ip_allocation(supernet, subnets)

    a = ip_allocation(supernet)
    with pytest.raises(ValueError, match=r"IP Version missmatch"):
        a._normalize_networks(subnets)


@pytest.mark.parametrize(
    ("networks", "network_class"),
    [
        ([net_attr(v4_supernet, "str"), *net_attr(v4_subnets, "str")], ipaddress.IPv4Network),
        ([net_attr(v6_supernet, "str"), *net_attr(v6_subnets, "str")], ipaddress.IPv6Network),
    ],
)
def test_network_normalize(networks, network_class):
    a = ip_allocation(networks[0])
    assert all(isinstance(n, network_class) for n in a._normalize_networks(networks))
    assert all(str(n) == networks[i] for i, n in enumerate(a._normalize_networks(networks)))


@pytest.mark.parametrize(
    ("supernet", "subnets", "new_subnets"),
    [
        ("10.0.0.0/8", ["10.0.0.0/24", "10.1.0.0/24"], ["10.255.0.0/16", "10.254.30.0/24"]),
    ],
)
def test_used_subnet_setter(supernet, subnets, new_subnets):
    allocation = ip_allocation(supernet, subnets)
    allocation.used_subnets = new_subnets
    assert sorted([str(n) for n in allocation.used_subnets]) == sorted(new_subnets)
