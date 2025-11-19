#!/usr/bin/env python3
"""
示例：如何使用 NotionHook 读取页面

演示了两种方式：
1. 直接使用 page_id
2. 先查询数据库，然后读取页面
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import Mock
from airflow.providers.notion.hooks.notion import NotionHook


def example_read_page_direct():
    """示例 1: 直接使用 page_id 读取页面"""
    print("\n" + "=" * 60)
    print("示例 1: 直接读取页面")
    print("=" * 60)

    # 模拟 Airflow 连接
    def mock_get_connection(conn_id):
        conn = Mock()
        conn.password = "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"
        conn.host = None
        conn.extra = None
        return conn

    # 创建 hook
    hook = NotionHook(notion_conn_id="notion_default")
    hook.get_connection = mock_get_connection

    # 如果你有一个页面 ID，可以直接读取
    page_id = "YOUR_PAGE_ID_HERE"  # 替换为实际的页面 ID

    try:
        print(f"\n读取页面: {page_id}")
        page = hook.get_page(page_id=page_id)

        print("✓ 页面读取成功!")
        print(f"  ID: {page.get('id')}")
        print(f"  URL: {page.get('url')}")
        print(f"  创建时间: {page.get('created_time')}")
        print(f"  最后编辑: {page.get('last_edited_time')}")

        # 显示属性
        properties = page.get("properties", {})
        print(f"\n  属性 ({len(properties)} 个):")
        for prop_name, prop_value in properties.items():
            prop_type = prop_value.get("type")
            print(f"    - {prop_name}: {prop_type}")

        # 显示父级信息
        parent = page.get("parent", {})
        print("\n  父级:")
        print(f"    类型: {parent.get('type')}")
        if parent.get("data_source_id"):
            print(f"    Data Source ID: {parent.get('data_source_id')}")

        return page

    except Exception as e:
        print(f"✗ 读取失败: {str(e)}")
        print("\n提示: 请将 page_id 替换为你实际的页面 ID")
        return None


def example_query_then_read():
    """示例 2: 查询数据库后读取第一个页面"""
    print("\n" + "=" * 60)
    print("示例 2: 查询后读取页面")
    print("=" * 60)

    # 模拟连接
    def mock_get_connection(conn_id):
        conn = Mock()
        conn.password = "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"
        conn.host = None
        conn.extra = None
        return conn

    # 创建 hook
    hook = NotionHook(notion_conn_id="notion_default")
    hook.get_connection = mock_get_connection

    # 替换为你的数据库 ID
    database_id = "YOUR_DATABASE_ID_HERE"

    try:
        print(f"\n步骤 1: 查询数据库 {database_id}")

        # 查询数据库（会自动发现 data_source_id）
        query_result = hook.query_database(
            database_id=database_id,
            page_size=1,  # 只获取第一个页面
        )

        results = query_result.get("results", [])
        print(f"✓ 查询成功，找到 {len(results)} 个页面")

        if not results:
            print("数据库为空")
            return None

        # 获取第一个页面的 ID
        first_page_id = results[0]["id"]
        print(f"\n步骤 2: 读取第一个页面 {first_page_id}")

        # 读取完整的页面信息
        page = hook.get_page(page_id=first_page_id)

        print("✓ 页面读取成功!")
        print(f"  ID: {page.get('id')}")
        print(f"  URL: {page.get('url')}")

        # 显示所有属性
        properties = page.get("properties", {})
        print("\n  所有属性:")
        for prop_name, prop_value in properties.items():
            prop_type = prop_value.get("type")
            print(f"    {prop_name} ({prop_type}):")

            # 根据类型显示值
            if prop_type == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    text = title_list[0].get("plain_text", "")
                    print(f"      值: {text}")
            elif prop_type == "rich_text":
                text_list = prop_value.get("rich_text", [])
                if text_list:
                    text = text_list[0].get("plain_text", "")
                    print(f"      值: {text}")
            elif prop_type == "select":
                select = prop_value.get("select")
                if select:
                    print(f"      值: {select.get('name')}")
            elif prop_type == "number":
                number = prop_value.get("number")
                print(f"      值: {number}")
            elif prop_type == "checkbox":
                checkbox = prop_value.get("checkbox")
                print(f"      值: {'✓' if checkbox else '✗'}")

        return page

    except Exception as e:
        print(f"✗ 操作失败: {str(e)}")
        print("\n提示:")
        print("  1. 请将 database_id 替换为你实际的数据库 ID")
        print("  2. 确保数据库已与集成共享")
        return None


def example_read_with_blocks():
    """示例 3: 读取页面和其内容块"""
    print("\n" + "=" * 60)
    print("示例 3: 读取页面和内容块")
    print("=" * 60)

    # 模拟连接
    def mock_get_connection(conn_id):
        conn = Mock()
        conn.password = "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"
        conn.host = None
        conn.extra = None
        return conn

    hook = NotionHook(notion_conn_id="notion_default")
    hook.get_connection = mock_get_connection

    page_id = "YOUR_PAGE_ID_HERE"

    try:
        print("\n步骤 1: 读取页面信息")
        page = hook.get_page(page_id=page_id)
        print(f"✓ 页面: {page.get('id')}")

        print("\n步骤 2: 读取页面内容块")
        blocks = hook.get_block_children(block_id=page_id)

        block_list = blocks.get("results", [])
        print(f"✓ 找到 {len(block_list)} 个内容块")

        # 显示每个块
        for i, block in enumerate(block_list, 1):
            block_type = block.get("type")
            print(f"\n  块 {i}: {block_type}")
            print(f"    ID: {block.get('id')}")

            # 根据块类型显示内容
            if block_type == "paragraph":
                paragraph = block.get("paragraph", {})
                text_list = paragraph.get("rich_text", [])
                if text_list:
                    text = text_list[0].get("plain_text", "")
                    print(f"    内容: {text}")
            elif block_type == "heading_1":
                heading = block.get("heading_1", {})
                text_list = heading.get("rich_text", [])
                if text_list:
                    text = text_list[0].get("plain_text", "")
                    print(f"    内容: {text}")

        return page, blocks

    except Exception as e:
        print(f"✗ 操作失败: {str(e)}")
        print("\n提示: 请将 page_id 替换为你实际的页面 ID")
        return None, None


def main():
    """运行所有示例"""
    print("\n╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Notion Hook - 读取页面示例".center(66) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    print("\n⚠️  注意：这些示例需要你提供实际的 ID")
    print("你可以：")
    print("  1. 修改代码中的 YOUR_PAGE_ID_HERE 和 YOUR_DATABASE_ID_HERE")
    print("  2. 或者直接运行测试脚本：")
    print("     python tests/test_notion_api_quick.py")
    print("     python tests/test_with_database_id.py <database_id>")

    # 运行示例（需要替换实际 ID）
    example_read_page_direct()
    example_query_then_read()
    example_read_with_blocks()

    print("\n" + "=" * 60)
    print("示例代码位置：")
    print("  tests/examples/read_page_example.py")
    print("\n完整文档：")
    print("  README.md")
    print("  tests/TEST_README.md")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
