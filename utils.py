# utils.py
def format_currency(val):
    try:
        return f"{int(val):,} kr".replace(",", " ")
    except:
        return f"{val} kr"
