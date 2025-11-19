"""
Compliance Audit Reporter for GDPR Article 30 and data governance.

This module provides reporting capabilities for compliance audits including:
- GDPR Article 30 Records of Processing Activities (RoPA)
- Data retention audit trails
- Cross-border data transfer documentation
- Governance completeness assessment

Example:
    >>> from pyspark_storydoc.history import LineageHistory, ComplianceAuditReporter
    >>>
    >>> history = LineageHistory(table_path="./lineage_history")
    >>> reporter = ComplianceAuditReporter(history)
    >>>
    >>> # Generate GDPR Article 30 report
    >>> report_path = reporter.generate_gdpr_article30_report(
    ...     pipeline_name="customer_processing",
    ...     output_dir="./compliance_reports",
    ...     data_controller="Acme Corporation Ltd"
    ... )
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ComplianceAuditReporter:
    """
    Generate compliance audit reports from lineage history.

    This reporter analyzes historical lineage snapshots to produce:
    1. GDPR Article 30 Records of Processing Activities
    2. Data retention and deletion audit trails
    3. Cross-border data transfer documentation
    4. Governance completeness assessments
    """

    def __init__(self, history):
        """
        Initialize the compliance audit reporter.

        Args:
            history: LineageHistory instance for querying snapshots
        """
        self.history = history

    def generate_gdpr_article30_report(
        self,
        pipeline_name: str,
        output_dir: str,
        data_controller: str = "Not Specified",
        lookback_days: int = 30,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate GDPR Article 30 Records of Processing Activities (RoPA) report.

        Args:
            pipeline_name: Name of the pipeline to audit
            output_dir: Directory to write the report
            data_controller: Name of the data controller organization
            lookback_days: Number of days to look back in history
            filename: Output filename (default: gdpr_article30_{pipeline_name}.md)

        Returns:
            Path to the generated report file
        """
        logger.info(f"Generating GDPR Article 30 report for pipeline: {pipeline_name}")

        # Query snapshots
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        snapshots = self.history.list_snapshots(
            pipeline_name=pipeline_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            include_details=True,
        )

        # Extract processing activities
        processing_activities = self._extract_processing_activities(snapshots)

        # Generate report content
        content = self._generate_gdpr_article30_content(
            pipeline_name=pipeline_name,
            data_controller=data_controller,
            processing_activities=processing_activities,
            start_date=start_date,
            end_date=end_date,
        )

        # Write report
        if filename is None:
            filename = f"gdpr_article30_{pipeline_name}.md"

        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"GDPR Article 30 report written to: {output_path}")
        return str(output_path)

    def generate_data_retention_audit(
        self,
        pipeline_name: str,
        output_dir: str,
        lookback_days: int = 30,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate data retention and deletion audit trail report.

        Args:
            pipeline_name: Name of the pipeline to audit
            output_dir: Directory to write the report
            lookback_days: Number of days to look back in history
            filename: Output filename (default: retention_audit_{pipeline_name}.md)

        Returns:
            Path to the generated report file
        """
        logger.info(f"Generating data retention audit for pipeline: {pipeline_name}")

        # Query snapshots
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        snapshots = self.history.list_snapshots(
            pipeline_name=pipeline_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            include_details=True,
        )

        # Analyze retention activities
        retention_activities = self._analyze_retention_activities(snapshots)

        # Generate report content
        content = self._generate_retention_audit_content(
            pipeline_name=pipeline_name,
            retention_activities=retention_activities,
            start_date=start_date,
            end_date=end_date,
        )

        # Write report
        if filename is None:
            filename = f"retention_audit_{pipeline_name}.md"

        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Retention audit report written to: {output_path}")
        return str(output_path)

    def generate_cross_border_transfer_report(
        self,
        pipeline_name: str,
        output_dir: str,
        lookback_days: int = 30,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate cross-border data transfer compliance report.

        Args:
            pipeline_name: Name of the pipeline to audit
            output_dir: Directory to write the report
            lookback_days: Number of days to look back in history
            filename: Output filename (default: cross_border_transfer_{pipeline_name}.md)

        Returns:
            Path to the generated report file
        """
        logger.info(f"Generating cross-border transfer report for pipeline: {pipeline_name}")

        # Query snapshots
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        snapshots = self.history.list_snapshots(
            pipeline_name=pipeline_name,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            include_details=True,
        )

        # Analyze cross-border transfers
        transfer_activities = self._analyze_cross_border_transfers(snapshots)

        # Generate report content
        content = self._generate_cross_border_content(
            pipeline_name=pipeline_name,
            transfer_activities=transfer_activities,
            start_date=start_date,
            end_date=end_date,
        )

        # Write report
        if filename is None:
            filename = f"cross_border_transfer_{pipeline_name}.md"

        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Cross-border transfer report written to: {output_path}")
        return str(output_path)

    def _extract_processing_activities(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract processing activities from snapshots.

        Args:
            snapshots: List of lineage snapshots

        Returns:
            List of processing activities with governance metadata
        """
        activities = []

        for snapshot in snapshots:
            # Get operations from snapshot
            operations = snapshot.get("operations", [])

            # Handle case where operations might be a JSON string
            if isinstance(operations, str):
                try:
                    operations = json.loads(operations)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse operations JSON in snapshot {snapshot.get('snapshot_id')}")
                    operations = []

            # CRITICAL FIX: Get governance data from separate table and create lookup
            governance_records = snapshot.get("governance", [])
            if isinstance(governance_records, str):
                try:
                    governance_records = json.loads(governance_records)
                except json.JSONDecodeError:
                    governance_records = []

            # Create governance lookup by operation_id
            governance_by_op = {}
            for gov_record in governance_records:
                op_id = gov_record.get("operation_id")
                if op_id:
                    governance_by_op[op_id] = gov_record

            for operation in operations:
                # Extract governance metadata from operation or lookup
                governance = operation.get("governance_metadata", {})

                # Handle case where governance might be a JSON string
                if isinstance(governance, str):
                    try:
                        governance = json.loads(governance)
                    except json.JSONDecodeError:
                        governance = {}

                # CRITICAL FIX: If no governance in operation, check governance table
                if not governance:
                    op_id = operation.get("operation_id")
                    if op_id and op_id in governance_by_op:
                        governance = governance_by_op[op_id]

                activity = {
                    "operation_name": operation.get("name", "Unknown Operation"),
                    "business_concept": operation.get("business_concept", ""),
                    "purpose": governance.get("business_justification", "Not documented"),
                    "legal_basis": governance.get("legal_basis", "Not documented"),
                    "retention_period": governance.get("retention_period", "Not documented"),
                    "recipients": governance.get("recipients", []),
                    "data_location": governance.get("data_location", "Not documented"),
                    "transfer_mechanism": governance.get("transfer_mechanism", "N/A"),
                    "compliance_status": governance.get("compliance_status", "Not documented"),
                    "regulatory_framework": governance.get("regulatory_framework", "Not specified"),
                    "timestamp": snapshot.get("captured_at", snapshot.get("timestamp", "Unknown")),
                }

                activities.append(activity)

        return activities

    def _analyze_retention_activities(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze data retention and deletion activities from snapshots.

        Args:
            snapshots: List of lineage snapshots

        Returns:
            List of retention-related activities
        """
        retention_activities = []

        for snapshot in snapshots:
            operations = snapshot.get("operations", [])

            # Handle JSON string operations
            if isinstance(operations, str):
                try:
                    operations = json.loads(operations)
                except json.JSONDecodeError:
                    operations = []

            for operation in operations:
                op_name = operation.get("name", "").lower()
                business_concept = operation.get("business_concept", "").lower()

                # Identify retention-related operations
                retention_keywords = ["archive", "delete", "purge", "retain", "expire", "cleanup"]
                if any(keyword in op_name or keyword in business_concept for keyword in retention_keywords):
                    governance = operation.get("governance_metadata", {})

                    # Handle JSON string governance
                    if isinstance(governance, str):
                        try:
                            governance = json.loads(governance)
                        except json.JSONDecodeError:
                            governance = {}

                    activity = {
                        "operation": operation.get("name", "Unknown"),
                        "action_type": self._classify_retention_action(op_name, business_concept),
                        "retention_period": governance.get("retention_period", "Not specified"),
                        "timestamp": snapshot.get("captured_at", snapshot.get("timestamp", "Unknown")),
                        "compliance_framework": governance.get("regulatory_framework", "Not specified"),
                    }

                    retention_activities.append(activity)

        return retention_activities

    def _analyze_cross_border_transfers(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze cross-border data transfer activities.

        Args:
            snapshots: List of lineage snapshots

        Returns:
            List of cross-border transfer activities
        """
        transfer_activities = []

        for snapshot in snapshots:
            operations = snapshot.get("operations", [])

            # Handle JSON string operations
            if isinstance(operations, str):
                try:
                    operations = json.loads(operations)
                except json.JSONDecodeError:
                    operations = []

            for operation in operations:
                governance = operation.get("governance_metadata", {})

                # Handle JSON string governance
                if isinstance(governance, str):
                    try:
                        governance = json.loads(governance)
                    except json.JSONDecodeError:
                        governance = {}

                # Check if transfer mechanism is documented (indicates cross-border transfer)
                transfer_mechanism = governance.get("transfer_mechanism", "")
                data_location = governance.get("data_location", "")

                if transfer_mechanism and transfer_mechanism != "N/A":
                    activity = {
                        "operation": operation.get("name", "Unknown"),
                        "business_concept": operation.get("business_concept", ""),
                        "data_location": data_location,
                        "transfer_mechanism": transfer_mechanism,
                        "recipients": governance.get("recipients", []),
                        "legal_basis": governance.get("legal_basis", "Not documented"),
                        "timestamp": snapshot.get("captured_at", snapshot.get("timestamp", "Unknown")),
                    }

                    transfer_activities.append(activity)

        return transfer_activities

    def _classify_retention_action(self, op_name: str, business_concept: str) -> str:
        """
        Classify the type of retention action.

        Args:
            op_name: Operation name
            business_concept: Business concept name

        Returns:
            Classification string
        """
        combined = f"{op_name} {business_concept}".lower()

        if "delete" in combined or "purge" in combined:
            return "Deletion"
        elif "archive" in combined:
            return "Archival"
        elif "retain" in combined:
            return "Retention"
        elif "expire" in combined:
            return "Expiration"
        elif "cleanup" in combined:
            return "Cleanup"
        else:
            return "Other"

    def _calculate_completeness_score(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate governance documentation completeness score.

        Args:
            activities: List of processing activities

        Returns:
            Dictionary with completeness metrics
        """
        if not activities:
            return {
                "total_activities": 0,
                "purpose_documented": 0,
                "legal_basis_documented": 0,
                "retention_documented": 0,
                "recipients_documented": 0,
                "location_documented": 0,
                "completeness_percentage": 0.0,
            }

        total = len(activities)
        purpose_count = sum(1 for a in activities if a["purpose"] != "Not documented")
        legal_basis_count = sum(1 for a in activities if a["legal_basis"] != "Not documented")
        retention_count = sum(1 for a in activities if a["retention_period"] != "Not documented")
        recipients_count = sum(1 for a in activities if a["recipients"])
        location_count = sum(1 for a in activities if a["data_location"] != "Not documented")

        # Calculate overall completeness (out of 5 key fields)
        total_fields = total * 5
        documented_fields = (
            purpose_count + legal_basis_count + retention_count +
            recipients_count + location_count
        )

        completeness_pct = (documented_fields / total_fields * 100) if total_fields > 0 else 0.0

        return {
            "total_activities": total,
            "purpose_documented": purpose_count,
            "legal_basis_documented": legal_basis_count,
            "retention_documented": retention_count,
            "recipients_documented": recipients_count,
            "location_documented": location_count,
            "completeness_percentage": completeness_pct,
        }

    def _generate_gdpr_article30_content(
        self,
        pipeline_name: str,
        data_controller: str,
        processing_activities: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        """Generate GDPR Article 30 report content."""
        lines = []

        # Header
        lines.append("# GDPR Article 30 - Records of Processing Activities")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc Compliance Audit Reporter*")
        lines.append("")

        # Metadata
        lines.append("## Report Metadata")
        lines.append("")
        lines.append(f"- **Data Controller:** {data_controller}")
        lines.append(f"- **Pipeline Name:** {pipeline_name}")
        lines.append(f"- **Report Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Check if we have data
        if not processing_activities:
            lines.append("## No Data Available")
            lines.append("")
            lines.append("No processing activities found for the specified pipeline and time period.")
            lines.append("")
            lines.append("**Possible reasons:**")
            lines.append("- Pipeline has not been executed during the report period")
            lines.append("- Governance metadata was not attached to operations")
            lines.append("- History tracking was not enabled")
            lines.append("")
            return "\n".join(lines)

        # Compliance Assessment
        completeness = self._calculate_completeness_score(processing_activities)

        lines.append("## Compliance Assessment")
        lines.append("")
        lines.append(f"**Documentation Completeness: {completeness['completeness_percentage']:.1f}%**")
        lines.append("")
        lines.append("| Requirement | Documented | Total | Percentage |")
        lines.append("|-------------|------------|-------|------------|")
        lines.append(
            f"| Purpose Documented | {completeness['purpose_documented']} | "
            f"{completeness['total_activities']} | "
            f"{completeness['purpose_documented'] / max(completeness['total_activities'], 1) * 100:.0f}% |"
        )
        lines.append(
            f"| Legal Basis Documented | {completeness['legal_basis_documented']} | "
            f"{completeness['total_activities']} | "
            f"{completeness['legal_basis_documented'] / max(completeness['total_activities'], 1) * 100:.0f}% |"
        )
        lines.append(
            f"| Retention Period Specified | {completeness['retention_documented']} | "
            f"{completeness['total_activities']} | "
            f"{completeness['retention_documented'] / max(completeness['total_activities'], 1) * 100:.0f}% |"
        )
        lines.append(
            f"| Recipients Listed | {completeness['recipients_documented']} | "
            f"{completeness['total_activities']} | "
            f"{completeness['recipients_documented'] / max(completeness['total_activities'], 1) * 100:.0f}% |"
        )
        lines.append(
            f"| Data Location Documented | {completeness['location_documented']} | "
            f"{completeness['total_activities']} | "
            f"{completeness['location_documented'] / max(completeness['total_activities'], 1) * 100:.0f}% |"
        )
        lines.append("")

        # Processing Activities
        lines.append("## Processing Activities")
        lines.append("")

        for i, activity in enumerate(processing_activities, 1):
            lines.append(f"### Activity {i}: {activity['operation_name']}")
            lines.append("")

            if activity['business_concept']:
                lines.append(f"**Business Concept:** {activity['business_concept']}")
                lines.append("")

            # Purpose
            lines.append("**Purpose:**")
            status = "✅" if activity['purpose'] != "Not documented" else "⚠️ requires review"
            lines.append(f"{status} {activity['purpose']}")
            lines.append("")

            # Legal Basis
            lines.append("**Legal Basis:**")
            status = "✅" if activity['legal_basis'] != "Not documented" else "⚠️ requires review"
            lines.append(f"{status} {activity['legal_basis']}")
            lines.append("")

            # Retention Period
            lines.append("**Retention Period:**")
            status = "✅" if activity['retention_period'] != "Not documented" else "⚠️ requires review"
            lines.append(f"{status} {activity['retention_period']}")
            lines.append("")

            # Recipients
            lines.append("**Recipients:**")
            if activity['recipients']:
                for recipient in activity['recipients']:
                    lines.append(f"- {recipient}")
            else:
                lines.append("⚠️ Not documented")
            lines.append("")

            # Data Location
            lines.append("**Data Location:**")
            status = "✅" if activity['data_location'] != "Not documented" else "⚠️ requires review"
            lines.append(f"{status} {activity['data_location']}")
            lines.append("")

            # Security Measures
            lines.append("**Security Measures:**")
            if activity.get('transfer_mechanism') and activity['transfer_mechanism'] != "N/A":
                lines.append(f"- Transfer Mechanism: {activity['transfer_mechanism']}")
            else:
                lines.append("⚠️ Not documented")
            lines.append("")

            # Compliance Status
            lines.append(f"**Regulatory Framework:** {activity['regulatory_framework']}")
            lines.append(f"**Compliance Status:** {activity['compliance_status']}")
            lines.append(f"**Last Updated:** {activity['timestamp']}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Recommendations
        if completeness['completeness_percentage'] < 100:
            lines.append("## Recommendations")
            lines.append("")
            lines.append("The following items require attention to achieve full GDPR Article 30 compliance:")
            lines.append("")

            if completeness['purpose_documented'] < completeness['total_activities']:
                lines.append("- **Purpose:** Document the purpose and business justification for all processing activities")

            if completeness['legal_basis_documented'] < completeness['total_activities']:
                lines.append("- **Legal Basis:** Specify the legal basis for processing (e.g., consent, contract, legitimate interest)")

            if completeness['retention_documented'] < completeness['total_activities']:
                lines.append("- **Retention Period:** Define retention periods for all data processing activities")

            if completeness['recipients_documented'] < completeness['total_activities']:
                lines.append("- **Recipients:** List all recipients of personal data")

            if completeness['location_documented'] < completeness['total_activities']:
                lines.append("- **Data Location:** Document where personal data is stored and processed")

            lines.append("")

        return "\n".join(lines)

    def _generate_retention_audit_content(
        self,
        pipeline_name: str,
        retention_activities: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        """Generate retention audit report content."""
        lines = []

        lines.append("# Data Retention and Deletion Audit Report")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc Compliance Audit Reporter*")
        lines.append("")

        lines.append("## Report Metadata")
        lines.append("")
        lines.append(f"- **Pipeline Name:** {pipeline_name}")
        lines.append(f"- **Report Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**Total Retention/Deletion Activities:** {len(retention_activities)}")
        lines.append("")

        if retention_activities:
            # Group by action type
            action_types = {}
            for activity in retention_activities:
                action = activity['action_type']
                action_types[action] = action_types.get(action, 0) + 1

            lines.append("**Activities by Type:**")
            lines.append("")
            for action, count in sorted(action_types.items()):
                lines.append(f"- {action}: {count}")
            lines.append("")

            # Activities table
            lines.append("## Retention and Deletion Activities")
            lines.append("")
            lines.append("| Timestamp | Operation | Action Type | Retention Period | Compliance Framework |")
            lines.append("|-----------|-----------|-------------|------------------|---------------------|")

            for activity in retention_activities:
                lines.append(
                    f"| {activity['timestamp']} | {activity['operation']} | "
                    f"{activity['action_type']} | {activity['retention_period']} | "
                    f"{activity['compliance_framework']} |"
                )

            lines.append("")
        else:
            lines.append("No retention or deletion activities found during the report period.")
            lines.append("")

        return "\n".join(lines)

    def _generate_cross_border_content(
        self,
        pipeline_name: str,
        transfer_activities: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        """Generate cross-border transfer report content."""
        lines = []

        lines.append("# Cross-Border Data Transfer Compliance Report")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc Compliance Audit Reporter*")
        lines.append("")

        lines.append("## Report Metadata")
        lines.append("")
        lines.append(f"- **Pipeline Name:** {pipeline_name}")
        lines.append(f"- **Report Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**Total Cross-Border Transfer Activities:** {len(transfer_activities)}")
        lines.append("")

        if transfer_activities:
            # Transfer Activities
            lines.append("## Transfer Activities")
            lines.append("")

            for i, activity in enumerate(transfer_activities, 1):
                lines.append(f"### Transfer {i}: {activity['operation']}")
                lines.append("")

                if activity['business_concept']:
                    lines.append(f"**Business Concept:** {activity['business_concept']}")
                    lines.append("")

                lines.append(f"**Data Location:** {activity['data_location']}")
                lines.append(f"**Transfer Mechanism:** {activity['transfer_mechanism']}")
                lines.append(f"**Legal Basis:** {activity['legal_basis']}")
                lines.append("")

                lines.append("**Recipients:**")
                if activity['recipients']:
                    for recipient in activity['recipients']:
                        lines.append(f"- {recipient}")
                else:
                    lines.append("- Not documented")
                lines.append("")

                lines.append(f"**Timestamp:** {activity['timestamp']}")
                lines.append("")
                lines.append("---")
                lines.append("")
        else:
            lines.append("No cross-border data transfer activities detected during the report period.")
            lines.append("")
            lines.append("**Note:** Cross-border transfers are identified by the presence of a transfer mechanism ")
            lines.append("in the governance metadata (e.g., Standard Contractual Clauses, Adequacy Decision).")
            lines.append("")

        return "\n".join(lines)
