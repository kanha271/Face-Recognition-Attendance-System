from database_manager import DatabaseManager


def seconds_to_hms(seconds):

    h = seconds // 3600

    m = (seconds % 3600) // 60

    s = seconds % 60

    return f"{h:02d}:{m:02d}:{s:02d}"


db = DatabaseManager()

rows = db.get_daily_summary()

print("\n")

print("=" * 70)

print("DAILY ATTENDANCE SUMMARY")

print("=" * 70)

print(
    f"{'Name':<15}"
    f"{'Arrival':<15}"
    f"{'Left':<15}"
    f"{'Duration':<15}"
)

print("-" * 70)

for row in rows:

    name = row[0]

    arrival = row[1]

    left = row[2]

    duration = seconds_to_hms(
        row[3]
    )

    print(

        f"{name:<15}"

        f"{arrival:<15}"

        f"{left:<15}"

        f"{duration:<15}"

    )

print("=" * 70)

db.close()