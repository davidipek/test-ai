import sqlite3
import pandas as pd

DB_NAME = 'data/budgetkoll.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            project_name TEXT,
            budget INTEGER,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            week INTEGER,
            activity TEXT,
            cost INTEGER,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_company(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO companies (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Company exists
    conn.close()

def get_companies():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query('SELECT * FROM companies', conn)
    conn.close()
    return df

def get_company_id(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM companies WHERE name = ?', (name,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def add_project(company_id, project_name, budget):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO projects (company_id, project_name, budget) VALUES (?, ?, ?)', 
              (company_id, project_name, budget))
    conn.commit()
    conn.close()

def get_projects(company_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM projects WHERE company_id={company_id}", conn)
    conn.close()
    return df

def add_cost(project_id, week, activity, cost):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO costs (project_id, week, activity, cost) VALUES (?, ?, ?, ?)', 
              (project_id, week, activity, cost))
    conn.commit()
    conn.close()

def get_costs(project_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM costs WHERE project_id={project_id} ORDER BY week", conn)
    conn.close()
    return df
