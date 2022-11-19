

from src.PromQL2NrqlService import PromQL2NrqlService
from src.PrometheusAlert import PrometheusAlert


class AlertFile:

    def __init__(self, config, prometheusData):
        self.alerts = []
        self.config = config
        self.conversionService = PromQL2NrqlService(self.config)

        # Detect what kind of file it is and process
        # Kubernetes
        if 'spec' in prometheusData:
            for group in prometheusData['spec']['groups']:
                self.processGroup(group)
        # Groups
        elif 'groups' in prometheusData:
            for group in prometheusData['groups']:
                for service in group['services']:
                    for exporter in service['exporters']:
                        self.processGroup(exporter)


    # Loop through rules in a group
    def processGroup(self, group):
        if 'rules' in group and type(group['rules']) is list:
            for rule in group['rules']:
                self.processRule(rule)

    # Check if an alert is set, and if so process it
    def processRule(self, rule):
        if 'alert' in rule or 'name' in rule:
            self.alerts.append(PrometheusAlert(self.config, self.conversionService, rule))

    def getAlerts(self):
        return self.alerts
