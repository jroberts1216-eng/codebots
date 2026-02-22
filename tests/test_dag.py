from __future__ import annotations

import pytest

from codebots.core.dag import DagError, topo_sort
from codebots.core.models import Role, WorkItem


def test_topo_sort_orders_dependencies() -> None:
    items = [
        WorkItem(id="a", title="a", description="a", owner=Role.software_engineer, depends_on=[]),
        WorkItem(id="b", title="b", description="b", owner=Role.software_engineer, depends_on=["a"]),
    ]
    ordered = topo_sort(items)
    assert [i.id for i in ordered] == ["a", "b"]


def test_topo_sort_detects_cycles() -> None:
    items = [
        WorkItem(id="a", title="a", description="a", owner=Role.software_engineer, depends_on=["b"]),
        WorkItem(id="b", title="b", description="b", owner=Role.software_engineer, depends_on=["a"]),
    ]
    with pytest.raises(DagError):
        topo_sort(items)
