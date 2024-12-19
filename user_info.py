import json
import os
import time
USER_PROFILE_PATH = "user_profile.json"

def _update_current_date():
    with open(USER_PROFILE_PATH, "r") as f:
        profile = json.load(f)
    profile["current_date"] = time.strftime("%Y-%m-%d")
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)

def load_user_profile():
    if not os.path.exists(USER_PROFILE_PATH):
        print("No available user profile")
        return None

    with open(USER_PROFILE_PATH, "r") as f:
        profile = json.load(f)
    return profile

def update_user_state(new_state):
    profile = load_user_profile()
    profile["current_state"] = new_state
    save_user_profile(profile)

def update_user_preferences(new_prefs):
    profile = load_user_profile()
    for key, value in new_prefs.items():
        profile["preferences"][key] = value
    save_user_profile(profile)

def save_user_profile(profile):
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)

def get_user_info():
    return load_user_profile()

def get_user_current_state():
    profile = load_user_profile()
    return profile.get("current_state", "unknown")

def get_user_hobbies():
    profile = load_user_profile()
    return profile.get("hobbies", [])

def get_user_preferences():
    profile = load_user_profile()
    return profile.get("preferences", {})
  
def get_user_schedule():
    profile = load_user_profile()
    return profile.get("schedule", {})

def get_user_key_events():
    profile = load_user_profile()
    return profile.get("key_events", {})

def get_most_expected_event():
    profile = load_user_profile()
    return profile.get("Most expected event", "unknown")

def get_attitude_for_today():
    profile = load_user_profile()
    return profile.get("Actitutde_for_today", "unknown")

def get_user_achieved_today():
    profile = load_user_profile()
    return profile.get("user_achieved_today", "unknown")

def get_user_history_past_day():
    profile = load_user_profile()
    return profile.get("user_history_past_day", "unknown")

def get_user_history_past_week():
    profile = load_user_profile()
    return profile.get("user_history_past_week", "unknown")

def get_user_history_past_month():
    profile = load_user_profile()
    return profile.get("user_history_past_month", "unknown")

def get_user_history_past_year():
    profile = load_user_profile()
    return profile.get("user_history_past_year", "unknown")

def get_user_target_date():
    profile = load_user_profile()
    return profile.get("target_date", "unknown")

def get_projected_begin_times():
    profile = load_user_profile()
    key_events = profile.get("key_events", {})
    begin_times = {}

    for event_id, event_details in key_events.items():
        if event_details.get("event_name") != "":
            begin_time = event_details.get("projected_begin_time", "unknown")
            begin_times[event_id] = begin_time

    return begin_times