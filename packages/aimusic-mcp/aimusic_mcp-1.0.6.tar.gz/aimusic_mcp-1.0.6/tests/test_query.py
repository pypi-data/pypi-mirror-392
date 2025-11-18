"""
测试 query_song_task 函数

状态码说明:
- status = 0: 失败
- status = 1: 成功
- status = 2: 生成中
"""
import asyncio
import os
from musicmcp_ai_mcp.api import query_song_task


# 状态码映射
STATUS_MAP = {
    0: "失败 (Error)",
    1: "成功 (Completed)",
    2: "生成中 (Processing)"
}


async def test_query_song_task():
    """测试查询歌曲状态功能"""

    # 检查 API 密钥
    api_key = os.getenv('MUSICMCP_API_KEY')
    if not api_key:
        print("⚠️  跳过测试: 需要设置 MUSICMCP_API_KEY")
        print("   使用方法: export MUSICMCP_API_KEY='your-api-key-here'")
        return

    print("🧪 测试 query_song_task 函数")
    print("=" * 60)

    # 测试 ID（你提供的示例）
    test_song_id = "769c894e-fb6d-43f7-b717-beddb0fcc6c5"

    print(f"📋 查询歌曲 ID: {test_song_id}")
    print()

    try:
        # 调用函数
        songs, overall_status = await query_song_task([test_song_id])

        print("✅ 查询成功!")
        print(f"   函数返回状态: {overall_status}")
        print(f"   返回歌曲数: {len(songs)}")
        print()

        # 显示详细信息
        if songs:
            for i, song in enumerate(songs, 1):
                song_status = song.get('status', -1)
                status_desc = STATUS_MAP.get(song_status, f"未知状态 ({song_status})")

                print(f"📌 歌曲 {i}:")
                print(f"   ID: {song.get('id', 'N/A')}")
                print(f"   标题: {song.get('songName', 'N/A')}")
                print(f"   状态码: {song_status} - {status_desc}")

                # 只在成功时显示音频信息
                if song_status == 1:
                    song_url = song.get('songUrl', 'N/A')
                    if song_url != 'N/A':
                        print(f"   歌曲 URL: {song_url[:60]}...")
                    print(f"   时长: {song.get('duration', 'N/A')} 秒")
                    print(f"   封面: {song.get('imgUrl', 'N/A')[:60]}..." if song.get('imgUrl') else "   封面: N/A")
                    print(f"   风格标签: {song.get('tags', 'N/A')}")

                print()

        # 验证状态判断
        if songs:
            first_song = songs[0]
            song_status = first_song.get('status', -1)

            print("🔍 状态验证:")
            print(f"   歌曲状态码 (status): {song_status}")
            print(f"   函数返回状态: {overall_status}")
            print()

            # 验证逻辑是否正确
            if song_status == 0 and overall_status == "error":
                print("   ✅ 状态判断正确！(失败)")
            elif song_status == 1 and overall_status == "completed":
                print("   ✅ 状态判断正确！(成功)")
            elif song_status == 2 and overall_status == "processing":
                print("   ✅ 状态判断正确！(生成中)")
            else:
                print(f"   ❌ 状态判断可能有误！")
                print(f"      status={song_status} 但函数返回 '{overall_status}'")

    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


async def test_query_multiple_songs():
    """测试批量查询"""

    api_key = os.getenv('MUSICMCP_API_KEY')
    if not api_key:
        print("⚠️  跳过批量查询测试: 需要设置 MUSICMCP_API_KEY")
        return

    print("🧪 测试批量查询功能")
    print("=" * 60)

    # 测试多个 ID（可以替换为实际的 ID）
    test_song_ids = [
        "769c894e-fb6d-43f7-b717-beddb0fcc6c5",
        # 可以添加更多 ID
    ]

    print(f"📋 查询 {len(test_song_ids)} 首歌曲")
    print()

    try:
        songs, overall_status = await query_song_task(test_song_ids)

        print("✅ 批量查询成功!")
        print(f"   总体状态: {overall_status}")
        print(f"   返回歌曲数: {len(songs)}")
        print()

        # 显示每首歌的状态
        for song in songs:
            song_status = song.get('status', -1)
            status_desc = STATUS_MAP.get(song_status, f"未知({song_status})")
            song_name = song.get('songName', 'N/A')
            print(f"   - {song_name}")
            print(f"     状态: {song_status} ({status_desc})")

    except Exception as e:
        print(f"❌ 批量查询失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_status_logic():
    """测试不同状态的判断逻辑"""

    api_key = os.getenv('MUSICMCP_API_KEY')
    if not api_key:
        print("⚠️  跳过状态逻辑测试: 需要设置 MUSICMCP_API_KEY")
        return

    print("🧪 测试状态判断逻辑")
    print("=" * 60)
    print()
    print("📋 状态码定义:")
    for code, desc in STATUS_MAP.items():
        print(f"   {code} = {desc}")
    print()
    print("📋 预期行为:")
    print("   - 所有歌曲 status=1 → 函数返回 'completed'")
    print("   - 任意歌曲 status=0 → 函数返回 'error'")
    print("   - 任意歌曲 status=2 → 函数返回 'processing'")
    print()


if __name__ == "__main__":
    print("🎵 MusicMCP.AI - query_song_task 测试")
    print()

    # 运行状态逻辑说明
    asyncio.run(test_status_logic())
    print()

    # 运行单个查询测试
    asyncio.run(test_query_song_task())
    print()

    # 运行批量查询测试
    asyncio.run(test_query_multiple_songs())

    print()
    print("=" * 60)
    print("🏁 测试完成!")
