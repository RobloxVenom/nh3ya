#!/usr/bin/env python3
import json
import sys
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def fetch_json(url):
    req = Request(url, headers={'User-Agent': 'nh3ya/1.0'})
    with urlopen(req, timeout=10) as resp:
        return json.load(resp)

def get_user_id(username):
    url = f'https://users.roblox.com/v1/usernames/users?username={username}'
    data = fetch_json(url)
    arr = data.get('data', [])
    return arr[0]['id'] if arr else None

def get_user_info(user_id):
    return fetch_json(f'https://users.roblox.com/v1/users/{user_id}')

def get_last_played(user_id):
    url = f'https://games.roblox.com/v1/users/{user_id}/games?sortOrder=Desc&limit=1'
    data = fetch_json(url)
    games = data.get('data') or []
    return games[0]['name'] if games else 'غير متوفر'

def format_date(iso):
    return iso.replace('T', ' ').split('.')[0] if iso else 'غير متوفر'

def main():
    parser = argparse.ArgumentParser(prog='nh3ya', description='nh3ya Roblox Viewer')
    parser.add_argument('-u', '--user',     help='اسم المستخدم', required=True)
    parser.add_argument('-s', '--silent',   help='عرض مدخلات فقط', action='store_true')
    parser.add_argument('-o', '--output',   help='حفظ النتائج (json أو csv)', choices=['json','csv'])
    args = parser.parse_args()

    username = args.user.strip()
    try:
        user_id = get_user_id(username)
        if not user_id:
            print("❌ لم يتم العثور على الحساب.")
            sys.exit(1)

        info = get_user_info(user_id)
        created     = format_date(info.get('created'))
        last_online = format_date(info.get('lastOnline'))
        last_game   = get_last_played(user_id)

        result = {
            "user_id":    user_id,
            "created":    created,
            "last_online": last_online,
            "last_game":  last_game
        }

        if args.silent:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("═" * 30)
            print("   nh3ya Roblox Viewer   ")
            print("═" * 30)
            print(f"معرف المستخدم : {user_id}")
            print(f"تاريخ الإنشاء  : {created}")
            print(f"آخر دخول      : {last_online}")
            print(f"آخر لعبة لعبت : {last_game}")
            print("═" * 30)

        if args.output == 'json':
            with open(f"{username}.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ الحفظ: {username}.json")
        elif args.output == 'csv':
            import csv
            fname = f"{username}.csv"
            with open(fname, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(result.keys())
                writer.writerow(result.values())
            print(f"✅ الحفظ: {fname}")

    except HTTPError as e:
        print(f"🚫 خطأ HTTP: {e.code}")
    except URLError as e:
        print("🚫 خطأ في الشبكة أو DNS — تأكد من اتصالك بالإنترنت وصلاحية اسم المضيف.")
    except Exception as e:
        print(f"⚠️ خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
