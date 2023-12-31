from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import requests

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://nixx-steam-lookup.netlify.app",
    # Add any other allowed origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session = requests.Session()
api_key = config('API_KEY', default='')


def get_steam3_id(account_id):
    return f"[U:1:{account_id}]"


def parse_steam2id(steam2id):
    parts = steam2id.split(":")
    return int(parts[1]), int(parts[2]) if len(parts) == 3 and parts[0] == "STEAM_0" else (None, None)


def get_steam64_id(steam2id):
    _, steam_x, steam_y = steam2id.split(':')
    return int(steam_y) * 2 + int(steam_x) + 76561197960265728


def hex_id_to_steam64(hex_id):
    hex_id_cleaned = hex_id.replace('steam:', '').upper()
    return int(hex_id_cleaned, 16)


def hex_id(steam64_id):
    return "steam:" + hex(steam64_id)[2:].upper().lower()


def get_steam2_id(steam64_id):
    Y = (steam64_id - 76561197960265728) % 2
    Z = (steam64_id - 76561197960265728 - Y) // 2
    return f"STEAM_0:{Y}:{Z}"


def check_profile_privacy(api_key, steam64_id):
    url = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam64_id}'
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json().get('response', {}).get('players', [{}])[0].get('communityvisibilitystate', 0)
    except requests.RequestException as e:
        print(f"Error in API request: {e}")
        return 0


def input_to_values(input_str):
    if input_str.startswith("[U:"):
        account_id_from_steam3 = int(input_str.split(':')[2][:-1])
        Y, Z = (0, account_id_from_steam3 // 2) if account_id_from_steam3 % 2 == 0 else (1, (account_id_from_steam3 - 1) // 2)
        steam_2id_from_steam3 = f"STEAM_0:{Y}:{Z}"
        steam64_id_from_steam3 = get_steam64_id(steam_2id_from_steam3)
        FiveM_Hex_id_from_steam3 = hex_id(steam64_id_from_steam3)
        privacy_status_from_steam3 = check_profile_privacy(api_key, steam64_id_from_steam3)
        profile_output_from_steam3 = 'STEAM_1:' if privacy_status_from_steam3 == 3 else 'STEAM_0:'
        steam2_id_from_steam3 = get_steam2_id(steam64_id_from_steam3)
        modified_output_from_steam3 = f"{profile_output_from_steam3}{steam2_id_from_steam3.replace('STEAM_0:', '')}"
        return FiveM_Hex_id_from_steam3, steam64_id_from_steam3, modified_output_from_steam3, input_str, account_id_from_steam3
    elif input_str.startswith("STEAM_"):
        _, Y, Z = input_str.split(':')
        Y, Z = int(Y), int(Z)
        account_id_from_steam2 = Y + Z * 2
        steam_3id_from_steam2 = get_steam3_id(account_id_from_steam2)
        steam64_id_from_steam2 = get_steam64_id(input_str)
        FiveM_Hex_id_from_steam2 = hex_id(steam64_id_from_steam2)
        privacy_status_from_steam2 = check_profile_privacy(api_key, steam64_id_from_steam2)
        profile_output_from_steam2 = 'STEAM_1:' if privacy_status_from_steam2 == 3 else 'STEAM_0:'
        steam2_id_from_steam2 = get_steam2_id(steam64_id_from_steam2)
        modified_output_from_steam2 = f"{profile_output_from_steam2}{steam2_id_from_steam2.replace('STEAM_0:', '')}"
        account_id = int(Y) + int(Z) * 2
        return FiveM_Hex_id_from_steam2, steam64_id_from_steam2, modified_output_from_steam2, steam_3id_from_steam2, account_id_from_steam2
    elif input_str.startswith("steam:"):
        steam64_id_from_hex = hex_id_to_steam64(input_str)
        Y_from_hex = (steam64_id_from_hex - 76561197960265728) % 2
        Z_from_hex = (steam64_id_from_hex - 76561197960265728 - Y_from_hex) // 2
        account_id_from_hex = Y_from_hex + Z_from_hex * 2
        steam_3id_from_hex = get_steam3_id(account_id_from_hex)
        steam_2id_from_hex = f"STEAM_0:{Y_from_hex}:{Z_from_hex}"
        FiveM_Hex_id_from_hex = hex_id(steam64_id_from_hex)
        privacy_status_from_hex = check_profile_privacy(api_key, steam64_id_from_hex)
        profile_output_from_hex = 'STEAM_1:' if privacy_status_from_hex == 3 else 'STEAM_0:'
        steam2_id_from_hex = get_steam2_id(steam64_id_from_hex)
        modified_output_from_hex = f"{profile_output_from_hex}{steam2_id_from_hex.replace('STEAM_0:', '')}"
        return FiveM_Hex_id_from_hex, steam64_id_from_hex, modified_output_from_hex, steam_3id_from_hex, account_id_from_hex
    else:
        steam64_id_from_input = int(input_str)
        Y_from_input = (steam64_id_from_input - 76561197960265728) % 2
        Z_from_input = (steam64_id_from_input - 76561197960265728 - Y_from_input) // 2
        account_id_from_input = Y_from_input + Z_from_input * 2
        steam_3id_from_input = get_steam3_id(account_id_from_input)
        steam2_id_from_input = f"STEAM_0:{Y_from_input}:{Z_from_input}"
        FiveM_Hex_id_from_input = hex_id(steam64_id_from_input)
        privacy_status_from_input = check_profile_privacy(api_key, steam64_id_from_input)
        profile_output_from_input = 'STEAM_1:' if privacy_status_from_input == 3 else 'STEAM_0:'
        modified_output_from_input = f"{profile_output_from_input}{steam2_id_from_input.replace('STEAM_0:', '')}"
        return FiveM_Hex_id_from_input, steam64_id_from_input, modified_output_from_input, steam_3id_from_input, account_id_from_input


def get_steam_user_details(steam64_id):
    url = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam64_id}'
    response = session.get(url)
    response.raise_for_status()
    return response.json().get('response', {}).get('players', [{}])[0]


@app.post('/api/getSteamUser')
async def get_steam_user(data: dict = Body(...)):
    user_input = data.get('steamId')
    FiveM_Hex_id, steam64_id, steam2_id, steam_3id, account_id = input_to_values(user_input)
    result = {
        "Account_ID": account_id,
        "FiveM_Hex_id": FiveM_Hex_id,
        "Steam64_ID": steam64_id,
        "Steam2_ID": steam2_id,
        "Steam3_ID": steam_3id,
        "FiveM_Hex_id": FiveM_Hex_id
    }
    user_details = get_steam_user_details(steam64_id)
    result.update({
        "ProfileImage": user_details.get('avatarfull', ''),
        "User": user_details.get('steamid', ''),
        "Username": user_details.get('personaname', '')
    })
    return result
