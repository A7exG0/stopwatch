
from datetime import datetime
from pathlib import Path 

script_dir = Path(__file__).parent.resolve()
today = datetime.today()
now = datetime.now()

file_name = script_dir / f"time/{today.strftime('%y-%m-%d')}.json"

with open(file_name, 'a+', encoding="utf-8") as f: 
    f.write(now.strftime("%H:%M:%S") + "\n")



    
    
