#!/usr/bin/env python3
"""
DataCube — Bulk Ingestion

Bulk ingestion of structured data (CSV/JSON).

One cube per record/row. Lands in UNKNOWN lens.

Usage:
    from core.datacube.bulk import bulk_ingest_json, bulk_ingest_csv

    cubes = bulk_ingest_json("data.json")
    cubes = bulk_ingest_csv("data.csv", namespace="domain.electronics")
"""

import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

from .cube import Cube, create_cube
from .store import CubeStore


def bulk_ingest_json(
    file_path: str,
    namespace: str = "domain.unknown",
    store: Optional[CubeStore] = None,
) -> List[Cube]:
    """
    Bulk ingest from a JSON file.

    Each JSON object becomes a cube in UNKNOWN lens.

    Args:
        file_path: Path to JSON file (array of objects)
        namespace: Default namespace
        store: CubeStore instance (creates if None)

    Returns:
        List of created cubes
    """
    if store is None:
        store = CubeStore()

    with open(file_path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    cubes = []

    for record in data:
        # Convert record to claim
        if isinstance(record, dict):
            # Use first non-empty value as claim
            claim = next((str(v) for v in record.values() if v), "Unknown record")
        else:
            claim = str(record)

        # Create cube in UNKNOWN
        cube = create_cube(
            claim=claim,
            namespace=namespace,
            lens="UNKNOWN",
            metadata=record if isinstance(record, dict) else {"data": record},
        )

        # Fill all lenses to 16% (basic)
        cube.fill_all_lenses()

        store.save(cube)
        cubes.append(cube)

    return cubes


def bulk_ingest_csv(
    file_path: str,
    namespace: str = "domain.unknown",
    store: Optional[CubeStore] = None,
    claim_column: Optional[str] = None,
) -> List[Cube]:
    """
    Bulk ingest from a CSV file.

    Each row becomes a cube in UNKNOWN lens.

    Args:
        file_path: Path to CSV file
        namespace: Default namespace
        store: CubeStore instance (creates if None)
        claim_column: Column to use as claim (default: first column)

    Returns:
        List of created cubes
    """
    if store is None:
        store = CubeStore()

    cubes = []

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)

        fieldnames = reader.fieldnames

        for row in reader:
            # Determine claim
            if claim_column and claim_column in row:
                claim = row[claim_column]
            else:
                # Use first non-empty value
                claim = next((v for v in row.values() if v), "Unknown record")

            # Create cube in UNKNOWN
            cube = create_cube(
                claim=claim,
                namespace=namespace,
                lens="UNKNOWN",
                metadata=row,
            )

            # Fill all lenses to 16% (basic)
            cube.fill_all_lenses()

            store.save(cube)
            cubes.append(cube)

    return cubes


def bulk_ingest_auto(
    file_path: str,
    namespace: str = "domain.unknown",
    store: Optional[CubeStore] = None,
) -> List[Cube]:
    """
    Auto-detect file type and bulk ingest.

    Args:
        file_path: Path to file (.json or .csv)
        namespace: Default namespace
        store: CubeStore instance (creates if None)

    Returns:
        List of created cubes
    """
    path = Path(file_path)

    if path.suffix == ".json":
        return bulk_ingest_json(file_path, namespace, store)
    elif path.suffix == ".csv":
        return bulk_ingest_csv(file_path, namespace, store)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


# ============================================================
# CLI
# ============================================================

def main():
    """Test bulk ingestion."""
    import argparse
    import sys
    import tempfile
    import json

    parser = argparse.ArgumentParser(description="DataCube — Bulk Ingestion")
    parser.add_argument("--file", "-f", type=str, help="File to ingest")
    parser.add_argument("--namespace", "-n", type=str, default="domain.unknown", help="Namespace")
    parser.add_argument("--test", "-t", action="store_true", help="Run test with sample data")

    args = parser.parse_args()

    store = CubeStore()

    if args.test:
        # Create sample JSON data
        sample_data = [
            {"id": 1, "name": "Resistor", "value": "100Ω", "tolerance": "5%"},
            {"id": 2, "name": "Capacitor", "value": "10µF", "voltage": "50V"},
            {"id": 3, "name": "Diode", "value": "1N4007", "package": "DO-41"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_data, f)
            temp_path = f.name

        print(f"📂 Testing with sample data: {temp_path}")
        cubes = bulk_ingest_json(temp_path, args.namespace, store)

        print(f"✅ Created {len(cubes)} cubes")
        for cube in cubes:
            print(f"  {cube.cube_id} — {cube.lens}: {cube.claim[:40]}...")

    elif args.file:
        if args.file.endswith(".json"):
            cubes = bulk_ingest_json(args.file, args.namespace, store)
        elif args.file.endswith(".csv"):
            cubes = bulk_ingest_csv(args.file, args.namespace, store)
        else:
            print(f"❌ Unsupported file type: {args.file}")
            sys.exit(1)

        print(f"✅ Created {len(cubes)} cubes from {args.file}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()