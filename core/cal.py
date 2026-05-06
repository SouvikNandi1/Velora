__version__ = "1.1.0"
__description__ = "Displays a visual terminal calendar for the current (or specified) month and year."
__author__ = "Souvik"
__website__ = ""

import sys
import calendar
import datetime

def main():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    
    if len(sys.argv) == 2:
        try:
            year = int(sys.argv[1])
            calendar.setfirstweekday(calendar.SUNDAY)
            print(f"\n\x1b[36;1m{calendar.calendar(year)}\x1b[0m")
            return
        except ValueError:
            pass
    elif len(sys.argv) == 3:
        try:
            month = int(sys.argv[1])
            year = int(sys.argv[2])
        except ValueError:
            print("\x1b[31;1mError:\x1b[0m Invalid month or year.")
            return
            
    try:
        # Set the first day of the week to Sunday to match standard Unix `cal`
        calendar.setfirstweekday(calendar.SUNDAY)
        
        cal_str = calendar.month(year, month)
        lines = cal_str.split('\n')
        print(f"\n\x1b[36;1m{lines[0]}\x1b[0m")
        print(f"\x1b[33;1m{lines[1]}\x1b[0m")
        for line in lines[2:]:
            if not line.strip(): continue
            if year == now.year and month == now.month:
                day_str = str(now.day).rjust(2)
                line = line.replace(day_str, f"\x1b[32;1m{day_str}\x1b[0m", 1)
            print(line)
    except Exception as e:
        print(f"\x1b[31;1mError generating calendar:\x1b[0m {e}")

if __name__ == "__main__":
    main()