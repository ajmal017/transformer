import os
import numpy as np
import pandas as pd
from transformer_lib import trading_calendar
from transformer_lib import european_pricer
from transformer_lib import pricer
from transformer_lib import constants
from transformer_lib import combostrategy
from datetime import datetime
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression

MINUTEBAR_LOCAL_ROOT='/Volumes/LaCie/optiondata_minutebar/'
MINUTEBAR_ALGOSEEK_PREFIX = 's3://us-options-1min-taq-'

def option_minutebar_local_dir( day, ticker ) :
    return MINUTEBAR_LOCAL_ROOT+day.strftime('%Y%m%d')+'/'+ticker[0]+'/'+ticker+'/'

def option_minutebar_remote_dir( day, ticker ) :
    return MINUTEBAR_ALGOSEEK_PREFIX+str(day.year)+'/'+day.strftime('%Y%m%d')+'/'+ticker[0]+'/'+ticker+'/'

def convert_dt64_to_dt( dt64 ):
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
    return datetime.utcfromtimestamp(ts).date()

def date_string_to_datetime( date_string) :
    return datetime.strptime(date_string, '%Y-%m-%d')

def get_vx_futures_hist():
    directory = 'futures_data/VX/'
    filenames = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filenames.append(filename)
        
    dfs = []
    for fn in filenames :
        df = pd.read_csv('futures_data/VX/' + fn)
        df['FutureDate'] = date_convert( fn.split('.')[0])
        dfs.append(df)
        
    futures_data = pd.concat(dfs)
    futures_data.reset_index( inplace = True)
    futures_data.drop(columns=['index'],inplace=True)
    futures_data['TradeDate'] = [ date_convert( x ) for x in futures_data['Trade Date'] ]
    return futures_data

def get_daily_stock_data( ticker, period ) :
    stock_obj = yf.Ticker( ticker )
    stock_data = stock_obj.history( period = period )
    return stock_data.reset_index()

def regress_xy( x, y ):
    X = np.array([x]).transpose()
    reg = LinearRegression(fit_intercept=True).fit(X, y)
    return { 'intercept': reg.intercept_, 'coef': reg.coef_[0], 'score': reg.score(X, y)}

def get_minutebar_raw_expiry( ticker, date, expiry, usecols = [] ) :
    directory = option_minutebar_local_dir( date, ticker )
    fn = ticker + '.' + expiry.strftime('%Y%m%d') + '.csv.gz'
    if len(usecols)>0 :
        return pd.read_csv(directory+fn, dtype = constants.MINUTE_BAR_DTYPE, usecols = usecols )
    else :
        return pd.read_csv(directory+fn, dtype = constants.MINUTE_BAR_DTYPE )

def get_minutebar_raw_symbol( ticker, date, usecols = [] ):
    directory = option_minutebar_local_dir( date, ticker )
    filenames = []
    if ticker == 'VXX' :
        for filename in os.listdir(directory):
            if ((date >=datetime(2018,11,1)) & (date<=datetime(2019,5,1))):
                if (filename.endswith(".gz") & filename.startswith("VXXB")) :
                    filenames.append(filename)
            else :
                if filename.endswith(".gz") & filename.startswith("VXX.") :
                    filenames.append(filename)
    else :
        for filename in os.listdir(directory):
            if filename.endswith(".gz") :
                filenames.append(filename)
         
    dfs = []
    for fn in filenames :
        try :
            if len(usecols)>0 :
                dfs.append(pd.read_csv(directory+fn, dtype = constants.MINUTE_BAR_DTYPE, usecols = usecols ))
            else :
                dfs.append(pd.read_csv(directory+fn, dtype = constants.MINUTE_BAR_DTYPE ))
        except :
            print( 'failed to read file - ', directory, ' ',fn )
            continue
            
    res = pd.concat(dfs)
    res.reset_index(drop=True, inplace=True)
    return res


