import pandas as pd
import numpy as np
import os
from datetime import datetime,timedelta
from transformer_lib import volfitter
from transformer_lib import pricer

DATA_ROOT_DIR = '/Volumes/Lacie/china_market/' 

def getExpTimeFromCode( expCode ) :
    expYear = int('20' + expCode[:2])
    expMonth = int(expCode[2:])

    expMonthFirstDay = datetime( expYear,expMonth, 1, 15, 0, 0)
    if expMonthFirstDay.isoweekday() == 7 :
        expTime = expMonthFirstDay + timedelta( days = 5 + 14)
    elif  expMonthFirstDay.isoweekday() == 6 :
        expTime = expMonthFirstDay + timedelta( days = 6 + 14)
    else :
        expTime = expMonthFirstDay + timedelta( days=( 5 - expMonthFirstDay.isoweekday() ) + 14 )
    return expTime
def get_futures_prices( tradeDate, expmonth = 3 ) :
    directory = DATA_ROOT_DIR + 'IO'+tradeDate.strftime('%Y%m%d')+'/'
    fn = 'IF'+datetime(2020, expmonth, 1).strftime('%y%m') + '_' + tradeDate.strftime('%Y%m%d') + '.csv'

    t = pd.read_csv(directory + fn)
    t=t[['markettime','bidprice1','askprice1','bidvolume1','askvolume1']]
    t['tradeTime']=[datetime.strptime( x+'000', '%Y-%m-%d %H:%M:%S.%f') for x in t['markettime']]
    return t

def get_eod_IO_options_raw( tradeDate, month = 3 ):
    
    directory = DATA_ROOT_DIR + 'IO'+tradeDate.strftime('%Y%m%d')+'/'
    call_fns = [] 
    put_fns = [] 
    for filename in os.listdir(directory):
        if (filename.find('-C-') >=0 ):
            call_fns.append(filename)
        elif (filename.find('-P-') >=0 ):
            put_fns.append(filename)
    closeTime = datetime.strptime( tradeDate.strftime('%Y-%m-%d') + ' 15:00:00.000', '%Y-%m-%d %H:%M:%S.%f' )  
    all_t = []
    for fn in call_fns :
        expCode = fn.split( '-')[0]
        expCode = expCode.replace('IO','')
        
        if int( expCode[2:] ) != month :
            continue
            
        t = pd.read_csv(directory + fn)
        t=t[['markettime','bidprice1','askprice1','bidvolume1','askvolume1','volume','openinterest']]
        t['tradeTime']=[datetime.strptime( x+'000', '%Y-%m-%d %H:%M:%S.%f') for x in t['markettime']]
        t=t[t['tradeTime']<closeTime]

        strike_str = fn.split( '-')[2]
        strike = float(strike_str.split('_')[0])
        tt = t[t['tradeTime'] ==t.tradeTime.max()].copy()
        
        tt['Strike'] =strike
        tt['expTime'] = getExpTimeFromCode(expCode)
        tt['optType'] ='C'
        all_t.append(tt)

    for fn in put_fns :
        expCode = fn.split( '-')[0]
        expCode = expCode.replace('IO','')
        if int( expCode[2:] ) != month :
            continue
        t = pd.read_csv(directory + fn)
        t=t[['markettime','bidprice1','askprice1','bidvolume1','askvolume1','volume','openinterest']]
        t['tradeTime']=[datetime.strptime( x+'000', '%Y-%m-%d %H:%M:%S.%f') for x in t['markettime']]
        t=t[t['tradeTime']<closeTime]
        
        strike_str = fn.split( '-')[2]
        strike = float(strike_str.split('_')[0])
        tt = t[t['tradeTime'] ==t.tradeTime.max()].copy()
        tt['Strike'] =strike
        tt['expTime'] = getExpTimeFromCode(expCode)
        tt['optType'] ='P'
        all_t.append(tt)
    allt=pd.concat(all_t)
    return allt

def get_eod_IO_options( tradeDate, month_code=3 ):
    option_d = get_eod_IO_options_raw( tradeDate, month_code )
    fut_d = get_futures_prices( tradeDate, month_code)
    return option_d.merge(fut_d, how='left',on=['tradeTime'],suffixes=('', '_future'))

