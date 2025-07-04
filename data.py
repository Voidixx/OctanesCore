
import json
import os

def load_data(filename):
    if not os.path.exists(filename):
        # Return appropriate empty structure based on filename
        if filename in ["matches.json", "queue.json", "tournaments.json", "match_history.json", "teams.json"]:
            return []
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        # Return appropriate empty structure based on filename
        if filename in ["matches.json", "queue.json", "tournaments.json", "match_history.json", "teams.json"]:
            return []
        return {}

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
