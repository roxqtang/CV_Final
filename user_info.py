import json
import os
import time
from datetime import datetime, timedelta

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

def get_user_conservative_goals():
    profile = load_user_profile()
    return profile.get("conservative_goals", {})

def get_user_ambitious_goals():
    profile = load_user_profile()
    return profile.get("ambitious_goals", {})

def get_user_hobbies():
    profile = load_user_profile()
    return profile.get("hobbies", [])

def get_user_preferences():
    profile = load_user_profile()
    return profile.get("preferences", {})
  
def get_user_schedule():
    profile = load_user_profile()
    return profile.get("top_priorities_today", {})

def get_user_key_events():
    profile = load_user_profile()
    return profile.get("key_events", {})

def get_most_expected_event():
    profile = load_user_profile()
    return profile.get("Most expected event", "unknown")

def get_attitude_for_today():
    profile = load_user_profile()
    return profile.get("Actitutde_for_today", "unknown")

def get_user_history_today():
    profile = load_user_profile()
    return profile.get("user_history_today", "unknown")

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
            begin_time = event_details.get("projected_begin_time")
            # Convert HH:MM to HH:MM:SS by appending ":00"
            begin_time = begin_time + ":00" if begin_time else begin_time
            begin_times[event_id] = begin_time

    return begin_times

from datetime import datetime, timedelta
def get_projected_end_times():
   profile = load_user_profile()
   key_events = profile.get("key_events", {})
   end_times = {}
  
   for event_id, event_details in key_events.items():
       if event_details.get("event_name") != "":
           try:
               # Get begin time
               begin_time_str = event_details.get("projected_begin_time")
               # Get duration string (in minutes)
               duration_str = event_details.get("projected_dur_mintues", "0:00")
               
               if begin_time_str and duration_str:
                   # Convert begin time to datetime
                   begin_time = datetime.strptime(begin_time_str, "%H:%M")
                   print(begin_time)
                   # Parse duration string to get minutes
                   duration_minutes = float(duration_str.split(":")[0])
                   duration_seconds = float(duration_str.split(":")[1])
                   # Calculate end time
                   end_time = begin_time + timedelta(minutes=duration_minutes, seconds=duration_seconds)
                   # Store formatted end time
                   end_times[event_id] = end_time.strftime("%H:%M:%S")
           except (ValueError, IndexError) as e:
               print(f"Error processing event {event_id}: {e}")
               end_times[event_id] = "unknown"
               
   return end_times           

def get_next_events():
    profile = load_user_profile()
    key_events = profile.get("key_events", {})
    next_events = {}
    
    current_time_str, current_datetime = get_current_time()
    # Get current time
    for event_id, event_details in key_events.items():
        if event_details.get("event_name") != "":
            try:
                # Get event timing details
                start_time_str = event_details.get("projected_begin_time")
                duration_str = event_details.get("projected_dur_mintues", "0:00")
                #print(f"start_time_str: {start_time_str}")
                #print(f"duration_str: {duration_str}")
                
                # Validate duration format
                #print(f'current_time_str: {current_time_str}')
                #print(f'start_time_str: {current_datetime}')
                #print(f'duration_str {duration_str}')
                if not has_enough_time(current_time_str, start_time_str, duration_str):
                    continue
                
                if start_time_str and duration_str:
                    # Convert start time to datetime with today's date
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    start_datetime = datetime.combine(datetime.now().date(), start_time)
                    
                    # Parse duration
                    try:
                        minutes, seconds = map(float, duration_str.split(":"))
                    except ValueError:
                        continue
                    
                    # Calculate end time with today's date
                    end_datetime = start_datetime + timedelta(minutes=minutes, seconds=seconds)
                    #print(f"end_datetime: {end_datetime}")
                    
                    # Determine event status and include if relevant
                    if end_datetime >= current_datetime:  # Event hasn't ended yet
                        status = "Ongoing" if current_datetime >= start_datetime else "Upcoming"
                        
                        remaining_time = (
                            str(end_datetime - current_datetime) 
                            if current_datetime >= start_datetime 
                            else "Not started"
                        )
                        
                        next_events[event_id] = {
                            "event_name": event_details.get("event_name"),
                            "start_time": start_time_str,
                            "duration": duration_str,
                            "remaining_time": remaining_time,
                            "status": status,
                            "location": event_details.get("projected_location", ""),
                            "activity": event_details.get("projected_activity", ""),
                            "interruptions": event_details.get("projected_interruptions", ""),
                            "solution": event_details.get("projected_solution", "")
                        }
                
            except (ValueError, IndexError) as e:
                print(f"Error processing event {event_id}: {e}")
                continue
        
    return next_events

def get_current_time():
    """
    Return: 
    current_time_str: date in HH:MM format
    current_datetime: time including date
    """
    current_time = datetime.now()
    # Format to include only hours and minutes
    current_time_str = current_time.strftime("%H:%M")
    #print(f"current_time_str: {current_time_str}")
    # Create a datetime object for today with the current time
    current_datetime = datetime.combine(
        current_time.date(),
        datetime.strptime(current_time_str, "%H:%M").time()
    )
    return current_time_str, current_datetime
# Helper function to check if there's enough time for an event

def has_enough_time(current_time, event_start, event_duration):
   """
   Input time format: 
   current_time: HH:MM
   event_start: HH:MM
   event_duration: MM:SS
   """
   try:
       current = datetime.strptime(current_time, "%H:%M")
       start = datetime.strptime(event_start, "%H:%M")
       duration_minutes = float(event_duration.split(":")[0])
       duration_seconds = float(event_duration.split(":")[1])
       #print(f'the duration is {duration_minutes} minutes and {duration_seconds} seconds')
       # Calculate end time of the event
       end = start + timedelta(minutes=duration_minutes, seconds=duration_seconds)
      # print(f'the end time is {end}')
       # Check if there's enough time
       return current <= start and (end - current).total_seconds() > 0
   except ValueError as e:
       print(f"Error checking time: {e}")
       return False
if __name__ == "__main__":
    has_enough_time("12:00", "12:00", "0:00")