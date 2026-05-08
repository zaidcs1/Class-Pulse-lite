from flask import Blueprint, render_template, session, redirect
import pymysql
from utils.db import mysql
# pymysql.install_as_MySQLdb()
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    request
)

teacher = Blueprint('teacher', __name__)

# =========================================
# TEACHER DASHBOARD for viewing
# =========================================

@teacher.route('/teacher/dashboard')
def dashboard():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    # Total Subjects
    cur.execute("SELECT COUNT(*) FROM subjects WHERE teacher_id=%s", (session['teacher_id'],))
    total_subjects = cur.fetchone()[0]

    # Total Attendance Records
    cur.execute("SELECT COUNT(*) FROM attendance_records")
    total_attendance = cur.fetchone()[0]

    cur.close()

    return render_template(
        'teacher/dashboard.html',
        total_students=total_students,
        total_subjects=total_subjects,
        total_attendance=total_attendance
    )
# =========================================
# VIEW STUDENTS
# =========================================

@teacher.route('/teacher/students')
def students():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM students
    ORDER BY created_at DESC
    """

    cur.execute(query)

    students = cur.fetchall()

    cur.close()

    return render_template(
        'teacher/students.html',
        students=students
    )
# =========================================
# ADD STUDENT
# =========================================

@teacher.route('/teacher/students/add', methods=['GET', 'POST'])
def add_student():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    if request.method == 'POST':

        roll_no = request.form['roll_no']
        name = request.form['name']
        password = request.form['password']
        branch = request.form['branch']
        semester = request.form['semester']
        email = request.form['email']

        cur = mysql.connection.cursor()

        query = """
        INSERT INTO students (
            roll_no,
            name,
            password,
            branch,
            semester,
            email
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            roll_no,
            name,
            password,
            branch,
            semester,
            email
        ))

        mysql.connection.commit()

        cur.close()

        return redirect('/teacher/students')

    return render_template('teacher/add_student.html')
# =========================================
# EDIT STUDENT
# =========================================

@teacher.route('/teacher/students/edit/<roll_no>', methods=['GET', 'POST'])
def edit_student(roll_no):

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        name = request.form['name']
        branch = request.form['branch']
        semester = request.form['semester']
        email = request.form['email']

        query = """
        UPDATE students
        SET
            name=%s,
            branch=%s,
            semester=%s,
            email=%s
        WHERE roll_no=%s
        """

        cur.execute(query, (
            name,
            branch,
            semester,
            email,
            roll_no
        ))

        mysql.connection.commit()

        cur.close()

        return redirect('/teacher/students')

    query = """
    SELECT *
    FROM students
    WHERE roll_no=%s
    """

    cur.execute(query, (roll_no,))

    student = cur.fetchone()

    cur.close()

    return render_template(
        'teacher/edit_student.html',
        student=student
    )
# =========================================
# DELETE STUDENT
# =========================================

@teacher.route('/teacher/students/delete/<roll_no>')
def delete_student(roll_no):

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    query = """
    DELETE FROM students
    WHERE roll_no=%s
    """

    cur.execute(query, (roll_no,))

    mysql.connection.commit()

    cur.close()

    return redirect('/teacher/students')
# =========================================
# VIEW SUBJECTS
# =========================================

@teacher.route('/teacher/subjects')
def subjects():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    query = """
    SELECT
        subjects.subject_id,
        subjects.subject_name,
        teachers.username
    FROM subjects
    JOIN teachers
    ON subjects.teacher_id = teachers.id
    ORDER BY subjects.created_at DESC
    """

    cur.execute(query)

    subjects = cur.fetchall()

    cur.close()

    return render_template(
        'teacher/subjects.html',
        subjects=subjects
    )
# =========================================
# ADD SUBJECT
# =========================================

@teacher.route('/teacher/subjects/add', methods=['GET', 'POST'])
def add_subject():

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    if request.method == 'POST':

        subject_name = request.form['subject_name']

        teacher_id = session['teacher_id']

        cur = mysql.connection.cursor()

        query = """
        INSERT INTO subjects (
            subject_name,
            teacher_id
        )
        VALUES (%s, %s)
        """

        cur.execute(query, (
            subject_name,
            teacher_id
        ))

        mysql.connection.commit()

        cur.close()

        return redirect('/teacher/subjects')

    return render_template('teacher/add_subject.html')
# =========================================
# DELETE SUBJECT
# =========================================

@teacher.route('/teacher/subjects/delete/<int:subject_id>')
def delete_subject(subject_id):

    if 'teacher_id' not in session:
        return redirect('/teacher/login')

    cur = mysql.connection.cursor()

    query = """
    DELETE FROM subjects
    WHERE subject_id=%s
    """

    cur.execute(query, (subject_id,))

    mysql.connection.commit()

    cur.close()

    return redirect('/teacher/subjects')