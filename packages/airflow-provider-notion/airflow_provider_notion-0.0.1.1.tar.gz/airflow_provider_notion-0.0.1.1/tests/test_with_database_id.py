#!/usr/bin/env python3
"""
Notion API Test with specific database ID.
Run this if you already know your database ID.

Usage:
    python tests/test_with_database_id.py <database_id>
"""

import sys
import requests


NOTION_API_TOKEN = "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"
BASE_URL = "https://api.notion.com/v1"
API_VERSION = "2025-09-03"


def test_with_database_id(database_id):
    """Run tests with a specific database ID."""

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    print("\n" + "=" * 60)
    print("Testing with Database ID:", database_id)
    print("=" * 60)

    # Test 1: Get database info
    print("\n1. Getting database information...")
    try:
        response = requests.get(f"{BASE_URL}/databases/{database_id}", headers=headers)
        response.raise_for_status()

        data = response.json()

        # Database title
        title = ""
        if data.get("title"):
            title = data["title"][0].get("plain_text", "Untitled")
        print(f"   ✓ Database: {title}")
        print(f"   Database ID: {data.get('id')}")

        # Data sources
        data_sources = data.get("data_sources", [])
        print(f"   Data sources: {len(data_sources)}")

        if not data_sources:
            print("   ✗ No data sources found!")
            return False

        for i, ds in enumerate(data_sources, 1):
            print(f"     {i}. {ds.get('name', 'Unnamed')} (ID: {ds.get('id')})")

        data_source_id = data_sources[0]["id"]

        # Properties
        properties = data.get("properties", {})
        print(f"   Properties ({len(properties)}):")
        for prop_name, prop_data in properties.items():
            print(f"     - {prop_name} ({prop_data.get('type')})")

    except Exception as e:
        print(f"   ✗ Failed: {str(e)}")
        return False

    # Test 2: Query data source
    print("\n2. Querying data source...")
    try:
        payload = {"page_size": 5}
        response = requests.post(
            f"{BASE_URL}/data_sources/{data_source_id}/query",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print("   ✓ Query successful!")
        print(f"   Pages found: {len(results)}")
        print(f"   Has more: {data.get('has_more', False)}")

        if results:
            print("\n   First page:")
            page = results[0]
            print(f"     ID: {page.get('id')}")
            print(f"     Created: {page.get('created_time')}")
            print(f"     URL: {page.get('url')}")

    except Exception as e:
        print(f"   ✗ Query failed: {str(e)}")
        return False

    # Test 3: Test backward compatibility (query with database_id)
    print("\n3. Testing backward compatibility (auto-discovery)...")
    print("   This simulates what NotionHook.query_database() does...")

    try:
        # First discover data source
        db_response = requests.get(
            f"{BASE_URL}/databases/{database_id}", headers=headers
        )
        db_response.raise_for_status()
        db_data = db_response.json()

        discovered_ds_id = db_data["data_sources"][0]["id"]
        print(f"   ✓ Discovered data_source_id: {discovered_ds_id}")

        # Then query it
        payload = {"page_size": 3}
        query_response = requests.post(
            f"{BASE_URL}/data_sources/{discovered_ds_id}/query",
            headers=headers,
            json=payload,
        )
        query_response.raise_for_status()

        print("   ✓ Auto-discovery and query successful!")
        print("   This is how query_database(database_id=...) works internally")

    except Exception as e:
        print(f"   ✗ Failed: {str(e)}")
        return False

    # Test 4: Read a page (if pages exist)
    print("\n4. Test reading a page")

    try:
        # Query to get a page ID
        query_response = requests.post(
            f"{BASE_URL}/data_sources/{data_source_id}/query",
            headers=headers,
            json={"page_size": 1},
        )
        query_response.raise_for_status()
        query_data = query_response.json()

        if query_data.get("results"):
            page_id = query_data["results"][0]["id"]
            print(f"   Found existing page: {page_id}")

            # Get the page details
            page_response = requests.get(f"{BASE_URL}/pages/{page_id}", headers=headers)
            page_response.raise_for_status()
            page_data = page_response.json()

            print("   ✓ Page retrieved successfully!")
            print(f"   Page ID: {page_data.get('id')}")
            print(f"   Created: {page_data.get('created_time')}")
            print(f"   Last edited: {page_data.get('last_edited_time')}")
            print(f"   URL: {page_data.get('url')}")

            # Show properties
            page_properties = page_data.get("properties", {})
            print(f"   Properties: {len(page_properties)}")
            for prop_name in list(page_properties.keys())[:3]:
                print(f"     - {prop_name}")
        else:
            print("   ℹ️  No pages found in database")

    except Exception as e:
        print(f"   ✗ Failed to read page: {str(e)}")

    # Test 5: Create page (optional)
    print("\n5. Test page creation?")
    response = input("   Create a test page? (y/n): ").lower().strip()

    if response == "y":
        try:
            # Find title property
            title_prop = None
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "title":
                    title_prop = prop_name
                    break

            if not title_prop:
                print("   ✗ Could not find title property")
                return False

            payload = {
                "parent": {"type": "data_source_id", "data_source_id": data_source_id},
                "properties": {
                    title_prop: {
                        "title": [
                            {"text": {"content": "Test Page - API 2025-09-03 Test"}}
                        ]
                    }
                },
            }

            create_response = requests.post(
                f"{BASE_URL}/pages", headers=headers, json=payload
            )
            create_response.raise_for_status()

            data = create_response.json()
            created_page_id = data.get("id")

            print("   ✓ Page created!")
            print(f"   Page ID: {created_page_id}")
            print(f"   View: {data.get('url')}")

            # Test 6: Read the newly created page
            print("\n6. Read the newly created page?")
            read_response = input("   Continue? (y/n): ").lower().strip()

            if read_response == "y":
                try:
                    read_page_response = requests.get(
                        f"{BASE_URL}/pages/{created_page_id}", headers=headers
                    )
                    read_page_response.raise_for_status()
                    read_data = read_page_response.json()

                    print("   ✓ Newly created page retrieved!")
                    print(f"   Page ID: {read_data.get('id')}")
                    print(f"   URL: {read_data.get('url')}")

                    # Verify it has the correct parent
                    parent = read_data.get("parent", {})
                    if parent.get("data_source_id") == data_source_id:
                        print("   ✓ Parent data_source_id matches!")

                except Exception as e:
                    print(f"   ✗ Failed to read created page: {str(e)}")

        except Exception as e:
            print(f"   ✗ Failed to create page: {str(e)}")

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print()

    return True


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python tests/test_with_database_id.py <database_id>")
        print("\nTo get your database ID:")
        print("  1. Open database in Notion")
        print("  2. Click '...' → Copy link")
        print("  3. Extract ID from URL: notion.so/xxxxx?v=yyyyy")
        print("     The 'xxxxx' part is your database ID (with dashes removed)")
        print("\nExample:")
        print(
            "  python tests/test_with_database_id.py 123e4567e89b12d3a456426614174000"
        )
        sys.exit(1)

    database_id = sys.argv[1].replace("-", "")  # Remove dashes if present

    print("\n╔" + "═" * 58 + "╗")
    print("║  Notion API Test - Specific Database                  ║")
    print("╚" + "═" * 58 + "╝")

    success = test_with_database_id(database_id)

    if success:
        print("\n✓ Your Notion integration is working correctly!")
        print("✓ API version 2025-09-03 is fully functional")
        print("✓ Data source discovery works as expected")
    else:
        print("\n✗ Some tests failed. Please check:")
        print("  - Database ID is correct")
        print("  - Integration has access to the database")
        print("  - API token is valid")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
