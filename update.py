
from datetime import datetime
from pathlib import Path 
import json
import sys
from stopwatch2 import Stopwatch

# Get the file path for saving and current date, time 
script_dir = Path(__file__).parent.resolve()
path = script_dir / f"update.txt"           # path.txt contain path to data
with open(path, 'r', encoding="utf-8") as f: 
    data_path = Path(f.read())
 
today = datetime.today()
now = datetime.now()
cur_time = now.strftime("%H:%M:%S")
today_date = now.strftime("%d/%m/%Y")

# Check existing file for the first starting of stopwatch
if not Path.exists(data_path): 
    data = {
    "is_working": "False",
    "total_time": "00:00:00",
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
    with open(data_path, 'w', encoding="utf-8") as f: 
        json.dump(data, f)


# Get data from file 
with open(data_path, 'r', encoding="utf-8") as f: 
    
    data = json.load(f)
    stopwatch = Stopwatch(data, cur_time, today_date)
    
    # can check duration only when stopwatch is working 
    if len(sys.argv) > 1 and sys.argv[1] == "duration":
        stopwatch.show_last_session()
        sys.exit()
    
    stopwatch.check_day()
    stopwatch.switch()
    # if working than add new session
    if stopwatch.is_working() == True:
        stopwatch.on()  
    else: # stopwatch off and save data
        stopwatch.off()
        
# save changes
with open(data_path, 'w', encoding="utf-8") as f: 
    json.dump(data, f)






    
    
