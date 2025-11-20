"""
AcknowledgeManager - Firestore-backed acknowledgment tracking for test issues.

New structure (no backward compatibility to the old map-based layout):

- One **document per test**: {repo}%{pipeline}%{test_name}
- One **subcollection per test**: `issues`
- One **document per issue** within that subcollection:

  Collection: pipeline_acknowledgments
  └── Document: {repo}%{pipeline}%{test_name}
      └── Subcollection: issues
          └── Document: {issue_key_simple}
              - acknowledged: bool
              - muted_until: timestamp (UTC)
              - identifier: str
              - details: str
              - issue_first_occurrence: timestamp (UTC)
              - issue_last_occurrence: timestamp (UTC)
              - issue_owner: str (defaults to 'analytic_hub.data_team_ack')
              - acknowledged_by / acknowledged_at / acknowledgment_reason
              - any pipeline-specific additional metadata (free-form fields)
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from google.cloud import firestore


class AcknowledgeManager:
    """
    Ultra-simple acknowledgment manager with minimal Firestore structure.
    
    Firestore Structure:
    Collection: pipeline_acknowledgments
    └── Document: {repo}%{pipeline}%{test_name}
        └── issues: {
            "issue1": {
                "acknowledged": true/false,
                "muted_until": timestamp,
                "identifier": "user@email.com",
                "details": "xxx hours expected, xx found"
            },
            "issue2": { ... }
        }
    """
    
    def __init__(
        self,
        firestore_client: firestore.Client,
        repository_name: str,
        pipeline_name: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the AcknowledgeManager.
        
        Args:
            firestore_client: Firestore client instance
            repository_name: Name of the repository (e.g., 'locate_2_pulls')
            pipeline_name: Name of the pipeline (e.g., 'capacity_tracker_linguists_days_off')
        """
        self.firestore_client = firestore_client
        self.repository_name = repository_name
        self.pipeline_name = pipeline_name

        # Acknowledgment-related configuration (all overridable via Firestore config)
        ack_cfg = (config or {}).get("acknowledgments", {})

        # Firestore collection that stores per-test documents
        self.collection = ack_cfg.get("collection_name", "pipeline_acknowledgments")
        # Name of the per-test subcollection that stores per-issue documents
        self.issue_subcollection_name = ack_cfg.get("issue_subcollection_name", "issues")

        # Default behavior knobs
        self.default_mute_days = ack_cfg.get("default_mute_days", 7)
        self.max_emails_per_day = ack_cfg.get("max_emails_per_day", 1)
    
    def _generate_document_id(self, test_name: str) -> str:
        """
        Generate document ID for a given test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            Document ID in format: {repo}%{pipeline}%{test_name}
        """
        return f"{self.repository_name}%{self.pipeline_name}%{test_name}"
    
    
    def check_issue_acknowledged(self, test_name: str, issue_identifier: str) -> bool:
        """
        Check if specific issue is acknowledged and still muted.
        
        Args:
            test_name: Name of the test
            issue_identifier: Primary identifier (email, ID, combination, etc.)
            
        Returns:
            True if issue is acknowledged and still muted, False otherwise
        """
        try:
            # Generate document ID for the test
            doc_id = self._generate_document_id(test_name)
            # Use subcollection `issues` with one document per issue
            # Create issue key (simple identifier)
            issue_key_simple = str(issue_identifier).lower().strip()
            issue_doc_ref = (
                self.firestore_client.collection(self.collection)
                .document(doc_id)
                .collection(self.issue_subcollection_name)
                .document(issue_key_simple)
            )
            issue_doc = issue_doc_ref.get()
            if not issue_doc.exists:
                return False
            
            issue = issue_doc.to_dict() or {}
            
            if not issue.get('acknowledged', False):
                return False
            
            # Check if mute period has expired
            mute_until = issue.get('muted_until')  # Fixed: use 'muted_until' not 'mute_until'
            if not mute_until:
                return False
            
            # Convert Firestore timestamp to datetime if needed
            if hasattr(mute_until, 'timestamp'):
                mute_until = datetime.fromtimestamp(mute_until.timestamp(), tz=timezone.utc)
            elif isinstance(mute_until, str):
                mute_until = datetime.fromisoformat(mute_until.replace('Z', '+00:00'))
            
            current_time = datetime.now(timezone.utc)
            return current_time < mute_until
            
        except Exception as e:
            print(f"Warning: Error checking acknowledgment status: {e}")
            return False
    
    def acknowledge_issue(self, test_name: str, issue_identifier: str, 
                         acknowledged_by: str) -> bool:
        """
        Acknowledge specific issue and mute for configured period.

        Pablo: is it used somewhere?
        
        Args:
            test_name: Name of the test
            issue_identifier: Primary identifier (email, ID, combination, etc.)
            acknowledged_by: Email of person acknowledging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate document ID for the test
            doc_id = self._generate_document_id(test_name)
            # Work directly with the per-issue document in the `issues` subcollection
            issues_collection = (
                self.firestore_client.collection(self.collection)
                .document(doc_id)
                .collection(self.issue_subcollection_name)
            )

            # Create issue key (simple identifier)
            issue_key_simple = str(issue_identifier).lower().strip()
            issue_doc_ref = issues_collection.document(issue_key_simple)
            existing_doc = issue_doc_ref.get()
            existing_data: Dict[str, Any] = existing_doc.to_dict() if existing_doc.exists else {}

            # Update the issue using the new per-document structure
            current_time = datetime.now(timezone.utc)
            mute_until = current_time + timedelta(days=self.default_mute_days)

            # Preserve existing owner / first occurrence where available
            issue_first_occurrence = existing_data.get("issue_first_occurrence", current_time)
            issue_owner = existing_data.get("issue_owner", "analytic_hub.data_team_ack")

            update_data = {
                "acknowledged": True,
                "muted_until": mute_until,
                "identifier": existing_data.get("identifier", issue_identifier),
                "details": existing_data.get("details", ""),
                "issue_first_occurrence": issue_first_occurrence,
                "issue_last_occurrence": current_time,
                "issue_owner": issue_owner,
                "acknowledged_by": acknowledged_by,
                "acknowledged_at": current_time,
            }

            # Save/merge the document so we don't drop other metadata fields
            issue_doc_ref.set(update_data, merge=True)
            return True
            
        except Exception as e:
            print(f"❌ Error acknowledging issue: {e}")
            return False
    
    def batch_update_issue_detections(
            self,
            test_name: str,
            issues: List[Dict[str, Any]]
    ) -> bool:
        """
        Batch update detection tracking for multiple issues of a single test.
        
        Args:
            test_name: Name of the test these issues belong to
            issues: List of issue dictionaries, each containing:
                - issue_identifier: Primary identifier (email, ID, etc.)
                - issue_details: Brief details about the issue
                - additional_metadata: Optional dict with extra fields
        
        Returns:
            True if successful, False otherwise
        """
        if not issues:
            # Nothing to update; treat as success
            return True
        
        try:
            # Generate document ID for the test
            doc_id = self._generate_document_id(test_name)
            test_doc_ref = self.firestore_client.collection(self.collection).document(doc_id)
            issues_collection = test_doc_ref.collection(self.issue_subcollection_name)

            now_utc = datetime.now(timezone.utc)

            # Preprocess issues to build refs and payloads
            issue_entries: List[Dict[str, Any]] = []
            doc_refs: List[firestore.DocumentReference] = []

            for issue in issues:
                issue_identifier = issue.get("issue_identifier")
                if not issue_identifier:
                    continue

                issue_details = issue.get("issue_details", "")
                additional_metadata = issue.get("additional_metadata") or {}

                # Create issue key (simple identifier)
                issue_key_simple = str(issue_identifier).lower().strip()
                issue_doc_ref = issues_collection.document(issue_key_simple)

                # Build enriched details string (preserve existing behaviour)
                details = f"{issue_details}"
                if additional_metadata:
                    if "absent_percentage" in additional_metadata:
                        details += f" - {additional_metadata['absent_percentage']}% absent"
                    elif "expected_weekly_hours" in additional_metadata:
                        details += f" - Expected {additional_metadata['expected_weekly_hours']}h/week"

                issue_entries.append(
                    {
                        "key": issue_key_simple,
                        "identifier": issue_identifier,
                        "details": details,
                        "additional_metadata": additional_metadata,
                        "doc_ref": issue_doc_ref,
                    }
                )
                doc_refs.append(issue_doc_ref)

            if not issue_entries:
                return True

            # Batch-fetch existing documents to minimise round trips
            existing_docs = {}
            for doc in self.firestore_client.get_all(doc_refs):
                if doc.exists:
                    existing_docs[doc.id] = doc.to_dict()

            batch = self.firestore_client.batch()

            # Ensure parent test document exists with at least one field (prevents placeholder/italic documents)
            # This ensures the document is visible in Firestore console and can be queried properly
            batch.set(test_doc_ref, {
                "test_name": test_name,
                "last_updated": now_utc,
            }, merge=True)

            for entry in issue_entries:
                key = entry["key"]
                issue_identifier = entry["identifier"]
                details = entry["details"]
                additional_metadata = entry["additional_metadata"]
                issue_doc_ref = entry["doc_ref"]

                existing_data = existing_docs.get(key) or {}
                is_new_issue = not bool(existing_data)

                # Determine owner (explicit override > existing > default)
                owner_override = additional_metadata.get("issue_owner")
                existing_owner = existing_data.get("issue_owner")
                issue_owner = owner_override or existing_owner or "analytic_hub.data_team_ack"

                # First / last occurrence handling
                issue_first_occurrence = existing_data.get("issue_first_occurrence") or now_utc

                update_data: Dict[str, Any] = {
                    "identifier": issue_identifier,
                    "details": details,
                    "issue_first_occurrence": issue_first_occurrence,
                    "issue_last_occurrence": now_utc,
                    "issue_owner": issue_owner,
                    **additional_metadata,
                }

                if is_new_issue:
                    # For new issues, explicitly initialise acknowledgment fields
                    update_data.setdefault("acknowledged", False)
                    update_data.setdefault("muted_until", None)

                # Merge so we don't clobber acknowledgment metadata or future fields
                batch.set(issue_doc_ref, update_data, merge=True)

            batch.commit()

            return True
        
        except Exception as e:
            print(f"❌ Error updating multiple issue detections: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def filter_acknowledged_issues(self, test_results: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Filter test results into new vs acknowledged issues.
        OPTIMIZED: Uses batch operations for better performance.
        
        Each test result must have its own 'issue_identifier' at the top level.
        The method extracts this identifier from each result to check acknowledgment status.
        
        Args:
            test_results: List of test result dictionaries. Each dict should have:
                - 'issue_identifier': Unique identifier for this specific issue
                - 'test_name': Name of the test that generated this result
                - 'acknowledgeable': Boolean indicating if issue can be acknowledged
            
        Returns:
            Dictionary with 'new_issues' and 'acknowledged_issues' lists
        """
        new_issues = []
        acknowledged_issues = []
        
        for result in test_results:
            if not result.get('acknowledgeable', True):
                # Non-acknowledgeable issues are always new
                new_issues.append(result)
                continue
            
            # Extract issue-specific identifier from the result (not the run-level parameter)
            # Each warning result has its own issue_identifier at the top level
            result_issue_identifier = result.get('issue_identifier')
            test_name = result.get('test_name')
            
            if not all([result_issue_identifier, test_name]):
                # Missing required metadata, treat as new
                new_issues.append(result)
                continue
            
            # Check if this specific issue is acknowledged
            is_acknowledged = self.check_issue_acknowledged(
                test_name, result_issue_identifier  # Use the issue-specific identifier
            )
            
            if is_acknowledged:
                acknowledged_issues.append(result)
            else:
                new_issues.append(result)
        
        return {
            'new_issues': new_issues,
            'acknowledged_issues': acknowledged_issues
        }
    


# Convenience functions for easy import
def create_acknowledge_manager(firestore_client: firestore.Client, 
                              repository_name: str, pipeline_name: str) -> AcknowledgeManager:
    """Create a new AcknowledgeManager instance."""
    return AcknowledgeManager(firestore_client, repository_name, pipeline_name)


