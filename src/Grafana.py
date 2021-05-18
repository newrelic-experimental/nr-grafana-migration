import os
import csv
import json
from grafana_api.grafana_face import GrafanaFace
import src.utils.constants as constants
import questionary

class Grafana:

    def __init__(self, config):
        self.apiKey = config['grafana']['apiKey']
        self.host = config['grafana']['host']
        self.createOutputDir()
        self.dahboardsPaths = []

        # Initiase Grafana API
        print("Connecting to Grafana API")
        self.grafana_api = GrafanaFace(auth=self.apiKey, host=self.host, protocol='https')
    
    def createOutputDir(self):
        # Create output directory if it doesn't exist
        if not os.path.exists(constants.OUTPUT_DIR):
            os.makedirs(constants.OUTPUT_DIR)

        if not os.path.exists(constants.GRAFANA_OUTPUT_DIR):
            os.makedirs(constants.GRAFANA_OUTPUT_DIR)
    
    def selectGrafanaDashboards(self):

        # Get a list of all dashboards
        print("Getting list of dashboards")
        dashboardData = self.grafana_api.search.search_dashboards()
        dashboardHeaders = ['id', 'title', 'tags', 'isStarred', 'url']

        print('\n')
        dashboards = questionary.checkbox('Select the Grafana Dashboards you woul like to migrate (based on dashboards URLs):', choices=[elem['url'] for elem in dashboardData]).ask()
        # Keep only selected dashboards
        dashboardData = [elem for elem in dashboardData if elem['url'] in dashboards]
        
        self.saveToOutput(dashboardData, dashboardHeaders)
        return self.dahboardsPaths
        
    def saveToOutput(self, dashboardData, dashboardHeaders):
        dashboardList = []
        for dashboard in dashboardData:
            dashboardList.append([
                dashboard['id'],
                dashboard['title'],
                ', '.join(dashboard['tags']),
                dashboard['isStarred'],
                dashboard['url']
            ])
        # Output list to csv
        print("Exporting to CSV")
        with open(constants.GRAFANA_DASHBOARD_LIST_CSV, 'w') as f:
            # creating a csv writer object
            csvwriter = csv.writer(f)

            # writing the fields
            csvwriter.writerow(dashboardHeaders)

            # writing the data rows
            csvwriter.writerows(dashboardList)

        # Output list to json
        with open(constants.GRAFANA_DASHBOARD_LIST_JSON, 'w') as f:
            f.write(json.dumps(dashboardData, indent=4, sort_keys=True))

        # Loop dashboards and download the json
        print("Downloading JSON data for each dashboard")
        for dashboard in dashboardData:
            content = self.grafana_api.dashboard.get_dashboard(dashboard['uid'])
            dashboardPath = f'{constants.GRAFANA_OUTPUT_DIR}/%s-%s.json' % (dashboard['uid'], dashboard['uri'].replace('db/', ''))
            self.dahboardsPaths.append(dashboardPath)
            # Write dashboard json to output directory
            with open(dashboardPath, 'w') as f:
                f.write(json.dumps(content, indent=4, sort_keys=True))