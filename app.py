import streamlit as st
from agent_logic import initialize_dj_agent
from playlist_logic import default_songs

from playlist_logic import (
    DEFAULT_PROFILE,
    Song,
    build_playlists,
    compute_playlist_stats,
    history_summary,
    lucky_pick,
    merge_playlists,
    normalize_song,
    search_songs,
)


def init_state():
    """Initialize Streamlit session state."""
    if "songs" not in st.session_state:
        st.session_state.songs = default_songs()
    if "profile" not in st.session_state:
        st.session_state.profile = dict(DEFAULT_PROFILE)
    if "history" not in st.session_state:
        st.session_state.history = []





def profile_sidebar():
    """Render and update the user profile."""
    st.sidebar.header("Mood profile")

    profile = st.session_state.profile

    profile["name"] = st.sidebar.text_input(
        "Profile name",
        value=str(profile.get("name", "")),
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        profile["hype_min_energy"] = st.sidebar.slider(
            "Hype min energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("hype_min_energy", 7)),
        )
    with col2:
        profile["chill_max_energy"] = st.sidebar.slider(
            "Chill max energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("chill_max_energy", 3)),
        )

    profile["favorite_genre"] = st.sidebar.selectbox(
        "Favorite genre",
        options=["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"],
        index=0,
    )

    profile["include_mixed"] = st.sidebar.checkbox(
        "Include Mixed playlist in views",
        value=bool(profile.get("include_mixed", True)),
    )

    st.sidebar.write("Current profile:", profile["name"])


def add_song_sidebar():
    """Render the Add Song controls in the sidebar."""
    st.sidebar.header("Add a song")

    title = st.sidebar.text_input("Title")
    artist = st.sidebar.text_input("Artist")
    genre = st.sidebar.selectbox(
        "Genre",
        options=["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"],
    )
    energy = st.sidebar.slider("Energy", min_value=1, max_value=10, value=5)
    tags_text = st.sidebar.text_input("Tags (comma separated)")

    if st.sidebar.button("Add to playlist"):
        raw_tags = [t.strip() for t in tags_text.split(",")]
        tags = [t for t in raw_tags if t]

        song: Song = {
            "title": title,
            "artist": artist,
            "genre": genre,
            "energy": energy,
            "tags": tags,
        }
        if title and artist:
            normalized = normalize_song(song)
            all_songs = st.session_state.songs[:]
            all_songs.append(normalized)
            st.session_state.songs = all_songs


def playlist_tabs(playlists):
    """Render playlists in tabs."""
    include_mixed = st.session_state.profile.get("include_mixed", True)

    tab_labels = ["Hype", "Chill"]
    if include_mixed:
        tab_labels.append("Mixed")

    tabs = st.tabs(tab_labels)

    for label, tab in zip(tab_labels, tabs):
        with tab:
            render_playlist(label, playlists.get(label, []))


def render_playlist(label, songs):
    st.subheader(f"{label} playlist")
    if not songs:
        st.write("No songs in this playlist.")
        return

    query = st.text_input(f"Search {label} playlist by artist", key=f"search_{label}")
    filtered = search_songs(songs, query, field="artist")

    if not filtered:
        st.write("No matching songs.")
        return

    for song in filtered:
        mood = song.get("mood", "?")
        tags = ", ".join(song.get("tags", []))
        st.write(
            f"- **{song['title']}** by {song['artist']} "
            f"(genre {song['genre']}, energy {song['energy']}, mood {mood}) "
            f"[{tags}]"
        )


def lucky_section(playlists):
    """Render the lucky pick controls and result."""
    st.header("Lucky pick")

    mode = st.selectbox(
        "Pick from",
        options=["any", "hype", "chill"],
        index=0,
    )

    if st.button("Feeling lucky"):
        pick = lucky_pick(playlists, mode=mode)
        if pick is None:
            st.warning("No songs available for this mode.")
            return

        st.success(
            f"Lucky song: {pick['title']} by {pick['artist']} "
            f"(mood {pick.get('mood', '?')})"
        )

        history = st.session_state.history
        history.append(pick)
        st.session_state.history = history


def stats_section(playlists):
    """Render statistics based on the playlists."""
    st.header("Playlist stats")

    stats = compute_playlist_stats(playlists)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total songs", stats["total_songs"])
    col2.metric("Hype songs", stats["hype_count"])
    col3.metric("Chill songs", stats["chill_count"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Mixed songs", stats["mixed_count"])
    col5.metric("Hype ratio", f"{stats['hype_ratio']:.2f}")
    col6.metric("Average energy", f"{stats['avg_energy']:.2f}")

    top_artist = stats["top_artist"]
    if top_artist:
        st.write(
            f"Most common artist: {top_artist} "
            f"({stats['top_artist_count']} songs)"
        )
    else:
        st.write("No top artist yet.")


def history_section():
    """Render the pick history overview."""
    st.header("History")

    history = st.session_state.history
    if not history:
        st.write("No history yet.")
        return

    summary = history_summary(history)
    st.write("Recent picks by mood:", summary)

    show_details = st.checkbox("Show full history")
    if show_details:
        for song in history:
            st.write(
                f"{song.get('mood', '?')}: {song['title']} by {song['artist']}"
            )


def clear_controls():
    """Render a small section for clearing data."""
    st.sidebar.header("Manage data")
    if st.sidebar.button("Reset songs to default"):
        st.session_state.songs = default_songs()
    if st.sidebar.button("Clear history"):
        st.session_state.history = []


def main():
    st.set_page_config(page_title="Playlist Chaos", layout="wide")
    st.title("Playlist Chaos")

    st.write(
        "An AI assistant tried to build a smart playlist engine. "
        "The code runs, but the behavior is a bit unpredictable."
    )

    init_state()
    profile_sidebar()
    add_song_sidebar()
    clear_controls()

    profile = st.session_state.profile
    songs = st.session_state.songs

    base_playlists = build_playlists(songs, profile)
    merged_playlists = merge_playlists(base_playlists, {})

    playlist_tabs(merged_playlists)
    st.divider()
    lucky_section(merged_playlists)
    st.divider()
    stats_section(merged_playlists)
    st.divider()
    history_section()


import streamlit as st
from agent_logic import initialize_dj_agent

# ... [Keep your other imports and old functions here if you want them] ...

def init_agent_state():
    """Initialize the AI chat session and message history."""
    if "agent_chat" not in st.session_state:
        # NEW: Unpack both the client and the chat session
        client, chat_session = initialize_dj_agent()
        
        # Keep the client alive in memory so the connection doesn't close
        st.session_state.gemini_client = client 
        st.session_state.agent_chat = chat_session
    
    if "chat_history" not in st.session_state:
        # Store UI messages for Streamlit to render
        st.session_state.chat_history = [
            {"role": "assistant", "content": "What kind of vibe are we looking for today?"}
        ]


def render_classic_view():
    """Renders the original UI with tabs, stats, and lucky picks."""
    st.write("An AI assistant tried to build a smart playlist engine. The code runs, but the behavior is a bit unpredictable.")
    
    profile = st.session_state.profile
    songs = st.session_state.songs

    # Original playlist logic
    base_playlists = build_playlists(songs, profile)
    merged_playlists = merge_playlists(base_playlists, {})

    # Render original components
    playlist_tabs(merged_playlists)
    st.divider()
    lucky_section(merged_playlists)
    st.divider()
    stats_section(merged_playlists)
    st.divider()
    history_section()


def render_agent_view():
    """Renders the chat interface for the Agentic DJ."""
    st.write("Tell me what you're doing, and I'll use my tools to build the perfect playlist.")
    
    # Initialize the agent state only when they visit this tab
    init_agent_state()

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input loop
    if prompt := st.chat_input("E.g., I need 3 high-energy rock songs for a workout..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Digging through the crates..."):
                response = st.session_state.agent_chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})


def main():
    st.set_page_config(page_title="Playlist Chaos", layout="wide")
    st.title("🎧 Playlist Chaos")

    # Always initialize the base app state (songs, history, etc.)
    init_state()

    # --- Navigation Router ---
    st.sidebar.title("Navigation")
    current_view = st.sidebar.radio("Go to", ["Classic Recommender", "Agentic DJ"])
    st.sidebar.divider()

    # --- Global Sidebar Tools ---
    # We keep the "Add Song" and "Clear Data" tools visible on both views
    add_song_sidebar()
    clear_controls()
    st.sidebar.divider()

    # --- Render Selected View ---
    if current_view == "Classic Recommender":
        # Only show the mood profile sliders on the classic view
        profile_sidebar() 
        render_classic_view()
    else:
        render_agent_view()


if __name__ == "__main__":
    main()