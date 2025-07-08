def format_currency(val):
    return f"{val:,.0f} kr"

def validate_project_name(name):
    return bool(name and len(name) > 2)

