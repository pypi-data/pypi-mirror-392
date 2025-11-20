"""
Compute Cluster Registry

Manages external compute cluster configurations for DVT.
Clusters are stored in .dvt/computes.yml.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from dbt.clients.yaml_helper import load_yaml_text
from dbt_common.clients.system import load_file_contents, write_file
from dbt_common.exceptions import DbtRuntimeError

# Default out-of-box compute engines
DEFAULT_COMPUTES = """# DVT Compute Engines Configuration
# This file defines compute engines for federated query execution

# Default compute engine for federated queries
target_compute: duckdb

# Available compute engines
computes:
  # DuckDB - Embedded engine (default)
  # Best for: Small-medium workloads, simple queries, < 5 sources
  # No setup required - works out of the box
  duckdb:
    type: duckdb
    config:
      memory_limit: "4GB"
      threads: 4
    description: "Embedded DuckDB engine for small-medium workloads"

  # Spark Local - Local Spark cluster
  # Best for: Large workloads (>1GB), complex queries, many sources
  # Requires: Spark installation
  spark-local:
    type: spark
    config:
      master: "local[*]"
      app_name: "dvt-spark-local"
      spark.driver.memory: "4g"
      spark.executor.memory: "4g"
    description: "Local Spark cluster for development and testing"

# Add more compute engines with 'dvt compute add'
"""


@dataclass
class ComputeCluster:
    """Configuration for an external compute cluster."""

    name: str  # Cluster identifier
    type: str  # 'spark' (currently only Spark supported for external)
    config: Dict[str, Any] = field(default_factory=dict)  # Cluster-specific config
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = {
            "name": self.name,
            "type": self.type,
            "config": self.config,
        }
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComputeCluster":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            type=data["type"],
            config=data.get("config", {}),
            description=data.get("description")
        )


class ComputeRegistry:
    """
    Registry for managing external compute clusters.

    Clusters are stored in .dvt/computes.yml.
    """

    def __init__(self, project_dir: str):
        """
        Initialize compute registry.

        :param project_dir: Path to project root directory
        """
        self.project_dir = project_dir
        self.dvt_dir = os.path.join(project_dir, ".dvt")
        self.compute_file = os.path.join(self.dvt_dir, "computes.yml")
        self._clusters: Dict[str, ComputeCluster] = {}
        self._target_compute: Optional[str] = None
        self._load()

    def _load(self) -> None:
        """Load clusters from .dvt/computes.yml."""
        if not os.path.exists(self.compute_file):
            # No computes.yml - use defaults
            self._load_defaults()
            return

        try:
            contents = load_file_contents(self.compute_file, strip=False)
            yaml_content = load_yaml_text(contents)

            if not yaml_content:
                self._load_defaults()
                return

            # Parse target_compute (default compute engine)
            self._target_compute = yaml_content.get("target_compute", "duckdb")

            # Parse computes (new format)
            computes_data = yaml_content.get("computes", {})
            for name, cluster_data in computes_data.items():
                cluster_data["name"] = name  # Add name to data
                cluster = ComputeCluster.from_dict(cluster_data)
                self._clusters[cluster.name] = cluster

            # Legacy format support: "clusters" list
            if not computes_data and "clusters" in yaml_content:
                clusters_data = yaml_content.get("clusters", [])
                for cluster_data in clusters_data:
                    cluster = ComputeCluster.from_dict(cluster_data)
                    self._clusters[cluster.name] = cluster

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to load .dvt/computes.yml: {str(e)}"
            ) from e

    def _load_defaults(self) -> None:
        """Load default out-of-box compute engines."""
        yaml_content = load_yaml_text(DEFAULT_COMPUTES)

        self._target_compute = yaml_content.get("target_compute", "duckdb")

        computes_data = yaml_content.get("computes", {})
        for name, cluster_data in computes_data.items():
            cluster_data["name"] = name
            cluster = ComputeCluster.from_dict(cluster_data)
            self._clusters[cluster.name] = cluster

    def _save(self) -> None:
        """Save clusters to .dvt/computes.yml."""
        # Ensure .dvt directory exists
        os.makedirs(self.dvt_dir, exist_ok=True)

        # Build computes dict (new format)
        computes_dict = {}
        for cluster in self._clusters.values():
            cluster_dict = cluster.to_dict()
            cluster_dict.pop("name")  # Don't duplicate name in value
            computes_dict[cluster.name] = cluster_dict

        yaml_content = {
            "target_compute": self._target_compute or "duckdb",
            "computes": computes_dict
        }

        # Convert to YAML string
        import yaml
        yaml_str = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)

        # Write to file
        write_file(self.compute_file, yaml_str)

    @property
    def target_compute(self) -> str:
        """Get the default target compute engine."""
        return self._target_compute or "duckdb"

    @target_compute.setter
    def target_compute(self, value: str) -> None:
        """Set the default target compute engine."""
        if value not in self._clusters:
            raise DbtRuntimeError(
                f"Cannot set target_compute to '{value}': compute engine not found. "
                f"Available engines: {', '.join(self._clusters.keys())}"
            )
        self._target_compute = value
        self._save()

    def register(
        self,
        name: str,
        cluster_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        replace: bool = False
    ) -> None:
        """
        Register a new compute cluster.

        :param name: Cluster name (must be unique)
        :param cluster_type: Type of cluster ('spark')
        :param config: Cluster configuration dict
        :param description: Optional cluster description
        :param replace: If True, replace existing cluster with same name
        :raises DbtRuntimeError: If cluster exists and replace=False
        """
        if name in self._clusters and not replace:
            raise DbtRuntimeError(
                f"Compute cluster '{name}' already exists. Use replace=True to overwrite."
            )

        if cluster_type not in ("spark",):
            raise DbtRuntimeError(
                f"Unsupported cluster type '{cluster_type}'. Supported types: spark"
            )

        cluster = ComputeCluster(
            name=name,
            type=cluster_type,
            config=config,
            description=description
        )

        self._clusters[name] = cluster
        self._save()

    def remove(self, name: str) -> None:
        """
        Remove a compute cluster.

        :param name: Cluster name
        :raises DbtRuntimeError: If cluster not found
        """
        if name not in self._clusters:
            raise DbtRuntimeError(f"Compute cluster '{name}' not found")

        del self._clusters[name]
        self._save()

    def get(self, name: str) -> Optional[ComputeCluster]:
        """
        Get a compute cluster by name.

        :param name: Cluster name
        :returns: ComputeCluster or None if not found
        """
        return self._clusters.get(name)

    def list(self) -> List[ComputeCluster]:
        """
        List all registered clusters.

        :returns: List of ComputeCluster objects
        """
        return list(self._clusters.values())

    def exists(self, name: str) -> bool:
        """
        Check if a cluster exists.

        :param name: Cluster name
        :returns: True if cluster exists
        """
        return name in self._clusters

    @staticmethod
    def initialize_default_computes(project_dir: str) -> None:
        """
        Initialize .dvt/computes.yml with default out-of-box engines.

        :param project_dir: Path to project root directory
        """
        dvt_dir = os.path.join(project_dir, ".dvt")
        compute_file = os.path.join(dvt_dir, "computes.yml")

        # Create .dvt directory if it doesn't exist
        os.makedirs(dvt_dir, exist_ok=True)

        # Write default computes.yml if it doesn't exist
        if not os.path.exists(compute_file):
            write_file(compute_file, DEFAULT_COMPUTES)
