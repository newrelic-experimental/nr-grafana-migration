#!/usr/bin/env python3
import argparse
import json
import math
import requests

verbose = True

# Parse arguments
parser = argparse.ArgumentParser(description='Convert Grafana dashboards to import into New Relic')
parser.add_argument('dashboard', metavar='path', type=str, help='Grafana json file you want to convert to New Relic')
args = parser.parse_args()

# Read config file
with open('config.json', 'r') as f:
    config = json.load(f)

apiUsername = config['auth']['username']
apiPassword = config['auth']['password']
apiAccountId = config['api']['accountId']
apiToken = config['api']['token']

# Login to New Relic
session = requests.Session()
session.hooks = {
    'response': lambda r, *args, **kwargs: r.raise_for_status()
}

login_data = {
    "login[email]": apiUsername,
    "login[password]": apiPassword
}
login_response = session.post("https://login.newrelic.com/login", data = login_data)

# Read file
with open(args.dashboard, 'r') as f:
    data = json.load(f)

# Read out vars
dashboardName = data['dashboard']['title']

# Result widgets
widgets = []

# Helpers functions
def convertQuery(promql):
    custom_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json"
    }
    nrql = session.post("https://promql-gateway.service.newrelic.com/api/v1/translate", headers=custom_headers, json={
        "promql": promql,
        "account_id": apiAccountId,
        "isRange": True,
        "startTime": "null",
        "endTime": "null",
        "step": 30
    })
    data = nrql.json()
    print(f'{promql} returned NRQL: {data}')

    return data['nrql']

def convertQueries(targets):
    queries = []
    for target in targets:
        if 'format' in target and target['format'] == 'time_series':
            queries.append({
                "accountId": apiAccountId,
                "query": convertQuery(target['expr'])
            })

    if len(queries) == 0:
        raise Exception('No queries found for {}'.format(targets))

    return {
        "nrqlQueries": queries
    }

def convertPanel(panel):
    widgetTitle = panel['title']
    panelType = panel['type']

    # New Relic supported graph types
    visualisation = None
    try:
        rawConfiguration = convertQueries(panel['targets'])

        if panelType == 'graph':
            visualisation = "viz.line"
        else:
            # No idea what to do with this
            raise Exception('Unknown type {}'.format(panel))

    except Exception as err:
        # Nullify all except Markdown to store error
        visualisation = "viz.markdown"
        rawConfiguration = {
            "text": json.dumps({
                "exception": type(err).__name__,
                "arguments": err.args
            })
        }

    # Coordinate conversion
    # Grafana has 24 column dashboards and New Relic has 12
    # We now devide by two and floor, but this will cause problems so a more complicate conversion method is needed
    # One height in New Relic = 3 heights in Grafana (Visually estimated)
    panelColumn = math.floor(panel['gridPos']['x'] / 2) + 1
    panelWidth = math.floor(panel['gridPos']['w'] / 2)
    panelRow = math.floor(panel['gridPos']['y'] / 3) + 1 # Grafana starts at 0, New Relic at 1
    panelHeight = math.ceil(panel['gridPos']['h'] / 3)

    # Append widget to dashboard
    widgets.append({
        "id": panel['id'],
        "visualization": {
            "id": visualisation,
        },
        "layout": {
            "column": panelColumn,
            "row": panelRow,
            "height": panelHeight,
            "width": panelWidth
        },
        "title": widgetTitle,
        "rawConfiguration": rawConfiguration
    })

# Loop panels, handy if we have panels in panels
def parsePanels(panels):
    for panel in panels:
        if 'panels' in panel:
            parsePanels(panel['panels'])
        else:
            convertPanel(panel)

# Start converting process
parsePanels(data['dashboard']['panels'])

# Create dashboard in New Relic account
newrelic = {
    "name": dashboardName,
    "description": "",
    "permissions": "PUBLIC_READ_WRITE",
    "pages": [
        {
            "name": dashboardName,
            "description": "",
            "widgets": widgets,
        }
    ],

}

output = json.dumps(newrelic, indent=4, sort_keys=True)
print(output)
f = open("export.json", "w")
f.write(output)
f.close()
