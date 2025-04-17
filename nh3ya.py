#!/usr/bin/env python3
"""
nh3ya: A professional CLI tool to fetch non-sensitive Roblox account info.
"""

import sys
import json
import argparse
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

API_HEADERS = {"User-Agent": "nh3ya/1.0"}


def fetch_json(url, timeout=10):
    """Fetch JSON data from the given URL."""
    req = Request(url, headers=API_HEADERS)
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def resolve_user_id(username):
    """Resolve a Roblox username to its user ID."""
    url = f"https://users.roblox.com/v1/usernames/users?username={username}"
    data = fetch_json(url)
    items = data.get("data", [])
    if not items:
        raise ValueError(f"User '{username}' not found")
    return items[0]["id"]


def fetch_user_info(user_id):
    """Fetch basic user info by ID."""
    url = f"https://users.roblox.com/v1/users/{user_id}"
    return fetch_json(url)


def fetch_last_game(user_id):
    """Fetch the name of the last game played by the user."""
    url = f"https://games.roblox.com/v1/users/{user_id}/games?sortOrder=Desc&limit=1"
    data = fetch_json(url)
    games = data.get("data", [])
    return games[0].get("name") if games else None


def format_timestamp(timestamp):
    """Format ISO8601 timestamp to a readable form."""
    return timestamp.replace("T", " ").split(".")[0] if timestamp else None


def parse_args():
    parser = argparse.ArgumentParser(
        prog="nh3ya",
        description="Roblox non-sensitive account info viewer"
    )
    parser.add_argument("username", help="Roblox username")
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Output JSON only"
    )
    parser.add_argument(
        "-o", "--output",
        choices=["json", "csv"],
        help="Save output to file"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

    try:
        user_id     = resolve_user_id(args.username)
        info        = fetch_user_info(user_id)
        created     = format_timestamp(info.get("created"))
        last_online = format_timestamp(info.get("lastOnline"))
        last_game   = fetch_last_game(user_id)

        result = {
            "user_id":     user_id,
            "created":     created     or "Unavailable",
            "last_online": last_online or "Unavailable",
            "last_game":   last_game   or "Unavailable"
        }

        if args.silent:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 40)
            print(f"nh3ya Roblox Viewer results for '{args.username}'")
            print("=" * 40)
            for key, value in result.items():
                label = key.replace("_", " ").title()
                print(f"{label:15}: {value}")
            print("=" * 40)

        if args.output:
            filename = f"{args.username}.{args.output}"
            if args.output == "json":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                import csv
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(result.keys())
                    writer.writerow(result.values())
            print(f"Saved output to {filename}")

    except ValueError as ve:
        logging.error(ve)
        sys.exit(1)
    except HTTPError as he:
        logging.error(f"HTTP error {he.code}")
        sys.exit(1)
    except URLError as ue:
        logging.error(f"Network error: {ue.reason}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
