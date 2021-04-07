import yaml
import sys
import os

# Create output directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

def processAlert(alert):
    name = alert['alert']
    expr = alert['expr'].replace('\n', '')
    severity = 'critical'
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

    with open("output/%s.yml" % name, 'w') as yamlfile:
        yaml.dump({
            "name": name,
            "expr": expr,
            "severity": severity,
            "timerange": timerange,
            "message": message,
            "runbook_url": runbook_url
        }, yamlfile, sort_keys = True, default_flow_style=False, width=1000)


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
