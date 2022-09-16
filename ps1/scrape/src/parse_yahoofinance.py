#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Rahul Zalkikar

import os
import requests
import json
import asyncio
import argparse
import subprocess
from decimal import Decimal
import yahooquery

DATA_PATH = '../dbops/dat/stocks/data.json'
ticks_path = "../scrape/dat/ticks.json"
MAX_REQ_AMOUNT = 10

# TODO
# Explain this script in detail. How are the data jsons being inserted into the databse?
# Are there are any code duplicates or unnecessary operations? Remove them if so.
# Is there a way to perform the logic in this script more efficiently?
# If so, how would you modify the script?

def save_json(path, data):
    # refactor from nested dict to list of dicts
    d = {'parse':[v for v in data['parse'].values()]}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # refactor from list of dicts to nested dict
    d = {'parse':{obj['coin_id']: obj for obj in data['parse']}}
    return d

def load_ticks():
    data = {"ticks": []}
    with open(ticks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

async def parse(targets = []):
    if not targets:
        ticks = load_ticks()
        ids = [tick.lower() for tick in ticks['ticks']]
        id_chunks = [ids[x:x+MAX_REQ_AMOUNT] for x in range(0, len(ids), MAX_REQ_AMOUNT)]
    else:
        id_chunks = [ids[x:x+MAX_REQ_AMOUNT] for x in range(0, len(targets), MAX_REQ_AMOUNT)]

    for idx, chunk in enumerate(id_chunks):
        res = yahooquery.Ticker(chunk)
        print(f"{round(100*(idx/len(id_chunks)),2)}% | {len(chunk)} stocks scraped")

        summary_detail = res.summary_detail
        summary_profile = res.summary_profile
        key_stats = res.key_stats
        for idx, tkr in enumerate(chunk):
            print(f"parsing {tkr} data")

            new = {'parse':{}}
            data = summary_detail[tkr]

            if type(data) != dict:
                continue

            obj = {
                'ratio_usd': '',
                'price_change': '',
                'marketcap_usd': '',
                'high_24h': '',
                'low_24h': ''
            }

            if 'bid' in data.keys():
                obj['ratio_usd'] = str(data['bid'])
                if 'open' in data.keys():
                    # TODO
                    # Compute price change between data['bid'] (current price) and data['open']
                    # Round to two decimal places
                    # Pretend this is a financial application that requires a high degree of precision with computes, sacrificing speed for precision
                    # hint: what data type should you use for high precision
                    obj['price_change'] = round((Decimal(data['bid'])-Decimal(data['open']))/Decimal(data['open']), 2)
            if 'marketCap' in data.keys():
                obj['marketcap_usd'] = round(data['marketCap'], 1)
            if 'dayHigh' in data.keys():
                obj['high_24h'] = str(data['dayHigh'])
            if 'dayLow' in data.keys():
                obj['low_24h'] = str(data['dayLow'])

            if obj['ratio_usd'] and obj['high_24h'] and obj['low_24h']:
                if (Decimal(obj['ratio_usd']) >= 1000):
                    obj['ratio_usd'] = round(Decimal(obj['ratio_usd']))
                    obj['ratio_usd'] = "{:,}".format(obj['ratio_usd'])
                    obj['high_24h'] = "{:,}".format(round(Decimal(obj['high_24h'])))
                    obj['low_24h'] = "{:,}".format(round(Decimal(obj['low_24h'])))
                elif (Decimal(obj['ratio_usd']) >= 0.1):
                    obj['ratio_usd'] = f"{Decimal(str(obj['ratio_usd'])):.2E}"
                    obj['high_24h'] = f"{Decimal(str(obj['high_24h'])):.2E}"
                    obj['low_24h'] = f"{Decimal(str(obj['low_24h'])):.2E}"
                else:
                    # TODO
                    # what is the below bit of code doing?
                    # Is there a better way to do it?
                    for i in range(2, 6):
                        thresh = 1 * (10**(-1 * i))
                        if (Decimal(obj['ratio_usd']) > thresh):
                            if i == 5:
                                obj['ratio_usd'] = round(Decimal(obj['ratio_usd']), i+1)
                                obj['high_24h'] = round(Decimal(obj['high_24h']), i+1)
                                obj['low_24h'] = round(Decimal(obj['low_24h']), i+1)
                            else:
                                obj['ratio_usd'] = round(Decimal(obj['ratio_usd']), i)
                                obj['high_24h'] = round(Decimal(obj['high_24h']), i)
                                obj['low_24h'] = round(Decimal(obj['low_24h']), i)
                            break

            if obj['marketcap_usd'] and (obj['marketcap_usd'] >= 1000):
                obj['marketcap_usd'] = "{:,}".format(round(obj['marketcap_usd']))

            new['parse'][tkr] = {
                'ticker': tkr,
                'ratio_usd': str(obj['ratio_usd']),
                'marketcap_usd': str(obj['marketcap_usd']),
                'price_change': str(obj['price_change']),
                'high_24h': str(obj['high_24h']),
                'low_24h': str(obj['low_24h'])
            }

            print(f"saving json of {tkr} data")
            save_json(DATA_PATH, new)

            print(f"running insertion of {tkr} data")
            cmd = './run.sh'
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            if (error):
                print(f"ERROR: {error}")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--targets',
                        type=str,
                        required=False)

    args = parser.parse_args()

    if args.targets:
        targets = args.targets.split(',')
        asyncio.run(parse(targets))
    else:
        asyncio.run(parse())
