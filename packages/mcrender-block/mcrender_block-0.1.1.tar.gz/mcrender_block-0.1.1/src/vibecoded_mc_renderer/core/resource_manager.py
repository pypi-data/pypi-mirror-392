"""Resource manager for handling Minecraft jar files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from zipfile import ZipFile
from io import BytesIO


class ResourceManager:
    """Manages resources from Minecraft jar files."""

    def __init__(self, jar_paths: List[Path]):
        """
        Initialize the resource manager with jar file paths.

        Args:
            jar_paths: List of paths to Minecraft jar files (vanilla or mods)
        """
        self.jar_paths = [Path(p) for p in jar_paths]
        self.archives: List[ZipFile] = []
        self.resource_index: Dict[str, ZipFile] = {}

        # Open all jar files
        for jar_path in self.jar_paths:
            if not jar_path.exists():
                raise FileNotFoundError(f"Jar file not found: {jar_path}")
            archive = ZipFile(jar_path, "r")
            self.archives.append(archive)

        # Build resource index
        self._build_index()

    def _build_index(self) -> None:
        """Build an index of all resources in the jar files."""
        for archive in self.archives:
            for name in archive.namelist():
                # Store the last occurrence (mods can override vanilla resources)
                self.resource_index[name] = archive

    def get_resource(self, resource_path: str) -> Optional[bytes]:
        """
        Get raw bytes of a resource from the jar files.

        Args:
            resource_path: Path within the jar (e.g., "assets/minecraft/textures/block/stone.png")

        Returns:
            Raw bytes of the resource, or None if not found
        """
        if resource_path in self.resource_index:
            archive = self.resource_index[resource_path]
            try:
                return archive.read(resource_path)
            except KeyError:
                pass
        return None

    def get_json(self, resource_path: str) -> Optional[Dict]:
        """
        Get and parse a JSON resource from the jar files.

        Args:
            resource_path: Path within the jar to a JSON file

        Returns:
            Parsed JSON as dictionary, or None if not found
        """
        data = self.get_resource(resource_path)
        if data:
            try:
                return json.loads(data.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        return None

    def list_blockstates(self) -> List[str]:
        """
        List all available blockstates in the jar files.

        Returns:
            List of block IDs (e.g., ["minecraft:stone", "minecraft:dirt"])
        """
        blockstates = set()
        for path in self.resource_index.keys():
            if path.startswith("assets/") and "/blockstates/" in path and path.endswith(".json"):
                # Parse path: assets/<namespace>/blockstates/<block_name>.json
                parts = path.split("/")
                if len(parts) >= 4:
                    namespace = parts[1]
                    block_name = parts[3].replace(".json", "")
                    blockstates.add(f"{namespace}:{block_name}")
        return sorted(blockstates)

    def list_namespaces(self) -> Set[str]:
        """
        List all namespaces in the jar files.

        Returns:
            Set of namespaces (e.g., {"minecraft", "create", "thermal"})
        """
        namespaces = set()
        for path in self.resource_index.keys():
            if path.startswith("assets/"):
                parts = path.split("/")
                if len(parts) >= 2:
                    namespaces.add(parts[1])
        return namespaces

    def resource_exists(self, resource_path: str) -> bool:
        """
        Check if a resource exists in the jar files.

        Args:
            resource_path: Path within the jar

        Returns:
            True if the resource exists
        """
        return resource_path in self.resource_index

    def close(self) -> None:
        """Close all open jar files."""
        for archive in self.archives:
            archive.close()
        self.archives.clear()
        self.resource_index.clear()

    def __enter__(self) -> "ResourceManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()

    def __del__(self) -> None:
        """Destructor to ensure jar files are closed."""
        self.close()
