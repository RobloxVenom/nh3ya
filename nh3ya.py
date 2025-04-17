#!/usr/bin/env python3
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def fetch_json(url):
    req = Request(url, headers={'User-Agent': 'nh3ya/1.0'})
    with urlopen(req, timeout=10) as resp:
        return json.load(resp)

def get_user_id(username):
    data = fetch_json(f'https://api.roblox.com/users/get-by-username?username={username}')
    return data.get('Id')

def get_user_info(user_id):
    return fetch_json(f'https://api.roblox.com/users/{user_id}')

def get_last_played(user_id):
    url = f'https://games.roblox.com/v1/users/{user_id}/games?sortOrder=Desc&limit=1'
    data = fetch_json(url)
    games = data.get('data') or []
    if games:
        return games[0].get('name')
    return 'غير متوفر'

def format_date(iso_str):
    try:
        return iso_str.replace('T', ' ').split('.')[0]
    except:
        return iso_str

def main():
    print("\033[1;36m========================\033[0m")
    print("\033[1;33m   nh3ya Roblox Viewer   \033[0m")
    print("\033[1;36m========================\033[0m\n")
    username = input("أدخل اسم المستخدم: ").strip()
    if not username:
        print("يرجى إدخال اسم مستخدم صالح.")
        sys.exit(1)
    try:
        user_id = get_user_id(username)
        if not user_id:
            print("لم يتم العثور على الحساب.")
            sys.exit(1)
        info = get_user_info(user_id)
        created = format_date(info.get('Created'))
        last_online = format_date(info.get('LastOnline'))
        last_game = get_last_played(user_id)
        print(f"\n\033[1;32mنتائج nh3ya:\033[0m")
        print(f"معرف المستخدم : {user_id}")
        print(f"تاريخ الإنشاء  : {created}")
        print(f"آخر دخول      : {last_online}")
        print(f"آخر خريطة لعب : {last_game}\n")
    except HTTPError as e:
        print(f"خطأ في الاتصال بالـ API: {e.code}")
    except URLError as e:
        print(f"خطأ في الشبكة: {e.reason}")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
