# api.py
import os
import sys
import time
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

mcp = FastMCP("MusicMCP.AI")

# Setup API key for calling MusicMCP.AI API
api_key = os.getenv('MUSICMCP_API_KEY')
api_url = os.getenv('MUSICMCP_API_URL', "https://www.musicmcp.ai/api")
default_time_out = float(os.getenv('TIME_OUT_SECONDS', '600'))


@mcp.tool(
    description="""🎼 Inspiration Mode: Generate songs based on simple text descriptions (AI automatically generates title, lyrics, style, etc.)

    Use case: Use when users only provide simple song themes or emotional descriptions without detailed specifications.

    Example inputs:
    - "Help me generate a song about a peaceful morning"
    - "Want a song that expresses longing"
    - "Create music about friendship"

    ⚠️ COST WARNING: This tool makes an API call to MusicMCP.AI which may incur costs (5 credits per generation). Each generation creates 2 songs. Only use when explicitly requested by the user.

    Language Note: Pass the prompt in the user's input language.

    Args:
        prompt (str): Song theme or emotional description, 1-1200 characters
        instrumental (bool): Whether instrumental only (no lyrics)
        style (str, optional): Music style (e.g., "ambient", "pop", "rock"), default None

    Returns:
        Song information including download URLs
    """
)
async def generate_prompt_song(
    prompt: str,
    instrumental: bool,
    style: str | None = None
) -> list[TextContent]:
    try:
        if not api_key:
            raise Exception("Cannot find API key. Please set MUSICMCP_API_KEY environment variable.")

        if not prompt or prompt.strip() == "":
            raise Exception("Prompt text is required.")

        if len(prompt.strip()) > 1200:
            raise Exception("Prompt text must be less than 1200 characters.")

        url = f"{api_url}/music/generate/inspiration"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }

        params = {
            "prompt": prompt,
            "instrumental": instrumental,
        }

        if style is not None:
            params["style"] = style

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, json=params, headers=headers)
            response.raise_for_status()
            result = response.json()

        # New API response format: {code, message, data}
        if not result or result.get("code") != 200:
            error_msg = result.get("message", "Unknown error") if result else "No response"
            raise Exception(f"Failed to create song generation task: {error_msg}")

        # New format: data contains {ids: [...]}
        data = result.get("data", {})
        song_ids = data.get("ids", [])

        if not song_ids:
            raise Exception("No song IDs returned from API")

        # Redirect debug info to stderr to avoid breaking JSON-RPC
        print(f"✅ Song generation task created. Song IDs: {song_ids}", file=sys.stderr)

        # Poll for task completion
        current_timestamp = datetime.now().timestamp()
        while True:
            if (datetime.now().timestamp() - current_timestamp) > default_time_out:
                raise Exception(f"Song generation timed out after {default_time_out} seconds")

            songs, status = await query_song_task(song_ids)

            if status == "error":
                raise Exception("Song generation failed with error status")
            elif status == "timeout":
                raise Exception("Song generation timed out")
            elif status == "completed" or status == "success":
                break
            else:
                time.sleep(2)

        # Return song information with URLs
        results = []
        for i, song in enumerate(songs, 1):
            song_url = song.get("songUrl") or song.get("audio_url") or song.get("url")
            song_title = song.get("songName", f"Song {i}").strip()
            song_id = song.get("id", "N/A")

            # Additional fields
            duration = song.get("duration", 0)
            tags = song.get("tags", "")
            img_url = song.get("imgUrl", "")
            lyric = song.get("lyric", "")
            instrumental = song.get("instrumental", 0)
            created_at = song.get("createdAt", "")

            if not song_url:
                continue

            # Format duration
            duration_str = f"{duration}s" if duration else "N/A"

            # Format instrumental status
            is_instrumental = "Yes" if instrumental == 1 else "No"

            text = f"""✅ Song {i} generated successfully!

📌 Title: {song_title}
🆔 ID: {song_id}
🔗 Download URL: {song_url}
🖼️  Cover Image: {img_url if img_url else "N/A"}
⏱️  Duration: {duration_str}
🎵 Style Tags: {tags if tags else "N/A"}
🎹 Instrumental: {is_instrumental}
📅 Created: {created_at if created_at else "N/A"}"""

            # Add lyrics if available and not instrumental
            if lyric and instrumental == 0:
                # Truncate lyrics if too long
                lyric_preview = lyric[:200] + "..." if len(lyric) > 200 else lyric
                text += f"\n📝 Lyrics Preview:\n{lyric_preview}"

            text += "\n\nYou can download or play the audio from the URL above."

            results.append(TextContent(type="text", text=text))

        if not results:
            raise Exception("No songs were generated successfully")

        return results

    except httpx.HTTPStatusError as e:
        error_detail = f"HTTP {e.response.status_code}"
        if e.response.status_code == 402:
            error_detail = "Insufficient credits. Please recharge your account."
        elif e.response.status_code == 401:
            error_detail = "Invalid API key. Please check your MUSICMCP_API_KEY."
        raise Exception(f"Request failed: {error_detail}") from e
    except Exception as e:
        raise Exception(f"Song generation failed: {str(e)}") from e


