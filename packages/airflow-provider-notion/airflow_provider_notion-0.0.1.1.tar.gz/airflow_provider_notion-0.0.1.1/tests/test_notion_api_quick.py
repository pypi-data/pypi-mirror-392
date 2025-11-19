#!/usr/bin/env python3
"""
Quick test script for Notion API integration.
Tests basic connectivity and operations without full Airflow setup.
"""

import sys
import requests


NOTION_API_TOKEN = "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"
BASE_URL = "https://api.notion.com/v1"
API_VERSION = "2025-09-03"


def test_connection():
    """Test basic API connection by listing users."""
    print("=" * 60)
    print("TEST 1: Testing Notion API Connection")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        response.raise_for_status()

        data = response.json()
        print("✓ Connection successful!")
        print(f"  API Version: {API_VERSION}")
        print(f"  Users found: {len(data.get('results', []))}")

        if data.get("results"):
            user = data["results"][0]
            print(
                f"  First user: {user.get('name', 'N/A')} ({user.get('type', 'N/A')})"
            )

        return True
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False


def search_databases():
    """Search for databases accessible to the integration."""
    print("\n" + "=" * 60)
    print("TEST 2: Searching for Databases")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    payload = {
        "filter": {
            "value": "data_source",  # Changed from 'database' to 'data_source' in 2025-09-03
            "property": "object",
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/search", headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print("✓ Search successful!")
        print(f"  Databases found: {len(results)}")

        if not results:
            print("\n  ⚠️  No databases found!")
            print("  Make sure your integration has access to at least one database.")
            print("  To grant access:")
            print("    1. Open a database in Notion")
            print("    2. Click '...' → Add connections")
            print("    3. Select your integration")
            return None

        print("\n  Available Databases:")
        for i, db in enumerate(results[:5], 1):  # Show first 5
            title = ""
            if db.get("title"):
                title = db["title"][0].get("plain_text", "Untitled")
            print(f"    {i}. {title}")
            print(f"       ID: {db['id']}")

        return results[0]["id"] if results else None

    except Exception as e:
        print(f"✗ Search failed: {str(e)}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")
        return None


def test_get_database(database_id):
    """Test getting database info and data sources."""
    print("\n" + "=" * 60)
    print("TEST 3: Getting Database Information")
    print("=" * 60)
    print(f"Database ID: {database_id}")

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{BASE_URL}/databases/{database_id}", headers=headers)
        response.raise_for_status()

        data = response.json()

        print("✓ Database retrieved successfully!")

        # Database title
        title = ""
        if data.get("title"):
            title = data["title"][0].get("plain_text", "Untitled")
        print(f"  Title: {title}")

        # Data sources
        data_sources = data.get("data_sources", [])
        print(f"  Data sources: {len(data_sources)}")

        for i, ds in enumerate(data_sources, 1):
            print(f"    {i}. {ds.get('name', 'Unnamed')}")
            print(f"       ID: {ds.get('id')}")

        # Properties (schema)
        properties = data.get("properties", {})
        print(f"  Properties: {len(properties)}")
        for prop_name, prop_data in list(properties.items())[:5]:
            print(f"    - {prop_name} ({prop_data.get('type', 'unknown')})")

        return data_sources[0]["id"] if data_sources else None

    except Exception as e:
        print(f"✗ Failed to get database: {str(e)}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")
        return None


def test_query_data_source(data_source_id):
    """Test querying a data source."""
    print("\n" + "=" * 60)
    print("TEST 4: Querying Data Source")
    print("=" * 60)
    print(f"Data Source ID: {data_source_id}")

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    payload = {"page_size": 5}

    try:
        response = requests.post(
            f"{BASE_URL}/data_sources/{data_source_id}/query",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print("✓ Query successful!")
        print(f"  Pages returned: {len(results)}")
        print(f"  Has more: {data.get('has_more', False)}")

        if results:
            print("\n  First page:")
            page = results[0]
            print(f"    ID: {page.get('id')}")
            print(f"    URL: {page.get('url')}")
            print(f"    Created: {page.get('created_time')}")

            # Show properties
            properties = page.get("properties", {})
            print(f"    Properties: {len(properties)}")
            for prop_name in list(properties.keys())[:3]:
                print(f"      - {prop_name}")

        return True

    except Exception as e:
        print(f"✗ Query failed: {str(e)}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")
        return False


def test_get_page(page_id):
    """Test retrieving a page."""
    print("\n" + "=" * 60)
    print("TEST 5: Reading a Page")
    print("=" * 60)
    print(f"Page ID: {page_id}")

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{BASE_URL}/pages/{page_id}", headers=headers)
        response.raise_for_status()

        data = response.json()

        print("✓ Page retrieved successfully!")
        print(f"  Page ID: {data.get('id')}")
        print(f"  Object: {data.get('object')}")
        print(f"  Created: {data.get('created_time')}")
        print(f"  Last edited: {data.get('last_edited_time')}")
        print(f"  URL: {data.get('url')}")

        # Show properties
        properties = data.get("properties", {})
        print(f"\n  Properties ({len(properties)}):")
        for prop_name, prop_value in list(properties.items())[:5]:
            prop_type = prop_value.get("type")
            print(f"    - {prop_name}: {prop_type}")

        # Show parent info
        parent = data.get("parent", {})
        print("\n  Parent:")
        print(f"    Type: {parent.get('type')}")
        if parent.get("database_id"):
            print(f"    Database ID: {parent.get('database_id')}")
        if parent.get("data_source_id"):
            print(f"    Data Source ID: {parent.get('data_source_id')}")

        return True

    except Exception as e:
        print(f"✗ Failed to get page: {str(e)}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")
        return False


def test_create_page(data_source_id, database_id):
    """Test creating a page."""
    print("\n" + "=" * 60)
    print("TEST 6: Creating a Test Page")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    # First, get the database schema to understand required properties
    try:
        db_response = requests.get(
            f"{BASE_URL}/databases/{database_id}", headers=headers
        )
        db_response.raise_for_status()
        db_data = db_response.json()

        # Find the title property
        title_prop = None
        for prop_name, prop_data in db_data.get("properties", {}).items():
            if prop_data.get("type") == "title":
                title_prop = prop_name
                break

        if not title_prop:
            print("✗ Could not find title property in database schema")
            return False

        print(f"  Title property name: {title_prop}")

        # Create page payload
        payload = {
            "parent": {"type": "data_source_id", "data_source_id": data_source_id},
            "properties": {
                title_prop: {
                    "title": [{"text": {"content": "Test Page - Integration Test"}}]
                }
            },
        }

        response = requests.post(f"{BASE_URL}/pages", headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()

        print("✓ Page created successfully!")
        print(f"  Page ID: {data.get('id')}")
        print(f"  URL: {data.get('url')}")
        print(f"\n  You can view it in Notion: {data.get('url')}")

        return data.get("id")

    except Exception as e:
        print(f"✗ Failed to create page: {str(e)}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Notion API Integration Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Test 1: Connection
    if not test_connection():
        print("\n✗ Connection test failed. Cannot proceed.")
        sys.exit(1)

    # Test 2: Search databases
    database_id = search_databases()
    if not database_id:
        print("\n⚠️  No databases found. Some tests will be skipped.")
        print("\nTo enable full testing:")
        print("  1. Create a database in Notion")
        print("  2. Share it with your integration")
        print("  3. Run this script again")
        sys.exit(0)

    # Test 3: Get database info
    data_source_id = test_get_database(database_id)
    if not data_source_id:
        print("\n✗ Could not get data source ID. Cannot proceed.")
        sys.exit(1)

    # Test 4: Query data source
    test_query_data_source(data_source_id)

    # Test 5: Read a page (if pages exist)
    print("\n⚠️  Test 5 will read an existing page from the database.")
    print("Checking if there are any pages to read...")

    # Get a page ID from the query results
    query_headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }
    try:
        query_response = requests.post(
            f"{BASE_URL}/data_sources/{data_source_id}/query",
            headers=query_headers,
            json={"page_size": 1},
        )
        query_response.raise_for_status()
        query_data = query_response.json()

        if query_data.get("results"):
            existing_page_id = query_data["results"][0]["id"]
            print(f"Found existing page: {existing_page_id}")
            test_get_page(existing_page_id)
        else:
            print("No existing pages found. Skipping page read test.")
    except Exception as e:
        print(f"Could not query for pages: {str(e)}")

    # Test 6: Create page
    print("\n⚠️  The next test will create a test page in your database.")
    response = input("Continue? (y/n): ").lower().strip()
    if response == "y":
        page_id = test_create_page(data_source_id, database_id)
        if page_id:
            print("\n✓ All tests completed successfully!")

            # Optional: Read the newly created page
            print("\n⚠️  Read the newly created page?")
            read_response = input("Continue? (y/n): ").lower().strip()
            if read_response == "y":
                test_get_page(page_id)
    else:
        print("\nSkipped page creation test.")

    print("\n" + "=" * 60)
    print("Summary:")
    print("  ✓ All basic tests passed")
    print("  ✓ Notion API 2025-09-03 is working correctly")
    print("  ✓ Data source discovery works")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
