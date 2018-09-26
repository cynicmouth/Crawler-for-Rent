# -*- coding: utf-8 -*-
"""
Spyder Editor

@author: Cynicmouth
"""


from __future__ import division, print_function, unicode_literals
import smtplib
import requests
from bs4 import BeautifulSoup
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# email credientials set up
gmail_user = 'sender@gmail.com'
gmail_password = 'P@ssword!'

sent_from = gmail_user
to = ['receiver@gmail.com']



# page source
url = 'https://cortonaforestpark.securecafe.com/onlineleasing/cortona-at-forest-park/availableunits.aspx'
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')

# initiate empty list
apt_num, sqft, price, avail = [], [], [], [],

for row in  soup.find_all('tr', {'class': 'AvailUnitRow'}):
    for idx, cell in enumerate(row.find_all('td')):
        if idx == 0: # appending apt #
            apt_num.append(cell.text)
        elif idx == 1: # appending sqft
            sqft.append(cell.text)
        elif idx == 2: # appending price range
            price.append(cell.text)
        elif idx ==3: # appending availability
            avail.append(cell.text)
        


# porting into pandas as a dataframe
df_dict = {
        'Apartment Number':apt_num,
        'Sqft': sqft,
        'Price':price,
        'Availability':avail,
        }

df = pd.DataFrame(df_dict)


# adding floor plan info

def floor_plan(sqft):
    if sqft == 650:
        return 'A1'
    elif sqft == 675:
        return 'A2'
    elif sqft == 711:
        return 'A3'
    elif sqft == 743:
        return 'A4'
    elif sqft == 575:
        return 'Studio'
    elif sqft == 978:
        return 'B1'
    elif sqft == 1097:
        return 'B2'
    elif sqft == 1299:
        return 'B3'
    
        
df['Apartment Type'] = df.Sqft.apply(lambda x: floor_plan(int(x)))

# getting rid of '$' and ',' to extract dollar value
            
for character in ['$', ',']:            
    df.Price = df.Price.apply(lambda x: x.replace(character, ''))

 
df['Min Price'], df['Max Price'] = df['Price'].str.split('-',1).str


# convert them into numeric
df['Min Price'] = pd.to_numeric(df['Min Price'], errors = 'coerce')
df['Max Price'] = pd.to_numeric(df['Max Price'], errors = 'coerce')


# resort values by price
df = df.sort_values(by = ['Min Price']).reset_index()

df_new = df.head()

print(df_new)


# now automate it with sending email


# porting lowest rent info info over
lowest_rent = df_new['Min Price'][0]
apt_num = df_new['Apartment Number'][0]
apt_type = df_new['Apartment Type'][0]

subject = "Today's lowest rent at Cortona is %s, at Apartment %s (%s)" % (lowest_rent, apt_num, apt_type)

# compiling email messages
msg = MIMEMultipart()
msg['Subject'] = subject
msg['From'] = sent_from

html = """\
<html>
    <head>See your rent info for today</head>
    <body>
    {0}
    </body>
</html>
""".format(df_new.to_html())

body = MIMEText(html, 'html')
msg.attach(body)


try:  
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_password)
    server.sendmail(msg['From'], to, msg.as_string())
    server.close()

    print('Email sent!')
except:  
    print('Something went wrong...')