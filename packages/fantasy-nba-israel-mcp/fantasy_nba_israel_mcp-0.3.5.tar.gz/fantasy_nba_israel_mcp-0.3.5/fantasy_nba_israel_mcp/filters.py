"""Player filtering utilities."""

from typing import List, Dict


def filter_by_status(players: List[Dict], status: str) -> List[Dict]:
    """Filter players by availability status."""
    if status == "AVAILABLE":
        return [p for p in players if p.get("status") in ["FREEAGENT", "WAIVERS"]]
    elif status == "ALL":
        return players
    else:
        return [p for p in players if p.get("status") == status]


def filter_by_position(players: List[Dict], position: str) -> List[Dict]:
    """Filter players by position."""
    if not position:
        return players
    return [
        p for p in players 
        if position.upper() in [pos.upper() for pos in p.get("positions", [])]
    ]


def filter_by_name(players: List[Dict], name: str) -> List[Dict]:
    """Filter players by name (partial match, case-insensitive)."""
    if not name:
        return players
    search_name = name.lower()
    return [
        p for p in players
        if search_name in p.get("player_name", "").lower()
    ]


def filter_by_min_games(players: List[Dict], min_games: int) -> List[Dict]:
    """Filter out players with too few games (likely injured)."""
    if not min_games:
        return players
    return [
        p for p in players
        if p.get("stats", {}).get("gp", 0) >= min_games
    ]


def strip_stats(players: List[Dict]) -> List[Dict]:
    """Remove stats from players to reduce payload size (names only)."""
    return [
        {
            "player_name": p["player_name"],
            "pro_team": p["pro_team"],
            "positions": p["positions"],
            "team_id": p["team_id"],
            "status": p["status"]
        }
        for p in players
    ]
