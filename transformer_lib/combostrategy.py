import os
import numpy as np
import pandas as pd
from datetime import datetime
from transformer_lib import util_funcs
from transformer_lib import trading_calendar

def universe_vertical_builder( ticker, date, optType, use_ttx_target = 15, term_date_int = 0 ):

#  THIS FUNCTION IS TO BUILD A TABLE LIKE BELOW, EACH LINE ONLY ONE LEG OF A COMBO TRADE, trade_id 
#  IS UNIQUE FOR EACH COMBO TRADE. BASIC FILTERING WAS APPLIED HERE, SO NO DUPLICATE COMBOS, EACH LEG 
#  HAS VALID PRICING TOO.
#
#  trade_id ticker ExpirationDateInt CallPut Strike position OpenBidPrice OpenAskPrice UnderOpenBidPrice ...
#  0        VXX    20200515          C       26.0   1        15.20        15.40        41.27 ...
#  0        VXX    20200515          C       27.0   -1       14.20        14.40        41.27 ...
#  1        VXX    20200515          C       26.0   1        15.20        15.40        41.27 ...
#  1        VXX    20200515          C       28.0   -1       13.25        13.45        41.27 ...
    
    t=util_funcs.get_saved_eod_enriched(ticker,date)
    #t=t.drop(['Unnamed: 0'],axis=1)
    t=t[(t['volErrorBar']>1e-6) & (t['volErrorBar']<10)]

    if use_ttx_target :
        t['dis']=np.abs(t['ttx_in_days']-use_ttx_target)
        term_date = t[t['dis'] == t.dis.min()].ExpirationDate.unique()[0]
        term_t=t[t['ExpirationDate']==term_date].copy()
    else :
        term_t=t[t['ExpirationDate']==term_date].copy()
    
    term_t=term_t[(term_t.mid.notna()) & (term_t['CallPut']==optType)]

    sks=term_t['Strike'].unique()
    sks.sort()
    mat=np.array([[[x,y] for x in sks ] for y in sks ])
    all_pairs=mat.reshape(mat.shape[0]*mat.shape[1],2)

    #### removing same strike combo and repeating ones. 
    #### For call verticals, we ask buy low strike call, and sell high strike call, for PUTs, it is opposite, 
    #### so by default, trading is buying debit spreads:

    pairs=all_pairs[[ x<y for x,y in all_pairs]]

    #### now zip trade_id, position, and strike
    trade_ids = np.array([ [i,i] for i in range(0,len(pairs))])
    positions  = np.array([ [1,-1] for i in range(0,len(pairs))])
    c=pd.DataFrame( {'trade_id':trade_ids.flatten(), 'ticker':ticker, 'ExpirationDate':term_date, 
                                'CallPut':optType,'Strike': pairs.flatten(), 'position':positions.flatten()})
    return c.merge( term_t, how='left', on=['ExpirationDate','Strike','CallPut'])


def net_vals(x):
    return [x.trade_id.min(),
            (x.position * x.gamma).sum(), 
            (x.position * x.theta).sum(), 
            (x.position * x.delta).sum(), 
            (x.position * x.vega).sum(),
            x.delta.min(),
            x.delta.max(),
            x.Strike.min(),
            x.Strike.max()]


def strategy_selector_LGST_baskline( univ_t ):
    agg_t=pd.DataFrame( list(np.array(univ_t.groupby(['trade_id'],as_index=False).apply(net_vals)).transpose()), 
             columns=['trade_id',
                      'net_gamma',
                      'net_theta',
                      'net_delta',
                      'net_vega',
                      'min_delta',
                      'max_delta',
                      'min_strike',
                      'max_strike'])
    
    #### IF NEEDED FILTERS CAN BE APPLIED HERE
    #### SUCH AS 
    #### 1. POSITIVE NET GAMMA AND NET THETA
    #### 2. MAX DELTA < 0.6, SO MOST OF SECS SELECTED ARE OTM
    
    #### CURRENT FUNCTION RETURNS EVERYTHING 
    
    return agg_t


def strategy_selector_LGST_secline( univ_t ):
    agg_t=strategy_selector_LGST_baskline( univ_t )
    return agg_t.merge(univ_t,how='left',on=['trade_id'])


