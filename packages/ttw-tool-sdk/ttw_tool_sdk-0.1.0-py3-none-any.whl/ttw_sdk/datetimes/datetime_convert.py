import datetime
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
from zoneinfo import ZoneInfo


class TimeZoneNameEnum(Enum):
    UTC = 'UTC'
    AsiaShanghai = 'Asia/Shanghai'


def local_datetime_info():
    """本机时区信息"""

    @dataclass
    class TimeZoneInfo:
        # utc 时间偏移. eg: -28800 (UTC时区 - 本机时区)
        utc_offset: int
        # 时区名称元祖, 第一个元素为标准时区名称, 第二个元素为夏令时名称. eg: ('中国标准时间', '中国夏令时')
        tz_tuple: tuple

    time_zone_info = TimeZoneInfo(
        utc_offset=time.timezone,
        tz_tuple=time.tzname
    )
    return time_zone_info


def local_timezone() -> datetime.timezone:
    return datetime.timezone(offset=datetime.timedelta(seconds=-time.timezone))


def local_datetime() -> datetime.datetime:
    return datetime.datetime.now(local_timezone())


def cst_datetime():
    cst_tz = ZoneInfo('Asia/Shanghai')
    return datetime.datetime.now(cst_tz)


def utc_datetime():
    utc_tz = ZoneInfo('UTC')
    return datetime.datetime.now(utc_tz)


def datetime_to_string(dt: datetime.datetime, fmt: str = '%Y-%m-%dT%H:%M:%S.%f%z'):
    return dt.strftime(fmt).strip()


def string_to_datetime(s: str, fmt: str = '%Y-%m-%dT%H:%M:%S.%f%z') -> datetime.datetime:
    return datetime.datetime.strptime(s, fmt)


def string_to_datetime_auto_try(
        s: str, fmt: str = '%Y-%m-%dT%H:%M:%S.%f%z'
) -> Optional[datetime.datetime]:
    fmt_list = [
        fmt,
        # 2022-03-29T02:19:49.000 CST+0800
        '%Y-%m-%dT%H:%M:%S.%f%z',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H',
        '%Y-%m-%d',
        '%H:%M:%S',
        '%H:%M',
        # 03/29/2024 02:19:49 AM
        "%m/%d/%Y %I:%M:%S %p",
    ]
    if 'T' in s:
        try:
            return datetime.datetime.fromisoformat(s)
        except ValueError:
            pass
    for f in fmt_list:
        try:
            return datetime.datetime.strptime(s, f)
        except ValueError as e:
            pass
    return


def format_seconds(
        seconds: int,
        fmt: str = '{d}天{h}小时{m}分钟{s}秒',
        max_level: int = 4
) -> Tuple[str, Tuple[int, int, int, int]]:
    if max_level < 1 or max_level > 4:
        raise ValueError('max_level must be between 1 and 4')
    if seconds < 0:
        raise ValueError('seconds must be a positive integer')
    d, h, m, s = 0, 0, 0, seconds
    if max_level == 2:
        m, s = seconds // 60, seconds % 60
    if max_level == 3:
        h, m, s = seconds // 3600, seconds // 60 % 60, seconds % 60
    if max_level == 4:
        d, h, m, s = seconds // 86400, seconds // 3600 % 24, seconds // 60 % 60, seconds % 60
    fmt_str = fmt.format(d=d, h=h, m=m, s=s)
    return fmt_str, (d, h, m, s)


def day_start_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(dt, datetime.time.min)


def day_end_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(dt, datetime.time.max)


def month_start_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(dt.date().replace(day=1), datetime.time.min)


def month_end_datetime(dt: datetime.datetime) -> datetime.datetime:
    next_month = dt.date().replace(day=28) + datetime.timedelta(days=4)
    return datetime.datetime.combine(next_month - datetime.timedelta(days=next_month.day), datetime.time.max)


def next_month_start_datetime(dt: datetime.datetime) -> datetime.datetime:
    next_month = dt.date().replace(day=1) + datetime.timedelta(days=32)
    return datetime.datetime.combine(next_month.replace(day=1), datetime.time.min)


def next_month_end_datetime(dt: datetime.datetime) -> datetime.datetime:
    next_month = dt.date().replace(day=1) + datetime.timedelta(days=64)
    return datetime.datetime.combine(next_month - datetime.timedelta(days=next_month.day), datetime.time.max)


def year_start_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(dt.date().replace(month=1, day=1), datetime.time.min)


def year_end_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(dt.date().replace(month=12, day=31), datetime.time.max)


def weekday_start_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(dt - datetime.timedelta(days=dt.weekday()), datetime.time.min)


def weekday_end_datetime(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(
        dt - datetime.timedelta(days=dt.weekday()) + datetime.timedelta(days=6),
        datetime.time.max
    )


def day_offset_monday(dt: datetime.datetime) -> int:
    # 0-6: 周一到周日
    return dt.weekday()


def days_count_of_month(year: int = None, month: int = None) -> int:
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    dt = datetime.datetime(year, month, 1)

    ms = datetime.datetime.combine(dt.date().replace(day=1), datetime.time.min)
    next_month = dt.date().replace(day=28) + datetime.timedelta(days=4)
    me = datetime.datetime.combine(next_month - datetime.timedelta(days=next_month.day), datetime.time.max)
    return (me - ms).days + 1


def month_calendar(year: int = None, month: int = None) -> list:
    """
    输出指定年月的日历
    :param year: 年份
    :param month: 月份
    :return: 日历列表，每个元素为一个列表，代表一周的日期
    """
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    days = days_count_of_month(year, month)
    calendar = [[None for _ in range(7)]]
    for i in range(1, days + 1):
        dt = datetime.datetime(year, month, i)
        if dt.weekday() == 0 and i > 1:
            calendar.append([None for _ in range(7)])
        calendar[-1][dt.weekday()] = dt
    return calendar

# now =local_datetime()
#
# print(month_calendar(now.year, now.month))
#

# now = datetime.datetime.now()
# print(now)
# # print(day_start_datetime(now))
# # print(day_end_datetime(now))
# # print(month_start_datetime(now))
# # print(month_end_datetime(now))
# # print(next_month_start_datetime(now))
# # print(next_month_end_datetime(now))
# # print(year_start_datetime(now))
# # print(year_end_datetime(now))
# # s = datetime_to_string(cst_datetime())
# # print(s)
# # print(cst_datetime().isoformat())
# # print(cst_datetime())
# # print(string_to_datetime_auto_try(
# #     cst_datetime().isoformat()
# # ))
#
# print(weekday_start_datetime(now + datetime.timedelta(days=-0)))
# print(weekday_end_datetime(now + datetime.timedelta(days=-0)))
# print(day_offset_monday(now))
# print((now + datetime.timedelta(days=2)).weekday())
# print(days_count_of_month())
# print(month_calendar())
