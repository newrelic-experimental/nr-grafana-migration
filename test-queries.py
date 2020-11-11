#!/usr/bin/env python3
import os
import json

# Helper function that checks expression against New Relic api
def checkExpressions(tabs, expr):
    print('%s- %s' % (tabs, expr['expr']))

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
