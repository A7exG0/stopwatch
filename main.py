
from datetime import datetime
from pathlib import Path 
import json
import subprocess
from plyer import notification
import sys

def stopwatch_off(data, end_time_str):
    '''Function for saving result of session'''
    
    # Take last day data and last session data 
    day_data = data["days_data"][-1]
    session_data = day_data["sessions_data"][-1]
    
    session_data["end"] = end_time_str
    # convert star_time and end_time into datetime class
    start_time = datetime.strptime(session_data["start"], "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")
    # find difference
    delta = end_time - start_time
    hours, minutes, seconds = convert_from_seconds(delta.seconds)
    session_data["duration"] = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # count day sum of time
    sum_time = datetime.strptime(day_data["sum_time"], "%H:%M:%S")
    sum_time += delta 
    sum_time_str = datetime.strftime(sum_time, "%H:%M:%S")
    day_data["sum_time"] = sum_time_str
    
    # also count total all days time 
    total_time = list(map(int, data["total_time"].split(":")))
    total_time_seconds = delta.seconds + convert_to_seconds(total_time[0], total_time[1], total_time[2])
    hours, minutes, seconds = convert_from_seconds(total_time_seconds)
    data["total_time"] = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # save session changes in data  
    data["days_data"][-1]["sessions_data"][-1] = session_data # last day, last session
    
    # notify(f"⏱ Stopwatch off! Session:{session_data['duration']}\n Day:{day_data['sum_time']}")
    notification.notify(
    title="⏱ Stopwatch",
    message=f"Stopwatch off!\nSession:{session_data['duration']}\n Day:{day_data['sum_time']}",
    timeout=5  # seconds
    )
     
def notify(text):
    '''Script for notifications linux'''
    subprocess.run(["notify-send", text])

def convert_from_seconds(total_seconds):
    '''Convert seconds to hours, minutes, seconds'''
    hours = total_seconds // 3600 
    rest = total_seconds % 3600
    minutes = rest // 60 
    seconds = rest % 60
    return hours, minutes, seconds

def convert_to_seconds(hours, minutes, seconds):
    '''Convert from hours, minutes, seconds to seconds'''
    return hours * 3600 + minutes *60 + seconds

# Get the file path for saving and current date, time 
script_dir = Path(__file__).parent.resolve()
today = datetime.today()
now = datetime.now()
cur_time = now.strftime("%H:%M:%S")
today_date = now.strftime("%d/%m/%Y")
file_name = script_dir / f"sessions.json" 

# Check existing file for the first starting of stopwatch
if not Path.exists(file_name): 
    data = {
    "is_working": "False",
    "total_time": "0:0:0",
    "num_days": "1",
    "days_data": [
        {
        "date": today_date,
        "sum_time": "00:00:00",
        "num_sessions": "0",
        "sessions_data": []
        }
    ]
    }
    with open(file_name, 'w', encoding="utf-8") as f: 
        json.dump(data, f)


# Get data from file 
with open(file_name, 'r', encoding="utf-8") as f: 
    data = json.load(f)
    
    # can check duration only when stopwatch is working 
    if len(sys.argv) > 1 and sys.argv[1] == "duration":
        if data["is_working"] == "True":
            last_session = data["days_data"][-1]["sessions_data"][-1] 
            
            start_time = datetime.strptime(last_session["start"], "%H:%M:%S")
            end_time = datetime.strptime(cur_time, "%H:%M:%S")
            # find difference
            delta = end_time - start_time
            hours, minutes, seconds = convert_from_seconds(delta.seconds)
            
            notification.notify(
            title="⏱ Stopwatch",
            message=f"Duration: {hours:02}:{minutes:02}:{seconds:02}",
            timeout=5  # seconds
            )
        else:
            notification.notify(
            title="⏱ Stopwatch",
            message=f"Stopwathc isn't working",
            timeout=5  # seconds
            )
        sys.exit()
    
    # Take data of the last day 
    day_data = data["days_data"][-1]
    
    # Check, match of the dates
    # if not, than add data for new day
    # Also check. If the stopwatch has been working
    # we should correctly count time of previous day session
    # (situation when starting and ending of stopwatch are on the different dates)
    if day_data["date"] != today_date and data["is_working"] == "False":
        data["num_days"] = int(data["num_days"]) + 1
        data["days_data"].append({
        "date": today_date,
        "sum_time": "00:00:00",
        "num_sessions": "0",
        "sessions_data": []
        }
        )
    elif day_data["date"] != today_date and data["is_working"] == "True":
        # count previous day session until midnight
        session_data = stopwatch_off(data, end_time_str = "00:00:00")
        
        data["num_days"] = int(data["num_days"]) + 1
        data["days_data"].append({
        "date": today_date,
        "sum_time": "00:00:00",
        "num_sessions": "0",
        "sessions_data": [{
            "start": "00:00:00",
            "end": "-",
            "duration": "-"
            }]
        }
        )
    
    # switch stopwatch
    data["is_working"] = "True" if data["is_working"] == "False" else "False"
    
    # if working than add new session
    if data["is_working"] == "True":
        data["days_data"][-1]["sessions_data"].append({
            "start": cur_time,
            "end": "-",
            "duration": "-"
            })
        data["days_data"][-1]["num_sessions"] = int(data["days_data"][-1]["num_sessions"]) + 1
        # notify("⏱ Stopwatch on!")
        notification.notify(
        title="⏱ Stopwatch",
        message="Stopwatch on!",
        timeout=5  # seconds
        )
        
    else: # else save data
        stopwatch_off(data, end_time_str=cur_time)
        


# save changes
with open(file_name, 'w', encoding="utf-8") as f: 
    json.dump(data, f)






    
    
