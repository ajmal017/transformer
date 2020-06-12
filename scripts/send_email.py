
import sys
from transformer_lib import util_email

if __name__ == '__main__':
    print( 'in  send_email python script now' )

    if len(sys.argv)>2 :
        util_email.transformer_send_email(sys.argv[1],sys.argv[2])
    elif len(sys.argv)>1 :
        util_email.transformer_send_email(sys.argv[1],'')
    else :
        util_email.transformer_send_email('love from transformer bot','')