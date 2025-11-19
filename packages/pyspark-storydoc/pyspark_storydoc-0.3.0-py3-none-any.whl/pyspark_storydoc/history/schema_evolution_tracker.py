"""
Schema Evolution Tracker for monitoring schema changes over time.

This module provides capabilities for tracking and reporting on schema evolution:
- Detect schema changes between snapshots (additions, removals, type changes)
- Classify changes as breaking vs non-breaking
- Generate comprehensive schema evolution reports
- Track schema timeline and version history

Example:
    >>> from pyspark_storydoc.history import LineageHistory, SchemaEvolutionTracker
    >>>
    >>> history = LineageHistory(table_path="./lineage_history")
    >>> tracker = SchemaEvolutionTracker(history)
    >>>
    >>> # Detect schema changes
    >>> snapshots = history.list_snapshots(pipeline_name="customer_pipeline")
    >>> changes = tracker.detect_schema_changes(snapshots[0], snapshots[1])
    >>>
    >>> # Generate evolution report
    >>> report_path = tracker.generate_evolution_report(
    ...     pipeline_name="customer_pipeline",
    ...     output_dir="./schema_reports"
    ... )
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of schema changes."""
    COLUMN_ADDED = "column_added"
    COLUMN_REMOVED = "column_removed"
    TYPE_CHANGED = "type_changed"
    NULLABILITY_CHANGED = "nullability_changed"
    COLUMN_RENAMED = "column_renamed"


class ImpactLevel(Enum):
    """Impact level of schema changes."""
    NON_BREAKING = "non_breaking"
    POTENTIALLY_BREAKING = "potentially_breaking"
    BREAKING = "breaking"


@dataclass
class SchemaChange:
    """
    Represents a detected schema change.

    Attributes:
        change_type: Type of change (added, removed, type changed, etc.)
        column_name: Name of the affected column
        old_value: Previous value (type, nullability, etc.)
        new_value: New value
        impact: Impact level (breaking, non-breaking, potentially breaking)
        description: Human-readable description of the change
    """
    change_type: ChangeType
    column_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    impact: ImpactLevel
    description: str


