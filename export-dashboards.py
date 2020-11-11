#!/usr/bin/env python3
from grafana_api.grafana_face import GrafanaFace
import json
import os
import csv
import argparse
import zipfile

# Parse arguments
parser = argparse.ArgumentParser(description='Export Grafana dashboards for processing by New Relic')
parser.add_argument('--host', type=str, help='hostname and port of Grafana instance (example: 127.0.0.1:8080)', required=True)
parser.add_argument('--token', type=str, help='api token for Grafana', required=True)
args = parser.parse_args()

# Create output directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

if not os.path.exists('output/dashboards'):
    os.makedirs('output/dashboards')

# Initiase Grafana API
print("Connecting to Grafana API")
grafana_api = GrafanaFace(auth=args.token, host=args.host)

# Get a list of all dashboards
print("Getting list of dashboards")
dashboardData = grafana_api.search.search_dashboards()
dashboardHeaders = ['id', 'title', 'tags', 'isStarred', 'url']
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
with open('output/dashboards.csv', 'w') as f:
    # creating a csv writer object
    csvwriter = csv.writer(f)

    # writing the fields
    csvwriter.writerow(dashboardHeaders)

    # writing the data rows
    csvwriter.writerows(dashboardList)

# Loop dashboards and download the json
print("Downloading JSON data for each dashboard")
for dashboard in dashboardData:
    content = grafana_api.dashboard.get_dashboard(dashboard['uid'])
    # Write dashboard json to output directory
    with open('output/dashboards/%s-%s.json' % (dashboard['uid'], dashboard['uri'].replace('db/', '')), 'w') as f:
        f.write(json.dumps(content, indent=4, sort_keys=True))

# Helper to zip directory
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

# Zip directory to share it with New Relic team
print("Create zip to share with New Relic account team")
zipf = zipfile.ZipFile('newrelic.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('output/', zipf)
zipf.close()
