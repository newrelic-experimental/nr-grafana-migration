import json
import os
import yaml
import src.utils.constants as constants


class Crossplane:

    def convert(self, nrDashboard):
        provider_name = "newrelic-provider"

        # Read file
        with open(nrDashboard, 'r') as f:
            data = json.load(f)

        for pages in data['pages']:
            for widget in pages['widgets']:
                if 'id' in widget:
                    del widget['id']
                if 'text' in widget['rawConfiguration']:
                    widget["visualization"]['id'] = "viz.markdown"
                else:
                    widget["visualization"]['id'] = "viz.line"

        pre, ext = os.path.splitext(nrDashboard)
        dashboardJson = {
            "apiVersion": "dashboard.provider-newrelic.crossplane.io/v1alpha1",
            "kind": "Dashboard",
            "metadata": {"name": os.path.basename(pre).lower()},
            "spec": {
                "deletionPolicy": "Delete",
                "forProvider": data,
                "providerConfigRef": {
                    "name": provider_name
                }
            }}

        # Create yaml
        output = yaml.dump(dashboardJson, default_flow_style=False)
        # Write out file
        filePath = f"{constants.NEWRELIC_OUTPUT_DIR}/crossplane-%s.yaml" % os.path.basename(pre)
        f = open(filePath, "w")
        f.write(output)
        f.close()

        return filePath