class SchemaEvolutionTracker:
    """
    Track and analyze schema evolution in data pipelines.

    This tracker analyzes lineage history to detect schema changes,
    classify their impact, and generate comprehensive reports.
    """

    def __init__(self, history):
        """
        Initialize the schema evolution tracker.

        Args:
            history: LineageHistory instance for querying snapshots
        """
        self.history = history

    def detect_schema_changes(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[SchemaChange]:
        """
        Detect schema changes between two snapshots.

        Args:
            snapshot_a: Older snapshot
            snapshot_b: Newer snapshot

        Returns:
            List of detected schema changes
        """
        logger.info(
            f"Detecting schema changes between snapshots: "
            f"{snapshot_a.get('snapshot_id', 'unknown')} → {snapshot_b.get('snapshot_id', 'unknown')}"
        )

        # Extract schemas from snapshots
        schema_a = self._extract_schema(snapshot_a)
        schema_b = self._extract_schema(snapshot_b)

        changes = []

        # Detect additions and modifications
        for col_name, col_info_b in schema_b.items():
            if col_name not in schema_a:
                # Column added
                changes.append(SchemaChange(
                    change_type=ChangeType.COLUMN_ADDED,
                    column_name=col_name,
                    old_value=None,
                    new_value=col_info_b['type'],
                    impact=ImpactLevel.NON_BREAKING,
                    description=f"Column '{col_name}' added with type {col_info_b['type']}",
                ))
            else:
                col_info_a = schema_a[col_name]

                # Check for type changes
                if col_info_a['type'] != col_info_b['type']:
                    impact = self._classify_type_change_impact(
                        col_info_a['type'],
                        col_info_b['type']
                    )
                    changes.append(SchemaChange(
                        change_type=ChangeType.TYPE_CHANGED,
                        column_name=col_name,
                        old_value=col_info_a['type'],
                        new_value=col_info_b['type'],
                        impact=impact,
                        description=f"Column '{col_name}' type changed from {col_info_a['type']} to {col_info_b['type']}",
                    ))

                # Check for nullability changes
                if col_info_a['nullable'] != col_info_b['nullable']:
                    impact = ImpactLevel.BREAKING if col_info_b['nullable'] is False else ImpactLevel.POTENTIALLY_BREAKING
                    changes.append(SchemaChange(
                        change_type=ChangeType.NULLABILITY_CHANGED,
                        column_name=col_name,
                        old_value=str(col_info_a['nullable']),
                        new_value=str(col_info_b['nullable']),
                        impact=impact,
                        description=f"Column '{col_name}' nullability changed from {col_info_a['nullable']} to {col_info_b['nullable']}",
                    ))

        # Detect removals
        for col_name in schema_a:
            if col_name not in schema_b:
                changes.append(SchemaChange(
                    change_type=ChangeType.COLUMN_REMOVED,
                    column_name=col_name,
                    old_value=schema_a[col_name]['type'],
                    new_value=None,
                    impact=ImpactLevel.BREAKING,
                    description=f"Column '{col_name}' removed (was {schema_a[col_name]['type']})",
                ))

        logger.info(f"Detected {len(changes)} schema changes")
        return changes

    def detect_breaking_changes(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[SchemaChange]:
        """
        Detect only breaking schema changes between snapshots.

        Args:
            snapshot_a: Older snapshot
            snapshot_b: Newer snapshot

        Returns:
            List of breaking schema changes only
        """
        all_changes = self.detect_schema_changes(snapshot_a, snapshot_b)
        breaking_changes = [
            change for change in all_changes
            if change.impact == ImpactLevel.BREAKING
        ]

        logger.info(f"Detected {len(breaking_changes)} breaking changes")
        return breaking_changes

    def get_schema_timeline(
        self,
        pipeline_name: str,
        operation_name: Optional[str] = None,
        lookback_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get schema evolution timeline for a pipeline.

        Args:
            pipeline_name: Name of the pipeline
            operation_name: Optional operation name to filter by
            lookback_days: Number of days to look back

        Returns:
            List of schema versions with timestamps
        """
        logger.info(f"Getting schema timeline for pipeline: {pipeline_name}")

        # Query snapshots
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        snapshots = self.history.list_snapshots(
            pipeline_name=pipeline_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            include_details=True,
        )

        timeline = []
        for snapshot in snapshots:
            schema = self._extract_schema(snapshot, operation_name)

            timeline.append({
                "snapshot_id": snapshot.get("snapshot_id", "unknown"),
                "timestamp": snapshot.get("captured_at", snapshot.get("timestamp", "unknown")),
                "version": snapshot.get("version", "unknown"),
                "column_count": len(schema),
                "columns": list(schema.keys()),
                "schema": schema,
            })

        logger.info(f"Retrieved {len(timeline)} schema versions")
        return timeline

    def generate_evolution_report(
        self,
        pipeline_name: str,
        output_dir: str,
        lookback_days: int = 30,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate a comprehensive schema evolution report.

        Args:
            pipeline_name: Name of the pipeline to analyze
            output_dir: Directory to write the report
            lookback_days: Number of days to look back in history
            filename: Output filename (default: schema_evolution_{pipeline_name}.md)

        Returns:
            Path to the generated report file
        """
        logger.info(f"Generating schema evolution report for pipeline: {pipeline_name}")

        # Query snapshots
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        snapshots = self.history.list_snapshots(
            pipeline_name=pipeline_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            include_details=True,
        )

        # Analyze all schema changes
        all_changes = []
        breaking_changes_list = []

        for i in range(len(snapshots) - 1):
            changes = self.detect_schema_changes(snapshots[i + 1], snapshots[i])
            all_changes.extend(changes)

            breaking = [c for c in changes if c.impact == ImpactLevel.BREAKING]
            breaking_changes_list.extend(breaking)

        # Generate report content
        content = self._generate_evolution_report_content(
            pipeline_name=pipeline_name,
            snapshots=snapshots,
            all_changes=all_changes,
            breaking_changes=breaking_changes_list,
            start_date=start_date,
            end_date=end_date,
        )

        # Write report
        if filename is None:
            filename = f"schema_evolution_{pipeline_name}.md"

        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Schema evolution report written to: {output_path}")
        return str(output_path)

    def _extract_schema(
        self,
        snapshot: Dict[str, Any],
        operation_name: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract schema information from a snapshot.

        Args:
            snapshot: Lineage snapshot
            operation_name: Optional operation name to filter by

        Returns:
            Dictionary mapping column names to type/nullability info
        """
        schema = {}

        # NEW APPROACH: Query lineage_operations table for this snapshot to get schema info
        snapshot_id = snapshot.get("snapshot_id")
        if snapshot_id and hasattr(self.history, 'spark') and self.history.spark:
            try:
                # Query operations table for this snapshot
                operations_df = self.history.spark.read.parquet(
                    f"{self.history.table_path}/lineage_operations"
                ).filter(f"snapshot_id = '{snapshot_id}'")

                # Find the first operation with non-empty columns_out
                operations = operations_df.collect()
                if operations:
                    # Find first operation with schema information
                    columns_out = []
                    for op in operations:
                        potential_cols = op.columns_out if op.columns_out else []
                        if potential_cols:
                            columns_out = potential_cols
                            break

                    if isinstance(columns_out, str):
                        try:
                            columns_out = json.loads(columns_out)
                        except (json.JSONDecodeError, TypeError):
                            columns_out = []

                    if isinstance(columns_out, list):
                        for col_info in columns_out:
                            if isinstance(col_info, dict):
                                # Direct dict format: dict with {name, type, nullable}
                                col_name = col_info.get("name", "unknown")
                                schema[col_name] = {
                                    "type": col_info.get("type", "string"),
                                    "nullable": col_info.get("nullable", True),
                                }
                            elif isinstance(col_info, str):
                                # Try to parse as JSON first (new storage format)
                                try:
                                    parsed = json.loads(col_info)
                                    if isinstance(parsed, dict):
                                        col_name = parsed.get("name", "unknown")
                                        schema[col_name] = {
                                            "type": parsed.get("type", "string"),
                                            "nullable": parsed.get("nullable", True),
                                        }
                                    else:
                                        # Not a dict - treat as column name
                                        schema[col_info] = {"type": "string", "nullable": True}
                                except (json.JSONDecodeError, TypeError):
                                    # Old format: just column names, assume string type
                                    schema[col_info] = {"type": "string", "nullable": True}

                    logger.debug(f"Extracted schema from operations table: {len(schema)} columns")

            except Exception as e:
                logger.debug(f"Could not extract schema from operations table: {e}")
                # Fall through to old method

        # FALLBACK: Try old method of extracting from lineage_graph
        if not schema:
            lineage_graph = snapshot.get("lineage_graph", {})

            # Handle JSON string
            if isinstance(lineage_graph, str):
                try:
                    lineage_graph = json.loads(lineage_graph)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse lineage_graph in snapshot {snapshot.get('snapshot_id')}")
                    lineage_graph = {}

            # Extract from graph nodes
            nodes = lineage_graph.get("nodes", [])
            if isinstance(nodes, dict):
                nodes_list = list(nodes.values())
            else:
                nodes_list = nodes

            for node_data in nodes_list:
                if operation_name:
                    if node_data.get("name") != operation_name:
                        continue

                columns = node_data.get("columns", [])
                if isinstance(columns, str):
                    try:
                        columns = json.loads(columns)
                    except json.JSONDecodeError:
                        columns = []

                if isinstance(columns, list):
                    for col in columns:
                        if isinstance(col, str):
                            schema[col] = {"type": "string", "nullable": True}
                        elif isinstance(col, dict):
                            col_name = col.get("name", col.get("column_name", "unknown"))
                            schema[col_name] = {
                                "type": col.get("type", col.get("data_type", "string")),
                                "nullable": col.get("nullable", True),
                            }

                schema_field = node_data.get("schema", {})
                if isinstance(schema_field, str):
                    try:
                        schema_field = json.loads(schema_field)
                    except json.JSONDecodeError:
                        schema_field = {}

                if isinstance(schema_field, dict):
                    for col_name, col_info in schema_field.items():
                        if col_name not in schema:
                            schema[col_name] = {
                                "type": col_info.get("type", "string") if isinstance(col_info, dict) else str(col_info),
                                "nullable": col_info.get("nullable", True) if isinstance(col_info, dict) else True,
                            }

        return schema

    def _classify_type_change_impact(self, old_type: str, new_type: str) -> ImpactLevel:
        """
        Classify the impact of a type change.

        Args:
            old_type: Previous type
            new_type: New type

        Returns:
            Impact level
        """
        # Normalize types
        old_type_normalized = old_type.lower().replace(" ", "")
        new_type_normalized = new_type.lower().replace(" ", "")

        # Check for widening conversions (safe, non-breaking)
        widening_conversions = [
            ("int", "long"),
            ("int", "bigint"),
            ("float", "double"),
            ("int", "decimal"),
            ("long", "decimal"),
            ("string", "text"),
        ]

        for from_type, to_type in widening_conversions:
            if from_type in old_type_normalized and to_type in new_type_normalized:
                return ImpactLevel.NON_BREAKING

        # Check for narrowing conversions (potentially breaking)
        narrowing_conversions = [
            ("long", "int"),
            ("bigint", "int"),
            ("double", "float"),
            ("decimal", "int"),
        ]

        for from_type, to_type in narrowing_conversions:
            if from_type in old_type_normalized and to_type in new_type_normalized:
                return ImpactLevel.BREAKING

        # Most type changes are potentially breaking
        return ImpactLevel.POTENTIALLY_BREAKING

    def _generate_evolution_report_content(
        self,
        pipeline_name: str,
        snapshots: List[Dict[str, Any]],
        all_changes: List[SchemaChange],
        breaking_changes: List[SchemaChange],
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        """Generate schema evolution report content."""
        lines = []

        # Header
        lines.append("# Schema Evolution Report")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc Schema Evolution Tracker*")
        lines.append("")

        # Metadata
        lines.append("## Report Metadata")
        lines.append("")
        lines.append(f"- **Pipeline Name:** {pipeline_name}")
        lines.append(f"- **Report Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **Snapshots Analyzed:** {len(snapshots)}")
        lines.append("")

        # Check if we have sufficient data
        if len(snapshots) < 2:
            lines.append("## Insufficient Data")
            lines.append("")
            lines.append("Not enough historical snapshots to analyze schema evolution.")
            lines.append(f"Found {len(snapshots)} snapshot(s), need at least 2.")
            lines.append("")
            return "\n".join(lines)

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")

        # Count changes by type and impact
        changes_by_type = {}
        for change in all_changes:
            change_type = change.change_type.value
            changes_by_type[change_type] = changes_by_type.get(change_type, 0) + 1

        changes_by_impact = {}
        for change in all_changes:
            impact = change.impact.value
            changes_by_impact[impact] = changes_by_impact.get(impact, 0) + 1

        lines.append(f"**Total Schema Changes:** {len(all_changes)}")
        lines.append(f"**Breaking Changes:** {len(breaking_changes)}")
        lines.append("")

        # Breaking changes warning
        if breaking_changes:
            lines.append("⚠️ **Warning:** Breaking changes detected! Review carefully before deployment.")
            lines.append("")

        # Changes by type
        lines.append("**Changes by Type:**")
        lines.append("")
        lines.append("| Change Type | Count |")
        lines.append("|-------------|-------|")
        for change_type, count in sorted(changes_by_type.items()):
            lines.append(f"| {change_type.replace('_', ' ').title()} | {count} |")
        lines.append("")

        # Changes by impact
        lines.append("**Changes by Impact:**")
        lines.append("")
        lines.append("| Impact Level | Count |")
        lines.append("|--------------|-------|")
        for impact, count in sorted(changes_by_impact.items()):
            icon = "✅" if impact == "non_breaking" else ("⚠️" if impact == "potentially_breaking" else "🚨")
            lines.append(f"| {icon} {impact.replace('_', ' ').title()} | {count} |")
        lines.append("")

        # Detailed Changes
        if all_changes:
            lines.append("## Detailed Schema Changes")
            lines.append("")

            # Group by change type
            for change_type in ChangeType:
                type_changes = [c for c in all_changes if c.change_type == change_type]
                if not type_changes:
                    continue

                lines.append(f"### {change_type.value.replace('_', ' ').title()}")
                lines.append("")

                lines.append("| Column | Old Value | New Value | Impact |")
                lines.append("|--------|-----------|-----------|--------|")

                for change in type_changes:
                    impact_icon = "✅" if change.impact == ImpactLevel.NON_BREAKING else (
                        "⚠️" if change.impact == ImpactLevel.POTENTIALLY_BREAKING else "🚨"
                    )
                    old_val = change.old_value or "-"
                    new_val = change.new_value or "-"

                    lines.append(f"| `{change.column_name}` | {old_val} | {new_val} | {impact_icon} {change.impact.value.replace('_', ' ').title()} |")

                lines.append("")

        # Schema Timeline
        lines.append("## Schema Timeline")
        lines.append("")

        lines.append("| Timestamp | Version | Column Count | Changes |")
        lines.append("|-----------|---------|--------------|---------|")

        for i, snapshot in enumerate(snapshots):
            timestamp = snapshot.get("captured_at", snapshot.get("timestamp", "Unknown"))
            version = snapshot.get("version", "unknown")
            schema = self._extract_schema(snapshot)
            col_count = len(schema)

            if i < len(snapshots) - 1:
                # Calculate changes from previous snapshot
                changes = self.detect_schema_changes(snapshots[i + 1], snapshots[i])
                change_summary = f"{len(changes)} change(s)"
            else:
                change_summary = "Baseline"

            lines.append(f"| {timestamp} | {version} | {col_count} | {change_summary} |")

        lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")

        if breaking_changes:
            lines.append("### ⚠️ Breaking Changes Require Action")
            lines.append("")
            lines.append("The following breaking changes have been detected:")
            lines.append("")

            for change in breaking_changes:
                lines.append(f"- **{change.column_name}:** {change.description}")

            lines.append("")
            lines.append("**Recommended Actions:**")
            lines.append("1. Review all downstream dependencies that rely on removed or changed columns")
            lines.append("2. Update data contracts and API documentation")
            lines.append("3. Implement data migration scripts if needed")
            lines.append("4. Consider deprecation period before removing columns")
            lines.append("5. Add backward compatibility layer if possible")
            lines.append("")

        else:
            lines.append("### ✅ No Breaking Changes Detected")
            lines.append("")
            lines.append("All schema changes are non-breaking. However, consider:")
            lines.append("")
            lines.append("1. Update documentation to reflect new columns")
            lines.append("2. Communicate changes to downstream consumers")
            lines.append("3. Monitor for potential data quality issues with new fields")
            lines.append("")

        return "\n".join(lines)
