import pytest
import asyncio
import os
from musicmcp_ai_mcp.api import (
    generate_prompt_song,
    generate_custom_song,
    check_credit_balance,
    check_api_health
)


@pytest.mark.asyncio
async def test_generate_prompt_song():
    """测试MusicMCP.AI灵感模式歌曲生成功能"""
    try:
        # 检查API密钥是否设置
        api_key = os.getenv('MUSICMCP_API_KEY')
        if not api_key:
            print("⚠️  Skipping prompt song generation test: MUSICMCP_API_KEY not set")
            return

        print("🎼 Testing prompt song generation with MusicMCP.AI API...")

        # 测试灵感模式歌曲生成
        result = await generate_prompt_song(
            prompt="A peaceful morning in the mountains with gentle piano and nature sounds",
            instrumental=True,
            style="ambient"
        )

        # 验证返回结果
        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Should return at least one song"

        # 验证返回包含完整的元数据字段
        for item in result:
            text = item.text
            # 核心字段
            assert "Title:" in text, "Result should contain song title"
            assert "ID:" in text, "Result should contain song ID"
            assert "Download URL:" in text, "Result should contain download URL"
            # 新增的元数据字段
            assert "Cover Image:" in text, "Result should contain cover image"
            assert "Duration:" in text, "Result should contain duration"
            assert "Style Tags:" in text, "Result should contain style tags"
            assert "Instrumental:" in text, "Result should contain instrumental status"
            assert "Created:" in text, "Result should contain creation timestamp"

        print("✅ Prompt song generation test passed")
        print(f"   Generated {len(result)} songs")

    except Exception as e:
        print(f"❌ Prompt song generation test failed: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_generate_custom_song():
    """测试MusicMCP.AI自定义模式歌曲生成功能"""
    try:
        # 检查API密钥是否设置
        api_key = os.getenv('MUSICMCP_API_KEY')
        if not api_key:
            print("⚠️  Skipping custom song generation test: MUSICMCP_API_KEY not set")
            return

        print("🎵 Testing custom song generation with MusicMCP.AI API...")

        # 测试自定义模式歌曲生成
        result = await generate_custom_song(
            title="Test Song",
            lyric="This is a test lyric for custom song generation",
            tags="pop",
            instrumental=False
        )

        # 验证返回结果
        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Should return at least one song"

        # 验证返回包含完整的元数据字段
        for item in result:
            text = item.text
            # 核心字段
            assert "Download URL:" in text, "Result should contain download URL"
            assert "Test Song" in text or "ID:" in text, "Result should contain song info"
            assert "Title:" in text, "Result should contain song title"
            # 新增的元数据字段
            assert "Cover Image:" in text, "Result should contain cover image"
            assert "Duration:" in text, "Result should contain duration"
            assert "Style Tags:" in text, "Result should contain style tags"
            assert "Instrumental:" in text, "Result should contain instrumental status"
            assert "Created:" in text, "Result should contain creation timestamp"
            # 非器乐曲应该包含歌词
            if "Instrumental: No" in text:
                assert "Lyrics Preview:" in text, "Non-instrumental songs should contain lyrics preview"

        print("✅ Custom song generation test passed")
        print(f"   Generated {len(result)} songs")

    except Exception as e:
        print(f"❌ Custom song generation test failed: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_check_credit_balance():
    """测试积分余额查询功能"""
    try:
        api_key = os.getenv('MUSICMCP_API_KEY')
        if not api_key:
            print("⚠️  Skipping credit balance check test: MUSICMCP_API_KEY not set")
            return

        print("✅ Testing credit balance check...")

        result = await check_credit_balance()

        # 验证返回结果
        assert result is not None, "Result should not be None"
        assert hasattr(result, 'text'), "Result should have text attribute"

        text = result.text
        assert "API key" in text or "valid" in text.lower(), "Result should contain API key validation status"
        # 应该包含积分信息
        assert "credits" in text.lower() or "credit" in text.lower(), "Result should contain credits information"

        print("✅ Credit balance check test passed")
        print(f"   {text}")

    except Exception as e:
        print(f"❌ Credit balance check test failed: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_check_api_health():
    """测试API健康检查功能"""
    try:
        print("🏥 Testing API health check...")

        result = await check_api_health()

        # 验证返回结果
        assert result is not None, "Result should not be None"
        assert hasattr(result, 'text'), "Result should have text attribute"

        print("✅ API health check test passed")
        print(f"   {result.text}")

    except Exception as e:
        print(f"❌ API health check test failed: {str(e)}")
        raise


def test_environment_setup():
    """测试环境配置"""
    print("🔧 Testing environment configuration...")

    required_vars = ['MUSICMCP_API_KEY']
    optional_vars = ['MUSICMCP_API_URL', 'TIME_OUT_SECONDS']

    # 检查必需的环境变量
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
    else:
        print("✅ All required environment variables are set")

    # 显示可选环境变量
    print("📋 Optional environment variables:")
    for var in optional_vars:
        value = os.getenv(var, "Not set")
        print(f"   {var}: {value}")


def test_mcp_tools_availability():
    """测试MCP工具是否可用"""
    print("🛠️  Testing MCP tools availability...")

    try:
        # 检查工具函数是否存在
        assert hasattr(generate_prompt_song, '__call__'), "generate_prompt_song function not found"
        assert hasattr(generate_custom_song, '__call__'), "generate_custom_song function not found"
        assert hasattr(check_credit_balance, '__call__'), "check_credit_balance function not found"
        assert hasattr(check_api_health, '__call__'), "check_api_health function not found"

        print("✅ All 4 MCP tools are available")

        # 检查工具描述
        tools = [
            ("generate_prompt_song", generate_prompt_song),
            ("generate_custom_song", generate_custom_song),
            ("check_credit_balance", check_credit_balance),
            ("check_api_health", check_api_health)
        ]

        for name, tool in tools:
            if hasattr(tool, '__name__'):
                print(f"   ✓ {name}")

    except Exception as e:
        print(f"❌ MCP tools test failed: {str(e)}")
        raise


if __name__ == "__main__":
    print("🧪 Running MusicMCP.AI MCP Server Tests")
    print("=" * 50)

    # 运行环境配置测试
    test_environment_setup()
    print()

    # 运行MCP工具可用性测试
    test_mcp_tools_availability()
    print()

    # 运行API健康检查测试
    try:
        asyncio.run(test_check_api_health())
    except Exception as e:
        print(f"❌ API health check failed: {str(e)}")
    print()

    # 运行积分余额查询测试（需要API密钥）
    try:
        asyncio.run(test_check_credit_balance())
    except Exception as e:
        print(f"❌ Credit balance check failed: {str(e)}")
    print()

    # 运行灵感模式歌曲生成测试（需要API密钥和积分）
    try:
        asyncio.run(test_generate_prompt_song())
    except Exception as e:
        print(f"❌ Prompt song generation test failed: {str(e)}")
    print()

    # 运行自定义模式歌曲生成测试（需要API密钥和积分）
    try:
        asyncio.run(test_generate_custom_song())
    except Exception as e:
        print(f"❌ Custom song generation test failed: {str(e)}")

    print("=" * 50)
    print("🏁 Tests completed!")
