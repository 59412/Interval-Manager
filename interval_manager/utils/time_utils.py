"""Utility module containing date/time related functions"""
import datetime


def time_displayer(time_to_display: int) -> str:
    """Display time in milliseconds to human readable format"""
    return str(datetime.timedelta(seconds=time_to_display/1000))


def get_current_time():
    """Get current epoch time in milliseconds"""
    return int(datetime.datetime.now().timestamp() * 1000)


def epoch_to_date(epoch_time: int):
    """Convert epoch time in milliseconds to standard datetime format"""
    return datetime.datetime.fromtimestamp(epoch_time/1000)
