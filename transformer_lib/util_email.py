import smtplib

TRANSFORMER_EMAIL = "fivethousand.below@gmail.com"
TRANSFORMER_PASSWORD = "Transformer@021"

def transformer_send_email( subject, body ) :
    try:
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.ehlo()
        server.starttls()
        server.login( TRANSFORMER_EMAIL, TRANSFORMER_PASSWORD )
    except:
        print('Something went wrong with email log in')

    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (TRANSFORMER_EMAIL, TRANSFORMER_EMAIL, subject, body)

    server.sendmail(TRANSFORMER_EMAIL, TRANSFORMER_EMAIL, email_text)
    print( 'just sent email to ', TRANSFORMER_EMAIL )
    return 