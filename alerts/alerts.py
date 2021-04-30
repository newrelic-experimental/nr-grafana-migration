#!/usr/bin/env python3

import yaml
import sys
import os
import re

# Create output directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

def processAlert(alert):
    name = alert['alert']
    expr = alert['expr'].replace('\n', '')
    severity = 'critical'.upper()
    timerange = alert['for'] if 'for' in alert else 5
    message = ""
    runbook_url = ""
    if 'labels' in alert:
        if 'severity' in alert['labels']:
            severity = alert['labels']['severity']
    if 'annotations' in alert:
        if 'message' in alert['annotations']:
            message = alert['annotations']['message']
        if 'runbook_url' in alert['annotations']:
            runbook_url = alert['annotations']['runbook_url']

    # Detect absent and parse out query
    absent = False
    match = re.search(r'^absent\((.*)\)$', expr)
    if match:
        absent = True
        expr = match.group(1)

    # Split expression
    match = re.search(r'^(.*)(==|>|<|<=|>=|!=)(.*)$', expr)
    if match is None:
        print("Error parsing expression, can't find operator %s", expr)
        return
    left = match.group(1).strip()
    operator = match.group(2).strip()
    right = match.group(3).strip()

    # Convert operator to New Relic format
    if operator == "==":
        operator = "EQUALS"
    elif operator == ">":
        operator = "ABOVE"
    elif operator == "<":
        operator = "BELOW"
    else:
        print("Error parsing expression, unsupported operator %s", expr)
        return

    # Figure out which is the treshold and which is the query
    # if both are queries fail
    # We do this by checking if it's only numbers and aritmatic expressions
    reNumber = r'^([0-9. *+-/])*$'
    isLeftThreshold = False
    isRightThreshold = False
    match = re.search(reNumber, left)
    if match:
        isLeftThreshold = True
        threshold = eval(match.group(1))

    match = re.search(reNumber, right)
    if match:
        isRightThreshold = True
        threshold = eval(match.group(1))

    if not isLeftThreshold and not isRightThreshold:
        print("Error parsing expression, no threshold found (maybe multi query): %s", expr)
        return

    # Set the query to the not threshold side
    if isLeftThreshold:
        expr = right

    if isRightThreshold:
        expr = left

    # Write out alert
    with open("output/%s.yml" % name, 'w') as yamlfile:
        # This is the New Relic alerts format
        yaml.dump({
            # Name of the alert
            "name": name,
            # Description and details
            "description": message,
            # Type of alert
            "type": "static",
            # NRQL query
            "nrql": {
                "query": expr # Needs to be translated
            },
            # Function used to aggregate the NRQL query value(s) for comparison to the terms.threshold (Default: SINGLE_VALUE)
            "valueFunction": "SINGLE_VALUE", # Options: SINGLE_VALUE | SUM"
            # List of Critical and Warning thresholds for the condition
            "terms": [
                {
                    "priority": severity,
                    # Value that triggers a violation
                    "threshold": threshold,
                    "thresholdDuration": timerange,
                    # Operator on the value
                    "operator": operator, # Options: ABOVE | BELOW | EQUALS
                    # How many data points must be in violation for the duration
                    "thresholdOccurrences": "ALL", # Options ALL | AT_LEAST_ONCE
                }
            ],
            # Loss of Signal Settings
            "expiration": {
                # Close open violations if signal is lost (Default: false)
                "closeViolationsOnExpiration": True, # Options true | false
                # Open "Loss of Signal" violation if signal is lost (Default: false)
                "openViolationOnExpiration": absent, # Options true | false
                # Time in seconds; Max value: 172800 (48hrs), null if closeViolationsOnExpiration and openViolationOnExpiration are both 'false'
                # Default to one day
                "expirationDuration": 86400,
            },
            "runbookUrl": runbook_url
        }, yamlfile, default_flow_style=False, width=1000)


def processRule(rule):
    if 'alert' in rule:
        processAlert(rule)

def processGroup(group):
    for rule in group['rules']:
        processRule(rule)

with open('examples/prometheus-rules.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    prometheusRule = yaml.load(file, Loader=yaml.FullLoader)

for group in prometheusRule['spec']['groups']:
    processGroup(group)
