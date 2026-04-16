from typing import Dict, List, Optional, Tuple

Song = Dict[str, object]
PlaylistMap = Dict[str, List[Song]]

DEFAULT_PROFILE = {
    "name": "Default",
    "hype_min_energy": 7,
    "chill_max_energy": 3,
    "favorite_genre": "rock",
    "include_mixed": True,
}

def default_songs():
    """Return a default list of songs."""
    return [
        {
            "title": "Thunderstruck",
            "artist": "AC/DC",
            "genre": "rock",
            "energy": 9,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Lo-fi Rain",
            "artist": "DJ Calm",
            "genre": "lofi",
            "energy": 2,
            "tags": ["study"],
        },
        {
            "title": "Night Drive",
            "artist": "Neon Echo",
            "genre": "electronic",
            "energy": 6,
            "tags": ["synth"],
        },
        {
            "title": "Soft Piano",
            "artist": "Sleep Sound",
            "genre": "ambient",
            "energy": 1,
            "tags": ["sleep"],
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "genre": "rock",
            "energy": 8,
            "tags": ["classic", "opera"],
        },
        {
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "genre": "pop",
            "energy": 8,
            "tags": ["synth", "dance"],
        },
        {
            "title": "Take Five",
            "artist": "Dave Brubeck",
            "genre": "jazz",
            "energy": 4,
            "tags": ["classic", "instrumental"],
        },
        {
            "title": "Strobe",
            "artist": "Deadmau5",
            "genre": "electronic",
            "energy": 7,
            "tags": ["progressive", "long"],
        },
        {
            "title": "Weightless",
            "artist": "Marconi Union",
            "genre": "ambient",
            "energy": 1,
            "tags": ["relax", "sleep"],
        },
        {
            "title": "Smells Like Teen Spirit",
            "artist": "Nirvana",
            "genre": "rock",
            "energy": 9,
            "tags": ["grunge", "90s"],
        },
        {
            "title": "Levitating",
            "artist": "Dua Lipa",
            "genre": "pop",
            "energy": 8,
            "tags": ["dance", "party"],
        },
        {
            "title": "So What",
            "artist": "Miles Davis",
            "genre": "jazz",
            "energy": 3,
            "tags": ["trumpet", "cool"],
        },
        {
            "title": "Midnight City",
            "artist": "M83",
            "genre": "electronic",
            "energy": 7,
            "tags": ["indie", "dream"],
        },
        {
            "title": "Gymnopedie No.1",
            "artist": "Erik Satie",
            "genre": "ambient",
            "energy": 1,
            "tags": ["piano", "calm"],
        },
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "genre": "rock",
            "energy": 8,
            "tags": ["guitar", "80s"],
        },
        {
            "title": "Bad Guy",
            "artist": "Billie Eilish",
            "genre": "pop",
            "energy": 6,
            "tags": ["bass", "dark"],
        },
        {
            "title": "Fly Me to the Moon",
            "artist": "Frank Sinatra",
            "genre": "jazz",
            "energy": 5,
            "tags": ["vocal", "swing"],
        },
        {
            "title": "Sandstorm",
            "artist": "Darude",
            "genre": "electronic",
            "energy": 10,
            "tags": ["trance", "meme"],
        },
        {
            "title": "Clair de Lune",
            "artist": "Claude Debussy",
            "genre": "ambient",
            "energy": 2,
            "tags": ["piano", "classical"],
        },
        {
            "title": "Hotel California",
            "artist": "Eagles",
            "genre": "rock",
            "energy": 6,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Uptown Funk",
            "artist": "Mark Ronson ft. Bruno Mars",
            "genre": "pop",
            "energy": 9,
            "tags": ["funk", "dance"],
        },
        {
            "title": "Feeling Good",
            "artist": "Nina Simone",
            "genre": "jazz",
            "energy": 6,
            "tags": ["soul", "vocal"],
        },
    ]

def normalize_title(title: str) -> str:
    """Normalize a song title for comparisons."""
    if not isinstance(title, str):
        return ""
    return title.strip()


def normalize_artist(artist: str) -> str:
    """Normalize an artist name for comparisons."""
    if not artist:
        return ""
    return artist.strip().lower()


def normalize_genre(genre: str) -> str:
    """Normalize a genre name for comparisons."""
    return genre.lower().strip()


def normalize_song(raw: Song) -> Song:
    """Return a normalized song dict with expected keys."""
    title = normalize_title(str(raw.get("title", "")))
    artist = normalize_artist(str(raw.get("artist", "")))
    genre = normalize_genre(str(raw.get("genre", "")))
    energy = raw.get("energy", 0)

    if isinstance(energy, str):
        try:
            energy = int(energy)
        except ValueError:
            energy = 0

    tags = raw.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    return {
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tags": tags,
    }


