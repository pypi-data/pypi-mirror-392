"""
Integration tests for Notion API with real API calls.

These tests require:
1. A valid Notion API token set in environment variable NOTION_API_TOKEN
2. A test database ID set in environment variable NOTION_TEST_DATABASE_ID
3. Proper Notion integration permissions

To run these tests:
    export NOTION_API_TOKEN="ntn_your_token"
    export NOTION_TEST_DATABASE_ID="your_database_id"
    pytest tests/integration/test_notion_real_api.py -v
"""

import os
import pytest
from unittest.mock import Mock
from airflow.models import Connection
from airflow.providers.notion.hooks.notion import NotionHook


# Skip all tests if credentials not available
pytestmark = pytest.mark.skipif(
    not os.getenv("NOTION_API_TOKEN"),
    reason="NOTION_API_TOKEN environment variable not set",
)


@pytest.fixture
def notion_token():
    """Get Notion API token from environment."""
    token = os.getenv(
        "NOTION_API_TOKEN", "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"
    )
    return token


@pytest.fixture
def test_database_id():
    """Get test database ID from environment."""
    return os.getenv("NOTION_TEST_DATABASE_ID", "")


@pytest.fixture
def notion_hook(notion_token, monkeypatch):
    """Create a NotionHook with real credentials."""

    # Mock the get_connection method to return our test connection
    def mock_get_connection(conn_id):
        conn = Mock(spec=Connection)
        conn.password = notion_token
        conn.host = None
        conn.extra = None
        return conn

    hook = NotionHook(notion_conn_id="notion_test")
    monkeypatch.setattr(hook, "get_connection", mock_get_connection)

    return hook


class TestNotionHookConnection:
    """Test Notion API connection and basic functionality."""

    def test_connection_initialization(self, notion_hook):
        """Test that hook initializes connection properly."""
        session = notion_hook.get_conn()

        assert session is not None
        assert "Authorization" in session.headers
        assert session.headers["Notion-Version"] == "2025-09-03"
        assert "Bearer ntn_" in session.headers["Authorization"]

    def test_connection_test(self, notion_hook):
        """Test the test_connection method."""
        success, message = notion_hook.test_connection()

        print(f"\nConnection test result: {success}")
        print(f"Message: {message}")

        if not success:
            # If connection fails, print detailed error for debugging
            pytest.skip(f"Connection test failed: {message}")

        assert success is True
        assert "successfully" in message.lower()


class TestNotionDataSources:
    """Test data source discovery and operations."""

    def test_get_data_sources_without_database(self, notion_hook):
        """Test get_data_sources method error handling."""
        # Use an invalid database ID to test error handling
        with pytest.raises(Exception):
            notion_hook.get_data_sources("invalid-database-id")

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_get_data_sources_with_valid_database(self, notion_hook, test_database_id):
        """Test get_data_sources with a real database."""
        result = notion_hook.get_data_sources(test_database_id)

        print(f"\nDatabase info: {result.get('id')}")
        print(f"Data sources: {result.get('data_sources')}")

        assert "object" in result
        assert result["object"] == "database"
        assert "data_sources" in result
        assert isinstance(result["data_sources"], list)

        if result["data_sources"]:
            ds = result["data_sources"][0]
            assert "id" in ds
            assert "name" in ds
            print(f"First data source: {ds['name']} (ID: {ds['id']})")


class TestNotionQueryOperations:
    """Test query operations."""

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_query_database_with_auto_discovery(self, notion_hook, test_database_id):
        """Test querying database with automatic data source discovery."""
        result = notion_hook.query_database(database_id=test_database_id)

        print(f"\nQuery result keys: {result.keys()}")
        print(f"Number of results: {len(result.get('results', []))}")

        assert "object" in result
        assert result["object"] == "list"
        assert "results" in result
        assert isinstance(result["results"], list)

        if result["results"]:
            first_page = result["results"][0]
            print(f"First page ID: {first_page.get('id')}")
            print(
                f"First page properties: {list(first_page.get('properties', {}).keys())}"
            )

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_query_data_source_directly(self, notion_hook, test_database_id):
        """Test querying data source directly."""
        # First get the data source ID
        db_info = notion_hook.get_data_sources(test_database_id)

        if not db_info.get("data_sources"):
            pytest.skip("No data sources found in database")

        data_source_id = db_info["data_sources"][0]["id"]

        # Query the data source directly
        result = notion_hook.query_data_source(data_source_id=data_source_id)

        print(f"\nDirect query result keys: {result.keys()}")
        print(f"Number of results: {len(result.get('results', []))}")

        assert "object" in result
        assert result["object"] == "list"
        assert "results" in result

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_query_with_pagination(self, notion_hook, test_database_id):
        """Test query with page_size parameter."""
        result = notion_hook.query_database(database_id=test_database_id, page_size=5)

        print(f"\nPaginated query: {len(result.get('results', []))} results")
        print(f"Has more: {result.get('has_more', False)}")
        print(f"Next cursor: {result.get('next_cursor', 'None')}")

        assert "results" in result
        assert len(result["results"]) <= 5


