-- =========================================
-- CLASS PULSE DATABASE SCHEMA
-- =========================================

CREATE DATABASE IF NOT EXISTS class_pulse;

USE class_pulse;

-- =========================================
-- TABLE: teachers
-- =========================================

CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(50) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- TABLE: students
-- =========================================

CREATE TABLE students (
    roll_no VARCHAR(20) PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    password VARCHAR(255) NOT NULL,

    branch VARCHAR(50) NOT NULL,

    semester INT NOT NULL,

    email VARCHAR(100) UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- TABLE: subjects
-- =========================================

CREATE TABLE subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,

    subject_name VARCHAR(100) NOT NULL,

    teacher_id INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (teacher_id)
    REFERENCES teachers(id)
    ON DELETE CASCADE
);

-- =========================================
-- TABLE: attendance_sessions
-- =========================================

CREATE TABLE attendance_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,

    subject_id INT NOT NULL,

    code VARCHAR(10) UNIQUE NOT NULL,

    start_time DATETIME NOT NULL,

    expiry_time DATETIME NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (subject_id)
    REFERENCES subjects(subject_id)
    ON DELETE CASCADE
);

-- =========================================
-- TABLE: attendance_records
-- =========================================

CREATE TABLE attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,

    roll_no VARCHAR(20) NOT NULL,

    subject_id INT NOT NULL,

    attendance_date DATE NOT NULL,

    status ENUM('Present', 'Absent') NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (roll_no)
    REFERENCES students(roll_no)
    ON DELETE CASCADE,

    FOREIGN KEY (subject_id)
    REFERENCES subjects(subject_id)
    ON DELETE CASCADE
);

-- =========================================
-- PREVENT DUPLICATE ATTENDANCE
-- =========================================

ALTER TABLE attendance_records
ADD CONSTRAINT unique_attendance
UNIQUE (
    roll_no,
    subject_id,
    attendance_date
);

-- =========================================
-- INDEXES FOR PERFORMANCE
-- =========================================

CREATE INDEX idx_student_roll
ON attendance_records(roll_no);

CREATE INDEX idx_subject
ON attendance_records(subject_id);

CREATE INDEX idx_attendance_date
ON attendance_records(attendance_date);

-- =========================================
-- SAMPLE TEACHER DATA
-- =========================================

INSERT INTO teachers (
    username,
    password
)
VALUES
(
    'admin',
    'admin123'
);

-- =========================================
-- SAMPLE STUDENT DATA
-- =========================================

INSERT INTO students (
    roll_no,
    name,
    password,
    branch,
    semester,
    email
)
VALUES
(
    '23CS001',
    'Mohammad Zaid',
    'zaid123',
    'CSE',
    3,
    'zaid@example.com'
),
(
    '23CS002',
    'Aman Sharma',
    'aman123',
    'CSE',
    3,
    'aman@example.com'
);

-- =========================================
-- SAMPLE SUBJECTS
-- =========================================

INSERT INTO subjects (
    subject_name,
    teacher_id
)
VALUES
(
    'Database Management System',
    1
),
(
    'Operating System',
    1
),
(
    'Python Programming',
    1
);