#!/usr/bin/env python3

import argparse
import json
from src.PromQL2NrqlService import PromQL2NrqlService
from src.Dashboard import Dashboard
import os

# Parse arguments
parser = argparse.ArgumentParser(description='Convert Grafana dashboards to import into New Relic')
parser.add_argument('dashboard', metavar='path', type=str, help='Grafana json file you want to convert to New Relic')
parser.add_argument('-v', '--verbose', action="store_true", help='Run in verbose mode')
args = parser.parse_args()

# Create output directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

if not os.path.exists('output/newrelic'):
    os.makedirs('output/newrelic')

# Read config file
with open('config.json', 'r') as f:
    config = json.load(f)

# Initiate PromQL2NrqlService provider
apiUsername = config['auth']['username']
apiPassword = config['auth']['password']
apiAccountId = config['api']['accountId']
promQL2NrqlService = PromQL2NrqlService(apiUsername, apiPassword, apiAccountId)

# Read file
with open(args.dashboard, 'r') as f:
    data = json.load(f)
if args.verbose:
    print("-------------------- Grafana JSON --------------------")
    print(data)

# Create and parse dashboard
if args.verbose:
    print("-------------------- Starting conversion --------------------")
dashboard = Dashboard(promQL2NrqlService, data)

# Create pretty json
output = json.dumps(dashboard.toJSON(), indent=4, sort_keys=True)
if args.verbose:
    print("-------------------- New Relic JSON --------------------")
    print(output)

# Write out file
f = open("output/newrelic/newrelic-%s" % os.path.basename(args.dashboard), "w")
f.write(output)
f.close()

# Close query cache
promQL2NrqlService.saveCache()
