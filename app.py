import streamlit as st
import sqlite3
import pandas as pd
import os

# ---------------------
# DATABASE SETUP
# ---------------------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    role TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    instructor TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    content TEXT,
                    file_path TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    course_id INTEGER,
                    progress INTEGER)''')

create_tables()

# ---------------------
# AUTH FUNCTIONS
# ---------------------
def add_user(username, password, role):
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              (username, password, role))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, password))
    return c.fetchone()

# ---------------------
# COURSE FUNCTIONS
# ---------------------
def add_course(title, instructor):
    c.execute("INSERT INTO courses (title, instructor) VALUES (?, ?)",
              (title, instructor))
    conn.commit()

def get_courses():
    c.execute("SELECT * FROM courses")
    return c.fetchall()

def add_lesson(course_id, content, file_path):
    c.execute("INSERT INTO lessons (course_id, content, file_path) VALUES (?, ?, ?)",
              (course_id, content, file_path))
    conn.commit()

def get_lessons(course_id):
    c.execute("SELECT * FROM lessons WHERE course_id=?", (course_id,))
    return c.fetchall()

def enroll(username, course_id):
    c.execute("INSERT INTO enrollments (username, course_id, progress) VALUES (?, ?, 0)",
              (username, course_id))
    conn.commit()

def get_enrollments(username):
    c.execute("SELECT * FROM enrollments WHERE username=?", (username,))
    return c.fetchall()

def update_progress(username, course_id, progress):
    c.execute("UPDATE enrollments SET progress=? WHERE username=? AND course_id=?",
              (progress, username, course_id))
    conn.commit()

# ---------------------
# UI
# ---------------------
st.title("🎓 HealthLearn MVP")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------------
# SIGNUP
# ---------------------
if choice == "Sign Up":
    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    role = st.selectbox("Role", ["student", "instructor"])

    if st.button("Sign Up"):
        add_user(username, password, role)
        st.success("Account created!")

# ---------------------
# LOGIN
# ---------------------
if choice == "Login":
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        user = login_user(username, password)

        if user:
            st.success(f"Welcome {username} ({user[3]})")

            # ---------------------
            # INSTRUCTOR PANEL
            # ---------------------
            if user[3] == "instructor":
                st.header("Instructor Dashboard")

                st.subheader("Create Course")
                course_title = st.text_input("Course Title")

                if st.button("Create"):
                    add_course(course_title, username)
                    st.success("Course created")

                courses = get_courses()

                st.subheader("Add Lesson")
                course_ids = [c[0] for c in courses]
                selected_course = st.selectbox("Course ID", course_ids)

                lesson_text = st.text_area("Lesson Content")
                uploaded_file = st.file_uploader("Upload file")

                file_path = None
                if uploaded_file:
                    file_path = os.path.join("uploads", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                if st.button("Add Lesson"):
                    add_lesson(selected_course, lesson_text, file_path)
                    st.success("Lesson added")

            # ---------------------
            # STUDENT PANEL
            # ---------------------
            else:
                st.header("Student Dashboard")

                courses = get_courses()

                st.subheader("Available Courses")
                for course in courses:
                    st.write(course)

                    if st.button(f"Enroll {course[0]}"):
                        enroll(username, course[0])
                        st.success("Enrolled!")

                st.subheader("My Courses")
                enrollments = get_enrollments(username)

                for e in enrollments:
                    st.write(f"Course ID: {e[2]} | Progress: {e[3]}%")

                    lessons = get_lessons(e[2])

                    for lesson in lessons:
                        st.write(lesson[2])

                        if lesson[3]:
                            st.download_button("Download File", open(lesson[3], "rb"))

                    if st.button(f"Mark Complete {e[2]}"):
                        update_progress(username, e[2], 100)
                        st.success("Progress updated!")

        else:
            st.error("Invalid login")
