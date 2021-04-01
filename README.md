# New Relic Migration tool for Grafana

## Requirements

- Python v3 & pip3
- `pip3 install -r requirements.txt`

## Get Started
`python3 main.py`

## Configuration Details
The tool will guide you through the needed configuration information.
The configuration will be requested only the first time you run the script. Future executions will use the `config.json` generated during the first execution. You can update this config file at any time if needed.

A `cache.json` will be generated as well where you can see the translated queries. This file is used to speed up the process in case of redundant queries in your dashboards.

Authentication is required as part of the configuration. Why?  because this tool is using an API that is not exposed via NR GraphQL schema.
- For SSO authenticated users: we will collect New Relic browser cookie and use it for authentication.
- For Non SSO users: you will be required to enter your username and password.

The script will guide you through the needed configuration for each case.

For New Relic, make sure to use a user API key. [Create one if needed](https://docs.newrelic.com/docs/apis/get-started/intro-apis/new-relic-api-keys/#user-key-create).

For Grafana, make sure you have an API key (you may need to be an admin in order to [generate one](https://grafana.com/docs/grafana-cloud/cloud-portal/create-api-key/)).

## Troubelshoot

Check the output folder to see the Grafana and New Relic dashbaords JSON files. 
You can also check the list of migrated dashboards in `dashboards.csv` and `dashboards.json`.