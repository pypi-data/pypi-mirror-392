# getdates/cli.py
import sys
from datetime import datetime, timedelta

def main():
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
            result = datetime.now() - timedelta(days=days)
        except ValueError:
            print("Please provide a valid integer.")
            sys.exit(1)
    else:
        result = datetime.now()

    print("Resulting datetime:", result.strftime("%Y-%m-%d %H:%M:%S"))

