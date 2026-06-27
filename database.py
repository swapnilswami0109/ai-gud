import sqlite3
from pathlib import Path

DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)

DATABASE = DB_DIR / "guardian.db"


def get_connection():
    conn = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    # ---------------- Users ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        email TEXT UNIQUE,

        password TEXT,

        role TEXT DEFAULT 'Developer',

        organization TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Projects ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS projects(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        description TEXT,

        owner TEXT,

        compliance REAL DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Datasets ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS datasets(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        project_id INTEGER,

        filename TEXT,

        rows INTEGER,

        columns INTEGER,

        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Models ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS models(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        project_id INTEGER,

        model_name TEXT,

        version TEXT,

        framework TEXT,

        accuracy REAL,

        fairness REAL,

        privacy REAL,

        explainability REAL,

        compliance REAL,

        model_path TEXT,

        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Reports ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS reports(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        project_id INTEGER,

        report_name TEXT,

        report_type TEXT,

        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Certificates ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS certificates(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        project_id INTEGER,

        certificate_id TEXT,

        score REAL,

        status TEXT,

        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Audit Logs ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS audit_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        action TEXT,

        severity TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # ---------------- Model Promotions / Approvals ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS model_promotions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        model_name TEXT,

        version TEXT,

        run_id TEXT,

        requested_by TEXT,

        requested_stage TEXT,

        status TEXT DEFAULT 'pending',

        approved_by TEXT,

        approved_at TIMESTAMP,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.commit()

    conn.close()


initialize_database()