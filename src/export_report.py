import csv

from database_manager import DatabaseManager


def seconds_to_hms(seconds):

    hours = seconds // 3600

    minutes = (seconds % 3600) // 60

    secs = seconds % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


db = DatabaseManager()

db.cursor.execute(
    """
    SELECT DISTINCT student_name
    FROM attendance_sessions
    """
)

students = db.cursor.fetchall()

with open(
    "../reports/attendance_report.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Student Name",
        "Total Attendance Time"
    ])

    for student in students:

        name = student[0]

        total_seconds = db.get_total_duration(
            name
        )

        writer.writerow([

            name,

            seconds_to_hms(
                total_seconds
            )

        ])

db.close()

print(
    "CSV Report Generated Successfully"
)