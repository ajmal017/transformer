# transformer library on utility functions to aid real-time trading analysis and gui
# Rongrong Zhao May 2020

import os
import pandas as pd
import numpy as np
from datetime import datetime
from transformer_lib import pricer
from transformer_lib import european_pricer
from transformer_lib import util_funcs

def get_fn_options() :
    directory = '/Users/kewang/transformer/data/RT_trading_snaps/'
    filenames = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filenames.append(filename)
    return filenames

def get_greeks( s, x, r, sigma, t, optType ):
    ep = european_pricer.european_pricer( s, x, r, sigma, t, optType )
    return ep.greeks()

def parse_rt_snapfile( fn ) :
    directory = '/Users/kewang/transformer/data/RT_trading_snaps/' 
    t=pd.read_csv( directory + fn)
    
    ### Test and get spot last price : 
    if (t.loc[0][1].split('\n')[0] == 'Last') :
        spot = float(t.loc[0][1].split('\n')[1])
    else :
        print( 'RECHECK DATA FILE FOR SPOT LAST PRICE, ROW OR COLUMN ID MIGHT BE OFF!!!')
   
    
    ticker=fn.split('_')[0]
    expTime = datetime.strptime( fn.split('_')[1] + ' 16:00:00', '%Y%m%d %H:%M:%S')
        
    snapday = fn.split('_')[3].split('.')[0]
    snaphour = fn.split('_')[2][0:2]
    snapminute = fn.split('_')[2][2:4]
    currentTime = datetime.strptime( snapday + ' ' + snaphour + ':' + snapminute +':00', '%Y%m%d %H:%M:%S')

    header_idx=t[t['Unnamed: 0']=='Select Contract'].index.values[0]
    header =list(t.loc[header_idx])
    t = t[header_idx+1:]

    header[4] = 'Call Bid'
    header[5] = 'Call Ask'
    header[12] = 'Put Bid'
    header[13] ='Put Ask'
    header[8] ='Strike'
    t.columns = header

    calls = t[['Call Bid','Call Ask','Strike']].copy()
    calls.rename(columns={'Call Bid':'Bid','Call Ask':'Ask'},inplace=True)
    calls['CallPut'] = 'C'
    puts = t[['Put Bid','Put Ask','Strike']].copy()
    puts.rename(columns={'Put Bid':'Bid','Put Ask':'Ask'},inplace=True)
    puts['CallPut'] = 'P'
    df=pd.concat([calls,puts], sort=False )
    
    df=df.astype({'Ask':'float','Bid':'float','Strike':'float'})
    
    df['ticker']=ticker
    df['currentTime'] = currentTime
    df['expTime'] = expTime
    df['ttx_in_days'] = [ x.days for x in (df['expTime']-df['currentTime'])]
    df['ttx']=[x.total_seconds()/(365* 24*60*60) for x in list(df['expTime']-df['currentTime'])]
    df['spot'] = spot
    df['mid'] = ( df['Bid'] + df['Ask'])/2
    df['width'] =df['Ask'] - df['Bid']
    


    spots = np.array(df['spot'].values)
    prices = np.array(df['mid'].values)
    sks = np.array(df['Strike'].values)
    ttxs = np.array(df['ttx'].values)
    optTypes = np.array(df['CallPut'].values)
    priceEBs = np.array(df['width'].values)
    
    
    ### calculate and fill in implied vols:
    vol_and_ebs = [ pricer.impVol(spot, sk, 0.01, mid, ttx, optType,priceEB) for spot,mid,sk,ttx,optType,priceEB in np.array([spots,prices,sks,ttxs,optTypes,priceEBs]).transpose()]
    df['impVol'] = [x['impVol'] for x in vol_and_ebs]
    df['volErrorBar'] = [x['volErrorBar'] for x in vol_and_ebs]

    ### get and fill in all the greeks:
    
    vols = [x['impVol'] for x in vol_and_ebs]
    greeks = [ get_greeks( spot, sk, 0.01, sigma, ttx, optType ) for spot,sk,sigma,ttx,optType in \
              np.array([spots,sks,vols,ttxs,optTypes]).transpose()]

    df['tv'] = [x['tv'] for x in greeks]
    df['delta'] = [x['delta'] for x in greeks]
    df['gamma'] = [x['gamma'] for x in greeks]
    df['theta'] = [x['theta'] for x in greeks]
    df['vega'] = [x['vega'] for x in greeks]
    df['vanna'] = [x['vanna'] for x in greeks]
    df['volga'] = [x['volga'] for x in greeks]
    
    df['gammadelta']= [x['gammadelta'] for x in greeks]
    df['gammatheta']= [x['gammatheta'] for x in greeks]
    df['gammavega'] = [x['gammavega'] for x in greeks]

    df['deltatheta'] = [x['deltatheta'] for x in greeks]
    df['vegatheta'] = [x['vegatheta'] for x in greeks]
    df['thetatheta'] = [x['thetatheta'] for x in greeks]
    
    return df


def get_pos_analysis( fn, posSks, optType ):
    df = parse_rt_snapfile(fn)
    df = df[df['CallPut'] ==optType ]
    return df[ [x in posSks for x in list(df['Strike']) ]]

def trds_enrich( trds_flat ) :
    jn=[]
    for key,val in trds_flat.groupby(['Date','ExpirationDate']) :
        print( 'processing ', key[0],' ',key[1], '\n')
        t_mb = util_funcs.get_minutebar_raw_expiry('VXX',key[0],key[1],usecols=['Date','ExpirationDate','CallPut','Strike','OpenBidTime','OpenAskTime','OpenBidPrice','OpenAskPrice','UnderOpenBidPrice','UnderOpenAskPrice'])
        t_mb['ExpirationDate']=[ datetime.strptime(x, '%Y%m%d') for x in t_mb['ExpirationDate']]

        for subkeys,subval in val.groupby(['Strike','CallPut']) :
            print( 'processing ', subkeys[0], ' ', subkeys[1])
            t_mb_sub=t_mb[(t_mb['Strike']==subkeys[0]) & (t_mb['CallPut']==subkeys[1])].copy()
            t_mb_sub=t_mb_sub[t_mb_sub['OpenBidTime'].notna()]
            t_mb_sub=t_mb_sub.drop(['Strike','CallPut'],axis=1)
            dds = t_mb_sub['Date']
            tts = t_mb_sub['OpenBidTime']
            t_mb_sub['time'] =[ datetime.strptime(x+' ' + y + '000','%Y%m%d %H:%M:%S.%f') for x,y in np.array([dds,tts]).transpose()]
            t_mb_sub=t_mb_sub.drop(['Date'],axis=1)
            jn.append(pd.merge_asof(subval, t_mb_sub, on=['time']))

    jns = pd.concat(jn)
    jns['mid']=(jns['OpenBidPrice']+jns['OpenAskPrice'])/2
    jns['spot']=(jns['UnderOpenBidPrice']+jns['UnderOpenAskPrice'])/2
    jns['simu_price']=jns['mid']*jns['qty']*100*(-1)
    jns['ExpirationTime']=[datetime.strptime(x.strftime('%Y%m%d')+' 16:00:00','%Y%m%d %H:%M:%S') for x in jns['ExpirationDate_x']]
    jns['ttx'] =[x.total_seconds()/(365.25*24*60*60) for x in jns['ExpirationTime']-jns['tradeTime']]
    jns['width']=jns['OpenAskPrice']-jns['OpenBidPrice']
   #jns['Strike']=jns['Strike_x']
    jns=util_funcs.enrich_vol_greeks(jns)
    jns['trdDelta']=jns['delta']*jns['qty']*100
    return jns