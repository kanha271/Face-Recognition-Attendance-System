from datetime import datetime


class AttendanceManager:

    EXIT_TIMEOUT = 12  # seconds

    def __init__(self):

        # Currently visible students
        self.active_students = {}

        # Total accumulated attendance time
        self.total_time = {}

    # -----------------------------------
    # Called whenever a face is detected
    # -----------------------------------
    def student_seen(self, name):

        now = datetime.now()

        if name not in self.active_students:

            self.active_students[name] = {
                "entry_time": now,
                "last_seen": now
            }

            print(f"[ENTER] {name}")

        else:

            self.active_students[name]["last_seen"] = now

    # -----------------------------------
    # Check for exits
    # -----------------------------------
    def update(self):

        now = datetime.now()

        exited_students = []

        for name, data in list(self.active_students.items()):

            gap = (
                now - data["last_seen"]
            ).total_seconds()

            if gap > self.EXIT_TIMEOUT:

                duration = (
                    data["last_seen"]
                    -
                    data["entry_time"]
                ).total_seconds()

                self.total_time[name] = (
                    self.total_time.get(name, 0)
                    + duration
                )

                exited_students.append({

                    "name": name,

                    "entry_time":
                        data["entry_time"],

                    "exit_time":
                        data["last_seen"],

                    "duration":
                        int(duration)
                })

                print(
                    f"[EXIT] {name} | "
                    f"{int(duration)} sec"
                )

                del self.active_students[name]

        return exited_students

    # -----------------------------------
    # Live duration while present
    # -----------------------------------
    def get_live_duration(self, name):

        if name not in self.active_students:

            return int(
                self.total_time.get(
                    name,
                    0
                )
            )

        now = datetime.now()

        current_session = (

            now
            -
            self.active_students[name][
                "entry_time"
            ]

        ).total_seconds()

        total = (

            self.total_time.get(
                name,
                0
            )

            + current_session

        )

        return int(total)

    # -----------------------------------
    # Human-readable duration
    # -----------------------------------
    def get_duration_string(self, name):

        seconds = self.get_live_duration(
            name
        )

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        secs = seconds % 60

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d}"
        )

    # -----------------------------------
    # Student currently present?
    # -----------------------------------
    def is_present(self, name):

        return (
            name
            in
            self.active_students
        )
    # -----------------------------------
    # Get entry time of active student
    # -----------------------------------

    def get_entry_time(self, name):

        if name in self.active_students:

            return self.active_students[
                name
            ]["entry_time"].strftime(
                "%H:%M:%S"
            )

        return "--:--:--"
    # -----------------------------------
    # Get all active students
    # -----------------------------------
    def get_active_students(self):

        return list(
            self.active_students.keys()
        )

    # -----------------------------------
    # Total attendance seconds
    # -----------------------------------
    def get_total_seconds(self, name):

        return int(

            self.total_time.get(
                name,
                0
            )

        )