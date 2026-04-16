import os
from dotenv import load_dotenv # 1. Import dotenv
from google import genai
from google.genai import types
from playlist_logic import default_songs

# 2. Load the .env file immediately
load_dotenv() 

# Treat this as your "Database" for the agent to query
SONG_LIBRARY = default_songs()

# --- 1. Define the Tools ---
# Gemini reads the docstrings and type hints to understand how to use these!

def filter_by_genre(target_genre: str) -> list[dict]:
    """
    Returns a list of songs that match the target genre.
    Use this when the user asks for a specific style of music like 'rock', 'lofi', or 'pop'.
    """
    return [s for s in SONG_LIBRARY if str(s.get("genre", "")).lower() == target_genre.lower()]

def filter_by_energy(min_energy: int = 1, max_energy: int = 10) -> list[dict]:
    """
    Returns a list of songs within a specific energy range (1 to 10).
    Use this when a user asks for 'hype', 'high energy' (7-10), or 'chill', 'low energy' (1-3) music.
    """
    return [s for s in SONG_LIBRARY if min_energy <= int(s.get("energy", 0)) <= max_energy]

def search_by_tag(target_tag: str) -> list[dict]:
    """
    Returns a list of songs that contain the specific tag.
    Use this to find specific vibes like 'synth', 'guitar', 'sleep', or 'party'.
    """
    filtered = []
    for s in SONG_LIBRARY:
        tags = [str(t).lower() for t in s.get("tags", [])]
        if target_tag.lower() in tags:
            filtered.append(s)
    return filtered

def log_playlist_generation(user_prompt: str, playlist_titles: list[str]) -> str:
    """
    Saves the final generated playlist to the database for reliability tracking.
    This MUST be called as the final step before returning the playlist to the user.
    """
    # For now, we will just print to the console. 
    # For your final project, replace this with a Supabase insert!
    print(f"\n[LOGGING TO DB] Prompt: '{user_prompt}'")
    print(f"[LOGGING TO DB] Generated Playlist: {playlist_titles}\n")
    return "Successfully logged to database."

# --- 2. Initialize the Gemini Agent ---

def initialize_dj_agent():
    """Sets up the Gemini client with the DJ tools."""
    client = genai.Client() 
    
    dj_tools = [filter_by_genre, filter_by_energy, search_by_tag, log_playlist_generation]
    
    config = types.GenerateContentConfig(
        tools=dj_tools,
        temperature=0.7,
        system_instruction=(
            "You are the Agentic DJ. Your goal is to build a personalized playlist "
            "based on the user's prompt using the tools provided. "
            "1. Analyze the user's prompt.\n"
            "2. Use the tools to query the song library.\n"
            "3. Select the best matching songs.\n"
            "4. IMPORTANT: You MUST call `log_playlist_generation` before giving your final answer.\n"
            "5. Present the final playlist to the user in a cool, formatted markdown list."
        )
    )
    
    chat_session = client.chats.create(
        model='gemini-2.5-flash',
        config=config
    )
    
    # NEW: Return the client as well so we can keep it alive in Streamlit!
    return client, chat_session