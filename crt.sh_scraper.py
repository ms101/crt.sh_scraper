#!/usr/bin/env python
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import os.path
import html
import re
import pprint
import json

orgname = 'My Company'
org = orgname.replace(' ', '_')
topic = 'crt.sh: ' + orgname
short = 'crt.sh_O_' + org

# search by Company Name (Organisation)
url = 'https://crt.sh/?O=' + orgname.replace(' ', '+') + '&output=json&exclude=expired'

# alternatively search by domain (Common Name)
#domain = 'mycompany.com'
#url = 'https://crt.sh/?CN=' + domain + '&output=json&exclude=expired'

botid = ''	# complete Telegram bot token
chatid = ''	# e.g. of a group with the bot in it

DEBUG = 0	# output debug messages
TESTMODE = 0	# save response to disk (tempfile), avoid making further requests

headers = {'Host': 'crt.sh', 'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'deflate'}
tempfile = short + '.page.tmp'
dbfile = short + '.db.json'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
today = datetime.today().strftime('%Y-%m-%d')
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
content = ''
articles = []
article = {}

if DEBUG: print('[*] Starting web scraper:\n\t' + topic + '\n\t' + timestamp)

# request webpage
if not os.path.exists(tempfile):
	if DEBUG: print('[*] Request:\n\t' + url)
	resp = requests.get(url, headers=headers)
	if DEBUG: print('[*] Response:\n\t' + str(resp.status_code) + ' ' + resp.reason + ' after ' + str(resp.elapsed))
	content = resp.content.decode('utf-8')

	# write to file if DEBUG enabled
	if TESTMODE:
		f = open(tempfile, 'w')
		f.write(content)
else:
	if DEBUG: print('[DEBUG] Using cached data')
	f = open(tempfile, 'r')
	content = f.read()

articles = json.loads(content)
articles.reverse()

#pprint.pprint(items)
#print('DEBUG items: ' + str(len(items)))
if len(articles) < 5:
	msg += 'BUG in scraper ' + short + '\nless than 5 items!'
	requests.post('https://api.telegram.org/bot' + botid + '/sendMessage?chat_id=' + chatid + '&text=' + msg)

dbexists = 0
newarticles = []

if os.path.exists(dbfile):
	oldarticles = json.load(open(dbfile, 'r'))
	dbexists = 1

# parsing
if dbexists:
	for article in articles:
		if int(article['id']) < 5400000000: # cap
			continue
		notfound = 1
		for oarticle in oldarticles:
			if oarticle['id'] == article['id']:
				notfound = 0
		if notfound:
			newarticles.append(article)

if DEBUG: print('[*] Number of entries:\n\t' + str(len(articles)))
#pprint.pprint(articles)

# write data to new json or update existing json and announce new entries
if not os.path.exists(dbfile):
	json.dump(articles, open(dbfile, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
	if DEBUG: print('[*] Database created as file:\n\t' + dbfile)
elif newarticles:
	if DEBUG: print('[*] Appending new entries to existing database:\n\t' + dbfile)
	db = json.load(open(dbfile, 'r'))
	for narticle in newarticles:
		db.append(narticle)
	json.dump(db, open(dbfile, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

	# output new entries
	if DEBUG: print('[*] Number of new entries:\n\t' + str(len(newarticles)))
	if DEBUG: print('[*] New entries:')
	pprint.pprint(newarticles)

	# announce new entires via Telegram
	if DEBUG: print('[*] Announcing new entries via Telegram...')
	
	for na in newarticles:
		msg = na['entry_timestamp'] + ' ' + short + '\n'
		msg += na['common_name'] + ' (' + na['issuer_name'] + ')\n'
		msg += na['not_before'] + ' <-> ' + na['not_after'] + '\n'
		msg += 'ID: ' + str(na['id'])
		if requests.post('https://api.telegram.org/bot' + botid + '/sendMessage?chat_id=' + chatid + '&text=' + msg):
			print('[*] Telegram notification sent (ID: ' + str(na['id']) + ')')

	if DEBUG: print('[*] Done. Exiting')
else:
	if DEBUG: print('[*] No new entries. Exiting')

x = open(short + '_lastcheck.txt', 'w')
x.write('x')
x.close()

