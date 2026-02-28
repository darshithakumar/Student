def attendance_percentage(records):
    if not records:
        return 0
    present = sum(1 for r in records if r.present)
    return int((present / len(records)) * 100)