def get_close_snap_raw_symbol( ticker, date ):
    date_str = date.strftime('%Y%m%d')
    directory = option_minutebar_local_dir( date, ticker )
    filenames = []
    if ticker == 'VXX' :
        for filename in os.listdir(directory):
            if ((date >=datetime(2018,11,1)) & (date<=datetime(2019,5,1))):
                if (filename.endswith(".gz") & filename.startswith("VXXB")) :
                    filenames.append(filename)
            else :
                if filename.endswith(".gz") & filename.startswith("VXX.") :
                    filenames.append(filename)
    else :
        for filename in os.listdir(directory):
            if filename.endswith(".gz") :
                filenames.append(filename)
        
                
    openSnaps = []
    for fn in filenames :
        try :
            df=pd.read_csv(directory+fn, dtype = constants.MINUTE_BAR_DTYPE )
        except :
            print( 'failed to read file - ', directory, ' ',fn )
            continue
        if date.date() in trading_calendar.HALF_TRADING_DAYS :
            close_mark = '12:59'
        else :
            close_mark = '15:59'
            
        openSnap=df[df.TimeBarStart==close_mark].copy()
        openSnap=openSnap[['TimeBarStart','ExpirationDate','CallPut','Strike',
                               'OpenBidPrice','OpenAskPrice', 'UnderOpenBidPrice', 'UnderOpenAskPrice']]
        openSnap['Date'] = date
        openSnap['ExpirationDate'] = [ datetime.strptime( str( x), '%Y%m%d' ) for x in openSnap['ExpirationDate'] ]
        openSnaps.append( openSnap)
        
    openSnapSymbol = pd.concat(openSnaps)
    openSnapSymbol.reset_index(drop=True, inplace=True)
    return openSnapSymbol

                
def get_close_snap_raw_term( ticker, date, expiration ) :
    date_str = date.strftime('%Y%m%d')
    exp_str = expiration.strftime('%Y%m%d')
    directory = 'data/options/minute_bars/'+date_str+'/'+ ticker[0]  +'/'+ ticker +'/'
    ticker_use = ticker
    if ((ticker == 'VXX') & (date >=datetime(2018,11,1)) & (date<=datetime(2019,5,1))):
        ticker_use = 'VXXB'
    fn = ticker_use + '.' + exp_str + '.csv.gz'
    termSnap = pd.read_csv(directory+fn, dtype = constants.MINUTE_BAR_DTYPE )
    if date.date() in trading_calendar.HALF_TRADING_DAYS :
        close_mark = '12:59'
    else :
        close_mark = '15:59'
    termSnap=termSnap[termSnap.TimeBarStart==close_mark]
    return termSnap

def get_close_snap_raw_option( ticker, date, expiration, optType, strike ):
    term_snap = get_close_snap_raw_term( ticker, date, expiration )
    return term_snap[ (term_snap[ 'Strike' ] == strike) & (term_snap['CallPut'] == optType)] 

def get_close_snap_symbol( ticker, date ) :
    openSnapSymbol = get_close_snap_raw_symbol(ticker, date)
    
    ## minimum fill and derived columns:
    openSnapSymbol.fillna(value={'OpenBidPrice': 0}, inplace=True)
    openSnapSymbol['mid'] = 0.5*(openSnapSymbol.OpenBidPrice+openSnapSymbol.OpenAskPrice)
    openSnapSymbol['spot'] = 0.5*(openSnapSymbol.UnderOpenBidPrice+openSnapSymbol.UnderOpenAskPrice)
    openSnapSymbol['width'] = openSnapSymbol.OpenAskPrice-openSnapSymbol.OpenBidPrice
    openSnapSymbol['cycleTime']= datetime.strptime(date.strftime('%Y%m%d')+' 16:00:00','%Y%m%d %H:%M:%S')
    openSnapSymbol['ExpirationTime']=[datetime.strptime(x.strftime('%Y%m%d')+' 16:00:00','%Y%m%d %H:%M:%S') for x in openSnapSymbol['ExpirationDate']]
    openSnapSymbol['ttx_in_days'] = [ x.days for x in (openSnapSymbol['ExpirationDate']-openSnapSymbol['Date'])]
    openSnapSymbol['ttx'] =[x.total_seconds()/(365.25*24*60*60) for x in openSnapSymbol['ExpirationTime']- openSnapSymbol['cycleTime']]
    return openSnapSymbol
    

def get_greeks( s, x, r, sigma, t, optType ):
    ep = european_pricer.european_pricer( s, x, r, sigma, t, optType )
    return ep.greeks()

