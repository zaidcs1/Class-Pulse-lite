from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from utils.db import mysql

import random
import string

from datetime import datetime, timedelta

from services.excel_export import (
    generate_subject_attendance_excel
)

attendance = Blueprint('attendance', __name__)

# =========================================
# ATTENDANCE DASHBOARD
# =========================================

@attendance.route('/teacher/attendance')
def attendance_dashboard():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM subjects
    WHERE teacher_id=%s
    """

    cur.execute(query, (
        session['teacher_id'],
    ))

    subjects = cur.fetchall()

    cur.close()

    return render_template(
        'teacher/attendance.html',
        subjects=subjects
    )

# =========================================
# CREATE ATTENDANCE SESSION
# =========================================

@attendance.route(
    '/teacher/attendance/create',
    methods=['POST']
)
def create_attendance_session():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    subject_id = request.form['subject_id']

    # RANDOM CODE

    code = ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=6
        )
    )

    start_time = datetime.now()

    expiry_time = (
        start_time +
        timedelta(seconds=60)
    )

    cur = mysql.connection.cursor()

    query = """
    INSERT INTO attendance_sessions (
        subject_id,
        code,
        start_time,
        expiry_time,
        is_active,
        processed
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cur.execute(query, (

        subject_id,

        code,

        start_time,

        expiry_time,

        True,

        False
    ))

    mysql.connection.commit()

    session_id = cur.lastrowid

    cur.close()

    return redirect(
        f'/teacher/attendance/session/{session_id}'
    )

# =========================================
# LIVE ATTENDANCE SESSION
# =========================================

@attendance.route(
    '/teacher/attendance/session/<int:session_id>'
)
def live_session(session_id):

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    # =========================================
    # SESSION DATA
    # =========================================

    query = """
    SELECT
        attendance_sessions.session_id,
        attendance_sessions.code,
        attendance_sessions.start_time,
        attendance_sessions.expiry_time,
        attendance_sessions.processed,
        subjects.subject_name

    FROM attendance_sessions

    JOIN subjects
    ON attendance_sessions.subject_id = subjects.subject_id

    WHERE attendance_sessions.session_id=%s
    """

    cur.execute(query, (session_id,))

    session_data = cur.fetchone()

    if not session_data:

        cur.close()

        return redirect('/teacher/attendance')

    # =========================================
    # PRESENT COUNT
    # =========================================

    query = """
    SELECT COUNT(*)

    FROM attendance_records

    WHERE subject_id=(

        SELECT subject_id
        FROM attendance_sessions
        WHERE session_id=%s
    )

    AND attendance_date=CURDATE()

    AND status='Present'
    """

    cur.execute(query, (session_id,))

    present_count = cur.fetchone()[0]

    # =========================================
    # TOTAL STUDENTS
    # =========================================

    query = """
    SELECT COUNT(*)
    FROM students
    """

    cur.execute(query)

    total_students = cur.fetchone()[0]

    absent_count = (
        total_students -
        present_count
    )

    # =========================================
    # SESSION STATUS
    # =========================================

    expiry_time = session_data[3]

    processed = session_data[4]

    session_expired = False

    if datetime.now() > expiry_time:

        session_expired = True

        # PROCESS ONLY ONCE

        if not processed:

            mark_absent_students(session_id)

            query = """
            UPDATE attendance_sessions
            SET
                processed=TRUE,
                is_active=FALSE
            WHERE session_id=%s
            """

            cur.execute(query, (session_id,))

            mysql.connection.commit()

            # RECALCULATE ABSENT COUNT

            query = """
            SELECT COUNT(*)

            FROM attendance_records

            WHERE subject_id=(

                SELECT subject_id
                FROM attendance_sessions
                WHERE session_id=%s
            )

            AND attendance_date=CURDATE()

            AND status='Absent'
            """

            cur.execute(query, (session_id,))

            absent_count = cur.fetchone()[0]

    cur.close()

    return render_template(

        'teacher/live_session.html',

        session_data=session_data,

        present_count=present_count,

        absent_count=absent_count,

        session_expired=session_expired
    )

# =========================================
# ATTENDANCE REPORTS
# =========================================

@attendance.route('/teacher/reports')
def attendance_reports():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    # =========================================
    # REPORTS
    # =========================================

    reports_query = """
    SELECT
        attendance_records.id,
        students.roll_no,
        students.name,
        subjects.subject_name,
        attendance_records.attendance_date,
        attendance_records.status

    FROM attendance_records

    JOIN students
    ON attendance_records.roll_no = students.roll_no

    JOIN subjects
    ON attendance_records.subject_id = subjects.subject_id

    ORDER BY attendance_records.attendance_date DESC
    """

    cur.execute(reports_query)

    reports = cur.fetchall()

    # =========================================
    # SUBJECTS
    # =========================================

    subjects_query = """
    SELECT *
    FROM subjects
    WHERE teacher_id=%s
    """

    cur.execute(subjects_query, (
        session['teacher_id'],
    ))

    subjects = cur.fetchall()

    cur.close()

    return render_template(

        'teacher/reports.html',

        reports=reports,

        subjects=subjects
    )

# =========================================
# EXPORT SUBJECT REPORT
# =========================================

@attendance.route(
    '/teacher/reports/export/<int:subject_id>'
)
def export_excel(subject_id):

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    from flask import send_file

    file_path = generate_subject_attendance_excel(
        subject_id
    )

    if file_path is None:

        return """
        <h2>
            No attendance data found.
        </h2>
        """

    return send_file(
        file_path,
        as_attachment=True
    )

# =========================================
# AUTO ABSENT ENGINE
# =========================================

def mark_absent_students(session_id):

    cur = mysql.connection.cursor()

    # =========================================
    # GET SUBJECT ID
    # =========================================

    query = """
    SELECT subject_id
    FROM attendance_sessions
    WHERE session_id=%s
    """

    cur.execute(query, (session_id,))

    session_data = cur.fetchone()

    if not session_data:

        cur.close()
        return

    subject_id = session_data[0]

    # =========================================
    # ALL STUDENTS
    # =========================================

    query = """
    SELECT roll_no
    FROM students
    """

    cur.execute(query)

    all_students = cur.fetchall()

    # =========================================
    # CHECK EACH STUDENT
    # =========================================

    for student in all_students:

        roll_no = student[0]

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

            roll_no,

            subject_id
        ))

        existing = cur.fetchone()

        # =========================================
        # NOT MARKED = ABSENT
        # =========================================

        if not existing:

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

                roll_no,

                subject_id,

                'Absent'
            ))

    mysql.connection.commit()

    cur.close()