# db_handler.py
import sqlite3, pandas as pd
from config import DATA_FILE

def get_conn():
    return sqlite3.connect(DATA_FILE, check_same_thread=False)

def init_db():
    c = get_conn().cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY, company_id INTEGER, project_name TEXT, budget INTEGER,
        FOREIGN KEY(company_id) REFERENCES companies(id));
    CREATE TABLE IF NOT EXISTS costs (
        id INTEGER PRIMARY KEY, project_id INTEGER, week INTEGER, activity TEXT, cost INTEGER,
        FOREIGN KEY(project_id) REFERENCES projects(id));
    """)
    get_conn().commit()

def add_company(name): ...
def get_companies(): ...
def get_company_id(name): ...
def add_project(cid,name,budget): ...
def get_projects(cid): ...
def add_cost(pid,week,activity,cost): ...
def get_costs(pid): ...
