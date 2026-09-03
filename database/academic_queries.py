from database.connection import get_connection
import pandas as pd


def get_all_subjects():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM subjects", conn)
    conn.close()
    return df


def get_curriculum_for_class(class_):
    """Returns the subjects a given Class studies."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT s.Subject_ID, s.Subject_Name, s.Subject_Code, s.Type
        FROM class_subjects cs
        JOIN subjects s ON cs.Subject_ID = s.Subject_ID
        WHERE cs.Class = ?
        ORDER BY s.Subject_Name
    """, conn, params=(class_,))
    conn.close()
    return df


def get_teacher_assignments(class_=None, section=None, branch_id=None):
    """Returns teacher assignments, optionally filtered by Class, Section, and Branch."""
    conn = get_connection()
    query = """
        SELECT ta.Assignment_ID, ta.Class, ta.Section, s.Subject_Name,
               ta.Staff_ID, st.Employee_Name
        FROM teacher_assignments ta
        JOIN subjects s ON ta.Subject_ID = s.Subject_ID
        JOIN staff st ON ta.Staff_ID = st.Staff_ID
        WHERE 1=1
    """
    params = []
    if class_:
        query += " AND ta.Class = ?"
        params.append(class_)
    if section:
        query += " AND ta.Section = ?"
        params.append(section)
    if branch_id is not None:
        query += " AND ta.Branch_ID = ?"
        params.append(branch_id)
    query += " ORDER BY ta.Class, ta.Section, s.Subject_Name"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def get_teachers_for_subject(subject_name, branch_id=None):
    subject_to_dept = {
        "English": "English", "Hindi": "Hindi", "Mathematics": "Math",
        "Environmental Studies": "Science", "Science": "Science", "Physics": "Science",
        "Chemistry": "Science", "Biology": "Science", "Social Studies": "Social Studies",
        "Economics": "Social Studies", "Computer Science": "Computer Science",
        "Art & Craft": "Arts", "Physical Education": "Physical Education",
    }
    dept = subject_to_dept.get(subject_name)
    if not dept:
        return pd.DataFrame(columns=["Staff_ID", "Employee_Name"])

    conn = get_connection()
    query = "SELECT Staff_ID, Employee_Name FROM staff WHERE Department = ? AND Status = 'Active'"
    params = [dept]
    if branch_id is not None:
        query += " AND Branch_ID = ?"
        params.append(branch_id)
    query += " ORDER BY Employee_Name"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


def update_teacher_assignment(assignment_id, new_staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE teacher_assignments SET Staff_ID = ? WHERE Assignment_ID = ?",
        (new_staff_id, assignment_id)
    )
    conn.commit()
    conn.close()

def get_timetable(class_, section, branch_id=None):
    conn = get_connection()
    query = """
        SELECT t.Timetable_ID, t.Day, t.Period, s.Subject_Name, st.Employee_Name, t.Room
        FROM timetable t
        JOIN subjects s ON t.Subject_ID = s.Subject_ID
        JOIN staff st ON t.Staff_ID = st.Staff_ID
        WHERE t.Class = ? AND t.Section = ?
    """
    params = [class_, section]
    if branch_id is not None:
        query += " AND t.Branch_ID = ?"
        params.append(branch_id)
    query += " ORDER BY t.Period"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

OVERRIDE_TYPES = [
    "Teacher Substitution", "Room Change", "Subject Replacement",
    "Holiday", "Examination", "Event", "Extra Class", "Full-Day Replacement",
]

WHOLE_DAY_TYPES = {"Holiday", "Event"}


