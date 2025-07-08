# db_handler.py
import sqlite3
import pandas as pd
from config import DATA_FILE

def get_connection():
    return sqlite3.connect(DATA_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Företag
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')
    # Projekt
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        project_name TEXT NOT NULL,
        budget INTEGER NOT NULL,
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )''')
    # Kostnader
    c.execute('''CREATE TABLE IF NOT EXISTS costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        week INTEGER NOT NULL,
        activity TEXT NOT NULL,
        cost INTEGER NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )''')
    conn.commit()
    conn.close()

def add_company(name: str):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO companies (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_companies():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM companies ORDER BY name", conn)
    conn.close()
    return df

def get_company_id(name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM companies WHERE name=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def add_project(company_id: int, name: str, budget: int):
    conn = get_connection()
    conn.execute("INSERT INTO projects (company_id, project_name, budget) VALUES (?, ?, ?)",
                 (company_id, name, budget))
    conn.commit()
    conn.close()

def get_projects(company_id: int):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM projects WHERE company_id=? ORDER BY project_name", conn, params=(company_id,))
    conn.close()
    return df

def add_cost(project_id: int, week: int, activity: str, cost: int):
    conn = get_connection()
    conn.execute("INSERT INTO costs (project_id, week, activity, cost) VALUES (?, ?, ?, ?)",
                 (project_id, week, activity, cost))
    conn.commit()
    conn.close()

def get_costs(project_id: int):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT week, activity, cost FROM costs WHERE project_id=? ORDER BY week", conn,
        params=(project_id,))
    conn.close()
    return df
