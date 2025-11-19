# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for SaveNodeToSqliteOperator.
"""

import pytest
import sqlite3
import json

from pristy.alfresco_operator.save_node_to_sqlite import SaveNodeToSqliteOperator


@pytest.fixture
def sqlite_db(tmp_path):
    """Create a temporary SQLite database with the nodes table schema."""
    db_path = tmp_path / "test_backup.db"

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL UNIQUE,
                parent_uuid TEXT,
                isFile INTEGER DEFAULT 0,
                isFolder INTEGER DEFAULT 0,
                pivot_json TEXT NOT NULL,
                sha1_checksum TEXT,
                file_size INTEGER,
                file_downloaded INTEGER DEFAULT 0,
                state TEXT DEFAULT 'new',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    return str(db_path)


@pytest.fixture
def sample_file_node():
    """Sample file node in Pristy pivot format."""
    return {
        "name": "document.pdf",
        "type": "cm:content",
        "owner": "admin",
        "path": {"root": "site:test-site", "short": "/folder1/folder2"},
        "properties": {
            "cm:title": "Test Document",
            "cm:description": "A test document",
        },
        "source": {
            "uuid": "workspace://SpacesStore/file-uuid-123",
            "server": "https://alfresco.example.com",
        },
        "content": {
            "sizeInBytes": 1024000,
            "mimeType": "application/pdf",
        },
        "__dag_param": {
            "parent_uuid": "workspace://SpacesStore/parent-uuid-456",
            "isFile": True,
            "isFolder": False,
        },
    }


@pytest.fixture
def sample_folder_node():
    """Sample folder node in Pristy pivot format."""
    return {
        "name": "Test Folder",
        "type": "cm:folder",
        "owner": "admin",
        "path": {"root": "site:test-site", "short": "/folder1"},
        "properties": {"cm:title": "Test Folder"},
        "source": {"uuid": "workspace://SpacesStore/folder-uuid-789"},
        "__dag_param": {
            "parent_uuid": "workspace://SpacesStore/root-uuid",
            "isFile": False,
            "isFolder": True,
        },
    }


class TestSaveNodeToSqliteOperator:
    """Tests for SaveNodeToSqliteOperator."""

    def test_save_single_file_node(
        self, sqlite_db, sample_file_node, mock_airflow_context
    ):
        """Test saving a single file node."""
        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[sample_file_node],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 1
        assert result["skipped_count"] == 0

        # Verify node was saved correctly
        with sqlite3.connect(sqlite_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM nodes WHERE uuid = ?",
                (sample_file_node["source"]["uuid"],),
            )
            row = cursor.fetchone()

            assert row is not None
            assert row["uuid"] == sample_file_node["source"]["uuid"]
            assert row["parent_uuid"] == sample_file_node["__dag_param"]["parent_uuid"]
            assert row["isFile"] == 1
            assert row["isFolder"] == 0
            assert row["file_size"] == 1024000
            assert row["file_downloaded"] == 0
            assert row["state"] == "success"

            # Verify pivot_json
            stored_node = json.loads(row["pivot_json"])
            assert stored_node["name"] == sample_file_node["name"]
            assert stored_node["type"] == sample_file_node["type"]

    def test_save_single_folder_node(
        self, sqlite_db, sample_folder_node, mock_airflow_context
    ):
        """Test saving a single folder node."""
        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[sample_folder_node],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 1
        assert result["skipped_count"] == 0

        # Verify folder was saved
        with sqlite3.connect(sqlite_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM nodes WHERE uuid = ?",
                (sample_folder_node["source"]["uuid"],),
            )
            row = cursor.fetchone()

            assert row is not None
            assert row["isFile"] == 0
            assert row["isFolder"] == 1
            assert row["file_size"] is None
            assert row["sha1_checksum"] is None

    def test_save_with_checksum(
        self, sqlite_db, sample_file_node, mock_airflow_context
    ):
        """Test saving a file node with SHA1 checksum."""
        checksum = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        uuid = sample_file_node["source"]["uuid"]

        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[sample_file_node],
            sqlite_path=sqlite_db,
            file_downloaded=True,
            checksums={uuid: checksum},
        )

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 1

        # Verify checksum was saved
        with sqlite3.connect(sqlite_db) as conn:
            cursor = conn.execute(
                "SELECT sha1_checksum, file_downloaded FROM nodes WHERE uuid = ?",
                (uuid,),
            )
            row = cursor.fetchone()

            assert row[0] == checksum
            assert row[1] == 1  # file_downloaded = True

    def test_save_multiple_nodes(
        self, sqlite_db, sample_file_node, sample_folder_node, mock_airflow_context
    ):
        """Test saving multiple nodes at once."""
        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[sample_file_node, sample_folder_node],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 2
        assert result["skipped_count"] == 0

        # Verify both nodes were saved
        with sqlite3.connect(sqlite_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM nodes")
            count = cursor.fetchone()[0]
            assert count == 2

    def test_update_existing_node(
        self, sqlite_db, sample_file_node, mock_airflow_context
    ):
        """Test updating a node that already exists."""
        uuid = sample_file_node["source"]["uuid"]

        # Insert initial node
        operator1 = SaveNodeToSqliteOperator(
            task_id="test_save_1",
            nodes=[sample_file_node],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )
        operator1.execute(mock_airflow_context)

        # Update the node with checksum
        checksum = "abcdef1234567890"
        operator2 = SaveNodeToSqliteOperator(
            task_id="test_save_2",
            nodes=[sample_file_node],
            sqlite_path=sqlite_db,
            file_downloaded=True,
            checksums={uuid: checksum},
        )
        result = operator2.execute(mock_airflow_context)

        assert result["saved_count"] == 1

        # Verify node was updated (not duplicated)
        with sqlite3.connect(sqlite_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM nodes WHERE uuid = ?", (uuid,))
            count = cursor.fetchone()[0]
            assert count == 1  # Should still be only 1 row

            cursor = conn.execute(
                "SELECT sha1_checksum, file_downloaded FROM nodes WHERE uuid = ?",
                (uuid,),
            )
            row = cursor.fetchone()
            assert row[0] == checksum
            assert row[1] == 1

    def test_skip_node_without_uuid(self, sqlite_db, mock_airflow_context):
        """Test that nodes without UUID are skipped."""
        invalid_node = {
            "name": "invalid.pdf",
            "type": "cm:content",
            "source": {},  # Missing uuid
        }

        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[invalid_node],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 0
        assert result["skipped_count"] == 1

        # Verify nothing was saved
        with sqlite3.connect(sqlite_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM nodes")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_save_empty_list(self, sqlite_db, mock_airflow_context):
        """Test saving an empty list of nodes."""
        operator = SaveNodeToSqliteOperator(
            task_id="test_save", nodes=[], sqlite_path=sqlite_db, file_downloaded=False
        )

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 0
        assert result["skipped_count"] == 0

    def test_preserve_special_characters(self, sqlite_db, mock_airflow_context):
        """Test that special characters in node names and properties are preserved."""
        node_with_special_chars = {
            "name": "Dossier éàç ñ ü.pdf",
            "type": "cm:content",
            "properties": {
                "cm:title": "Caractères spéciaux: àéèù ñ ü",
                "cm:description": "Test with emoji: 🚀📁",
            },
            "source": {"uuid": "workspace://SpacesStore/special-123", "size": 1024},
        }

        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[node_with_special_chars],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        result = operator.execute(mock_airflow_context)
        assert result["saved_count"] == 1

        # Verify special characters are preserved
        with sqlite3.connect(sqlite_db) as conn:
            cursor = conn.execute(
                "SELECT pivot_json FROM nodes WHERE uuid = ?",
                (node_with_special_chars["source"]["uuid"],),
            )
            row = cursor.fetchone()
            stored_node = json.loads(row[0])

            assert stored_node["name"] == node_with_special_chars["name"]
            assert (
                stored_node["properties"]["cm:title"]
                == node_with_special_chars["properties"]["cm:title"]
            )
            assert (
                stored_node["properties"]["cm:description"]
                == node_with_special_chars["properties"]["cm:description"]
            )

    def test_checksums_dict_optional(
        self, sqlite_db, sample_file_node, mock_airflow_context
    ):
        """Test that checksums parameter is optional."""
        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[sample_file_node],
            sqlite_path=sqlite_db,
            file_downloaded=False,
            # No checksums parameter
        )

        result = operator.execute(mock_airflow_context)
        assert result["saved_count"] == 1

        # Verify checksum is NULL
        with sqlite3.connect(sqlite_db) as conn:
            cursor = conn.execute(
                "SELECT sha1_checksum FROM nodes WHERE uuid = ?",
                (sample_file_node["source"]["uuid"],),
            )
            row = cursor.fetchone()
            assert row[0] is None

    def test_warn_missing_dag_param(self, sqlite_db, mock_airflow_context, mocker):
        """Test that missing __dag_param generates a warning."""
        node_without_dag_param = {
            "name": "incomplete.pdf",
            "type": "cm:content",
            "source": {"uuid": "workspace://SpacesStore/test-123"},
        }

        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[node_without_dag_param],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        # Mock the log.warning method to verify it's called
        mock_warning = mocker.spy(operator.log, "warning")

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 1
        # Verify warning was called with the expected message
        assert mock_warning.call_count >= 1
        warning_calls = [str(call) for call in mock_warning.call_args_list]
        assert any("missing '__dag_param' field" in call for call in warning_calls)

    def test_warn_incomplete_dag_param(self, sqlite_db, mock_airflow_context, mocker):
        """Test that incomplete __dag_param generates a warning."""
        node_incomplete = {
            "name": "incomplete.pdf",
            "type": "cm:content",
            "source": {"uuid": "workspace://SpacesStore/test-456"},
            "__dag_param": {
                "parent_uuid": "workspace://SpacesStore/parent-123"
                # Missing isFile and isFolder
            },
        }

        operator = SaveNodeToSqliteOperator(
            task_id="test_save",
            nodes=[node_incomplete],
            sqlite_path=sqlite_db,
            file_downloaded=False,
        )

        # Mock the log.warning method to verify it's called
        mock_warning = mocker.spy(operator.log, "warning")

        result = operator.execute(mock_airflow_context)

        assert result["saved_count"] == 1
        # Verify warning was called with the expected message about missing keys
        assert mock_warning.call_count >= 1
        warning_calls = [str(call) for call in mock_warning.call_args_list]
        assert any("incomplete '__dag_param'" in call for call in warning_calls)
        assert any("isFile" in call and "isFolder" in call for call in warning_calls)