# FIXED: classify_song should check chill conditions first, then hype, then mixed
def classify_song(song: Song, profile: Dict[str, object]) -> str:
    """Return a mood label given a song and user profile."""
    energy = song.get("energy", 0)
    genre = song.get("genre", "")
    title = song.get("title", "")

    hype_min_energy = profile.get("hype_min_energy", 7)
    chill_max_energy = profile.get("chill_max_energy", 3)
    favorite_genre = profile.get("favorite_genre", "")

    hype_keywords = ["rock", "punk", "party"]
    chill_keywords = ["lofi", "ambient", "sleep"]

    is_hype_keyword = any(k in genre for k in hype_keywords)
    is_chill_keyword = any(k in genre for k in chill_keywords)

    # Check Chill first
    if energy <= chill_max_energy or is_chill_keyword:
        return "Chill"
    if genre == favorite_genre or energy >= hype_min_energy or is_hype_keyword:
        return "Hype"
    return "Mixed"


def build_playlists(songs: List[Song], profile: Dict[str, object]) -> PlaylistMap:
    """Group songs into playlists based on mood and profile."""
    playlists: PlaylistMap = {
        "Hype": [],
        "Chill": [],
        "Mixed": [],
    }

    for song in songs:
        normalized = normalize_song(song)
        mood = classify_song(normalized, profile)
        normalized["mood"] = mood
        playlists[mood].append(normalized)

    return playlists


def merge_playlists(a: PlaylistMap, b: PlaylistMap) -> PlaylistMap:
    """Merge two playlist maps into a new map."""
    merged: PlaylistMap = {}
    for key in set(list(a.keys()) + list(b.keys())):
        merged[key] = a.get(key, [])
        merged[key].extend(b.get(key, []))
    return merged


def compute_playlist_stats(playlists: PlaylistMap) -> Dict[str, object]:
    """Compute statistics across all playlists."""
    all_songs: List[Song] = []
    for songs in playlists.values():
        all_songs.extend(songs)

    hype = playlists.get("Hype", [])
    chill = playlists.get("Chill", [])
    mixed = playlists.get("Mixed", [])

    # FIXED: total should include all songs, not just hype
    total = len(all_songs)
    hype_ratio = len(hype) / total if total > 0 else 0.0

    avg_energy = 0.0
    if all_songs:
        # FIXED: only summed up hype --> changed to all_songs
        total_energy = sum(song.get("energy", 0) for song in all_songs)
        avg_energy = total_energy / len(all_songs)

    top_artist, top_count = most_common_artist(all_songs)

    return {
        "total_songs": len(all_songs),
        "hype_count": len(hype),
        "chill_count": len(chill),
        "mixed_count": len(mixed),
        "hype_ratio": hype_ratio,
        "avg_energy": avg_energy,
        "top_artist": top_artist,
        "top_artist_count": top_count,
    }


def most_common_artist(songs: List[Song]) -> Tuple[str, int]:
    """Return the most common artist and count."""
    counts: Dict[str, int] = {}
    for song in songs:
        artist = str(song.get("artist", ""))
        if not artist:
            continue
        counts[artist] = counts.get(artist, 0) + 1

    if not counts:
        return "", 0

    items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return items[0]


def search_songs(
    songs: List[Song],
    query: str,
    field: str = "artist",
) -> List[Song]:
    """Return songs matching the query on a given field."""
    if not query:
        return songs

    q = query.lower().strip()
    filtered: List[Song] = []

    for song in songs:
        value = str(song.get(field, "")).lower()
        # FIXED: Check if the query is a substring of the value
        if value and q in value:
            filtered.append(song)

    return filtered


def lucky_pick(
    playlists: PlaylistMap,
    mode: str = "any",
) -> Optional[Song]:
    """Pick a song from the playlists according to mode."""
    if mode == "hype":
        songs = playlists.get("Hype", [])
    elif mode == "chill":
        songs = playlists.get("Chill", [])
    else:
        songs = playlists.get("Hype", []) + playlists.get("Chill", [])

    return random_choice_or_none(songs)


def random_choice_or_none(songs: List[Song]) -> Optional[Song]:
    """Return a random song or None."""
    import random
    # FIXED: should return None if songs is empty, not raise an error
    if not songs:
        return None
    return random.choice(songs)


def history_summary(history: List[Song]) -> Dict[str, int]:
    """Return a summary of moods seen in the history."""
    counts = {"Hype": 0, "Chill": 0, "Mixed": 0}
    for song in history:
        mood = song.get("mood", "Mixed")
        if mood not in counts:
            counts["Mixed"] += 1
        else:
            counts[mood] += 1
    return counts
