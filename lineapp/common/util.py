def join_with_space(*args):
    return " ".join(filter(None, args))

def join_without_space(*args):
    return "".join(filter(None, args))

def format_currency(value, prefix="¥"):
    return f"{prefix}{value:,.0f}" if value else f"{prefix}0"

def format_date(date, date_format='%Y-%m-%d'):
    return date.strftime(date_format) if date else None

def format_datetime(date, date_format='%Y-%m-%d %H:%M:%S'):
    return date.strftime(date_format) if date else None

def summarize_items(items):
    return ', '.join([f"{item.product_name} x{item.account}" for item in items])