def getTermVerticals( term_t, optType ) :
    x_axis = np.array(term_t['Strike'])
    y_axis = np.array(term_t['Strike'])
    mat=np.array([[[x,y] for x in x_axis ] for y in y_axis ])
    mat=np.concatenate(mat)
    vertical_base = pd.DataFrame(mat, columns=['strike_l','strike_r'])

    vertical = vertical_base.merge(term_t, left_on=['strike_l'],right_on='Strike')
    vertical = vertical.merge( term_t, left_on=['strike_r'], right_on='Strike',suffixes=['_l','_r'])
    
    vertical=vertical[vertical['strike_l']<vertical['strike_r']]
    
    ## if put, we long higher strike and short lower strike , if call, we do opposite:
    if optType == 'P' :
        vertical['pnl_5b']=vertical['mid_5b_r']-vertical['mid_5b_l'] - (vertical['mid_r']-vertical['mid_l'])
        vertical['delta_pnl_attri']=(vertical['delta_r']-vertical['delta_l']) * (vertical['spot_5b_l']-vertical['spot_l'])
    else :
        vertical['pnl_5b']=vertical['mid_5b_l']-vertical['mid_5b_r'] - (vertical['mid_l']-vertical['mid_r'])
        vertical['delta_pnl_attri']=(vertical['delta_l']-vertical['delta_r']) * (vertical['spot_5b_l']-vertical['spot_l'])


    vertical.rename(columns={'Date_l':'Date','ExpirationDate_l':'ExpirationDate','ttx_in_days_l':'ttx_in_days'},inplace=True)
    return vertical[['Date','ExpirationDate','ttx_in_days','Strike_l','Strike_r','delta_l','delta_r', 'mid_l','mid_r',
                     'spot_l','width_l','width_r', 'vega_l','vega_r','gamma_l','gamma_r','theta_l','theta_r',
                     'impVol_l','impVol_r','mid_5b_l','mid_5b_r',
                     'width_5b_l','width_5b_r', 'impVol_5b_l', 'impVol_5b_r', 'spot_5b_l','pnl_5b','delta_pnl_attri']]

def getSymbolVerticals( ticker, date, target_ttx, holding_target = 10, return_grped = True, optType = 'P' ) :
#    print( 'processing ', date)
    t=util_funcs.get_saved_eod_enriched(ticker,date)
    t=t[(t['volErrorBar']>1e-6) & (t['volErrorBar']<10)]

    tPlusN=trading_calendar.getTPlusNDate(date, holding_target)
    t_fut = util_funcs.get_saved_eod_enriched(ticker,tPlusN)

    jn = t.merge(t_fut,how='left', left_on=['ExpirationDate','CallPut','Strike'], \
                     right_on=['ExpirationDate','CallPut','Strike'], suffixes=('', '_5b') )

    jn_filtered=jn[jn['delta']!=0].copy()
    jn_filtered=jn_filtered[jn_filtered['CallPut']==optType]
    
    jn_filtered['dis']=np.abs(jn_filtered['ttx_in_days']-target_ttx)
    expPicked = jn_filtered[jn_filtered['dis'] == jn_filtered.dis.min()].ExpirationDate.unique()[0]
    jn_filtered=jn_filtered[jn_filtered['ExpirationDate']==expPicked]
    
    verts=getTermVerticals(jn_filtered, optType )
    if not return_grped :
        return verts
    else: 
        verts['avg_delta']=(verts['delta_l']+verts['delta_r'])/2
        verts['dif_delta']=verts['delta_r']-verts['delta_l']
        verts['vert_mid'] = verts['mid_r']-verts['mid_l']
        delta_bins_bnd = [x*0.1-1 for x in range(0,11)]
        delta_bins = delta_bins_bnd[0:10]
        delta_bins = [ x + 0.05 for x in delta_bins]
        verts['dif_delta_bin']= pd.cut(verts['dif_delta'],delta_bins_bnd,labels=delta_bins)
        verts['avg_delta_bin']= pd.cut(verts['avg_delta'],delta_bins_bnd,labels=delta_bins)
        verts['width_max'] = verts[['width_l','width_r']].max(axis=1)
        verts_grped=verts.groupby(['Date','ExpirationDate','avg_delta_bin','dif_delta_bin']).agg(
            {'vert_mid': 'sum', 'pnl_5b':'sum','spot_l': 'first', 'spot_5b_l':'first', 'delta_pnl_attri':'sum',
            'width_max':'min','Date':'first','ExpirationDate':'first','avg_delta_bin':'first','ttx_in_days':'first',
            'dif_delta_bin':'first'})
        verts_grped = verts_grped.reset_index(drop=True)
        return verts_grped
    
