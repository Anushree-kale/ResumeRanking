import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL configuration from environment variables
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as e:
        raise Exception(f"Failed to connect to MySQL: {str(e)}")

def init_db():
    """Sets up the MySQL database schema and populates it with initial data."""
    conn = get_db_connection()
    c = conn.cursor()

    # Users table: Stores recruiter credentials
    c.execute('''CREATE TABLE IF NOT EXISTS Users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL)''')

    # Job_Roles table: Stores predefined job roles
    c.execute('''CREATE TABLE IF NOT EXISTS Job_Roles (
                    job_role_id INT AUTO_INCREMENT PRIMARY KEY,
                    job_role_name VARCHAR(100) UNIQUE NOT NULL)''')

    # Job_Role_Keywords table: Stores keywords and weights
    c.execute('''CREATE TABLE IF NOT EXISTS Job_Role_Keywords (
                    job_keyword_id INT AUTO_INCREMENT PRIMARY KEY,
                    job_role_id INT,
                    keyword VARCHAR(50) NOT NULL,
                    weight INT NOT NULL,
                    FOREIGN KEY (job_role_id) REFERENCES Job_Roles(job_role_id))''')

    # Resumes table: Stores uploaded resume details
    c.execute('''CREATE TABLE IF NOT EXISTS Resumes (
                    resume_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    file_name VARCHAR(255) NOT NULL,
                    text_content TEXT,
                    upload_date DATETIME,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id))''')

    # Ranking_Sessions table: Tracks ranking attempts
    c.execute('''CREATE TABLE IF NOT EXISTS Ranking_Sessions (
                    session_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    session_type ENUM('job_role', 'description') NOT NULL,
                    job_role_id INT,
                    description TEXT,
                    created_date DATETIME,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id),
                    FOREIGN KEY (job_role_id) REFERENCES Job_Roles(job_role_id))''')

    # Resume_Rankings table: Stores resume scores
    c.execute('''CREATE TABLE IF NOT EXISTS Resume_Rankings (
                    resume_ranking_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT,
                    resume_id INT,
                    rank_score FLOAT,
                    FOREIGN KEY (session_id) REFERENCES Ranking_Sessions(session_id),
                    FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id))''')

    # Large dictionary of sample job roles with weighted keywords
    sample_roles = [
        ("Data Scientist", [
            ("python", 5), ("machine learning", 4), ("sql", 3), ("statistics", 2),
            ("data analysis", 3), ("pandas", 2), ("tensorflow", 2), ("deep learning", 3)
        ]),
        ("Web Developer", [
            ("javascript", 5), ("html", 4), ("css", 3), ("react", 2),
            ("node.js", 3), ("angular", 2), ("typescript", 2), ("bootstrap", 1)
        ]),
        ("Project Manager", [
            ("management", 5), ("communication", 4), ("agile", 3), ("leadership", 2),
            ("scrum", 3), ("planning", 2), ("teamwork", 2), ("budgeting", 1)
        ]),
        ("Software Engineer", [
            ("java", 5), ("c++", 4), ("python", 3), ("git", 2),
            ("algorithms", 3), ("data structures", 3), ("oop", 2), ("testing", 1)
        ]),
        ("DevOps Engineer", [
            ("docker", 5), ("aws", 4), ("linux", 3), ("ci/cd", 3),
            ("kubernetes", 3), ("jenkins", 2), ("terraform", 2), ("bash", 1)
        ])
    ]

    # Insert sample job roles and keywords
    for role_name, keywords in sample_roles:
        c.execute("INSERT IGNORE INTO Job_Roles (job_role_name) VALUES (%s)", (role_name,))
        c.execute("SELECT job_role_id FROM Job_Roles WHERE job_role_name = %s", (role_name,))
        job_role_id = c.fetchone()[0]
        for keyword, weight in keywords:
            c.execute("INSERT IGNORE INTO Job_Role_Keywords (job_role_id, keyword, weight) VALUES (%s, %s, %s)",
                      (job_role_id, keyword, weight))

    conn.commit()
    conn.close()

# User management functions
def add_user(username, password_hash):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
    except mysql.connector.IntegrityError:
        raise ValueError("Username already exists!")
    finally:
        conn.close()

def get_user(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, password_hash FROM Users WHERE username = %s", (username,))
    user = c.fetchone()
    conn.close()
    return user

# Resume management
def add_resume(user_id, file_name, text_content):
    conn = get_db_connection()
    c = conn.cursor()
    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO Resumes (user_id, file_name, text_content, upload_date) VALUES (%s, %s, %s, %s)",
              (user_id, file_name, text_content, upload_date))
    conn.commit()
    c.execute("SELECT LAST_INSERT_ID()")
    resume_id = c.fetchone()[0]
    conn.close()
    return resume_id

# Ranking session management
def create_ranking_session(user_id, session_type, job_role_id=None, description=None):
    conn = get_db_connection()
    c = conn.cursor()
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO Ranking_Sessions (user_id, session_type, job_role_id, description, created_date) VALUES (%s, %s, %s, %s, %s)",
              (user_id, session_type, job_role_id, description, created_date))
    conn.commit()
    c.execute("SELECT LAST_INSERT_ID()")
    session_id = c.fetchone()[0]
    conn.close()
    return session_id

def add_ranking(session_id, resume_id, rank_score):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Resume_Rankings (session_id, resume_id, rank_score) VALUES (%s, %s, %s)",
              (session_id, resume_id, rank_score))
    conn.commit()
    conn.close()

# Data retrieval
def get_job_roles():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT job_role_name FROM Job_Roles")
    roles = [row[0] for row in c.fetchall()]
    conn.close()
    return roles

def get_keywords_for_role(job_role_name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT keyword, weight FROM Job_Role_Keywords WHERE job_role_id = (SELECT job_role_id FROM Job_Roles WHERE job_role_name = %s)",
              (job_role_name,))
    keywords = c.fetchall()
    conn.close()
    return keywords

def get_resumes_for_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT resume_id, file_name, text_content FROM Resumes WHERE user_id = %s", (user_id,))
    resumes = c.fetchall()
    conn.close()
    return resumes

def get_rankings(session_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT r.file_name, rr.rank_score FROM Resume_Rankings rr JOIN Resumes r ON rr.resume_id = r.resume_id WHERE rr.session_id = %s",
              (session_id,))
    rankings = c.fetchall()
    conn.close()
    return rankings

if __name__ == "__main__":
    init_db()