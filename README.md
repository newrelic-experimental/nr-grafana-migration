# New Relic Migration tools for Grafana

## Requirements

- Python v3 & pip3
- `pip3 install -r requirements.txt`

## Configuration

To use these tools you need to copy `config.json.example` to `config.json` and enter the account details:

```
"auth": {
        "username": "[ YOUR NEW RELIC USERNAME ]",
        "password": "[ YOUR NEW RELIC PASSWORD ]"
},
"api": {
    "token": "[ USER API TOKEN ]",
    "accountId": "[ ACCOUNT ID WHERE YOU WANT TO IMPORT THE DASHBOARDS ]"
}
```

## Scripts

### Grafana dashboard export tool

To export a list of all your Grafana dashboards including the JSON structure you can use `get-grafana-dashboards.py`. The script will create a zipfile called `newrelic.zip` which you can share with your New Relic account team.

To run `get-grafana-dashboards.py` you need to pass the following parameters:

* `--host`: Host and port of your Grafana instance, for example `grafana-dns:3000`
* `--token`: API Token used to authenticate with Grafana API, for more information check out Grafana docs: https://grafana.com/docs/grafana/latest/http_api/auth/#create-api-token

The content of the zip files matches what's in the `output` directory.

### Grafana dashboard conversion tool

To convert a Grafana dashboard to New Relic you can use `convert-dashboard.py`. The script will take a path to a Grafana dashboard json and create a file with same name in `output/newrelic`.

Use the following command to convert a dashboard from Grafana to New Relic: `./convert-dashboard.py output/grafana/[DASHBOARD NAME].json`.

## New Relic import dashboard tool

To import a New Relic dashboard you can use `import-dashboard.py`. The script will take a path to a New Relic dashboard json and import it into the account defined in `config.json`.

Use the following command to import a New Relic dashboard JSON in New Relic: `./import-dashboard.py output/newrelic/[DASHBOARD NAME].json`.