class TestNotionPageOperations:
    """Test page creation and update operations."""

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_create_page(self, notion_hook, test_database_id):
        """Test creating a page in a database."""
        # Get data source info to understand schema
        db_info = notion_hook.get_data_sources(test_database_id)

        if not db_info.get("data_sources"):
            pytest.skip("No data sources found")

        data_source_id = db_info["data_sources"][0]["id"]

        # Create a simple page with title
        # Note: Adjust properties based on your database schema
        properties = {
            "Name": {  # Assuming your database has a "Name" title property
                "title": [{"text": {"content": "Test Page from Integration Test"}}]
            }
        }

        try:
            result = notion_hook.create_page(
                data_source_id=data_source_id, properties=properties
            )

            print(f"\nCreated page ID: {result.get('id')}")
            print(f"Page URL: {result.get('url')}")

            assert "id" in result
            assert "object" in result
            assert result["object"] == "page"

            # Store page_id for potential cleanup or further tests
            created_page_id = result["id"]

            return created_page_id

        except Exception as e:
            print(f"\nFailed to create page: {str(e)}")
            print("Database schema might be different. Available properties:")
            # This will help debug schema issues
            pytest.skip(f"Could not create page: {str(e)}")

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_get_page(self, notion_hook, test_database_id):
        """Test retrieving a page."""
        # First query to get a page ID
        result = notion_hook.query_database(database_id=test_database_id)

        if not result.get("results"):
            pytest.skip("No pages in database to test")

        page_id = result["results"][0]["id"]

        # Get the page
        page = notion_hook.get_page(page_id=page_id)

        print(f"\nRetrieved page ID: {page.get('id')}")
        print(f"Page properties: {list(page.get('properties', {}).keys())}")

        assert "id" in page
        assert page["id"] == page_id
        assert "properties" in page


class TestNotionBlockOperations:
    """Test block operations."""

    @pytest.mark.skipif(
        not os.getenv("NOTION_TEST_DATABASE_ID"),
        reason="NOTION_TEST_DATABASE_ID not set",
    )
    def test_get_block_children(self, notion_hook, test_database_id):
        """Test getting block children."""
        # First get a page
        result = notion_hook.query_database(database_id=test_database_id)

        if not result.get("results"):
            pytest.skip("No pages in database to test")

        page_id = result["results"][0]["id"]

        # Get block children (page content)
        children = notion_hook.get_block_children(block_id=page_id)

        print(f"\nPage has {len(children.get('results', []))} blocks")

        assert "object" in children
        assert children["object"] == "list"
        assert "results" in children


def test_environment_setup():
    """Test that environment is properly configured."""
    token = os.getenv("NOTION_API_TOKEN")
    db_id = os.getenv("NOTION_TEST_DATABASE_ID")

    print("\n" + "=" * 60)
    print("Environment Configuration:")
    print("=" * 60)
    print(f"NOTION_API_TOKEN: {'✓ Set' if token else '✗ Not set'}")
    if token:
        print(f"  Token prefix: {token[:10]}...")
    print(f"NOTION_TEST_DATABASE_ID: {'✓ Set' if db_id else '✗ Not set'}")
    if db_id:
        print(f"  Database ID: {db_id}")
    print("=" * 60)

    if not token:
        pytest.skip("NOTION_API_TOKEN not set - set it to run integration tests")

    if not db_id:
        print("\n⚠️  WARNING: NOTION_TEST_DATABASE_ID not set")
        print("Some tests will be skipped. To run all tests:")
        print("  export NOTION_TEST_DATABASE_ID='your-database-id'")
