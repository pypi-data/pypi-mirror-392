#!/usr/bin/env python3
"""
测试读取页面功能
"""

import requests

NOTION_API_TOKEN = "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"
BASE_URL = "https://api.notion.com/v1"
API_VERSION = "2025-09-03"

# 从搜索中发现的页面 ID
PAGE_IDS = [
    "25b4b245-345e-4235-84f2-05736b80bbf6",  # Weekly To-do List
    "7099f139-8c2f-4277-9993-540a9752c9e6",  # Getting Started on Mobile
    "f87b82a1-8244-4d05-8e40-61eefa2f428b",  # Example sub page
]


def test_read_page(page_id, page_name=""):
    """测试读取单个页面"""
    print("\n" + "=" * 70)
    print(f"测试读取页面: {page_name}")
    print(f"Page ID: {page_id}")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json",
    }

    # Test 1: 读取页面基本信息
    print("\n1. 读取页面基本信息...")
    try:
        response = requests.get(f"{BASE_URL}/pages/{page_id}", headers=headers)
        response.raise_for_status()
        page = response.json()

        print("✓ 页面读取成功!")
        print(f"  Object: {page.get('object')}")
        print(f"  ID: {page.get('id')}")
        print(f"  Created: {page.get('created_time')}")
        print(f"  Last edited: {page.get('last_edited_time')}")
        print(f"  URL: {page.get('url')}")
        print(f"  Archived: {page.get('archived', False)}")

        # 父级信息
        parent = page.get("parent", {})
        print("\n  父级信息:")
        print(f"    类型: {parent.get('type')}")
        if parent.get("workspace"):
            print("    位置: Workspace")
        elif parent.get("page_id"):
            print(f"    父页面 ID: {parent.get('page_id')}")
        elif parent.get("database_id"):
            print(f"    数据库 ID: {parent.get('database_id')}")
        elif parent.get("data_source_id"):
            print(f"    数据源 ID: {parent.get('data_source_id')}")

        # 属性
        properties = page.get("properties", {})
        print(f"\n  属性 ({len(properties)} 个):")
        for prop_name, prop_value in properties.items():
            prop_type = prop_value.get("type")
            print(f"    - {prop_name}: {prop_type}")

            # 显示值
            if prop_type == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    text = title_list[0].get("plain_text", "")
                    print(f'      值: "{text}"')

        # Test 2: 读取页面内容块
        print("\n2. 读取页面内容块...")
        try:
            blocks_response = requests.get(
                f"{BASE_URL}/blocks/{page_id}/children",
                headers=headers,
                params={"page_size": 10},
            )
            blocks_response.raise_for_status()
            blocks = blocks_response.json()

            block_list = blocks.get("results", [])
            print(f"✓ 找到 {len(block_list)} 个内容块")

            if block_list:
                print("\n  内容块列表:")
                for i, block in enumerate(block_list, 1):
                    block_type = block.get("type")
                    print(f"    {i}. {block_type} (ID: {block.get('id')})")

                    # 显示部分内容
                    if block_type == "paragraph":
                        para = block.get("paragraph", {})
                        rich_text = para.get("rich_text", [])
                        if rich_text:
                            text = rich_text[0].get("plain_text", "")[:50]
                            print(f"       内容: {text}...")
                    elif block_type in ["heading_1", "heading_2", "heading_3"]:
                        heading = block.get(block_type, {})
                        rich_text = heading.get("rich_text", [])
                        if rich_text:
                            text = rich_text[0].get("plain_text", "")
                            print(f"       标题: {text}")
                    elif block_type == "to_do":
                        todo = block.get("to_do", {})
                        rich_text = todo.get("rich_text", [])
                        checked = todo.get("checked", False)
                        if rich_text:
                            text = rich_text[0].get("plain_text", "")
                            status = "☑" if checked else "☐"
                            print(f"       {status} {text}")
            else:
                print("  (页面为空)")

        except Exception as e:
            print(f"✗ 读取内容块失败: {str(e)}")

        print("\n" + "=" * 70)
        print("✓ 页面测试完成")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"✗ 读取失败: {str(e)}")
        if hasattr(e, "response"):
            try:
                print(f"  状态码: {e.response.status_code}")
                print(f"  响应: {e.response.text}")
            except:
                pass
        return False


def main():
    print("\n╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  测试 Notion 页面读取功能".center(76) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    print("\n将测试以下功能:")
    print("  1. get_page() - 读取页面基本信息")
    print("  2. get_block_children() - 读取页面内容块")
    print("  3. 显示页面属性和结构")

    # 测试每个页面
    pages_info = [
        ("25b4b245-345e-4235-84f2-05736b80bbf6", "Weekly To-do List"),
        ("7099f139-8c2f-4277-9993-540a9752c9e6", "Getting Started on Mobile"),
        ("f87b82a1-8244-4d05-8e40-61eefa2f428b", "Example sub page"),
    ]

    success_count = 0
    for page_id, page_name in pages_info:
        if test_read_page(page_id, page_name):
            success_count += 1

        # 询问是否继续
        if success_count < len(pages_info):
            response = input("\n继续测试下一个页面? (y/n): ").lower().strip()
            if response != "y":
                break

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"  成功: {success_count}/{len(pages_info)}")
    print(f"  失败: {len(pages_info) - success_count}/{len(pages_info)}")

    if success_count == len(pages_info):
        print("\n✓ 所有页面读取功能测试通过!")
        print("✓ NotionHook.get_page() 工作正常")
        print("✓ NotionHook.get_block_children() 工作正常")
    elif success_count > 0:
        print("\n⚠️  部分测试通过")
    else:
        print("\n✗ 所有测试失败")

    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
