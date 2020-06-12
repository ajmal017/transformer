import os, sys
from datetime import datetime
from transformer_lib import util_funcs
from transformer_lib import trading_calendar
from transformer_lib import util_email

def download_data( day ):
    print( 'processing for ', day )
    command = 'aws s3 sync '+util_funcs.option_minutebar_remote_dir(day,'VXX')+' '+util_funcs.option_minutebar_local_dir(day,'VXX')+' --request-payer requester'
    os.system(command) 
    command = 'aws s3 sync '+util_funcs.option_minutebar_remote_dir(day,'SPY')+' '+util_funcs.option_minutebar_local_dir(day,'SPY')+' --request-payer requester'
    os.system(command)
    return

if __name__ == '__main__':
    if len(sys.argv)>1 :
        datestr = sys.argv[1]
        day = datetime.strptime( datestr, '%Y%m%d' )
        download_data( day )
    else :
        prev_bday = trading_calendar.getTPlusNDate( datetime.today(), -1)
        download_data(prev_bday)
        
    util_email.transformer_send_email('love from transformer bot','i sweetly finished algoseek download work, xxoo')
    print( 'at ', datetime.today(), ' all work done, email sent' )