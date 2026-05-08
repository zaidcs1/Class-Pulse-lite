from flask import Blueprint, render_template, request, redirect, session, url_for
from utils.db import mysql

auth = Blueprint('auth', __name__)

# =========================================
# TEACHER LOGIN
# =========================================

@auth.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        query = """
        SELECT * FROM teachers
        WHERE username=%s AND password=%s
        """

        cur.execute(query, (username, password))

        teacher = cur.fetchone()

        cur.close()

        if teacher:

            session['teacher_id'] = teacher[0]
            session['teacher_username'] = teacher[1]

            return redirect('/teacher/dashboard')

        return "Invalid Teacher Credentials"

    return render_template('auth/teacher_login.html')

# =========================================
# STUDENT LOGIN
# =========================================

@auth.route('/student/login', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':

        roll_no = request.form['roll_no']
        password = request.form['password']

        cur = mysql.connection.cursor()

        query = """
        SELECT * FROM students
        WHERE roll_no=%s AND password=%s
        """

        cur.execute(query, (roll_no, password))

        student = cur.fetchone()

        cur.close()

        if student:

            session['student_roll'] = student[0]
            session['student_name'] = student[1]

            return redirect('/student/dashboard')

        return "Invalid Student Credentials"

    return render_template('auth/student_login.html')

# =========================================
# LOGOUT
# =========================================

@auth.route('/logout')
def logout():

    session.clear()

    return redirect('/')
# =========================================
# TEACHER REGISTER
# =========================================

@auth.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        query = """
        INSERT INTO teachers (username, password)
        VALUES (%s, %s)
        """

        cur.execute(query, (username, password))

        mysql.connection.commit()

        cur.close()

        return redirect('/teacher/login')

    return render_template('auth/teacher_register.html')
# =========================================
# STUDENT REGISTER
# =========================================

@auth.route('/student/register', methods=['GET', 'POST'])
def student_register():

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

        return redirect('/student/login')

    return render_template('auth/student_register.html')