@mcp.tool(
    description="""🎵 Custom Mode: Generate songs based on detailed song information (user specifies song name, lyrics, style, etc.)

    Use case: Use when users provide detailed song information including song name, complete lyrics, and style.

    Example inputs:
    - "Song name: Summer of Cicada Shedding, Lyrics: [complete lyrics], style: folk"

    ⚠️ COST WARNING: This tool makes an API call to MusicMCP.AI which may incur costs (5 credits per generation). Each generation creates 2 songs. Only use when explicitly requested by the user.

    Language Note: Pass the title and lyrics in the user's input language.

    Args:
        title (str): Song title, required
        lyric (str, optional): Complete lyrics content, not required when instrumental is True
        tags (str, optional): Music style tags (e.g., 'pop', 'rock', 'folk')
        instrumental (bool): Whether instrumental only (no lyrics)

    Returns:
        Song information including download URLs
    """
)
async def generate_custom_song(
    title: str,
    instrumental: bool,
    lyric: str | None = None,
    tags: str | None = None
) -> list[TextContent]:
    try:
        if not api_key:
            raise Exception("Cannot find API key. Please set MUSICMCP_API_KEY environment variable.")

        if not title or title.strip() == "":
            raise Exception("Title is required.")

        # Lyric is only required when not instrumental
        if not instrumental and (not lyric or lyric.strip() == ""):
            raise Exception("Lyrics are required when instrumental is False.")

        url = f"{api_url}/music/generate/custom"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }

        params = {
            "title": title,
            "instrumental": instrumental,
        }

        # Add optional parameters
        if lyric is not None and lyric.strip():
            params["lyric"] = lyric

        if tags is not None and tags.strip():
            params["tags"] = tags

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, json=params, headers=headers)
            response.raise_for_status()
            result = response.json()

        # New API response format: {code, message, data}
        if not result or result.get("code") != 200:
            error_msg = result.get("message", "Unknown error") if result else "No response"
            raise Exception(f"Failed to create custom song generation task: {error_msg}")

        # New format: data contains {ids: [...]}
        data = result.get("data", {})
        song_ids = data.get("ids", [])

        if not song_ids:
            raise Exception("No song IDs returned from API")

        # Redirect debug info to stderr to avoid breaking JSON-RPC
        print(f"✅ Custom song generation task created. Song IDs: {song_ids}", file=sys.stderr)

        # Poll for task completion
        current_timestamp = datetime.now().timestamp()
        while True:
            if (datetime.now().timestamp() - current_timestamp) > default_time_out:
                raise Exception(f"Custom song generation timed out after {default_time_out} seconds")

            songs, status = await query_song_task(song_ids)
            # Redirect debug info to stderr to avoid breaking JSON-RPC
            print(f"🎵 Custom song generation task status: {status}", file=sys.stderr)
            print(f"🎵 Custom song generation task songs: {songs}", file=sys.stderr)

            if status == "error":
                raise Exception("Custom song generation failed with error status")
            elif status == "timeout":
                raise Exception("Custom song generation timed out")
            elif status == "completed" or status == "success":
                break
            else:
                time.sleep(2)

        # Return song information with URLs
        results = []
        for i, song in enumerate(songs, 1):
            song_url = song.get("songUrl") or song.get("audio_url") or song.get("url")
            song_title = song.get("songName", title).strip()
            song_id = song.get("id", "N/A")

            # Additional fields
            duration = song.get("duration", 0)
            tags = song.get("tags", "")
            img_url = song.get("imgUrl", "")
            lyric = song.get("lyric", "")
            instrumental_flag = song.get("instrumental", 0)
            created_at = song.get("createdAt", "")

            if not song_url:
                continue

            # Format duration
            duration_str = f"{duration}s" if duration else "N/A"

            # Format instrumental status
            is_instrumental = "Yes" if instrumental_flag == 1 else "No"

            text = f"""✅ Custom song '{title}' (version {i}) generated successfully!

📌 Title: {song_title}
🆔 ID: {song_id}
🔗 Download URL: {song_url}
🖼️  Cover Image: {img_url if img_url else "N/A"}
⏱️  Duration: {duration_str}
🎵 Style Tags: {tags if tags else "N/A"}
🎹 Instrumental: {is_instrumental}
📅 Created: {created_at if created_at else "N/A"}"""

            # Add lyrics if available and not instrumental
            if lyric and instrumental_flag == 0:
                # Truncate lyrics if too long
                lyric_preview = lyric[:200] + "..." if len(lyric) > 200 else lyric
                text += f"\n📝 Lyrics Preview:\n{lyric_preview}"

            text += "\n\nYou can download or play the audio from the URL above."

            results.append(TextContent(type="text", text=text))

        if not results:
            raise Exception("No songs were generated successfully")

        return results

    except httpx.HTTPStatusError as e:
        error_detail = f"HTTP {e.response.status_code}"
        if e.response.status_code == 402:
            error_detail = "Insufficient credits. Please recharge your account."
        elif e.response.status_code == 401:
            error_detail = "Invalid API key. Please check your MUSICMCP_API_KEY."
        raise Exception(f"Request failed: {error_detail}") from e
    except Exception as e:
        raise Exception(f"Custom song generation failed: {str(e)}") from e


