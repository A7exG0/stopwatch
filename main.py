
from datetime import datetime
from pathlib import Path 
import json
import subprocess

def notify(text):
    subprocess.run(["notify-send", text])

def convert(total_seconds):
    '''Convert seconds to hours, minutes, seconds'''
    hours = total_seconds // 3600 
    rest = total_seconds % 3600
    minutes = rest // 60 
    seconds = rest % 60
    return hours, minutes, seconds

#TODO add checking of midnight
script_dir = Path(__file__).parent.resolve()
today = datetime.today()
now = datetime.now()
cur_time = now.strftime("%H:%M:%S")
today_date = now.strftime("%d/%m/%Y")

file_name = script_dir / f"sessions.json" #TODO rename json file

#Check existing file for the first starting of stopwatch
if not Path.exists(file_name): 
    data = {
    "total_time": "0:0:0",
    "num_days": "1",
    "days_data": [
        {
        "date": "-",
        "sum_time": "0:0:0",
        "num_sessions": "1",
        "sessions_data": [
            {
            "start": "-",
            "end": "-",
            "duration": "-"
            }
        ]
        }
    ]
    }
    with open(file_name, 'w', encoding="utf-8") as f: 
        json.dump(data, f)


with open(file_name, 'r', encoding="utf-8") as f: 
    data = json.load(f)
    
    day_data = data["days_data"][-1]
    
    if day_data["date"] == "-": #TODO somethin to do with date
        day_data["date"] = today_date
    
    session_data = day_data["sessions_data"][-1]
    
    if session_data["end"] != "-":
        day_data["num_sessions"] = int(day_data["num_sessions"]) + 1
        day_data["sessions_data"].append({
            "start": "-",
            "end": "-",
            "duration": "-"
            })
        session_data = day_data["sessions_data"][-1]
    
    if session_data["start"] == "-": 
        session_data["start"] = cur_time
        notify("⏱ Stopwatch on!")
    else:
        session_data["end"] = cur_time 
        # get start time
        start_time = datetime.strptime(session_data["start"], "%H:%M:%S")
        delta = now - start_time
        hours, minutes, seconds = convert(delta.seconds)
        session_data["duration"] = f"{hours}:{minutes}:{seconds}"
        
        sum_time = datetime.strptime(day_data["sum_time"], "%H:%M:%S")
        sum_time += delta 
        sum_time_str = datetime.strftime(sum_time, "%H:%M:%S")
        day_data["sum_time"] = sum_time_str
        notify("⏱ Stopwatch off!")
        
    
    day_data["sessions_data"][-1] = session_data
    data["days_data"][-1] = day_data  
        

with open(file_name, 'w', encoding="utf-8") as f: 
    json.dump(data, f)






    
    
