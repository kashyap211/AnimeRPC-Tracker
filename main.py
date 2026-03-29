from pypresence import Presence
import time
import pygetwindow as gw
import os
from dotenv import load_dotenv
import requests
import re
import atexit

load_dotenv()

client_id = os.getenv("DISCORD_CLIENT_ID")

if not client_id:
    raise ValueError("DISCORD_CLIENT_ID not set")




start_time = time.time()

last_anime = None
last_seen_time = 0
timeout = 10

ICONS = {
    "one piece":"op",
    "bleach": "bleach",
    "jujutsu kaisen": "jjk",
    "yu yu hakusho":"yu",
    "my hero academia":"mha",
    "high school dxd":"logo",
    "kenichi":"ken",
    "that time i got reincarnated as a slime":"slime",
    "shangri":"shangri",
    "soul eater":"soulea"
}

def cleanup():
    global RPC
    try:
        if RPC:
            RPC.clear()
            RPC.close()
            print("Discord presence cleared")
    except:
        pass

def get_aniwatch():
    try:
        title = find_aniwatch_window()
        if not title:
            return None, None

        title_lower = title.lower()

        if "aniwatch" in title_lower and "watch" in title_lower:

            parts = title.split("Watch")

            if len(parts) > 1:
                anime_part = parts[1]

                # 🔥 Extract episode if present
                match = re.search(r"(.*?)\s+episode\s+(\d+)", anime_part, re.IGNORECASE)

                if match:
                    anime_name = match.group(1).strip()
                    episode = match.group(2).strip()
                    return anime_name, episode

                # fallback (no episode found)
                anime_name = anime_part.split("English")[0].strip()
                return anime_name, None

    except Exception as e:
        print("Error:", e)

    return None, None

last_img = None  # 🔥 track last image
last_ep_id = None
episode_counter = 1

def get_episode_id(title):
    match = re.search(r'ep=(\d+)', title)
    if match:
        return int(match.group(1))
    return None

def find_aniwatch_window():
    windows = gw.getAllTitles()
    
    for title in windows:
        t = title.lower()
        if "aniwatch" in t and "watch" in t:
            return title
    
    return None

def connect_rpc():
    global RPC
    try:
        RPC = Presence(client_id)
        RPC.connect()
        print("Connected to Discord")
    except Exception as e:
        print("Reconnect failed:", e)

RPC = None
connect_rpc()
atexit.register(cleanup)

try:
    while True:
        anime, episode = get_aniwatch()
        current_time = time.time()

        title = find_aniwatch_window()

        ep_id = get_episode_id(title if title else "")

    

        if ep_id:
            if last_ep_id is None:
                episode_counter = 1
            elif ep_id != last_ep_id:
                episode_counter += 1

            last_ep_id = ep_id

        if anime != last_anime:
            episode_counter = 1
            last_ep_id = None
        if anime != last_anime:
            start_time = time.time()
        if anime:
            anime_clean = anime.strip().lower()

            # 🔥 ICON LOGIC
            img = "ani"
            for key in ICONS:
                if key in anime_clean:
                    img = ICONS[key]
                    break

            # 🔥 UPDATE if anime OR icon changed
            if anime != last_anime or img != last_img:
                if anime!=last_anime:
                    episode_counter=1
                    last_ep_id=None

                last_anime = anime
                last_img = img
                last_seen_time = current_time
                

                try:
                    RPC.update(
                        state = f"Episode {episode}" if episode else f"Episode {episode_counter}",
                        details=anime,
                        large_image=img,
                        large_text=anime,
                        small_image="play",
                        small_text="Watching",
                        start=start_time
                    )
                except:
                    print("Disconnected → reconnecting...")
                    connect_rpc()

                print(f"Updated: {anime} with icon: {img}")

        else:
            if last_anime and (current_time - last_seen_time < timeout):
                pass
            else:
                try:
                    RPC.clear()
                except:
                    pass
                last_anime = None
                last_img = None
                last_ep_id=None
                episode_counter=1

    # 🔍 Debug (optional)
except KeyboardInterrupt:
    print("Exiting...")
    cleanup()
   
    time.sleep(5)