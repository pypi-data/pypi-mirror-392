import sys
from datetime import datetime, timedelta

def get_previous_datetime(days=None):
    now = datetime.now()
    if days is None:
        return now
    else:
        return now - timedelta(days=days)

if __name__ == "__main__":
    # Check if user provided a number as argument
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
            result = get_previous_datetime(days)
        except ValueError:
            print("Please provide a valid integer.")
            sys.exit(1)
    else:
        result = get_previous_datetime()

    print("Resulting datetime:", result.strftime("%Y-%m-%d %H:%M:%S"))

