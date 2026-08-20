#!/usr/bin/env python3
"""
Mimir — Codebase Ingestion Pipeline

Walks a repository, parses source files, and creates SCP capsules.
Each file becomes a capsule with:
- Purpose (inferred from content)
- Exports (functions, classes)
- Dependencies (imports)
- Structured summary

Usage:
    from intelligence.mimir.ingest import MimirIngest

    ingester = MimirIngest()
    result = ingester.ingest("/path/to/repo")
    print(result["capsules_created"])
"""

import os
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class MimirIngest:
    """
    Mimir ingestion pipeline — creates SCP capsules from code.
    """

    # Language parsers
    PARSERS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".scp.json": "scp",
    }

    def __init__(self, output_dir: str = "capsules"):
        """
        Initialise ingester.

        Args:
            output_dir: Directory to write capsules
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.capsules_created = 0
        self.skipped = 0
        self.errors = 0

    def ingest(self, repo_path: Union[str, Path], force: bool = False) -> Dict[str, Any]:
        """
        Ingest a repository.

        Args:
            repo_path: Path to repository (string or Path)
            force: Overwrite existing capsules

        Returns:
            Stats dict with capsules_created, skipped, errors
        """
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {
                "error": f"Repository not found: {repo_path}",
                "capsules_created": 0,
                "skipped": 0,
                "errors": 0,
            }

        if not repo_path.is_dir():
            return {
                "error": f"Path is not a directory: {repo_path}",
                "capsules_created": 0,
                "skipped": 0,
                "errors": 0,
            }

        print(f"📂 Ingesting: {repo_path}")

        # Walk directory
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common exclusions
            dirs[:] = [
                d for d in dirs
                if not d.startswith('.')
                and d not in ['node_modules', '__pycache__', 'target', 'build', 'dist', '.git']
            ]

            for file in files:
                file_path = Path(root) / file
                self._process_file(file_path, repo_path, force)

        return {
            "capsules_created": self.capsules_created,
            "skipped": self.skipped,
            "errors": self.errors,
        }

    def _process_file(self, file_path: Path, repo_path: Path, force: bool = False) -> None:
        """
        Process a single file.

        Args:
            file_path: Path to the file
            repo_path: Root repository path
            force: Overwrite existing capsules
        """
        # Check extension
        ext = file_path.suffix.lower()
        if ext not in self.PARSERS:
            return

        # Skip if capsule exists and not forcing
        capsule_path = self._get_capsule_path(file_path, repo_path)
        if capsule_path.exists() and not force:
            self.skipped += 1
            return

        try:
            # Read file
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Skip empty files
            if not content.strip():
                self.skipped += 1
                return

            # Parse file
            parsed = self._parse_file(content, ext)

            # Create capsule
            capsule = self._create_capsule(file_path, repo_path, parsed, content)

            # Write capsule
            capsule_path.parent.mkdir(parents=True, exist_ok=True)
            capsule_path.write_text(json.dumps(capsule, indent=2))

            self.capsules_created += 1

        except Exception as e:
            self.errors += 1
            print(f"  ❌ Error processing {file_path}: {e}")

    def _get_capsule_path(self, file_path: Path, repo_path: Path) -> Path:
        """
        Get capsule output path.

        Args:
            file_path: Path to the file
            repo_path: Root repository path

        Returns:
            Path to capsule file
        """
        rel_path = file_path.relative_to(repo_path)
        capsule_name = f"{rel_path.name}.scp.json"
        return self.output_dir / str(rel_path.parent) / capsule_name

    def _parse_file(self, content: str, ext: str) -> Dict[str, Any]:
        """
        Parse file content based on language.

        Args:
            content: File content
            ext: File extension

        Returns:
            Parsed data dict
        """
        lang = self.PARSERS.get(ext, "unknown")

        if lang == "python":
            return self._parse_python(content)
        elif lang in ["javascript", "typescript"]:
            return self._parse_javascript(content)
        elif lang in ["c", "cpp"]:
            return self._parse_c(content)
        else:
            return self._parse_generic(content)

    def _parse_python(self, content: str) -> Dict[str, Any]:
        """Parse Python file."""
        imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
        functions = re.findall(r'^def\s+([a-zA-Z0-9_]+)\s*\(', content, re.MULTILINE)
        classes = re.findall(r'^class\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)

        # Try to find docstring
        docstring = re.search(r'"""(.*?)"""', content, re.DOTALL)
        docstring = docstring.group(1).strip() if docstring else ""

        return {
            "language": "python",
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "docstring": docstring,
            "lines": len(content.split('\n')),
        }

    def _parse_javascript(self, content: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript file."""
        imports = re.findall(r'^(?:import|require)\s*\(?([\'"])([^\'"]+)\1', content, re.MULTILINE)
        exports = re.findall(r'^export\s+(?:default\s+)?(?:function|class|const|let)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
        functions = re.findall(r'^function\s+([a-zA-Z0-9_]+)\s*\(', content, re.MULTILINE)

        return {
            "language": "javascript",
            "imports": [imp[1] for imp in imports],
            "exports": exports,
            "functions": functions,
            "lines": len(content.split('\n')),
        }

    def _parse_c(self, content: str) -> Dict[str, Any]:
        """Parse C/C++ file."""
        includes = re.findall(r'^#include\s*[<"]([^>"]+)[>"]', content, re.MULTILINE)
        functions = re.findall(r'^[a-zA-Z_][a-zA-Z0-9_]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content, re.MULTILINE)

        return {
            "language": "c",
            "includes": includes,
            "functions": functions,
            "lines": len(content.split('\n')),
        }

    def _parse_generic(self, content: str) -> Dict[str, Any]:
        """Parse generic file."""
        return {
            "language": "unknown",
            "lines": len(content.split('\n')),
            "size": len(content),
        }

    def _create_capsule(
        self,
        file_path: Path,
        repo_path: Path,
        parsed: Dict[str, Any],
        content: str
    ) -> Dict[str, Any]:
        """
        Create an SCP capsule from parsed content.

        Args:
            file_path: Path to the file
            repo_path: Root repository path
            parsed: Parsed data dict
            content: Raw file content

        Returns:
            SCP capsule dict
        """
        rel_path = str(file_path.relative_to(repo_path))

        # Generate scp_id
        scp_id = f"mimir/{rel_path.replace('/', '.')}"

        # Determine intent
        intent = self._infer_intent(parsed)

        # Build capsule
        capsule = {
            "scp_version": "0.1",
            "scp_id": scp_id,
            "object_class": "Safe",
            "intent": intent,
            "containment": {
                "read_only": True,
                "audit_log": True,
                "kill_switch": False
            },
            "content": {
                "language": parsed.get("language", "unknown"),
                "lines": parsed.get("lines", 0),
                "exports": parsed.get("exports", parsed.get("functions", [])),
                "imports": parsed.get("imports", parsed.get("includes", [])),
                "classes": parsed.get("classes", []),
                "docstring": parsed.get("docstring", ""),
                "summary": self._generate_summary(parsed),
            },
            "provenance": {
                "source_file": rel_path,
                "repo": str(repo_path.name),
                "ingested": datetime.utcnow().isoformat() + "Z",
                "hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            },
            "_trust": 1.0,  # Initial neutral trust
        }

        return capsule

    def _infer_intent(self, parsed: Dict[str, Any]) -> str:
        """
        Infer intent from parsed content.

        Args:
            parsed: Parsed data dict

        Returns:
            Intent string
        """
        if parsed.get("classes"):
            return f"Provides {', '.join(parsed['classes'][:3])} classes"
        elif parsed.get("functions"):
            return f"Provides functions: {', '.join(parsed['functions'][:3])}"
        elif parsed.get("exports"):
            return f"Exports: {', '.join(parsed['exports'][:3])}"
        else:
            return f"Source file ({parsed.get('language', 'unknown')})"

    def _generate_summary(self, parsed: Dict[str, Any]) -> str:
        """
        Generate a summary from parsed content.

        Args:
            parsed: Parsed data dict

        Returns:
            Summary string
        """
        parts = []
        if parsed.get("language"):
            parts.append(f"Language: {parsed['language']}")
        if parsed.get("functions"):
            parts.append(f"Functions: {', '.join(parsed['functions'][:5])}")
        if parsed.get("classes"):
            parts.append(f"Classes: {', '.join(parsed['classes'][:3])}")
        if parsed.get("imports"):
            parts.append(f"Dependencies: {', '.join(parsed['imports'][:3])}")
        return "; ".join(parts) if parts else "No summary available"


def ingest_repo(
    repo_path: Union[str, Path],
    output_dir: str = "capsules",
    force: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to ingest a repository.

    Args:
        repo_path: Path to repository
        output_dir: Output directory for capsules
        force: Overwrite existing capsules

    Returns:
        Stats dict
    """
    ingester = MimirIngest(output_dir)
    return ingester.ingest(repo_path, force)


# ============================================================
# CLI
# ============================================================

def main():
    """Test ingestion."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Mimir — Codebase Ingestion")
    parser.add_argument("repo", type=str, help="Repository path")
    parser.add_argument("--output", "-o", type=str, default="capsules", help="Output directory")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing")

    args = parser.parse_args()

    print("🔍 Mimir — Codebase Ingestion")
    print("=" * 60)

    result = ingest_repo(args.repo, args.output, args.force)

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)

    print(f"\n📊 Results:")
    print(f"   Capsules created: {result.get('capsules_created', 0)}")
    print(f"   Skipped: {result.get('skipped', 0)}")
    print(f"   Errors: {result.get('errors', 0)}")


if __name__ == "__main__":
    main()