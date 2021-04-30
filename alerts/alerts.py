#!/usr/bin/env python3

import yaml
import sys
import os

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

    print("{%s}" % expr)
    # Parsing expression
    # Problems
    # - The threshold we need for New Relic is contained in the PromQL query, usually in form of >, >=, ==, <, <=
    # - Function absent needs to be converted to loss of Signal Settings in New Relic

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
                    # TODO: Replace with correct value
                    "threshold": 0,
                    "thresholdDuration": timerange,
                    # Operator on the value
                    # TODO: Replace with correct value
                    "operator": "ABOVE", # Options: ABOVE | BELOW | EQUALS
                    # How many data points must be in violation for the duration
                    "thresholdOccurrences": "ALL", # Options ALL | AT_LEAST_ONCE
                }
            ],
            # Loss of Signal Settings
            "expiration": {
                # Close open violations if signal is lost (Default: false)
                # TODO: Replace with correct value
                "closeViolationsOnExpiration": "replaceMe", # Options true | false
                # Open "Loss of Signal" violation if signal is lost (Default: false)
                # TODO: Replace with correct value
                "openViolationOnExpiration": True, # Options true | false
                # Time in seconds; Max value: 172800 (48hrs), null if closeViolationsOnExpiration and openViolationOnExpiration are both 'false'
                # TODO: Replace with correct value
                "expirationDuration": 0,
            },

            # Advanced Signal Settings
            "signal": {
                # Duration of the time window used to evaluate the NRQL Condition
                # Time in seconds; 30 - 900 (Default: 60)
                # TODO: Replace with correct value
                "aggregationWindow": 0,
                # The number of windows we look back at the aggregated data
                # Max 20 minutes, multiple of aggregationWindow
                # TODO: Replace with correct value
                "evaluationOffset": 0,
                # Type of value that should be used to fill gaps
                # TODO: Replace with correct value
                "fillOption": "replaceMe", # Options LAST_VALUE | NONE | STATIC
                # Integer; Used in conjunction with STATIC fillOption, otherwise null
                # TODO: Replace with correct value
                "fillValue": 0,
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
