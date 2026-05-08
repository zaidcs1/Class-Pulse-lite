from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from utils.db import mysql

from datetime import datetime

student = Blueprint('student', __name__)
# =========================================
# STUDENT DASHBOARD
# =========================================

@student.route('/student/dashboard')
def dashboard():

    if 'student_roll' not in session:
        return redirect('/student/login')

    cur = mysql.connection.cursor()

    roll_no = session['student_roll']

    # =========================================
    # SUBJECT-WISE ANALYTICS
    # =========================================

    query = """
    SELECT
        subjects.subject_name,

        COUNT(attendance_records.id) AS total_classes,

        SUM(
            CASE
                WHEN attendance_records.status='Present'
                THEN 1
                ELSE 0
            END
        ) AS total_present,

        SUM(
            CASE
                WHEN attendance_records.status='Absent'
                THEN 1
                ELSE 0
            END
        ) AS total_absent

    FROM attendance_records

    JOIN subjects
    ON attendance_records.subject_id = subjects.subject_id

    WHERE attendance_records.roll_no=%s

    GROUP BY subjects.subject_name
    """

    cur.execute(query, (roll_no,))

    analytics = cur.fetchall()

    subject_data = []

    for row in analytics:

        subject_name = row[0]
        classes = row[1] or 0
        present = row[2] or 0
        absent = row[3] or 0

        percentage = 0

        if classes > 0:

            percentage = round(
                (present / classes) * 100,
                2
            )

        # STATUS

        if percentage >= 75:

            status = "Good"

        elif percentage >= 60:

            status = "Warning"

        else:

            status = "Detention Risk"

        subject_data.append({

            'subject': subject_name,

            'classes': classes,

            'present': present,

            'absent': absent,

            'percentage': percentage,

            'status': status
        })
    # =========================================
    # ACTIVE ATTENDANCE SESSION
    # =========================================

    from datetime import datetime

    query = """
    SELECT
        attendance_sessions.session_id,
        attendance_sessions.code,
        attendance_sessions.start_time,
        attendance_sessions.expiry_time,
        subjects.subject_name

    FROM attendance_sessions

    JOIN subjects
    ON attendance_sessions.subject_id = subjects.subject_id

    WHERE attendance_sessions.is_active=TRUE

    ORDER BY attendance_sessions.session_id DESC
    LIMIT 1
    """

    cur.execute(query)

    session_data = cur.fetchone()

    active_session = None

    if session_data:

        current_time = datetime.now()

        start_time = session_data[2]
        expiry_time = session_data[3]

        # TRUE LIVE VALIDATION

        if start_time <= current_time <= expiry_time:

            active_session = session_data
    # =========================================
    # FINAL RESPONSE
    # =========================================

    return render_template(

        'student/dashboard.html',

        subject_data=subject_data,

        active_session=active_session
    )
# =========================================
# MARK ATTENDANCE PAGE
# =========================================

@student.route('/student/attendance')
def mark_attendance_page():

    if 'student_roll' not in session:
        return redirect('/student/login')

    cur = mysql.connection.cursor()

    from datetime import datetime

    query = """
    SELECT
        attendance_sessions.session_id,
        attendance_sessions.code,
        attendance_sessions.start_time,
        attendance_sessions.expiry_time,
        subjects.subject_name

    FROM attendance_sessions

    JOIN subjects
    ON attendance_sessions.subject_id = subjects.subject_id

    WHERE attendance_sessions.is_active=TRUE

    ORDER BY attendance_sessions.session_id DESC
    LIMIT 1
    """

    cur.execute(query)

    session_data = cur.fetchone()

    if not session_data:

        cur.close()

        return redirect('/student/dashboard')

    start_time = session_data[2]
    expiry_time = session_data[3]

    current_time = datetime.now()

    # VALID ACTIVE SESSION

    if not (
        start_time <= current_time <= expiry_time
    ):

        cur.close()

        return redirect('/student/dashboard')

    cur.close()

    return render_template(

        'student/mark_attendance.html',

        subject_name=session_data[4]
    )
# =========================================
# MARK ATTENDANCE
# =========================================

@student.route(
    '/student/attendance/mark',
    methods=['POST']
)
def mark_attendance():

    if 'student_roll' not in session:
        return redirect('/student/login')

    code = request.form['code']

    cur = mysql.connection.cursor()

    # =========================================
    # CHECK SESSION
    # =========================================

    query = """
    SELECT
        session_id,
        subject_id,
        expiry_time,
        is_active
    FROM attendance_sessions
    WHERE code=%s
    """

    cur.execute(query, (code,))

    session_data = cur.fetchone()

    # INVALID CODE

    if not session_data:

        cur.close()

        return """
        <h2 style='text-align:center;margin-top:50px;color:red;'>
            Invalid Attendance Code
        </h2>
        """

    session_id = session_data[0]
    subject_id = session_data[1]
    expiry_time = session_data[2]
    is_active = session_data[3]

    # =========================================
    # SESSION EXPIRED
    # =========================================

    if datetime.now() > expiry_time:

        cur.close()

        return """
        <h2 style='text-align:center;margin-top:50px;color:red;'>
            Attendance Session Expired
        </h2>
        """

    # =========================================
    # SESSION NOT ACTIVE
    # =========================================

    if not is_active:

        cur.close()

        return """
        <h2 style='text-align:center;margin-top:50px;color:red;'>
            Session Not Active
        </h2>
        """

    # =========================================
    # DUPLICATE CHECK
    # =========================================

    query = """
    SELECT *
    FROM attendance_records
    WHERE
        roll_no=%s
    AND
        subject_id=%s
    AND
        attendance_date=CURDATE()
    """

    cur.execute(query, (
        session['student_roll'],
        subject_id
    ))

    existing = cur.fetchone()

    if existing:

        cur.close()

        return """
        <h2 style='text-align:center;margin-top:50px;color:orange;'>
            Attendance Already Marked
        </h2>
        """

    # =========================================
    # MARK PRESENT
    # =========================================

    query = """
    INSERT INTO attendance_records (
        roll_no,
        subject_id,
        attendance_date,
        status
    )
    VALUES (%s, %s, CURDATE(), %s)
    """

    cur.execute(query, (
        session['student_roll'],
        subject_id,
        'Present'
    ))

    mysql.connection.commit()

    cur.close()

    return """
    <h2 style='text-align:center;margin-top:50px;color:green;'>
        Attendance Marked Successfully
    </h2>
    """