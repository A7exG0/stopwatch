from datetime import datetime
import subprocess
from plyer import notification

class Stopwatch():
    def __init__(self, data, cur_time, today_date):
        self.data = data
        self.cur_time = cur_time
        self.today_date = today_date
    
        
    def show_last_session(self):
        if self.is_working() == True:
            last_session = self.data["days_data"][-1]["sessions_data"][-1] 
            
            start_time = datetime.strptime(last_session["start"], "%H:%M:%S")
            end_time = datetime.strptime(self.cur_time, "%H:%M:%S")
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
            message=f"Stopwatch isn't working",
            timeout=5  # seconds
            )   
    
    def is_working(self): 
        return True if self.data["is_working"] == "True" else False
    
    def switch(self):
        self.data["is_working"] = "True" if self.data["is_working"] == "False" else "False"

    def on(self, cur_time=None): 
        if not cur_time: cur_time = self.cur_time
        self._add_session()
        self.data["days_data"][-1]["num_sessions"] = int(self.data["days_data"][-1]["num_sessions"]) + 1
        notification.notify(
            title="⏱ Stopwatch",
            message="Stopwatch on!",
            timeout=5  # seconds
            )

    def off(self, end_time=None):
        '''Function for saving result of session'''
        
        if not end_time: end_time = self.cur_time
        
        # Take last day data and last session data 
        day_data = self.data["days_data"][-1]
        session_data = day_data["sessions_data"][-1]
        
        session_data["end"] = end_time
        # convert star_time and end_time into datetime class
        start_time = datetime.strptime(session_data["start"], "%H:%M:%S")
        end_time = datetime.strptime(end_time, "%H:%M:%S")
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
        total_time = list(map(int, self.data["total_time"].split(":")))
        total_time_seconds = delta.seconds + convert_to_seconds(total_time[0], total_time[1], total_time[2])
        hours, minutes, seconds = convert_from_seconds(total_time_seconds)
        self.data["total_time"] = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        # save session changes in data  
        self.data["days_data"][-1]["sessions_data"][-1] = session_data # last day, last session
        
        # notify(f"⏱ Stopwatch off! Session:{session_data['duration']}\n Day:{day_data['sum_time']}")
        notification.notify(
            title="⏱ Stopwatch",
            message=f"Stopwatch off!\nSession:{session_data['duration']}\n Day:{day_data['sum_time']}",
            timeout=5  # seconds
        )
        
    def _add_day(self):
        data = self.data
        data["num_days"] = int(data["num_days"]) + 1
        data["days_data"].append({
            "date": self.today_date,
            "sum_time": "00:00:00",
            "num_sessions": "0",
            "sessions_data": []
            }
        )
            
    def _add_session(self, time=None):
        if not time: time = self.cur_time
        self.data["days_data"][-1]["sessions_data"].append({
            "start": time,
            "end": "-",
            "duration": "-"
            })
        
    def check_day(self):
        data = self.data
        
        # Take data of the last day 
        day_data = data["days_data"][-1]
        
        # Check, match of the dates
        # if not, than add data for new day
        # Also check. If the stopwatch has been working
        # we should correctly count time of previous day session
        # (situation when starting and ending of stopwatch are on the different dates)
        
        if day_data["date"] != self.today_date and self.is_working() == False:
            self._add_day()
        elif day_data["date"] != self.today_date and self.is_working() == True:
            # count previous day session until midnight
            self.off(end_time = "00:00:00")
            self._add_day()
            self._add_session(time = "00:00:00")



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
