import sys,os
from datetime import datetime
from transformer_lib import util_funcs
from transformer_lib import trading_calendar
from transformer_lib import util_email

FILEPATH = '/Users/kewang/transformer/data/options/eod_enriched/'

def process_eod_enrich( date ):
    print( 'processing for ', date )
    t = util_funcs.get_close_snap_enriched( 'VXX', date )
    fn = 'VXX_' + date.strftime('%Y%m%d') + '.csv'
    t.to_csv( FILEPATH + fn)
    
    t = util_funcs.get_close_snap_enriched( 'SPY', date )
    fn = 'SPY_' + date.strftime('%Y%m%d') + '.csv'
    t.to_csv( FILEPATH + fn)
    return

if __name__ == '__main__':
    print( 'print from eod_enriched_process' )
    
    if len(sys.argv)>1 :
        datestr = sys.argv[1]
        day = datetime.strptime( datestr, '%Y%m%d' )
        process_eod_enrich( day )
    else :
        prev_bday = trading_calendar.getTPlusNDate( datetime.today(), -1)
        process_eod_enrich(prev_bday)
    
    util_email.transformer_send_email('love from transformer bot','i sweetly finished eod enrichment work, xxoo')
    print( 'at ', datetime.today(), ' all work done, email sent' )