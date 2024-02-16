<a href="https://opensource.newrelic.com/oss-category/#archived"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/newrelic/opensource-website/raw/main/src/images/categories/dark/Archived.png"><source media="(prefers-color-scheme: light)" srcset="https://github.com/newrelic/opensource-website/raw/main/src/images/categories/Archived.png"><img alt="New Relic Open Source archived project banner." src="https://github.com/newrelic/opensource-website/raw/main/src/images/categories/Archived.png"></picture></a>

# Archival Notice

❗Notice: This project has been archived _as is_ and is no longer actively maintained.

# New Relic Migration tool for Grafana

## Installation

### Requirements

- Python v3 & pip3
- `pip3 install -r requirements.txt`

## Getting Started

`python3 main.py`

## Usage

### Configuration Details
The tool will guide you through the needed configuration information.
The configuration will be requested only the first time you run the script. Future executions will use the `config.json` generated during the first execution. You can update this config file at any time if needed.

A `cache.json` will be generated as well where you can see the translated queries. This file is used to speed up the process in case of redundant queries in your dashboards.

Authentication is required as part of the configuration. Why?  because this tool is using an API that is not exposed via NR GraphQL schema.
- For SSO authenticated users: we will collect New Relic browser cookie and use it for authentication.
- For Non SSO users: you will be required to enter your username and password.

The script will guide you through the needed configuration for each case.

For New Relic, make sure to use a user API key. [Create one if needed](https://docs.newrelic.com/docs/apis/get-started/intro-apis/new-relic-api-keys/#user-key-create).

For Grafana, make sure you have an API key (you may need to be an admin in order to [generate one](https://grafana.com/docs/grafana-cloud/cloud-portal/create-api-key/)).

## Troubleshooting

Check the output folder to see the Grafana and New Relic dashbaords JSON files.
You can also check the list of migrated dashboards in `dashboards.csv` and `dashboards.json`.

## Contributing
We encourage your contributions to improve New Relic Migration tool for Grafana! Keep in mind when you submit your pull request, you'll need to sign the CLA via the click-through using CLA-Assistant. You only have to sign the CLA one time per project.
If you have any questions, or to execute our corporate CLA, required if your contribution is on behalf of a company,  please drop us an email at opensource@newrelic.com.

**A note about vulnerabilities**

As noted in our [security policy](../../security/policy), New Relic is committed to the privacy and security of our customers and their data. We believe that providing coordinated disclosure by security researchers and engaging with the security community are important means to achieve our security goals.

If you believe you have found a security vulnerability in this project or any of New Relic's products or websites, we welcome and greatly appreciate you reporting it to New Relic through [HackerOne](https://hackerone.com/newrelic).

## License
New Relic Migration tool for Grafana is licensed under the [Apache 2.0](http://apache.org/licenses/LICENSE-2.0.txt) License.
