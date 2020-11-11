# New Relic Migration tools for Grafana

## Grafana dashboard export tool

To export a list of all your Grafana dashboards including the JSON structure you can use `export-dashboards.py`. The script will create a zipfile called `newrelic.zip` which you can share with your New Relic account team.

To run `export-dashboards.py` you need to pass the following parameters:

* `--host`: Host and port of your Grafana instance, for example `grafana-dns:3000`
* `--token`: API Token used to authenticate with Grafana API, for more information check out Grafana docs: https://grafana.com/docs/grafana/latest/http_api/auth/#create-api-token

The content of the zip files matches what's in the `output` directory.
