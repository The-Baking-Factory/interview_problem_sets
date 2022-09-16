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
from datetime import datetime, timezone
import yahooquery

DATA_PATH = '../dbops/dat/stocks/data.json'
ticks_path = "../scrape/dat/ticks.json"
MAX_REQ_AMOUNT = 10

def save_json(path, data):
    # refactor from nested dict to list of dicts
    d = {'parse':[]}
    for c,v in data['parse'].items():
        d['parse'].append(v)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # refactor from list of dicts to nested dict
    d = {'parse':{}}
    for obj in data['parse']:
        d['parse'][obj['coin_id']] = obj
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

            new = {'parse':{}}
            data = summary_detail[tkr]

            if type(data) != dict:
                continue

            website = ""
            if type(summary_profile[tkr]) == dict and ('website' in summary_profile[tkr].keys()):
                website = summary_profile[tkr]['website']

            ratio_usd = ""
            price_change = ""
            if 'bid' in data.keys():
                ratio_usd = str(data['bid'])
                if 'open' in data.keys():
                    price_change = str((float(data['bid'])-float(data['open']))/float(data['open']))

            marketcap_usd = ""
            high_24h = ""
            low_24h = ""
            fifty_two_w_high = ""
            beta = ""
            if 'marketCap' in data.keys():
                marketcap_usd = str(data['marketCap'])
            if 'dayHigh' in data.keys():
                high_24h = str(data['dayHigh'])
            if 'dayLow' in data.keys():
                low_24h = str(data['dayLow'])
            if 'fiftyTwoWeekHigh' in data.keys():
                fifty_two_w_high = str(data['fiftyTwoWeekHigh'])
            if 'beta' in data.keys():
                beta = str(data['beta'])

            high_24h_change = ""
            low_24h_change = ""
            short_ratio = ""
            held_per_insiders = ""
            held_per_institutions = ""
            if ratio_usd and high_24h:
                high_24h_change = str((float(ratio_usd)-float(high_24h))/float(high_24h))
            if ratio_usd and low_24h:
                low_24h_change = str((float(ratio_usd)-float(low_24h))/float(low_24h))
            if type(key_stats[tkr]) == dict and ('shortRatio' in key_stats[tkr].keys()):
                short_ratio = str(key_stats[tkr]['shortRatio'])
            if type(key_stats[tkr]) == dict and ('heldPercentInsiders' in key_stats[tkr].keys()):
                held_per_insiders = key_stats[tkr]['heldPercentInsiders']
            if type(key_stats[tkr]) == dict and ('heldPercentInstitutions' in key_stats[tkr].keys()):
                held_per_institutions = key_stats[tkr]['heldPercentInstitutions']

            if high_24h_change:
                high_24h_change = round(float(high_24h_change), 2)
            if low_24h_change:
                low_24h_change = round(float(low_24h_change), 2)
            if held_per_insiders:
                held_per_insiders = round(float(held_per_insiders), 2)
            if held_per_institutions:
                held_per_institutions = round(float(held_per_institutions), 2)
            if price_change:
                price_change = round(float(price_change), 2)
            if marketcap_usd:
                marketcap_usd = round(float(marketcap_usd), 1)

            if ratio_usd and high_24h and low_24h:
                if (Decimal(ratio_usd) >= 1000):
                    ratio_usd = round(Decimal(ratio_usd))
                    ratio_usd = "{:,}".format(ratio_usd)
                    high_24h = "{:,}".format(round(Decimal(high_24h)))
                    low_24h = "{:,}".format(round(Decimal(low_24h)))
                elif (Decimal(ratio_usd) > 0.01):
                    ratio_usd = round(Decimal(ratio_usd), 2)
                    high_24h = round(Decimal(high_24h), 2)
                    low_24h = round(Decimal(low_24h), 2)
                elif (Decimal(ratio_usd) > 0.001):
                    ratio_usd = round(Decimal(ratio_usd), 3)
                    high_24h = round(Decimal(high_24h), 3)
                    low_24h = round(Decimal(low_24h), 3)
                elif (Decimal(ratio_usd) > 0.0001):
                    ratio_usd = round(Decimal(ratio_usd), 4)
                    high_24h = round(Decimal(high_24h), 4)
                    low_24h = round(Decimal(low_24h), 4)
                elif (Decimal(ratio_usd) > 0.00001):
                    ratio_usd = round(Decimal(ratio_usd), 6)
                    high_24h = round(Decimal(high_24h), 6)
                    low_24h = round(Decimal(low_24h), 6)
                else:
                    ratio_usd = f"{Decimal(str(ratio_usd)):.2E}"
                    high_24h = f"{Decimal(str(high_24h)):.2E}"
                    low_24h = f"{Decimal(str(low_24h)):.2E}"

            if marketcap_usd and (float(marketcap_usd) >= 1000):
                marketcap_usd = "{:,}".format(round(marketcap_usd))

            new['parse'][tkr] = {
                'ticker': tkr,
                'website': str(website),
                'ratio_usd': str(ratio_usd),
                'marketcap_usd': str(marketcap_usd),
                'price_change': str(price_change),
                'high_24h': str(high_24h),
                'low_24h': str(low_24h),
                'high_24h_change': str(high_24h_change),
                'low_24h_change': str(low_24h_change),
                'short_ratio': str(short_ratio),
                'held_per_insiders': str(held_per_insiders),
                'held_per_institutions': str(held_per_institutions),
            }

            save_json(DATA_PATH, new)

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
