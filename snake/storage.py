"""Storage module for Snake game: leaderboard and settings persistence."""

import os
import json

STORAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(STORAGE_DIR, 'snake_leaderboard.json')
SETTINGS_FILE = os.path.join(STORAGE_DIR, 'snake_settings.json')


def load_leaderboard():
    """Load the Top-5 high scores from file."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                scores = json.load(f)
                if isinstance(scores, list):
                    return sorted([int(s) for s in scores], reverse=True)[:5]
        except Exception:
            pass
    # Fallback to legacy single-score file if present
    legacy_file = os.path.join(STORAGE_DIR, 'snake_highscore.txt')
    if os.path.exists(legacy_file):
        try:
            with open(legacy_file, 'r', encoding='utf-8') as f:
                val = int(f.read().strip())
                return sorted([val, 20, 15, 10, 5], reverse=True)[:5]
        except Exception:
            pass
    return [24, 18, 12, 8, 5]


def save_leaderboard(scores):
    """Save the Top-5 high scores to file."""
    try:
        top_5 = sorted([int(s) for s in scores], reverse=True)[:5]
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(top_5, f, indent=2)
        # Also update legacy file with top score
        legacy_file = os.path.join(STORAGE_DIR, 'snake_highscore.txt')
        with open(legacy_file, 'w', encoding='utf-8') as f:
            f.write(str(top_5[0] if top_5 else 0))
    except Exception:
        pass


def add_high_score(score):
    """Insert a new score into Top-5 leaderboard if qualified and save."""
    scores = load_leaderboard()
    scores.append(int(score))
    scores = sorted(scores, reverse=True)[:5]
    save_leaderboard(scores)
    return scores


def load_settings():
    """Load user settings (e.g., snake color) from file."""
    default_settings = {"color": "Green"}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    default_settings.update(data)
        except Exception:
            pass
    return default_settings


def save_settings(settings):
    """Save user settings to file."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
