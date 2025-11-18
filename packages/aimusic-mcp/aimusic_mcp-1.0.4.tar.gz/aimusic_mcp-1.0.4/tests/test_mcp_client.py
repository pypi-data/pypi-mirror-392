"""
MCP 客户端测试脚本
直接测试 MCP 服务器的工具调用功能
"""
import pytest
import asyncio
import os
from musicmcp_ai_mcp.api import (
    check_credit_balance,
    check_api_health,
    generate_prompt_song
)


@pytest.mark.asyncio
async def test_mcp_tools():
    """测试所有 MCP 工具"""
    print("🧪 开始 MCP 工具测试")
    print("=" * 60)

    # 检查环境变量
    api_key = os.getenv('MUSICMCP_API_KEY')
    if not api_key:
        print("⚠️  警告: MUSICMCP_API_KEY 未设置")
        print("   某些测试可能会跳过")
    print()

    # 测试 1: API 健康检查（不需要密钥）
    print("1️⃣ 测试 API 健康检查")
    print("-" * 60)
    try:
        result = await check_api_health()
        print(f"✅ 成功")
        print(f"   返回类型: {type(result)}")
        print(f"   内容: {result.text}")
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
    print()

    # 测试 2: 检查积分余额（需要密钥）
    if api_key:
        print("2️⃣ 测试积分余额查询")
        print("-" * 60)
        try:
            result = await check_credit_balance()
            print(f"✅ 成功")
            print(f"   返回类型: {type(result)}")
            print(f"   内容: {result.text}")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
        print()
    else:
        print("2️⃣ 跳过积分余额查询（未设置密钥）")
        print()

    # 测试 3: 生成音乐（需要密钥和积分，慎重执行）
    # 默认注释掉，避免消耗积分
    """
    if api_key:
        print("3️⃣ 测试音乐生成（灵感模式）")
        print("-" * 60)
        print("⚠️  此测试会消耗 5 积分！")

        # 取消注释以启用测试
        # try:
        #     result = await generate_prompt_song(
        #         prompt="A peaceful morning test song",
        #         instrumental=True
        #     )
        #     print(f"✅ 成功")
        #     print(f"   生成歌曲数: {len(result)}")
        #     for i, item in enumerate(result, 1):
        #         print(f"   歌曲 {i}: {item.text[:100]}...")
        # except Exception as e:
        #     print(f"❌ 失败: {str(e)}")
        # print()
    """

    print("=" * 60)
    print("🏁 MCP 工具测试完成！")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
