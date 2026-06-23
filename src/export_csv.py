import csv
from database_manager import DatabaseManager

db = DatabaseManager()

rows = db.get_daily_summary()

with open(
    "../reports/attendance.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Name",
        "Arrival Time",
        "Leaving Time",
        "Duration (Seconds)"
    ])

    for row in rows:

        writer.writerow(row)

db.close()

print(
    "CSV exported successfully."
)