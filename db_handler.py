import pandas as pd

# Simulerad "databas" som lagrar allt i minnet

companies_df = pd.DataFrame(columns=["id", "name"])
projects_df = pd.DataFrame(columns=["id", "company_id", "project_name", "budget"])
costs_df = pd.DataFrame(columns=["id", "project_id", "week", "activity", "cost"])

def add_company(name):
    global companies_df
    if name in companies_df['name'].values:
        return
    new_id = companies_df['id'].max() + 1 if not companies_df.empty else 1
    companies_df = pd.concat([companies_df, pd.DataFrame([{"id": new_id, "name": name}])], ignore_index=True)

def get_companies():
    return companies_df.copy()

def get_company_id(name):
    row = companies_df[companies_df['name'] == name]
    if not row.empty:
        return int(row.iloc[0]['id'])
    return None

def add_project(company_id, project_name, budget):
    global projects_df
    if project_name in projects_df['project_name'].values:
        return
    new_id = projects_df['id'].max() + 1 if not projects_df.empty else 1
    projects_df = pd.concat([projects_df, pd.DataFrame([{
        "id": new_id,
        "company_id": company_id,
        "project_name": project_name,
        "budget": budget
    }])], ignore_index=True)

def get_projects(company_id):
    return projects_df[projects_df['company_id'] == company_id].copy()

def add_cost(project_id, week, activity, cost):
    global costs_df
    new_id = costs_df['id'].max() + 1 if not costs_df.empty else 1
    costs_df = pd.concat([costs_df, pd.DataFrame([{
        "id": new_id,
        "project_id": project_id,
        "week": week,
        "activity": activity,
        "cost": cost
    }])], ignore_index=True)

def get_costs(project_id):
    return costs_df[costs_df['project_id'] == project_id].copy()
