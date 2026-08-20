#!/usr/bin/env python3
"""
DataCube — Store

Storage for cubes.

Features:
- JSON file storage (default)
- SQLite storage (planned)
- Search by lens, namespace, completeness

Usage:
    from core.datacube.store import CubeStore

    store = CubeStore("cubes/")
    store.save(cube)
    cube = store.get("cube-123")
"""

import json
import os
import glob
from typing import Dict, Any, List, Optional
from pathlib import Path

from .cube import Cube


class CubeStore:
    """
    DataCube store — persistent storage for cubes.
    """

    def __init__(self, store_dir: str = "cubes"):
        """
        Initialise the cube store.

        Args:
            store_dir: Directory to store cubes
        """
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def save(self, cube: Cube) -> str:
        """
        Save a cube to storage.

        Args:
            cube: Cube instance

        Returns:
            Cube ID
        """
        file_path = self.store_dir / f"{cube.cube_id}.json"
        with open(file_path, "w") as f:
            f.write(cube.to_json())
        return cube.cube_id

    def get(self, cube_id: str) -> Optional[Cube]:
        """
        Get a cube by ID.

        Args:
            cube_id: Cube ID

        Returns:
            Cube instance or None
        """
        file_path = self.store_dir / f"{cube_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            data = json.load(f)

        # Reconstruct cube
        cube = Cube(
            claim=data["claim"],
            namespace=data["namespace"],
            lens=data["lens"],
            metadata=data.get("metadata", {}),
            contradictory_cubes=data.get("contradictory_cubes", []),
        )
        cube.cube_id = data["cube_id"]
        cube.lens_completeness = data.get("lens_completeness", {})
        cube.human_validated = data.get("human_validated", False)
        cube.human_validator = data.get("human_validator")
        cube.human_validation_timestamp = data.get("human_validation_timestamp")
        cube.created = data.get("created", cube.created)
        cube.updated = data.get("updated", cube.updated)

        return cube

    def search(
        self,
        lens: Optional[str] = None,
        namespace: Optional[str] = None,
        min_completeness: float = 0.0,
        max_results: int = 20,
    ) -> List[Cube]:
        """
        Search for cubes.

        Args:
            lens: Filter by lens
            namespace: Filter by namespace
            min_completeness: Minimum completeness
            max_results: Maximum results

        Returns:
            List of cubes
        """
        results = []

        for file_path in glob.glob(str(self.store_dir / "*.json")):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                # Apply filters
                if lens and data.get("lens") != lens:
                    continue

                if namespace and data.get("namespace") != namespace:
                    continue

                completeness = data.get("completeness", 0.0)
                if completeness < min_completeness:
                    continue

                # Reconstruct cube
                cube = Cube(
                    claim=data["claim"],
                    namespace=data["namespace"],
                    lens=data["lens"],
                    metadata=data.get("metadata", {}),
                    contradictory_cubes=data.get("contradictory_cubes", []),
                )
                cube.cube_id = data["cube_id"]
                cube.lens_completeness = data.get("lens_completeness", {})
                cube.human_validated = data.get("human_validated", False)
                cube.human_validator = data.get("human_validator")
                cube.human_validation_timestamp = data.get("human_validation_timestamp")
                cube.created = data.get("created", cube.created)
                cube.updated = data.get("updated", cube.updated)

                results.append(cube)

            except (json.JSONDecodeError, OSError):
                continue

        # Sort by completeness
        results.sort(key=lambda c: c.get_completeness(), reverse=True)

        return results[:max_results]

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        total = 0
        by_lens = {lens: 0 for lens in ["FACT", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"]}
        by_namespace = {}
        validated = 0

        for file_path in glob.glob(str(self.store_dir / "*.json")):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                total += 1
                lens = data.get("lens", "UNKNOWN")
                if lens in by_lens:
                    by_lens[lens] += 1

                namespace = data.get("namespace", "unknown")
                by_namespace[namespace] = by_namespace.get(namespace, 0) + 1

                if data.get("human_validated", False):
                    validated += 1

            except (json.JSONDecodeError, OSError):
                continue

        return {
            "total": total,
            "by_lens": by_lens,
            "by_namespace": by_namespace,
            "validated": validated,
        }


def save_cube(cube: Cube, store_dir: str = "cubes") -> str:
    """Convenience function to save a cube."""
    store = CubeStore(store_dir)
    return store.save(cube)


def get_cube(cube_id: str, store_dir: str = "cubes") -> Optional[Cube]:
    """Convenience function to get a cube."""
    store = CubeStore(store_dir)
    return store.get(cube_id)


def search_cubes(
    lens: Optional[str] = None,
    namespace: Optional[str] = None,
    min_completeness: float = 0.0,
    max_results: int = 20,
    store_dir: str = "cubes",
) -> List[Cube]:
    """Convenience function to search for cubes."""
    store = CubeStore(store_dir)
    return store.search(lens, namespace, min_completeness, max_results)


# ============================================================
# CLI
# ============================================================

def main():
    """Test store."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="DataCube — Store")
    parser.add_argument("--create", "-c", type=str, help="Create a cube with claim")
    parser.add_argument("--namespace", "-n", type=str, default="domain.general", help="Namespace")
    parser.add_argument("--lens", "-l", type=str, default="UNKNOWN", help="Lens")
    parser.add_argument("--list", "-L", action="store_true", help="List cubes")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats")

    args = parser.parse_args()

    store = CubeStore()

    if args.create:
        cube = Cube(args.create, args.namespace, args.lens)
        cube.fill_all_lenses()
        cube_id = store.save(cube)
        print(f"✅ Cube created: {cube_id}")
        print(f"   Claim: {cube.claim}")
        print(f"   Lens: {cube.lens}")
        print(f"   Completeness: {cube.get_completeness():.2%}")

    elif args.list:
        cubes = store.search(max_results=20)
        print(f"📋 Cubes ({len(cubes)}):")
        for c in cubes:
            print(f"  {c.cube_id} — {c.lens} ({c.get_completeness():.0%})")
            print(f"    {c.claim[:60]}...")

    elif args.stats:
        stats = store.get_stats()
        print(f"📊 DataCube Store")
        print("=" * 60)
        print(f"  Total cubes: {stats['total']}")
        print(f"  Validated: {stats['validated']}")
        print(f"\n  By lens:")
        for lens, count in stats['by_lens'].items():
            print(f"    {lens}: {count}")
        print(f"\n  By namespace:")
        for ns, count in stats['by_namespace'].items():
            print(f"    {ns}: {count}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()