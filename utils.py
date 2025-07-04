
import json
import os
from data import load_data, save_data

def load_teams():
    return load_data("teams.json")

def save_teams(teams):
    save_data("teams.json", teams)

def load_matches():
    return load_data("matches.json")

def save_matches(matches):
    save_data("matches.json", matches)

def load_queue():
    return load_data("queue.json")

def save_queue(queue):
    save_data("queue.json", queue)

def load_tournaments():
    return load_data("tournaments.json")

def save_tournaments(tournaments):
    save_data("tournaments.json", tournaments)

def load_stats():
    return load_data("stats.json")

def save_stats(stats):
    save_data("stats.json", stats)

def load_mvp_votes():
    return load_data("mvp_votes.json")

def save_mvp_votes(votes):
    save_data("mvp_votes.json", votes)

def load_match_history():
    return load_data("match_history.json")

def save_match_history(history):
    save_data("match_history.json", history)

def load_admin_settings():
    defaults = {
        "allow_queue": True,
        "allow_tournaments": True,
        "max_tournament_teams": 32,
        "auto_mmr_updates": True,
        "mvp_voting_enabled": True
    }
    settings = load_data("admin_settings.json")
    return {**defaults, **settings}

def save_admin_settings(settings):
    save_data("admin_settings.json", settings)
