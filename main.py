
from datetime import datetime
from pathlib import Path 
import json



script_dir = Path(__file__).parent.resolve()
today = datetime.today()
now = datetime.now().strftime("%H:%M:%S")

file_name = script_dir / f"time/{today.strftime('%y-%m-%d')}.json"

if not Path.exists(file_name): 
    data = {"total_time": "0", "num_session": "0"}
    with open(file_name, 'w', encoding="utf-8") as f: 
        json.dump(data, f)
else:
    with open(file_name, 'r', encoding="utf-8") as f: 
        data = json.load(f)
        num_session = int(data["num_session"]) + 1
        if f"session{num_session}" in data:
            data[f"session{num_session}"]["end"] = now 
            data[f"session{num_session}"]["duration"] = "1"
            data["num_session"] = num_session
            # data["total_time"] = int(data["total_time"]) - data[f"session{num_session}"]["start"]   #TODO make normal data_time
        else:
            data[f"session{num_session}"] = {"start":now, "end": '-', "duration" : "-"}
            
        # f.write(now.strftime("%H:%M:%S") + "\n")
    
    print(data)
    with open(file_name, 'w', encoding="utf-8") as f: 
        json.dump(data, f)





    
    
