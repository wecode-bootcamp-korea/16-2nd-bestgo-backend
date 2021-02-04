from datetime import datetime

def get_date(date):
    time = datetime.now()
    if date.day == time.day:
        return str(time.hour - date.hour) + "시간 전"
    elif date.month == time.month:
        return str(time.day - date.day) + "일 전"
    elif date.year == time.year:
        return str(time.month - date.month) + "달 전"