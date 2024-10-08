# crt.sh Scraper
Monitoring Certificate Transparency for company name or domain by scraping crt.sh

## What?
This script checks https://crt.sh for newly published certificates and announces them via Telegram

## Setup & Usage
* set basic variables in the script
    * a company name
    * setup Telegram bot and add its token +chatid
* choose between searching for Organisation (O) or Common Name (CN)
* let it run regularly for staying up to date
