import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sqlite3
import pandas as pd
import sys
import cv2
import os
DB_PATH = "../database/attendance.db"


# =====================================================
# START ATTENDANCE
# =====================================================

def start_attendance():

    try:

        subprocess.Popen(
            [
                sys.executable,
                "realtime_attendance.py"
            ]
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

print(sys.executable)

# =====================================================
# REGISTER STUDENT
# =====================================================

def register_student():

    register_window = tk.Toplevel(root)

    register_window.title(
        "Register Student"
    )

    register_window.geometry(
        "350x180"
    )

    tk.Label(
        register_window,
        text="Student Name:",
        font=("Arial", 12)
    ).pack(pady=10)

    name_entry = tk.Entry(
        register_window,
        font=("Arial", 12)
    )

    name_entry.pack(pady=5)

    def capture_images():

        student_name = (
            name_entry.get()
            .strip()
        )

        if not student_name:

            messagebox.showerror(
                "Error",
                "Enter Student Name"
            )

            return

        folder = os.path.join(
            "../dataset",
            student_name
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        cap = cv2.VideoCapture(0)

        count = 0

        while count < 20:

            ret, frame = cap.read()

            if not ret:
                continue

            count += 1

            cv2.imwrite(

                os.path.join(
                    folder,
                    f"img_{count}.jpg"
                ),

                frame

            )

            display = frame.copy()

            cv2.putText(

                display,

                f"Capturing {count}/20",

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 255, 0),

                2

            )

            cv2.imshow(
                "Student Registration",
                display
            )

            cv2.waitKey(150)

        cap.release()

        cv2.destroyAllWindows()

        messagebox.showinfo(
            "Success",
            "Images Captured\n\nTraining Model..."
        )

        try:

            subprocess.run(
                [
                    sys.executable,
                    "train_embeddings.py"
                ],
                check=True
            )

            subprocess.run(
                [
                    sys.executable,
                    "train_classifier.py"
                ],
                check=True
            )

            messagebox.showinfo(
                "Success",
                f"{student_name} Registered Successfully!"
            )

        except Exception as e:

            messagebox.showerror(
                "Training Error",
                str(e)
            )

    tk.Button(

        register_window,

        text="Register",

        width=20,

        command=capture_images

    ).pack(
        pady=20
    )

# =====================================================
# EXPORT CSV
# =====================================================

def export_csv():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        student_name,
        date,
        entry_time,
        exit_time,
        duration_seconds
    FROM attendance_sessions
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    df.to_csv(
        "../reports/attendance_report.csv",
        index=False
    )

    messagebox.showinfo(
        "Success",
        "CSV Exported Successfully!"
    )


# =====================================================
# VIEW DATABASE
# =====================================================

def view_database():

    window = tk.Toplevel(root)

    window.title(
        "Attendance Records"
    )

    window.geometry(
        "900x500"
    )

    tree = ttk.Treeview(

        window,

        columns=(

            "Name",
            "Date",
            "Entry",
            "Exit",
            "Duration"

        ),

        show="headings"

    )

    tree.heading(
        "Name",
        text="Student"
    )

    tree.heading(
        "Date",
        text="Date"
    )

    tree.heading(
        "Entry",
        text="Arrival"
    )

    tree.heading(
        "Exit",
        text="Leaving"
    )

    tree.heading(
        "Duration",
        text="Duration(sec)"
    )

    tree.pack(
        fill=tk.BOTH,
        expand=True
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            student_name,

            date,

            entry_time,

            exit_time,

            duration_seconds

        FROM attendance_sessions

        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    for row in rows:

        tree.insert(
            "",
            tk.END,
            values=row
        )


# =====================================================
# VIEW DAILY REPORT
# =====================================================

def view_report():

    window = tk.Toplevel(root)

    window.title(
        "Daily Attendance Report"
    )

    window.geometry(
        "700x400"
    )

    text = tk.Text(
        window,
        font=("Consolas", 11)
    )

    text.pack(
        fill=tk.BOTH,
        expand=True
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            student_name,

            MIN(entry_time),

            MAX(exit_time),

            SUM(duration_seconds)

        FROM attendance_sessions

        GROUP BY student_name
        """
    )

    rows = cursor.fetchall()

    conn.close()

    text.insert(
        tk.END,
        "\nDAILY ATTENDANCE SUMMARY\n\n"
    )

    text.insert(
        tk.END,
        f"{'Name':<15}"
        f"{'Arrival':<15}"
        f"{'Leaving':<15}"
        f"{'Duration(sec)':<15}\n"
    )

    text.insert(
        tk.END,
        "-" * 60 + "\n"
    )

    for row in rows:

        text.insert(
            tk.END,
            f"{row[0]:<15}"
            f"{row[1]:<15}"
            f"{row[2]:<15}"
            f"{row[3]:<15}\n"
        )


# =====================================================
# MAIN WINDOW
# =====================================================

root = tk.Tk()

root.title(
    "Face Attendance Management System"
)

root.geometry(
    "500x550"
)

root.resizable(
    False,
    False
)

title = tk.Label(

    root,

    text=
    "FACE ATTENDANCE\nMANAGEMENT SYSTEM",

    font=(
        "Arial",
        18,
        "bold"
    )

)

title.pack(
    pady=20
)

btn1 = tk.Button(

    root,

    text=
    "Start Attendance",

    font=(
        "Arial",
        12
    ),

    width=25,

    height=2,

    command=
    start_attendance

)

btn1.pack(
    pady=10
)

btn_register = tk.Button(

    root,

    text=
    "Register Student",

    font=(
        "Arial",
        12
    ),

    width=25,

    height=2,

    command=
    register_student

)

btn_register.pack(
    pady=10
)

btn2 = tk.Button(

    root,

    text=
    "View Report",

    font=(
        "Arial",
        12
    ),

    width=25,

    height=2,

    command=
    view_report

)

btn2.pack(
    pady=10
)

btn3 = tk.Button(

    root,

    text=
    "View Database",

    font=(
        "Arial",
        12
    ),

    width=25,

    height=2,

    command=
    view_database

)

btn3.pack(
    pady=10
)

btn4 = tk.Button(

    root,

    text=
    "Export CSV",

    font=(
        "Arial",
        12
    ),

    width=25,

    height=2,

    command=
    export_csv

)

btn4.pack(
    pady=10
)

btn5 = tk.Button(

    root,

    text=
    "Exit",

    font=(
        "Arial",
        12
    ),

    width=25,

    height=2,

    command=
    root.destroy

)

btn5.pack(
    pady=10
)

root.mainloop()