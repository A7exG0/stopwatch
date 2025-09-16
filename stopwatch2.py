from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from plyer import notification
import logging

logger = logging.getLogger(__name__)


class Stopwatch:
    """
    Stopwatch that operates on an external `data` dict.
    `data` expected structure (example):
    {
      "is_working": "False",            # or True/False
      "total_time": "00:00:00",
      "num_days": "1",
      "days_data": [
        {
          "date": "2025-09-13",
          "sum_time": "00:00:00",
          "num_sessions": "0",
          "sessions_data": [
            {"start": "12:00:00", "end": "12:30:00", "duration": "00:30:00"}
          ]
        }
      ]
    }
    """
    TIME_FMT = "%H:%M:%S"

    def __init__(self, data: Dict[str, Any], cur_time: str, today_date: str):
        self.data = data
        self.cur_time = cur_time
        self.today_date = today_date
        # ensure structure minimally exists
        if "days_data" not in self.data or not self.data["days_data"]:
            self._add_day(initial=True)

    # ----------------- helpers -----------------
    def _notify(self, title: str, message: str, timeout: int = 5) -> None:
        """Uniform notification wrapper (uses plyer)."""
        try:
            notification.notify(title=title, message=message, timeout=timeout)
        except Exception:
            # fallback: just log if notifications fail
            logger.exception("Notification failed")
            logger.info("%s: %s", title, message)

    @staticmethod
    def _parse_hms(hms: str) -> int:
        """Parse 'HH:MM:SS' into seconds. Returns 0 for invalid inputs like '-'."""
        if not hms or hms == "-" or hms == "--":
            return 0
        try:
            h, m, s = map(int, hms.split(":"))
            return h * 3600 + m * 60 + s
        except Exception:
            logger.exception("Failed to parse time string: %s", hms)
            return 0

    @staticmethod
    def _format_hms(total_seconds: int) -> str:
        """Format seconds into 'HH:MM:SS' (hours can exceed 24)."""
        hours = total_seconds // 3600
        rest = total_seconds % 3600
        minutes = rest // 60
        seconds = rest % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _seconds_diff(self, start_str: str, end_str: str) -> int:
        """
        Return non-negative difference in seconds between start and end times.
        If end < start (cross-midnight), adds 24h.
        """
        s = self._parse_hms(start_str)
        e = self._parse_hms(end_str)
        delta = e - s
        if delta < 0:
            # crossed midnight — add 24h
            delta += 24 * 3600
        return delta

    # convenient accessors
    def _last_day(self) -> Dict[str, Any]:
        if not self.data.get("days_data"):
            self._add_day()
        return self.data["days_data"][-1]

    def _last_session(self) -> Optional[Dict[str, Any]]:
        day = self._last_day()
        if not day.get("sessions_data"):
            return None
        return day["sessions_data"][-1]

    # ----------------- public API -----------------
    def is_working(self) -> bool:
        """Return True if stopwatch is on. Accepts boolean or 'True'/'False' strings."""
        val = self.data.get("is_working", False)
        if isinstance(val, bool):
            return val
        return str(val).lower() == "true"

    def switch(self) -> None:
        """Toggle working state (and store as string to preserve JSON format)."""
        new_state = not self.is_working()
        # preserve original style (string) to avoid breaking external consumers:
        self.data["is_working"] = "True" if new_state else "False"

    def on(self, cur_time: Optional[str] = None) -> None:
        """Start a session (add session entry and increment counters)."""
        if cur_time is None:
            cur_time = self.cur_time

        # ensure we have today's day entry
        last_day = self._last_day()
        if last_day.get("date") != self.today_date:
            self._add_day()

        # add session and increment counters (store numbers as strings to match original)
        self._add_session(time=cur_time)
        day = self._last_day()
        # num_sessions may be stored as string
        try:
            num = int(day.get("num_sessions", "0")) + 1
        except Exception:
            num = 1
        day["num_sessions"] = str(num)

        # mark working
        self.data["is_working"] = "True"
        self._notify("⏱ Stopwatch", "Stopwatch on!")

    def off(self, end_time: Optional[str] = None) -> None:
        """Stop the last session, compute duration, update day sum and total_time."""
        if end_time is None:
            end_time = self.cur_time

        day = self._last_day()
        session = self._last_session()
        if session is None:
            # nothing to stop
            self._notify("⏱ Stopwatch", "No active session to stop.")
            return

        session["end"] = end_time

        # compute session duration in seconds (handle cross-midnight)
        duration_seconds = self._seconds_diff(session["start"], end_time)
        session["duration"] = self._format_hms(duration_seconds)

        # update day's sum_time
        day_sum_seconds = self._parse_hms(day.get("sum_time", "00:00:00"))
        day_sum_seconds += duration_seconds
        day["sum_time"] = self._format_hms(day_sum_seconds)

        # update total_time
        total_seconds = self._parse_hms(self.data.get("total_time", "00:00:00"))
        total_seconds += duration_seconds
        self.data["total_time"] = self._format_hms(total_seconds)

        # store session back (though we edited in place)
        # mark not working
        self.data["is_working"] = "False"

        self._notify(
            "⏱ Stopwatch",
            f"Stopwatch off!\nSession: {session['duration']}\nDay: {day['sum_time']}"
        )

    def show_last_session(self) -> None:
        """Show duration of the last session; if currently running, compute to cur_time."""
        if not self.is_working():
            self._notify("⏱ Stopwatch", "Stopwatch isn't working")
            return

        session = self._last_session()
        if session is None:
            self._notify("⏱ Stopwatch", "No sessions found")
            return

        # If session has an 'end' set and is not '-', use it, else use cur_time
        end = session.get("end")
        if end and end != "-":
            end_time = end
        else:
            end_time = self.cur_time

        seconds = self._seconds_diff(session["start"], end_time)
        duration = self._format_hms(seconds)
        self._notify("⏱ Stopwatch", f"Duration: {duration}")

    def check_day(self) -> None:
        """
        Ensure days_data contains today's date.
        If date changed and stopwatch was running, split session at midnight.
        """
        day = self._last_day()
        if day.get("date") == self.today_date:
            return  # all good

        # date changed
        if not self.is_working():
            # simply add a new day record
            self._add_day()
            return

        # was running across midnight -> finish previous day at 00:00:00, start new day continuing from 00:00:00
        # end previous day session at 00:00:00
        self.off(end_time="00:00:00")
        # add new day and start session at 00:00:00
        self._add_day()
        self._add_session(time="00:00:00")
        # leave is_working as True

    # ----------------- low-level updaters -----------------
    def _add_day(self, initial: bool = False) -> None:
        """Append a new day entry. `initial=True` sets today's date if possible."""
        # increment num_days safely
        try:
            self.data["num_days"] = str(int(self.data.get("num_days", "0")) + 1)
        except Exception:
            self.data["num_days"] = "1"

        date_to_use = self.today_date if initial or self.data.get("days_data") == [] else self.today_date
        self.data.setdefault("days_data", []).append({
            "date": date_to_use,
            "sum_time": "00:00:00",
            "num_sessions": "0",
            "sessions_data": []
        })

    def _add_session(self, time: Optional[str] = None) -> None:
        """Append a new session to the last day."""
        if time is None:
            time = self.cur_time
        day = self._last_day()
        day.setdefault("sessions_data", []).append({
            "start": time,
            "end": "-",
            "duration": "-"
        })
