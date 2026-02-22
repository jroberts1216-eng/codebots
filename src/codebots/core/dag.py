from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from codebots.core.models import WorkItem


class DagError(RuntimeError):
    pass


def topo_sort(items: Iterable[WorkItem]) -> list[WorkItem]:
    by_id = {i.id: i for i in items}
    # validate dependencies
    for i in by_id.values():
        for dep in i.depends_on:
            if dep not in by_id:
                raise DagError(f"Work item {i.id} depends on unknown item {dep}")

    in_degree = {i.id: 0 for i in by_id.values()}
    children: dict[str, list[str]] = {i.id: [] for i in by_id.values()}
    for i in by_id.values():
        for dep in i.depends_on:
            in_degree[i.id] += 1
            children[dep].append(i.id)

    queue = [i_id for i_id, deg in in_degree.items() if deg == 0]
    out: list[WorkItem] = []
    while queue:
        cur = queue.pop(0)
        out.append(by_id[cur])
        for child in children[cur]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(out) != len(by_id):
        remaining = [i_id for i_id, deg in in_degree.items() if deg > 0]
        raise DagError(f"Cycle detected in work DAG; remaining nodes: {remaining}")

    return out
