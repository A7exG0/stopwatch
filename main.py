
from datetime import datetime
from pathlib import Path 
import json
import subprocess

def stopwatch_off(data, end_time_str):
    day_data = data["days_data"][-1]
    session_data = day_data["sessions_data"][-1]
    
    session_data["end"] = end_time_str
    # get start time
    start_time = datetime.strptime(session_data["start"], "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")
    delta = end_time - start_time
    hours, minutes, seconds = convert_from_seconds(delta.seconds)
    session_data["duration"] = f"{hours}:{minutes}:{seconds}"
    
    
    sum_time = datetime.strptime(day_data["sum_time"], "%H:%M:%S")
    sum_time += delta 
    sum_time_str = datetime.strftime(sum_time, "%H:%M:%S")
    day_data["sum_time"] = sum_time_str
    
    total_time = list(map(int, data["total_time"].split(":")))
    total_time_seconds = delta.seconds + convert_to_seconds(total_time[0], total_time[1], total_time[2])
    hours, minutes, seconds = convert_from_seconds(total_time_seconds)
    data["total_time"] = f"{hours}:{minutes}:{seconds}"
    
    notify("⏱ Stopwatch off!")
    return session_data

def notify(text):
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


script_dir = Path(__file__).parent.resolve()
today = datetime.today()
now = datetime.now()
cur_time = now.strftime("%H:%M:%S")
today_date = now.strftime("%d/%m/%Y")

file_name = script_dir / f"sessions.json" #TODO rename json file

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



with open(file_name, 'r', encoding="utf-8") as f: 
    data = json.load(f)
    
    day_data = data["days_data"][-1]
       
    if day_data["date"] != today_date and data["is_working"] == "False":
        data["num_days"] = int(data["num_days"]) + 1
        data["days_data"].append({
        "date": today_date,
        "sum_time": "00:00:00",
        "num_sessions": "0",
        "sessions_data": []
        }
        )
        # day_data = data["days_data"][-1]
    elif day_data["date"] != today_date and data["is_working"] == "True":
        session_data = stopwatch_off(data, end_time_str = "00:00:00")
        data["days_data"][-1]["sessions_data"][-1] = session_data
        print(session_data)
        
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
    
    data["is_working"] = "True" if data["is_working"] == "False" else "False"
    
    if data["is_working"] == "True":
        data["days_data"][-1]["sessions_data"].append({
            "start": cur_time,
            "end": "-",
            "duration": "-"
            })
        # session_data = day_data["sessions_data"][-1]
        notify("⏱ Stopwatch on!")
    else:
        session_data = stopwatch_off(data, end_time_str=cur_time)
        data["days_data"][-1]["sessions_data"][-1] = session_data
    
    data["days_data"][-1]["num_sessions"] = len(data["days_data"][-1]["sessions_data"])
    
    # data["days_data"][-1] = day_data  
    
        

with open(file_name, 'w', encoding="utf-8") as f: 
    json.dump(data, f)






    
    
