from datetime import datetime

def calculate_year(batch_year, override=None):
    if override:
        return override
    return min(max(datetime.now().year - batch_year + 1, 1), 4)
