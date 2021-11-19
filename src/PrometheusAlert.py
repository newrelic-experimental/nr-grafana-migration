import re

class PrometheusAlert:

    def __init__(self, config, conversionService, alert):
        self.failed = True
        self.name = alert['alert'] if 'alert' in alert else alert['name']
        self.expr = alert['expr'].replace('\n', '') if 'expr' in alert else alert['query'].replace('\n', '')
        self.severity = 'critical'.upper()
        self.timerange = alert['for'] if 'for' in alert else 5
        self.message = ""
        self.runbook_url = ""
        if 'labels' in alert:
            if 'severity' in alert['labels']:
                self.severity = alert['labels']['severity']
        if 'severity' in alert:
            self.severity = alert['severity']
        if 'annotations' in alert:
            if 'message' in alert['annotations']:
                self.message = alert['annotations']['message']
            if 'runbook_url' in alert['annotations']:
                self.runbook_url = alert['annotations']['runbook_url']
        if 'description' in alert:
            self.message = alert['description']

        # Detect absent and parse out query
        absent = False
        match = re.search(r'^absent\((.*)\)$', self.expr)
        if match:
            absent = True
            self.expr = match.group(1)

        # Split expression
        match = re.search(r'^(.*)(==|>|<|<=|>=|!=)(.*)$', self.expr)
        if match is None:
            print("Error parsing expression, can't find operator %s", self.expr)
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
            print("Error parsing expression, unsupported operator %s", self.expr)
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
            self.threshold = eval(match.group(1))

        match = re.search(reNumber, right)
        if match:
            isRightThreshold = True
            self.threshold = eval(match.group(1))

        if not isLeftThreshold and not isRightThreshold:
            print("Error parsing expression, no threshold found (maybe multi query): %s", self.expr)
            return

        # Set the query to the not threshold side
        if isLeftThreshold:
            self.expr = right

        if isRightThreshold:
            self.expr = left

        # Now that we have everything ready, we convert the PromQL query to New Relic NRQL
        try:
            self.nrql = conversionService.convertQuery(self.expr)
        except:
            print("Conversion to NRQL failed for %s" % self.expr)
            return

        # Conversion complete
        self.failed = False

    def getNRAlert(self):
        return {
            # Name of the alert
            "name": self.name,
            # Description and details
            "description": self.message,
            # Type of alert
            "type": "static",
            # NRQL query
            "nrql": {
                "query": self.nrql
            },
            # Function used to aggregate the NRQL query value(s) for comparison to the terms.threshold (Default: SINGLE_VALUE)
            "valueFunction": "SINGLE_VALUE", # Options: SINGLE_VALUE | SUM"
            # List of Critical and Warning thresholds for the condition
            "terms": [
                {
                    "priority": self.severity,
                    # Value that triggers a violation
                    "threshold": self.threshold,
                    "thresholdDuration": self.timerange,
                    # Operator on the value
                    "operator": self.operator, # Options: ABOVE | BELOW | EQUALS
                    # How many data points must be in violation for the duration
                    "thresholdOccurrences": "ALL", # Options ALL | AT_LEAST_ONCE
                }
            ],
            # Loss of Signal Settings
            "expiration": {
                # Close open violations if signal is lost (Default: false)
                "closeViolationsOnExpiration": True, # Options true | false
                # Open "Loss of Signal" violation if signal is lost (Default: false)
                "openViolationOnExpiration": self.absent, # Options true | false
                # Time in seconds; Max value: 172800 (48hrs), null if closeViolationsOnExpiration and openViolationOnExpiration are both 'false'
                # Default to one day
                "expirationDuration": 86400,
            },
            "runbookUrl": self.runbook_url
        }
