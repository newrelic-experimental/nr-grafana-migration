#!/usr/bin/env python3
import os
import json
import argparse
import sys
import requests
import time
import math

# Parse arguments
parser = argparse.ArgumentParser(description='Export Grafana dashboards for processing by New Relic')
parser.add_argument('--endpoint', type=str, help='endpoint to test queries on', default='https://prometheus-api.newrelic.com')
parser.add_argument('--token', type=str, help='New Relic Insights Query Keys', required=True)
args = parser.parse_args()

# Some nice colors we can play with
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Array to keep all failing queries to output to json
errors = []

# Helper function that checks expression against New Relic api
def checkExpressions(tabs, expr):
    query = expr['expr']
    getResult = requests.get(
        '%s/api/v1/query_range' % (args.endpoint),
        params = {
            'query': query,
            'start': math.floor(time.time()) - 300,
            'stop': math.floor(time.time()),
        },
        headers = { 'X-Query-Key': args.token }
    )
    data = json.loads(getResult.content)
    if data['status'] == 'success':
        print(bcolors.OKGREEN + '%s  OK' % tabs + bcolors.ENDC + ' %s' % (query))
    else:
        print(bcolors.WARNING + '%s FAILED (%s) %s' % (tabs, data['status'], query))
        print(data)
        errors.append({
            "query": query,
            "return": data
        })

# Helper function that checks a panel and finds expressions, or other panels
def checkPanels(panels, depth=0):
    tabs = depth * '\t'
    depth += 1

    # Check each panel
    for panel in panels:
        print('%s> %s' % (tabs, panel['title']))
        # If we have more panels in the panel, loop the panels in the panel
        if 'panels' in panel:
            checkPanels(panel['panels'], depth)

        # Retrieve targets and check them against New Relic api
        if 'targets' in panel:
            for target in panel['targets']:
                checkExpressions(tabs, target)
        print()

# Helper function that parses file for queries
def parse(file):
    print("Checking dashboard %s" % file)

    # Read Json content
    with open('output/dashboards/%s' % file, 'r') as f:
        dashboardData = json.loads(f.read())

    # Start loop
    checkPanels(dashboardData['dashboard']['panels'])

# Read each file and test queries
dashboards = os.listdir('output/dashboards')
for file in dashboards:
	parse(file)

# Output errors to json
with open('query-errors.json', 'w') as f:
    f.write(json.dumps(errors, indent=4, sort_keys=True))
