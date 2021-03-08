#!/usr/bin/env python3
import argparse
import json
import math
import requests
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
if args.verbose:
    print("-------------------- Grafana JSON --------------------")
    print(data)

# Read out vars
dashboardName = data['dashboard']['title']

# Result pages
pages = list()

# Helpers functions
def convertQuery(promql, range=True):
    custom_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json"
    }
    nrql = session.post("https://promql-gateway.service.newrelic.com/api/v1/translate", headers=custom_headers, json={
        "promql": promql,
        "account_id": apiAccountId,
        "isRange": range,
        "startTime": "null",
        "endTime": "null",
        "step": 30
    })
    data = nrql.json()
    if args.verbose:
        print(f'{promql} returned NRQL: {data}')

    return data['nrql']

def convertQueries(targets, range=True):
    queries = []
    for target in targets:
        if 'format' in target and target['format'] == 'time_series':
            queries.append({
                "accountId": apiAccountId,
                "query": convertQuery(target['expr'], range=range)
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
        # Detect visualisation
        range = True
        limit = None
        if panelType == 'graph':
            visualisation = "viz.line"
        elif panelType == 'singlestat':
            visualisation = "viz.billboard"
            range = False
        elif panelType == 'gauge':
            visualisation = "viz.bullet"
            range = False

            if 'gauge' in panel and 'maxValue' in panel['gauge']:
                limit = panel['gauge']['maxValue']

            if 'fieldConfig' in panel and 'defaults' in panel['fieldConfig'] and 'max' in panel['fieldConfig']['defaults']:
                limit = panel['fieldConfig']['defaults']['max']
            '''try: 
                limit = panel['options']['fieldOptions']['defaults']['max']
            except KeyError:
                    # Don't catch exception here and throw error because limit is manadatory for bullet viz
                    limit = panel['gauge']['maxValue']'''
            
        else:
            # No idea what to do with this
            raise Exception('Unknown type {}'.format(panel))

        # Parse queries
        rawConfiguration = convertQueries(panel['targets'], range=range)
        if limit:
            rawConfiguration['limit'] = limit

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
    panelRow = math.floor(panel['gridPos']['y'] / 2) + 1 # Grafana starts at 0, New Relic at 1
    panelHeight = math.ceil(panel['gridPos']['h'] / 2)

    # Append widget to dashboard
    widget = {
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
    }

    return widget

# For collapse = true , you have to put row’s pannels inside the row definition , in panels[ ] section.
# For collapse = false, you have to put row’s pannels below the row definition.
def parsePanels(panels):
    '''for panel in panels:
        if 'panels' in panel:
            parsePanels(panel['panels'])
        else:
            convertPanel(panel)'''

    page = { "name": "","description": "","widgets": []}
    succesivePanels = False

    for panel in panels:
        if panel['type'] == 'row':
            if succesivePanels:
                pages.append(page)
                succesivePanels = False
                page = { "name": "","description": "","widgets": []}

            page['name'] = panel['title']
            if panel['collapsed']:
                for nestedPanel in panel['panels']:
                    page['widgets'].append(convertPanel(nestedPanel))
                pages.append(page)
                page = { "name": "","description": "","widgets": []}
            else:
                succesivePanels = True
        else:
            page['widgets'].append(convertPanel(panel))
            
    ## Edge cases ##
    # If last row is not collapsed don't forget to add last row's panels
    if succesivePanels:
        pages.append(page)
    # Don't forget to add any panel that don't belong to a row at the end of Grafana dashboard to the last NR page
    elif page['widgets']:
        if pages:
            pages[-1]['widgets'].extend(page['widgets'])
        ## in case no rows in the grafana dashboard
        else:
            pages.append({ "name": dashboardName,"description": "","widgets": page['widgets']})


# Start converting process
if args.verbose:
    print("-------------------- Starting conversion --------------------")
parsePanels(data['dashboard']['panels'])

# Create dashboard in New Relic account
newrelic = {
    "name": dashboardName,
    "description": "",
    "permissions": "PUBLIC_READ_WRITE",
    "pages": pages,
}

# Create pretty json
output = json.dumps(newrelic, indent=4, sort_keys=True)
if args.verbose:
    print("-------------------- New Relic JSON --------------------")
    print(output)

# Write out file
f = open("output/newrelic/newrelic-%s" % os.path.basename(args.dashboard), "w")
f.write(output)
f.close()
