import sqlite3


def create_database():

    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT UNIQUE,

        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        date TEXT,

        score TEXT,

        report TEXT
    )
    """)

    conn.commit()
    conn.close()


def register_user(name, email, password):

    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    try:

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return True

    except:

        conn.close()

        return False


def login_user(email, password):

    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def save_interview(user_id, date, score, report):

    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    cursor.execute(

        "INSERT INTO interviews(user_id,date,score,report) VALUES(?,?,?,?)",

        (user_id, date, score, report)

    )

    conn.commit()

    conn.close()


def get_interviews(user_id):

    conn = sqlite3.connect("interview_history.db")
    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT *
        FROM interviews
        WHERE user_id=?
        ORDER BY id DESC
        """,

        (user_id,)
    )

    data = cursor.fetchall()

    conn.close()

    return data