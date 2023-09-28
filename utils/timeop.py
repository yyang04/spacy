from datetime import datetime


def getTimestampForDawn():
    current_date = datetime.now().date()
    zero_time = datetime.combine(current_date, datetime.min.time())
    timestamp = zero_time.timestamp()
    return timestamp


def getDaysBetweenTimestamp(beginTimeStamp, endTimeStamp):
    dt1 = datetime.fromtimestamp(beginTimeStamp)
    dt2 = datetime.fromtimestamp(endTimeStamp)
    delta = dt2 - dt1
    days = delta.days
    return days