def get_verts_multi_days( ticker, start_date, end_date, target_ttx=15, holding_days=5, optType = 'P' ) :
    date = start_date
    all_t=[]
    while date < end_date :
        try :
            all_t.append(getSymbolVerticals(ticker, date, target_ttx, holding_days, False, optType))
        except :
            print( 'failed to process ', date )

        date = trading_calendar.getTPlusNDate(date,1)
    return pd.concat(all_t)

def get_combo_trades( ticker, optType ) :
    if (ticker == 'VXX') :
        combos = pd.read_csv(os.environ['TRANSFORMER_ROOT'] + 'data/options/combo_research/verts_15d_1hold_2018_' + optType +'.csv')
        combos2 = pd.read_csv(os.environ['TRANSFORMER_ROOT'] + 'data/options/combo_research/verts_15d_1hold_2019_'+ optType +'.csv')
        combos3 = pd.read_csv(os.environ['TRANSFORMER_ROOT'] + 'data/options/combo_research/verts_15d_1hold_2020_'+ optType +'.csv')
        combos = pd.concat([combos, combos2, combos3])
    else :
        combos = pd.read_csv(os.environ['TRANSFORMER_ROOT'] + 'data/options/combo_research/'+ticker+'_verts_15d_1hold_2019_' + optType +'.csv')
        combos2 = pd.read_csv(os.environ['TRANSFORMER_ROOT'] + 'data/options/combo_research/'+ticker+'_verts_15d_1hold_2020_' + optType +'.csv')
        combos = pd.concat([combos, combos2])
        
    combos['Date_d'] = [ datetime.strptime(x, '%Y-%m-%d') for x in combos['Date'] ]
    if optType == 'Put' :
        delta_bins_bnd = [x*0.1-1 for x in range(0,11)]
        delta_bins = delta_bins_bnd[0:10]
        delta_bins = [ x - 0.05 for x in delta_bins]
        combos['delta_l_bin']= pd.cut(combos['delta_l'],delta_bins_bnd,labels=delta_bins)
        combos['delta_r_bin']= pd.cut(combos['delta_r'],delta_bins_bnd,labels=delta_bins)
        combos['d1_bin']= combos.delta_l_bin.cat.codes
        combos['d2_bin']= combos.delta_r_bin.cat.codes
        combos['netTheta']=combos['theta_l'] - combos['theta_r']
        combos['netGamma'] = combos['gamma_r'] - combos['gamma_l']
        combos['netDelta'] = combos['delta_r'] - combos['delta_l']
        combos['intrinsic_l']=combos['Strike_l'] - combos['spot_l']
        combos['intrinsic_r']=combos['Strike_r'] - combos['spot_l']
    elif optType == 'Call' :
        delta_bins_bnd = [x*0.1 for x in range(0,11)]
        delta_bins = delta_bins_bnd[0:10]
        delta_bins = [ x + 0.05 for x in delta_bins]
        combos['delta_l_bin']= pd.cut(combos['delta_l'],delta_bins_bnd,labels=delta_bins)
        combos['delta_r_bin']= pd.cut(combos['delta_r'],delta_bins_bnd,labels=delta_bins)
        combos['d1_bin']= combos.delta_l_bin.cat.codes
        combos['d2_bin']= combos.delta_r_bin.cat.codes
        combos['netTheta']=combos['theta_r'] - combos['theta_l']
        combos['netGamma'] = combos['gamma_l'] - combos['gamma_r']
        combos['netDelta'] = combos['delta_l'] - combos['delta_r']
        combos['intrinsic_l']=combos['spot_l'] - combos['Strike_l']
        combos['intrinsic_r']=combos['spot_l'] - combos['Strike_r']
    else :
        print( 'wrong option type, exit!')
    return combos