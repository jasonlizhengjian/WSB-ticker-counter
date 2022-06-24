import praw
import os
import re
from datetime import datetime, date, time
from pytz import timezone
from replit import db
from stocksymbol import StockSymbol
from keep_alive import keep_alive
import time

reddit = praw.Reddit(client_id = os.environ['client_id'],
                     client_secret = os.environ['client_secret'],
                     username = os.environ['username'],
                     password = os.environ['password'],
                     user_agent="<WSBTickercountBOT>"
                    )

api_key = os.environ['api_key']
ss = StockSymbol(api_key)

def clean_string(raw_string):
  cleaned_string = raw_string
  cleaned_string = re.sub(r'[^A-Za-z0-9 ]+', '', cleaned_string)
  return cleaned_string

class RedditBot:
  def __init__(self):
    self.tickercounts = {}
    today = date.today().isoformat()
    print(db.keys())
    if today not in db.keys():
      for item in ss.get_symbol_list(market="US"):
        if len(item['symbol']) >= 3 and item['symbol'] != 'LMAO' and item['symbol'] != 'ING' and item['symbol'] != 'YOU' and item['symbol'] != 'NEW' and item['symbol'] != 'FOR':
          self.tickercounts[item['symbol']] = 0
      db[today] = self.tickercounts
    else:
      print('Pull from DB')
      self.tickercounts = db[today]

  def checkComment(self, comment):
    today = date.today().isoformat()
    for key in self.tickercounts:
      keyincomment = re.search(r"\b{}\b".format(key), comment.body)
      if keyincomment:
        self.tickercounts[key] += 1
        db[today] = self.tickercounts
        print(key, self.tickercounts[key])
        print(comment.body)
    cur_time = datetime.now()
    
    if cur_time.hour == 23 and cur_time.minute >= 50 :
      self.printData()
      time.sleep(610)
      for item in ss.get_symbol_list(market="US"):
        if len(item['symbol']) >= 3 and item['symbol'] != 'LMAO' and item['symbol'] != 'ING' and item['symbol'] != 'YOU' and item['symbol'] != 'NEW' and item['symbol'] != 'FOR':
          self.tickercounts[item['symbol']] = 0
      db[today] = self.tickercounts
        

  def printData(self):
    today = date.today().isoformat()
    username = os.environ['username']
    sub = reddit.subreddit(f"u_{username}")
    title = "Today's most mentioned tickers"
    data = self.tickercounts
    data_sorted = sorted(data.items(), key=lambda x: x[1], reverse=True)
    body = f"## The following are the top 10 most mentioned stock tickers on WSB for {today} \n\n\n\n"
    for i in range(10):
      body = body + str(data_sorted[i][0]) + ' ' + str(data_sorted[i][1]) + "\n\n"
    body = body + '\n\n\n\n I wrote a python script to try and count all the tickers being mentioned on WSB, these are the results for today.'
    print(body)
    sub.submit(title, selftext = body)

keep_alive()
bot = RedditBot()
wsb = reddit.subreddit('wallstreetbets')
for comment in wsb.stream.comments(skip_existing = True):
  bot.checkComment(comment)
  

#db.clear()