def get_enriched( snap ) :
    snap['forward'] = (snap['bidprice1_future'] + snap['askprice1_future'])/2
    snap['mid'] = (snap['bidprice1'] + snap['askprice1'])/2
    snap['width'] = snap['askprice1'] - snap['bidprice1']
    snap['ttx'] =[x.total_seconds()/(365.25*24*60*60) for x in snap['expTime']-snap['tradeTime']]
    
    forwards = np.array(snap['forward'].values)
    prices = np.array(snap['mid'].values)
    sks = np.array(snap['Strike'].values)
    ttxs = np.array(snap['ttx'].values)
    optTypes = np.array(snap['optType'].values)
    priceEBs = np.array(snap['width'].values)
    vol_and_ebs = [ pricer.impVol(spot, sk, 0.0, mid, ttx, optType,priceEB) for spot,mid,sk,ttx,optType,priceEB in np.array([forwards,prices,sks,ttxs,optTypes,priceEBs]).transpose()]
    snap['impVol'] = [x['impVol'] for x in vol_and_ebs]
    snap['volErrorBar'] = [x['volErrorBar'] for x in vol_and_ebs]

    vols = [x['impVol'] for x in vol_and_ebs]
    greeks = [ pricer.getGreeks( spot, sk, 0.0, sigma, ttx, optType ) for spot,sk,sigma,ttx,optType in \
              np.array([forwards,sks,vols,ttxs,optTypes]).transpose()]

    snap['delta'] = [x['delta'] for x in greeks]
    snap['theta'] = [x['theta'] for x in greeks]
    snap['vega'] = [x['vega'] for x in greeks]
    snap['gamma'] = [x['gamma'] for x in greeks]
    return snap

def get_IO_eod_enriched( tradeDate, month_code ):
    snap = get_eod_IO_options( tradeDate, month_code )
    return get_enriched( snap )


def get_IO_options_raw( tradeDate, month = 3 ):
    directory = DATA_ROOT_DIR + 'IO'+tradeDate.strftime('%Y%m%d')+'/'
    call_fns = [] 
    put_fns = [] 
    for filename in os.listdir(directory):
        if (filename.find('-C-') >=0 ):
            call_fns.append(filename)
        elif (filename.find('-P-') >=0 ):
            put_fns.append(filename)
    closeTime = datetime.strptime( tradeDate.strftime('%Y-%m-%d') + ' 15:00:00.000', '%Y-%m-%d %H:%M:%S.%f' )  
    all_t = []
    for fn in call_fns :
        expCode = fn.split( '-')[0]
        expCode = expCode.replace('IO','')

        if int( expCode[2:] ) != month :
            continue

        t = pd.read_csv(directory + fn)
        t=t[['markettime','bidprice1','askprice1','bidvolume1','askvolume1','volume','openinterest']]
        t['tradeTime']=[datetime.strptime( x+'000', '%Y-%m-%d %H:%M:%S.%f') for x in t['markettime']]
        t=t[t['tradeTime']<closeTime]

        strike_str = fn.split( '-')[2]
        strike = float(strike_str.split('_')[0])
        tt = t #t[t['tradeTime'] ==t.tradeTime.max()].copy()

        tt['Strike'] = strike
        tt['expTime'] = getExpTimeFromCode(expCode)
        tt['optType'] ='C'
        all_t.append(tt)

    for fn in put_fns :
        expCode = fn.split( '-')[0]
        expCode = expCode.replace('IO','')
        if int( expCode[2:] ) != month :
            continue
        t = pd.read_csv(directory + fn)
        t=t[['markettime','bidprice1','askprice1','bidvolume1','askvolume1','volume','openinterest']]
        t['tradeTime']=[datetime.strptime( x+'000', '%Y-%m-%d %H:%M:%S.%f') for x in t['markettime']]
        t=t[t['tradeTime']<closeTime]

        strike_str = fn.split( '-')[2]
        strike = float(strike_str.split('_')[0])
        tt = t #t[t['tradeTime'] ==t.tradeTime.max()].copy()
        tt['Strike'] = strike
        tt['expTime'] = getExpTimeFromCode(expCode)
        tt['optType'] = 'P'
        all_t.append(tt)
    allt=pd.concat(all_t)
    
    fut_d = get_futures_prices( tradeDate, month )
    fitsecraw = allt.merge(fut_d, how='left',on=['tradeTime'],suffixes=('', '_future'))
    return fitsecraw[['expTime','Strike','optType', 'tradeTime', 'bidprice1','askprice1','bidvolume1', 'askvolume1', 'volume','openinterest','bidprice1_future','askprice1_future','bidvolume1_future','askvolume1_future']]