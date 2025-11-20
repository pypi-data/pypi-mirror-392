from typing import NamedTuple

from labels.model.file import DependencyType
from labels.model.package import Package, PackageType
from labels.model.relationship import Relationship


class _PathContext(NamedTuple):
    rel_map: dict[str, list[str]]
    package_names_cache: dict[str, str]
    packages_by_id: dict[str, Package]
    current_name: str
    current_version: str


def calculate_top_parents_for_packages(
    packages: list[Package],
    relationships: list[Relationship],
) -> list[Package]:
    rel_map = build_relationship_map(relationships)

    package_names_cache = {pkg.id_: f"{pkg.name}@{pkg.version}" for pkg in packages}
    packages_by_id = {pkg.id_: pkg for pkg in packages}

    for pkg in packages:
        if pkg.type != PackageType.NpmPkg:
            continue
        for location in pkg.locations:
            node_id = f"{pkg.id_}@{location.location_id()}"
            context = _PathContext(
                rel_map=rel_map,
                package_names_cache=package_names_cache,
                packages_by_id=packages_by_id,
                current_name=pkg.name,
                current_version=pkg.version,
            )
            top_parents = find_top_parents(node_id, context)
            current_pkg_name_version = f"{pkg.name}@{pkg.version}"
            if location.dependency_type in (DependencyType.DIRECT, DependencyType.ROOT):
                top_parents = [tp for tp in top_parents if tp != current_pkg_name_version]
            location.top_parents = top_parents

    return packages


def build_relationship_map(relationships: list[Relationship]) -> dict[str, list[str]]:
    rel_map: dict[str, list[str]] = {}
    for rel in relationships:
        if rel.type.value == "dependency-of":
            if rel.from_ not in rel_map:
                rel_map[rel.from_] = []
            rel_map[rel.from_].append(rel.to_)
    return rel_map


def find_top_parents(
    node_id: str,
    context: _PathContext,
) -> list[str]:
    top_parents: set[str] = set()

    def dfs(current_id: str, visited: set[str]) -> None:
        if current_id in visited:
            return

        new_visited = visited | {current_id}
        parents = context.rel_map.get(current_id, [])

        if not parents:
            pkg_id = current_id.split("@")[0]
            pkg_name_version = context.package_names_cache.get(pkg_id, pkg_id)
            top_parents.add(pkg_name_version)
            return

        for parent_id in parents:
            parent_pkg_id = parent_id.split("@")[0]
            parent_pkg = context.packages_by_id.get(parent_pkg_id)

            if parent_pkg:
                parent_location_id = parent_id.split("@", 1)[1]
                parent_location = next(
                    (
                        loc
                        for loc in parent_pkg.locations
                        if loc.location_id() == parent_location_id
                    ),
                    None,
                )
                if parent_location and parent_location.dependency_type == DependencyType.ROOT:
                    current_pkg_id = current_id.split("@")[0]
                    current_pkg_name_version = context.package_names_cache.get(
                        current_pkg_id, current_pkg_id
                    )
                    top_parents.add(current_pkg_name_version)
                    continue

            dfs(parent_id, new_visited)

    dfs(node_id, set())

    if not top_parents:
        return [f"{context.current_name}@{context.current_version}"]

    return sorted(top_parents)
