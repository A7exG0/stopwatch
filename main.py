
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
    # data = {"date": today_date, "total_time": "0:0:0", "num_session": "0"}
    data = {
    "total_time": "0:0:0",
    "num_days": "1",
    "days_data": [
        {
        "day_id": "0",
        "date": "-",
        "sum_time": "0:0:0",
        "num_sessions": "1",
        "sessions_data": [
            {
            "session_id" : 0,
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
    
    day_id = int(data["num_days"]) - 1
    day_data = data["days_data"][day_id]
    
    if day_data["date"] == "-": #TODO somethin to do with date
        day_data["date"] = today_date
    
    session_id = int(day_data["num_sessions"]) - 1
    session_data = day_data["sessions_data"][session_id]
    
    if session_data["end"] != "-":
        day_data["num_sessions"] = int(day_data["num_sessions"]) + 1
        session_id = int(day_data["num_sessions"]) - 1
        day_data["sessions_data"].append({
            "session_id" : session_id,
            "start": "-",
            "end": "-",
            "duration": "-"
            })
        session_data = day_data["sessions_data"][session_id]
    
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
        # hours, minutes, seconds = convert(sum_time.seconds)
        day_data["sum_time"] = sum_time_str
        notify("⏱ Stopwatch off!")
        
    
    day_data["sessions_data"][session_id] = session_data
    data["days_data"][day_id] = day_data  
        
    # if f"session{num_session}" in data:
    #     data[f"session{num_session}"]["end"] = cur_time 
    #     data[f"session{num_session}"]["duration"] = "1"
    #     data["num_session"] = num_session
    #     notify("⏱ Stopwatch off!")
        
    #     #get start time
    #     start_time = datetime.strptime(data[f"session{num_session}"]["start"], "%H:%M:%S")
    #     delta = now - start_time
    #     # print(delta.seconds // 60, "minutes", delta.seconds % 60, "seconds")
        
    #     hours, minutes, seconds = convert(delta.seconds)
    #     data[f"session{num_session}"]["duration"] = f"{hours}:{minutes}:{seconds}"
        
    #     total_time = datetime.strptime(data["total_time"], "%H:%M:%S")
    #     # print(total_time)
    #     #! I stop here. Need to find how to add duration to total_time 
    #     print(total_time.hour)
    # else:
    #     data[f"session{num_session}"] = {"start" :cur_time, "end": '-', "duration" : "-"}
    #     notify("⏱ Stopwatch on!")
        
    # f.write(now.strftime("%H:%M:%S") + "\n")

with open(file_name, 'w', encoding="utf-8") as f: 
    json.dump(data, f)






    
    
