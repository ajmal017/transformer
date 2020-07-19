import os, sys
from datetime import datetime
from transformer_lib import util_funcs
from transformer_lib import trading_calendar
from transformer_lib import util_email

def download_data( datestr ):
    print( 'processing for ', datestr )
    command = 'rsync -rv user1@172.37.44.98:/data/cffex/' + datestr + ' /Volumes/LaCie/china_market/cffex/'
    os.system(command) 
    return

if __name__ == '__main__':
    if len(sys.argv)>1 :
        datestr = sys.argv[1]
        download_data( datestr )
    else :
        prev_bday = trading_calendar.getTPlusNDate( datetime.today(), -1)
        download_data(prev_bday.strftime('%Y%m%d'))
        
    util_email.transformer_send_email('love from transformer bot','i sweetly finished cffex download work, xxoo')
    print( 'at ', datetime.today(), ' all work done, email sent' )