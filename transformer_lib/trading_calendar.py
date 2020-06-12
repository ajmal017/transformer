import datetime as dt
from transformer_lib import util_funcs
from datetime import timedelta,datetime
import numpy as np

from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
    USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay, \
    USLaborDay, USThanksgivingDay

SPECIAL_HOLIDAYS = [datetime(2018,12,5).date(),
                      datetime(2019,11,29).date()]

HALF_TRADING_DAYS = [datetime(2018, 7, 3).date(),
                     datetime(2018,11,23).date(),
                     datetime(2018,12,24).date(),
                     datetime(2019, 7, 3).date(),
                     datetime(2019,11,29).date(),
                     datetime(2019,12,24).date(),
                     datetime(2020,11,27).date(),
                     datetime(2020,12,24).date()]

class USTradingCalendar( AbstractHolidayCalendar ):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]
    
def get_trading_close_holidays(year):
    inst = USTradingCalendar()
    return inst.holidays(dt.datetime(year-1, 12, 31), dt.datetime(year, 12, 31))


def get_holidays( begin_year, end_year ) :
    holidays = []
    for year in range( begin_year, end_year ) :
        holidays = holidays + list(get_trading_close_holidays(year).values)
    holidays = [ util_funcs.convert_dt64_to_dt(x) for x in holidays ]
    holidays = holidays + SPECIAL_HOLIDAYS
    holidays.sort()
    return holidays

def getTPlusNDate( date, n ) :
    ## this function can be applied for both positive Business days or negative Business days
    holidays = get_holidays( date.year - 2, date.year + 2 )
    if n == 0 :
        return date

    i = 0
    tPlusN = date
    while ( i < abs(n) ) & ( i > -abs(n) ) :
        tPlusN = tPlusN + timedelta(days=1) * n/abs(n)
        if tPlusN.date() in holidays :
            continue
        elif (tPlusN.isoweekday() == 6) | (tPlusN.isoweekday() == 7) :
            continue
        else:
            i = i + n/abs(n)
    return tPlusN
