# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Dict, Any, Optional

from airflow.models import BaseOperator


class SaveNodeToSqliteOperator(BaseOperator):
    """
    Saves Alfresco node metadata to a SQLite database for backup purposes.

    This operator stores nodes in Pristy pivot format as JSON strings in a SQLite
    database, along with checksum information for file integrity verification.

    **Internal Metadata (`__dag_param`):**

    This operator expects nodes to include a `__dag_param` field containing internal
    DAG metadata (NOT part of the Pristy pivot format):

    - `parent_uuid` (str): UUID of the parent node in the hierarchy
    - `isFile` (bool): True if the node is a file (cm:content)
    - `isFolder` (bool): True if the node is a folder (cm:folder)

    The `__dag_param` field is used to populate SQLite tracking columns and should
    not be sent to Pristy Injector API or Kafka.

    **Warning:** Missing or incomplete `__dag_param` will result in NULL values for
    `parent_uuid`, `isFile`, and `isFolder` columns in the database, and a warning
    will be logged.

    The SQLite database must have the following schema (created by backup init DAG):
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL UNIQUE,
            parent_uuid TEXT,
            isFile INTEGER DEFAULT 0,
            isFolder INTEGER DEFAULT 0,
            pivot_json TEXT NOT NULL, -- Complete Pristy pivot format as JSON
            sha1_checksum TEXT,       -- SHA1 hash of binary content (NULL for folders)
            file_size INTEGER,        -- File size in bytes (NULL for folders)
            file_downloaded INTEGER DEFAULT 0,  -- 1 if binary downloaded
            state TEXT DEFAULT 'new',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

    :param nodes: (required) List of nodes in Pristy pivot format to save
    :param sqlite_path: (required) Path to SQLite database file
    :param file_downloaded: Flag indicating if binary content was downloaded (default: False)
    :param checksums: Optional dict mapping node UUID to SHA1 checksum

    :returns: Dictionary with:
        - saved_count: Number of nodes saved
        - skipped_count: Number of nodes skipped (already exist)

    Example usage:
        save_task = SaveNodeToSqliteOperator(
            task_id="save_metadata",
            nodes=[
                {
                    "name": "document.pdf",
                    "type": "cm:content",
                    "path": {"root": "site:my-site", "short": "/folder1"},
                    "properties": {"cm:title": "My Document"},
                    "source": {
                        "uuid": "workspace://SpacesStore/abc123",
                        "size": 1024000
                    },
                    "__dag_param": {"parent_uuid": "workspace://SpacesStore/parent123"}
                }
            ],
            sqlite_path="/datas/backups/backup_20250110/backup.db",
            file_downloaded=True,
            checksums={"workspace://SpacesStore/abc123": "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"}
        )
    """

    # Required keys in __dag_param for proper node tracking
    REQUIRED_DAG_PARAM_KEYS = ["parent_uuid", "isFile", "isFolder"]

    def __init__(
        self,
        *,
        nodes: List[Dict[str, Any]],
        sqlite_path: str,
        file_downloaded: bool = False,
        checksums: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.nodes = nodes
        self.sqlite_path = sqlite_path
        self.file_downloaded = file_downloaded
        self.checksums = checksums or {}

    def _resolve_xcom_parameters(self, context):
        """
        Resolve XCom arguments for nodes and sqlite_path.

        :param context: Airflow context dictionary
        :return: Tuple of (nodes_resolved, sqlite_path_resolved)
        :raises AirflowException: If sqlite_path cannot be resolved from XCom dict
        """
        from airflow.exceptions import AirflowException

        # Resolve XComArg if needed for nodes
        nodes_resolved = self.nodes
        if hasattr(self.nodes, "resolve"):
            nodes_resolved = self.nodes.resolve(context)

        # Resolve XComArg if needed for sqlite_path
        sqlite_path_resolved = self.sqlite_path
        if hasattr(self.sqlite_path, "resolve"):
            sqlite_path_resolved = self.sqlite_path.resolve(context)

        # If it's a dict (complete output), extract the sqlite_path key
        if isinstance(sqlite_path_resolved, dict):
            sqlite_path_resolved = sqlite_path_resolved.get("sqlite_path")
            if not sqlite_path_resolved:
                raise AirflowException("sqlite_path not found in XCom dict")

        return nodes_resolved, sqlite_path_resolved

    def _extract_node_uuid(self, node: Dict[str, Any]) -> Optional[str]:
        """
        Extract and validate node UUID from source.

        :param node: Node dictionary
        :return: UUID if present, None otherwise (logs warning)
        """
        source = node.get("source", {})
        uuid = source.get("uuid")

        if not uuid:
            self.log.warning(
                f"Node missing source.uuid, skipping: {node.get('name', 'unknown')}"
            )

        return uuid

    def _validate_dag_param(
        self, node: Dict[str, Any], uuid: str, dag_param: Dict[str, Any]
    ) -> None:
        """
        Validate __dag_param completeness and log warnings if incomplete.

        :param node: Node dictionary
        :param uuid: Node UUID (for logging)
        :param dag_param: The __dag_param dictionary to validate
        """
        if not dag_param:
            self.log.warning(
                f"Node '{node.get('name', 'unknown')}' (UUID: {uuid}) "
                "is missing '__dag_param' field. "
                "parent_uuid, isFile, and isFolder will be NULL/0 in database."
            )
        elif not all(key in dag_param for key in self.REQUIRED_DAG_PARAM_KEYS):
            missing_keys = [
                k for k in self.REQUIRED_DAG_PARAM_KEYS if k not in dag_param
            ]
            self.log.warning(
                f"Node '{node.get('name', 'unknown')}' (UUID: {uuid}) "
                f"has incomplete '__dag_param'. Missing keys: {missing_keys}"
            )

    def _extract_node_metadata(
        self, node: Dict[str, Any], dag_param: Dict[str, Any], uuid: str
    ) -> Dict[str, Any]:
        """
        Extract all node metadata required for database storage.

        :param node: Node dictionary in Pristy pivot format
        :param dag_param: The __dag_param dictionary
        :param uuid: Node UUID
        :return: Dictionary with all metadata fields
        """
        import json
        from datetime import datetime, timezone

        return {
            "parent_uuid": dag_param.get("parent_uuid"),
            "isFile": 1 if dag_param.get("isFile", False) else 0,
            "isFolder": 1 if dag_param.get("isFolder", False) else 0,
            "file_size": node.get("content", {}).get("sizeInBytes"),
            "sha1_checksum": self.checksums.get(uuid),
            "pivot_json": json.dumps(node, ensure_ascii=False),
            "now": datetime.now(timezone.utc).isoformat(),
        }

    def _upsert_node(self, cursor, uuid: str, metadata: Dict[str, Any]) -> None:
        """
        Insert or update a node in the database using UPSERT pattern.

        Uses SQLite's INSERT ... ON CONFLICT to handle both insert and update
        in a single query, improving performance and simplifying logic.

        :param cursor: SQLite cursor
        :param uuid: Node UUID (primary key)
        :param metadata: Dictionary with all node metadata fields
        """
        cursor.execute(
            """
            INSERT INTO nodes
                (uuid, parent_uuid, isFile, isFolder, pivot_json, sha1_checksum,
                 file_size, file_downloaded, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'success', ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                parent_uuid = excluded.parent_uuid,
                isFile = excluded.isFile,
                isFolder = excluded.isFolder,
                pivot_json = excluded.pivot_json,
                sha1_checksum = excluded.sha1_checksum,
                file_size = excluded.file_size,
                file_downloaded = excluded.file_downloaded,
                state = 'success',
                updated_at = excluded.updated_at
            """,
            (
                uuid,
                metadata["parent_uuid"],
                metadata["isFile"],
                metadata["isFolder"],
                metadata["pivot_json"],
                metadata["sha1_checksum"],
                metadata["file_size"],
                1 if self.file_downloaded else 0,
                metadata["now"],
                metadata["now"],
            ),
        )
        self.log.debug(f"Upserted node: {uuid}")

    def _process_nodes(
        self, cursor, nodes_resolved: List[Dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Process all nodes and save them to the database.

        :param cursor: SQLite cursor
        :param nodes_resolved: List of node dictionaries
        :return: Tuple of (saved_count, skipped_count)
        """
        saved_count = 0
        skipped_count = 0

        for node in nodes_resolved:
            # Extract and validate UUID
            uuid = self._extract_node_uuid(node)
            if not uuid:
                skipped_count += 1
                continue

            # Extract and validate __dag_param
            dag_param = node.get("__dag_param", {})
            self._validate_dag_param(node, uuid, dag_param)

            # Extract metadata and save to database
            metadata = self._extract_node_metadata(node, dag_param, uuid)
            self._upsert_node(cursor, uuid, metadata)
            saved_count += 1

        return saved_count, skipped_count

    def execute(self, context):
        """
        Execute the operator to save nodes to SQLite database.

        :param context: Airflow context dictionary
        :return: Dictionary with saved_count and skipped_count
        :raises AirflowException: If SQLite operations fail
        """
        import sqlite3
        from airflow.exceptions import AirflowException

        # Resolve XCom parameters
        nodes_resolved, sqlite_path_resolved = self._resolve_xcom_parameters(context)

        if not nodes_resolved:
            self.log.info("No nodes to save")
            return {"saved_count": 0, "skipped_count": 0}

        self.log.info(
            f"Saving {len(nodes_resolved)} nodes to SQLite: {sqlite_path_resolved}"
        )

        # Process nodes in database transaction
        try:
            with sqlite3.connect(sqlite_path_resolved) as conn:
                cursor = conn.cursor()
                saved_count, skipped_count = self._process_nodes(cursor, nodes_resolved)
                conn.commit()

            self.log.info(
                f"Successfully saved {saved_count} nodes "
                f"({skipped_count} skipped without UUID)"
            )

            return {"saved_count": saved_count, "skipped_count": skipped_count}

        except sqlite3.Error as e:
            raise AirflowException(f"SQLite error: {str(e)}") from e
        except Exception as e:
            raise AirflowException(f"Failed to save nodes: {str(e)}") from e