def enrich_vol_greeks( t ) :
    spots = np.array(t['spot'].values)
    prices = np.array(t['mid'].values)
    sks = np.array(t['Strike'].values)
    ttxs = np.array(t['ttx'].values)
    optTypes = np.array(t['CallPut'].values)
    priceEBs = np.array(t['width'].values)
    vol_and_ebs = [ pricer.impVol(spot, sk, 0.01, mid, ttx, optType,priceEB) for spot,mid,sk,ttx,optType,priceEB in np.array([spots,prices,sks,ttxs,optTypes,priceEBs]).transpose()]
    t['impVol'] = [x['impVol'] for x in vol_and_ebs]
    t['volErrorBar'] = [x['volErrorBar'] for x in vol_and_ebs]

    vols = [x['impVol'] for x in vol_and_ebs]
       
#    greeks = [ pricer.getGreeks( spot, sk, 0.01, sigma, ttx, optType ) for spot,sk,sigma,ttx,optType in \
#              np.array([spots,sks,vols,ttxs,optTypes]).transpose()]

    greeks = [ get_greeks( spot, sk, 0.01, sigma, ttx, optType ) for spot,sk,sigma,ttx,optType in \
              np.array([spots,sks,vols,ttxs,optTypes]).transpose()]

    t['tv'] = [x['tv'] for x in greeks]
    t['delta'] = [x['delta'] for x in greeks]
    t['gamma'] = [x['gamma'] for x in greeks]
    t['theta'] = [x['theta'] for x in greeks]
    t['vega'] = [x['vega'] for x in greeks]
    t['vanna'] = [x['vanna'] for x in greeks]
    t['volga'] = [x['volga'] for x in greeks]
    
    t['gammadelta']= [x['gammadelta'] for x in greeks]
    t['gammatheta']= [x['gammatheta'] for x in greeks]
    t['gammavega'] = [x['gammavega'] for x in greeks]

    t['deltatheta'] = [x['deltatheta'] for x in greeks]
    t['vegatheta'] = [x['vegatheta'] for x in greeks]
    t['deltatheta'] = [x['deltatheta'] for x in greeks]
    t['thetatheta'] = [x['thetatheta'] for x in greeks]    
    return t
    
    
def get_close_snap_enriched( ticker, date ) :
    openSnapSymbol = get_close_snap_symbol( ticker, date)
    return enrich_vol_greeks(openSnapSymbol)

def get_saved_eod_enriched( ticker, date, usecols =[] ):
    if len(usecols)>0 :
        t=pd.read_csv( os.environ['TRANSFORMER_ROOT'] +'data/options/eod_enriched/' + ticker +'_'+ datetime.strftime(date, '%Y%m%d')+'.csv', usecols=usecols)
    else :
        t=pd.read_csv( os.environ['TRANSFORMER_ROOT'] +'data/options/eod_enriched/' + ticker +'_'+ datetime.strftime(date, '%Y%m%d')+'.csv')
       
    if 'Unnamed: 0' in (list(t.columns)) : 
        t.drop(['Unnamed: 0'], axis = 1, inplace=True)
    if 'Date' in (list(t.columns)) :
        t['Date']=[ datetime.strptime(x,'%Y-%m-%d') for x in  t['Date']]
    if 'ExpirationDate' in (list(t.columns)) :
        t['ExpirationDate']=[ datetime.strptime(x,'%Y-%m-%d') for x in  t['ExpirationDate']]
    if 'ExpirationTime' in (list(t.columns)) :    
        t['ExpirationTime']=[ datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in  t['ExpirationTime']]
    if 'cycleTime' in (list(t.columns)) :
        t['cycleTime']=[ datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in  t['cycleTime']]
        
    t=t[t['OpenAskPrice'].notna()]
    t.fillna(value={'OpenBidPrice': 0}, inplace=True)
    return t

def get_saved_eod_target_term(ticker, target_ttx, date, usecols=[] ) :
    tv_symbol=get_saved_eod_enriched(ticker,date,usecols)
    min_dis=np.abs(tv_symbol['ttx_in_days']-target_ttx).min()
    return tv_symbol[abs(tv_symbol['ttx_in_days']-target_ttx) ==min_dis]