async def query_song_task(song_ids: list[str]) -> tuple[list, str]:
    """Query song generation task status

    Args:
        song_ids: List of song IDs (batch query supported)

    Returns:
        Tuple of (songs_list, status_string)
    """
    try:
        url = f"{api_url}/music/generate/query"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        params = {"ids": song_ids}

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, json=params, headers=headers)
            response.raise_for_status()
            result = response.json()

        # New API response format: {code, message, data}
        if not result or result.get("code") != 200:
            return [], "error"

        # New format: data contains {songs: [...]}
        data = result.get("data", {})
        songs = data.get("songs", [])

        if songs and len(songs) > 0:
            all_complete = True
            any_error = False

            for song in songs:
                status = song.get("status", 0)
                if status == 0:  # 0 = Failed
                    any_error = True
                    break
                elif status != 1:  # 1 = Completed, 2 = In Progress
                    all_complete = False

            if any_error:
                return songs, "error"
            elif all_complete:
                return songs, "completed"
            else:
                return songs, "processing"
        else:
            return [], "processing"

    except Exception as e:
        # Redirect error info to stderr to avoid breaking JSON-RPC
        print(f"Query error: {str(e)}", file=sys.stderr)
        raise Exception(f"Failed to query song status: {str(e)}") from e


@mcp.tool(description="Check your credit balance.")
async def check_credit_balance() -> TextContent:
    """Check credit balance"""
    try:
        if not api_key:
            raise Exception("Cannot find API key. Please set MUSICMCP_API_KEY environment variable.")

        url = f"{api_url}/credit"
        headers = {'api-key': api_key}

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()

        # New API response format: {code, message, data}
        if not result or result.get("code") != 200:
            error_msg = result.get("message", "Unknown error")
            return TextContent(type="text", text=f"❌ Credit balance check failed: {error_msg}")

        data = result.get("data", {})
        if data.get("valid"):
            has_credits = data.get("hasCredits", False)
            credits = data.get("credits", 0)
            if has_credits:
                return TextContent(
                    type="text",
                    text=f"✅ API key is valid! You have {credits} credits remaining."
                )
            else:
                return TextContent(
                    type="text",
                    text="⚠️ API key is valid but you have insufficient credits. Please recharge."
                )
        else:
            return TextContent(type="text", text="❌ API key is invalid.")

    except Exception as e:
        return TextContent(type="text", text=f"❌ Failed to check credit balance: {str(e)}")


@mcp.tool(description="Check the health status of the MusicMCP.AI API service.")
async def check_api_health() -> TextContent:
    """Check API service health status"""
    try:
        url = f"{api_url}/health"

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()

        # New API response format: {code, message, data}
        if result and result.get("code") == 200:
            return TextContent(type="text", text="✅ MusicMCP.AI API service is healthy and operational.")
        else:
            return TextContent(type="text", text="⚠️ MusicMCP.AI API service health check failed.")

    except Exception as e:
        return TextContent(type="text", text=f"❌ Failed to check API health: {str(e)}")


def main():
    """Run MCP server"""
    # Do not print to stdout - it will break JSON-RPC communication
    # All MCP communication uses stdin/stdout for JSON-RPC
    mcp.run()


if __name__ == "__main__":
    main()
