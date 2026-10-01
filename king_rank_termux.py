#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import getpass
import requests

# =========================
# KING RANK / CPM1
# =========================
API_KEY = os.getenv("CPM_API_KEY", "").strip()
LOGIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
KING_RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating6"

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
    "X-Unity-Version": "2022.3.62f2",
}

RATING_DATA = {
    "RatingData": {
        "time": 1e22,
        "cars": 1e16,
        "car_fix": 1e13,
        "car_collided": 1e12,
        "car_exchange": 1e13,
        "car_trade": 1e13,
        "car_wash": 1e13,
        "slicer_cut": 1e13,
        "drift_max": 1e14,
        "drift": 1e14,
        "cargo": 1e5,
        "delivery": 1e5,
        "race_win": 3e20,
        "taxi": 1e10,
        "levels": 10000990000,
        "gifts": 1e9,
        "fuel": 1e10,
        "offroad": 1e10,
        "speed_banner": 1e9,
        "reactions": 1e17,
        "run": 1e9,
        "real_estate": 1e9,
        "t_distance": 1e10,
        "treasure": 1e10,
        "block_post": 1e10,
        "push_ups": 1e12,
        "burnt_tire": 1e10,
        "passanger_distance": 1e8,
    }
}


def login(email: str, password: str):
    if not API_KEY:
        return False, "CPM_API_KEY nije podešen."

    url = f"{LOGIN_URL}?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
        "clientType": "CLIENT_TYPE_ANDROID",
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=HEADERS,
            timeout=30,
        )

        try:
            data = response.json()
        except ValueError:
            return False, f"Server nije vratio JSON (HTTP {response.status_code})."

        if "idToken" in data:
            return True, {
                "token": data["idToken"],
                "uid": data.get("localId", ""),
                "email": data.get("email", email),
            }

        error = data.get("error", {})
        message = str(error.get("message", "LOGIN_FAILED")).upper()

        known = {
            "EMAIL_NOT_FOUND": "EMAIL_NOT_FOUND",
            "INVALID_PASSWORD": "INVALID_PASSWORD",
            "INVALID_LOGIN_CREDENTIALS": "INVALID_LOGIN_CREDENTIALS",
            "USER_DISABLED": "USER_DISABLED",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "TOO_MANY_ATTEMPTS",
            "INVALID_EMAIL": "INVALID_EMAIL",
        }

        for key, value in known.items():
            if key in message:
                return False, value

        return False, f"LOGIN_FAILED: {message[:150]}"

    except requests.RequestException as e:
        return False, f"NETWORK_ERROR: {e}"


def set_king_rank(token: str):
    payload = {
        "data": json.dumps(RATING_DATA, separators=(",", ":"))
    }

    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(
            KING_RANK_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )

        try:
            data = response.json()
        except ValueError:
            return False, f"HTTP {response.status_code}: {response.text[:300]}"

        if response.ok:
            return True, data

        return False, data

    except requests.RequestException as e:
        return False, f"NETWORK_ERROR: {e}"


def main():
    print("=" * 45)
    print("        CPM KING RANK - TERMUX")
    print("=" * 45)

    global API_KEY

    if not API_KEY:
        API_KEY = getpass.getpass("Firebase API KEY: ").strip()

    if not API_KEY:
        print("\n[!] API KEY nije unet.")
        return

    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    if not email or not password:
        print("\n[!] Email i password su obavezni.")
        return

    print("\n[*] Login...")

    ok, result = login(email, password)

    if not ok:
        print(f"[X] Login failed: {result}")
        return

    print("[+] Login successful.")
    print(f"[+] Firebase UID: {result['uid']}")

    print("\n[*] Slanje King Rank podataka...")

    ok, response = set_king_rank(result["token"])

    if ok:
        print("[+] King Rank request je prihvaćen.")
        print(f"[+] Server response: {json.dumps(response, ensure_ascii=False)}")
    else:
        print("[X] King Rank request failed.")
        print(f"[X] Response: {response}")


if __name__ == "__main__":
    main()
