import calendar
from datetime import date, timedelta
import re


def compute_period_key(frequency: str, day: date) -> str:
    if frequency == 'daily':
        return day.isoformat()
    if frequency == 'weekly':
        year, week, _ = day.isocalendar()
        return f'{year:04d}-W{week:02d}'
    if frequency == 'monthly':
        return f'{day.year:04d}-{day.month:02d}'
    raise ValueError('不支持的打卡频率')


def period_bounds(frequency: str, key: str) -> tuple[date, date]:
    try:
        if frequency == 'daily' and re.fullmatch(r'\d{4}-\d{2}-\d{2}', key):
            day = date.fromisoformat(key)
            return day, day
        if frequency == 'weekly' and re.fullmatch(r'\d{4}-W\d{2}', key):
            year, week = key.split('-W')
            return date.fromisocalendar(int(year), int(week), 1), date.fromisocalendar(int(year), int(week), 7)
        if frequency == 'monthly' and re.fullmatch(r'\d{4}-\d{2}', key):
            year, month = map(int, key.split('-'))
            return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    except (ValueError, OverflowError):
        pass
    raise ValueError('period_key 必须是与任务频率匹配的有效日、ISO 周或月份')


def previous_period(frequency, key):
    start, _ = period_bounds(frequency, key)
    return compute_period_key(frequency, start - timedelta(days=1))


def streak_from_keys(keys, frequency, key):
    count = 0
    while key in keys:
        count += 1
        try:
            key = previous_period(frequency, key)
        except (ValueError, OverflowError):
            break
    return count


def check_task_period(task, key):
    start, end = period_bounds(task.frequency, key)
    if end < task.start_date or (task.end_date is not None and start > task.end_date):
        raise ValueError('该周期不在任务有效日期内')
    return start, end
