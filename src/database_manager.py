import sqlite3
from datetime import datetime

DB_PATH = "../database/attendance.db"


class DatabaseManager:

    def __init__(self):

        self.conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.cursor = self.conn.cursor()

        self.create_tables()

    # ----------------------------------
    # Create Tables
    # ----------------------------------

    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE

        )

        """)

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS attendance_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_name TEXT,

            date TEXT,

            entry_time TEXT,

            exit_time TEXT,

            duration_seconds INTEGER

        )

        """)

        self.conn.commit()

    # ----------------------------------
    # Add Student
    # ----------------------------------

    def add_student(self, name):

        try:

            self.cursor.execute(
                """
                INSERT INTO students(name)
                VALUES(?)
                """,
                (name,)
            )

            self.conn.commit()

        except sqlite3.IntegrityError:
            pass

    # ----------------------------------
    # Save Attendance Session
    # ----------------------------------

    def save_session(

        self,

        student_name,

        entry_time,

        exit_time,

        duration_seconds

    ):

        date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        self.cursor.execute(
            """
            INSERT INTO attendance_sessions(

                student_name,

                date,

                entry_time,

                exit_time,

                duration_seconds

            )

            VALUES (?, ?, ?, ?, ?)

            """,

            (

                student_name,

                date,

                entry_time,

                exit_time,

                duration_seconds

            )
        )

        self.conn.commit()

    # ----------------------------------
    # Get Today's Attendance
    # ----------------------------------

    def get_today_attendance(self):

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        self.cursor.execute(
            """
            SELECT *

            FROM attendance_sessions

            WHERE date = ?
            """,
            (today,)
        )

        return self.cursor.fetchall()

    # ----------------------------------
    # Total Attendance
    # ----------------------------------

    def get_total_duration(

        self,

        student_name

    ):

        self.cursor.execute(
            """
            SELECT

                SUM(duration_seconds)

            FROM

                attendance_sessions

            WHERE

                student_name = ?
            """,
            (student_name,)
        )

        result = self.cursor.fetchone()[0]

        return result if result else 0

       # ----------------------------------
    # Attendance Percentage
    # ----------------------------------

    def get_attendance_percentage(

        self,

        student_name,

        total_class_seconds

    ):

        attended = self.get_total_duration(
            student_name
        )

        if total_class_seconds == 0:
            return 0

        return round(

            (attended /
             total_class_seconds)

            * 100,

            2
        )

    # ----------------------------------
    # Daily Summary Report
    # ----------------------------------

    def get_daily_summary(self):

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        self.cursor.execute(
            """
            SELECT

                student_name,

                MIN(entry_time),

                MAX(exit_time),

                SUM(duration_seconds)

            FROM attendance_sessions

            WHERE date = ?

            GROUP BY student_name
            """,
            (today,)
        )

        return self.cursor.fetchall()

    # ----------------------------------
    # Close Database
    # ----------------------------------

    def close(self):

        self.conn.close()