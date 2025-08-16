
from datetime import datetime
import os 


today = datetime.today()
now = datetime.now()

today_date = today.strftime("%y-%m-%d")
current_dir = os.getcwd()
file_name = current_dir + '/' + today_date + '.json'

with open(file_name, 'a+', encoding="utf-8")