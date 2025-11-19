#!/usr/bin/env python3
"""
辅助脚本：帮助获取 Notion 数据库 ID 并测试完整功能
"""

import requests

NOTION_API_TOKEN = "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"
BASE_URL = "https://api.notion.com/v1"
API_VERSION = "2025-09-03"


def get_headers():
    return {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }


def search_all_accessible_content():
    """搜索所有可访问的内容（页面和数据库）"""
    print("\n" + "=" * 70)
    print("搜索所有可访问的 Notion 内容")
    print("=" * 70)

    headers = get_headers()

    # 搜索所有内容
    print("\n1. 搜索所有内容...")
    try:
        response = requests.post(f"{BASE_URL}/search", headers=headers, json={})
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        print(f"✓ 找到 {len(results)} 个项目")

        databases = []
        pages = []
        data_sources = []

        for item in results:
            obj_type = item.get("object")
            if obj_type == "database":
                databases.append(item)
            elif obj_type == "page":
                pages.append(item)
            elif obj_type == "data_source":
                data_sources.append(item)

        print("\n分类统计:")
        print(f"  - 数据库 (database): {len(databases)}")
        print(f"  - 数据源 (data_source): {len(data_sources)}")
        print(f"  - 页面 (page): {len(pages)}")

        # 显示数据源
        if data_sources:
            print(f"\n✓ 找到 {len(data_sources)} 个数据源:")
            for i, ds in enumerate(data_sources, 1):
                name = ds.get("name", "未命名")
                ds_id = ds.get("id")
                parent = ds.get("parent", {})
                db_id = parent.get("database_id", "N/A")

                print(f"\n  {i}. {name}")
                print(f"     Data Source ID: {ds_id}")
                print(f"     Database ID: {db_id}")

                # 获取更多信息
                try:
                    # 查询这个数据源
                    query_response = requests.post(
                        f"{BASE_URL}/data_sources/{ds_id}/query",
                        headers=headers,
                        json={"page_size": 1},
                    )
                    query_response.raise_for_status()
                    query_data = query_response.json()
                    page_count = len(query_data.get("results", []))
                    has_more = query_data.get("has_more", False)

                    print(f"     页面数: {page_count}+（has_more: {has_more}）")
                except Exception as e:
                    print(f"     查询失败: {str(e)}")
        else:
            print("\n⚠️  未找到数据源")

        # 显示数据库（旧格式）
        if databases:
            print(f"\n找到 {len(databases)} 个数据库（旧格式）:")
            for i, db in enumerate(databases, 1):
                title = ""
                if db.get("title"):
                    title = db["title"][0].get("plain_text", "未命名")
                print(f"  {i}. {title}")
                print(f"     Database ID: {db['id']}")

        # 显示页面
        if pages:
            print(f"\n找到 {len(pages)} 个页面:")
            for i, page in enumerate(pages[:5], 1):  # 只显示前5个
                # 获取标题
                props = page.get("properties", {})
                title = "未命名"
                for prop_name, prop_value in props.items():
                    if prop_value.get("type") == "title":
                        title_list = prop_value.get("title", [])
                        if title_list:
                            title = title_list[0].get("plain_text", "未命名")
                        break

                print(f"  {i}. {title}")
                print(f"     Page ID: {page['id']}")
                print(f"     URL: {page.get('url', 'N/A')}")

        return data_sources, pages

    except Exception as e:
        print(f"✗ 搜索失败: {str(e)}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"  错误详情: {e.response.text}")
        return [], []


def test_with_data_source(data_source_id, database_id=None):
    """使用数据源 ID 进行完整测试"""
    print("\n" + "=" * 70)
    print(f"完整测试 - Data Source ID: {data_source_id}")
    print("=" * 70)

    headers = get_headers()

    # Test 1: 查询数据源
    print("\n1. 查询数据源...")
    try:
        response = requests.post(
            f"{BASE_URL}/data_sources/{data_source_id}/query",
            headers=headers,
            json={"page_size": 5},
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        print("✓ 查询成功!")
        print(f"  返回 {len(results)} 个页面")
        print(f"  Has more: {data.get('has_more', False)}")

        if results:
            first_page_id = results[0]["id"]

            # Test 2: 读取页面
            print(f"\n2. 读取页面 {first_page_id}...")
            try:
                page_response = requests.get(
                    f"{BASE_URL}/pages/{first_page_id}", headers=headers
                )
                page_response.raise_for_status()
                page = page_response.json()

                print("✓ 页面读取成功!")
                print(f"  ID: {page.get('id')}")
                print(f"  URL: {page.get('url')}")
                print(f"  Created: {page.get('created_time')}")

                # 显示属性
                properties = page.get("properties", {})
                print(f"\n  属性 ({len(properties)} 个):")
                for prop_name, prop_value in list(properties.items())[:5]:
                    print(f"    - {prop_name}: {prop_value.get('type')}")

                # Test 3: 读取页面内容块
                print("\n3. 读取页面内容块...")
                try:
                    blocks_response = requests.get(
                        f"{BASE_URL}/blocks/{first_page_id}/children", headers=headers
                    )
                    blocks_response.raise_for_status()
                    blocks = blocks_response.json()

                    block_list = blocks.get("results", [])
                    print(f"✓ 找到 {len(block_list)} 个内容块")

                    for i, block in enumerate(block_list[:3], 1):
                        print(f"    {i}. {block.get('type')}")

                except Exception as e:
                    print(f"✗ 读取内容块失败: {str(e)}")

            except Exception as e:
                print(f"✗ 读取页面失败: {str(e)}")

        # Test 4: 测试创建页面（可选）
        print("\n4. 是否要测试创建页面?")
        response = input("   输入 y 继续，其他键跳过: ").lower().strip()

        if response == "y":
            # 获取数据库模式
            if database_id:
                db_response = requests.get(
                    f"{BASE_URL}/databases/{database_id}", headers=headers
                )
                db_response.raise_for_status()
                db_data = db_response.json()

                # 找到 title 属性
                title_prop = None
                for prop_name, prop_data in db_data.get("properties", {}).items():
                    if prop_data.get("type") == "title":
                        title_prop = prop_name
                        break

                if title_prop:
                    payload = {
                        "parent": {
                            "type": "data_source_id",
                            "data_source_id": data_source_id,
                        },
                        "properties": {
                            title_prop: {
                                "title": [{"text": {"content": "测试页面 - API 验证"}}]
                            }
                        },
                    }

                    create_response = requests.post(
                        f"{BASE_URL}/pages", headers=headers, json=payload
                    )
                    create_response.raise_for_status()
                    created_page = create_response.json()

                    print("✓ 页面创建成功!")
                    print(f"  Page ID: {created_page.get('id')}")
                    print(f"  URL: {created_page.get('url')}")

        print("\n" + "=" * 70)
        print("✓ 所有测试完成!")
        print("=" * 70)

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"  错误详情: {e.response.text}")


def main():
    print("\n╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Notion API 测试助手".center(76) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    print("\n本脚本将帮助你:")
    print("  1. 查找所有可访问的数据库和数据源")
    print("  2. 测试完整的 API 功能（查询、读取、创建）")
    print("  3. 验证 API 2025-09-03 的所有特性")

    # 搜索内容
    data_sources, pages = search_all_accessible_content()

    # 如果找到数据源，进行测试
    if data_sources:
        print("\n" + "=" * 70)
        ds = data_sources[0]
        ds_id = ds.get("id")
        parent = ds.get("parent", {})
        db_id = parent.get("database_id")

        print("使用第一个数据源进行测试:")
        print(f"  Data Source ID: {ds_id}")
        print(f"  Database ID: {db_id}")

        response = input("\n是否继续完整测试? (y/n): ").lower().strip()
        if response == "y":
            test_with_data_source(ds_id, db_id)
    else:
        print("\n" + "=" * 70)
        print("⚠️  未找到任何数据源")
        print("\n要启用测试，请:")
        print("  1. 在 Notion 中创建或打开一个数据库")
        print("  2. 点击右上角 '...' → Add connections")
        print("  3. 选择你的集成")
        print("  4. 重新运行此脚本")
        print("=" * 70)

    print()


if __name__ == "__main__":
    main()