def get_next_override_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Override_ID) FROM timetable_overrides")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def add_override(class_, section, date_str, period, override_type,
                  new_subject_id, new_staff_id, new_room, remarks, branch_id):
    conn = get_connection()
    cursor = conn.cursor()
    override_id = get_next_override_id()

    cursor.execute("""
        INSERT INTO timetable_overrides
        (Override_ID, Class, Section, Date, Period, Override_Type,
         New_Subject_ID, New_Staff_ID, New_Room, Remarks, Branch_ID)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (override_id, class_, section, date_str, period, override_type,
          new_subject_id, new_staff_id, new_room, remarks, branch_id))

    conn.commit()
    conn.close()
    return override_id


def get_overrides_for_class(class_, section, branch_id=None):
    conn = get_connection()
    query = "SELECT * FROM timetable_overrides WHERE Class = ? AND Section = ?"
    params = [class_, section]
    if branch_id is not None:
        query += " AND Branch_ID = ?"
        params.append(branch_id)
    query += " ORDER BY Date DESC"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def delete_override(override_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timetable_overrides WHERE Override_ID = ?", (int(override_id),))
    conn.commit()
    conn.close()


def get_effective_schedule_for_date(class_, section, target_date, branch_id=None):
    weekday_name = target_date.strftime("%A")
    conn = get_connection()

    master_query = """
        SELECT t.Period, s.Subject_Name, st.Employee_Name AS Teacher, t.Room, t.Staff_ID, t.Subject_ID
        FROM timetable t
        JOIN subjects s ON t.Subject_ID = s.Subject_ID
        JOIN staff st ON t.Staff_ID = st.Staff_ID
        WHERE t.Class = ? AND t.Section = ? AND t.Day = ?
    """
    master_params = [class_, section, weekday_name]
    if branch_id is not None:
        master_query += " AND t.Branch_ID = ?"
        master_params.append(branch_id)
    master_query += " ORDER BY t.Period"

    master = pd.read_sql(master_query, conn, params=master_params)

    overrides_query = """
        SELECT o.*, s.Subject_Name AS New_Subject_Name, st.Employee_Name AS New_Teacher_Name
        FROM timetable_overrides o
        LEFT JOIN subjects s ON o.New_Subject_ID = s.Subject_ID
        LEFT JOIN staff st ON o.New_Staff_ID = st.Staff_ID
        WHERE o.Class = ? AND o.Section = ? AND o.Date = ?
    """
    overrides_params = [class_, section, target_date.isoformat()]
    if branch_id is not None:
        overrides_query += " AND o.Branch_ID = ?"
        overrides_params.append(branch_id)

    overrides = pd.read_sql(overrides_query, conn, params=overrides_params)
    conn.close()

    # (rest of the function stays exactly the same from here down)
    
    if weekday_name == "Sunday" or master.empty:
        return pd.DataFrame(), "No school (Sunday / no timetable defined)."

    # Whole-day override (Holiday / Event with no specific period) replaces everything
    whole_day = overrides[overrides["Period"].isna() & overrides["Override_Type"].isin(WHOLE_DAY_TYPES)]
    if not whole_day.empty:
        note = whole_day.iloc[0]["Remarks"] or whole_day.iloc[0]["Override_Type"]
        return pd.DataFrame(), f"{whole_day.iloc[0]['Override_Type']}: {note}"

    result_rows = []
    period_overrides = overrides[overrides["Period"].notna()].set_index("Period")

    for _, row in master.iterrows():
        period = row["Period"]
        subject, teacher, room = row["Subject_Name"], row["Teacher"], row["Room"]
        note = ""

        if period in period_overrides.index:
            ov = period_overrides.loc[period]
            if isinstance(ov, pd.DataFrame):  # multiple overrides same period, take first
                ov = ov.iloc[0]

            if ov["Override_Type"] == "Teacher Substitution":
                teacher = ov["New_Teacher_Name"] or teacher
                note = f"Substitute: {ov['Remarks'] or ''}"
            elif ov["Override_Type"] == "Room Change":
                room = ov["New_Room"] or room
                note = f"Room changed: {ov['Remarks'] or ''}"
            elif ov["Override_Type"] in ("Subject Replacement", "Full-Day Replacement", "Extra Class"):
                subject = ov["New_Subject_Name"] or subject
                teacher = ov["New_Teacher_Name"] or teacher
                room = ov["New_Room"] or room
                note = f"{ov['Override_Type']}: {ov['Remarks'] or ''}"
            elif ov["Override_Type"] == "Examination":
                subject = f"Exam: {ov['New_Subject_Name'] or subject}"
                note = ov["Remarks"] or ""

        result_rows.append({
            "Period": period, "Subject": subject, "Teacher": teacher,
            "Room": room, "Note": note,
        })

    return pd.DataFrame(result_rows), None
