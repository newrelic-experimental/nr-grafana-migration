#!/usr/bin/env python3
import argparse
import json
import math

verbose = True

# Parse arguments
parser = argparse.ArgumentParser(description='Convert Grafana dashboards to import into New Relic')
parser.add_argument('dashboard', metavar='path', type=str, help='Grafana json file you want to convert to New Relic')
parser.add_argument('--accountId', type=int, help='New Relic account id', required=True)
args = parser.parse_args()

# Read file
with open(args.dashboard, 'r') as f:
    data = json.load(f)
if verbose:
    print(json.dumps(data, indent=4, sort_keys=True))

# Read out vars
accountId = args.accountId
dashboardName = data['dashboard']['title']

# Helpers functions
def convertQuery(promql):
    # TODO: Insert magic converter
    return promql

def convertQueries(targets):
    queries = []
    for target in targets:
        if 'format' in target and target['format'] == 'time_series':
            queries.append({
                "accountId": accountId,
                "nrql": convertQuery(target['expr'])
            })

    return queries


# Read out Grafana panels and convert to New Relicwidgets
widgets = []
for panel in data['dashboard']['panels']:
    widgetTitle = panel['title']
    panelType = panel['type']

    # New Relic supported graph types
    widgetTypeArea = None
    widgetTypeLine = None
    widgetTypeBar = None
    widgetTypeBillboard = None
    widgetTypePie = None
    widgetTypeTable = None
    widgetTypeMarkdown = None

    if panelType == 'graph':
        widgetTypeLine = {
            "queries": convertQueries(panel['targets'])
        }

    # Coordinate conversion
    # Grafana has 24 column dashboards and New Relic has 12
    # We now devide by two and floor, but this will cause problems so a more complicate conversion method is needed
    panelColumn = math.floor(panel['gridPos']['x'] / 2)
    panelWidth = math.floor(panel['gridPos']['w'] / 2)
    panelRow = panel['gridPos']['y']
    panelHeight = panel['gridPos']['h']

    # Append widget to dashboard
    widgets.append({
        "visualization": {},
        "layout": {
            "column": panelColumn,
            "row": panelRow,
            "height": panelHeight,
            "width": panelWidth
        },
        "title": widgetTitle,
        "configuration": {
            "area": widgetTypeArea,
            "line": widgetTypeLine,
            "bar": widgetTypeBar,
            "billboard": widgetTypeBillboard,
            "pie": widgetTypePie,
            "table": widgetTypeTable,
            "markdown": widgetTypeMarkdown
        },
        "rawConfiguration": {
            "queries": convertQueries(panel['targets'])
        },
    })

# Output New Relic dashboard
newrelic = {
    "name": dashboardName,
    "description": "",
    "pages": [
        {
            "name": dashboardName,
            "description": "",
            "widgets": widgets,
        }
    ],

}

print(json.dumps(newrelic, indent=4, sort_keys=True))
