import pandas as pd

from utils.db import mysql

def generate_subject_attendance_excel(subject_id):

    cur = mysql.connection.cursor()

    # Get Subject Name

    query = """
    SELECT subject_name
    FROM subjects
    WHERE subject_id=%s
    """

    cur.execute(query, (subject_id,))

    subject = cur.fetchone()

    subject_name = subject[0]

    # Get Attendance Data

    query = """
    SELECT
        students.roll_no,
        students.name,
        attendance_records.attendance_date,
        attendance_records.status

    FROM attendance_records

    JOIN students
    ON attendance_records.roll_no = students.roll_no

    WHERE attendance_records.subject_id=%s

    ORDER BY attendance_records.attendance_date
    """

    cur.execute(query, (subject_id,))

    records = cur.fetchall()

    cur.close()

    # Convert to DataFrame

    df = pd.DataFrame(records, columns=[
        'Roll No',
        'Name',
        'Date',
        'Status'
    ])

    if df.empty:

        return None

    # Convert Present/Absent

    df['Status'] = df['Status'].apply(
        lambda x: 'P' if x == 'Present' else 'A'
    )

    # Format Date Column

    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')

    # Pivot Table

    pivot_df = df.pivot_table(
        index=['Roll No', 'Name'],
        columns='Date',
        values='Status',
        aggfunc='first'
).fillna('-')
    # Pivot Table

    pivot_df = df.pivot_table(
        index=['Roll No', 'Name'],
        columns='Date',
        values='Status',
        aggfunc='first'
    ).fillna('-')

    # Calculate Percentage

    attendance_percentage = []

    for index, row in pivot_df.iterrows():

        total_classes = 0
        total_present = 0

        for value in row:

            if value in ['P', 'A']:

                total_classes += 1

            if value == 'P':

                total_present += 1

        percentage = 0

        if total_classes > 0:

            percentage = round(
                (total_present / total_classes) * 100,
                2
            )

        attendance_percentage.append(
            f"{percentage}%"
        )

    pivot_df['Attendance %'] = attendance_percentage

    # Export Path

    file_path = f'exports/{subject_name}.xlsx'

    # Save Excel

    pivot_df.to_excel(file_path)

    return file_path