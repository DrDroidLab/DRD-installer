import requests
from datetime import datetime, timedelta

import json
from openpyxl import Workbook

import os

# Grafana API parameters
GRAFANA_URL = os.getenv('GRAFANA_HOST')
GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY')

# Prometheus API parameters
PROMETHEUS_QUERY_RANGE_URL = os.getenv('PROMETHEUS_HOST') + "/api/v1/query_range"

# Function to fetch alerts from Grafana
def fetch_alerts():
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"{GRAFANA_URL}/api/v1/provisioning/alert-rules", headers=headers)
    alerts = response.json()
    return alerts


def fetch_datasources():
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"{GRAFANA_URL}/api/datasources", headers=headers)
    alerts = response.json()
    return alerts

# Function to query Prometheus for metric values with 5 minute resolution for past 60 minutes
def query_prometheus(metric_query):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=60*24*7)

    url = PROMETHEUS_QUERY_RANGE_URL + '?query={}&start={}&end={}&step={}'.format(metric_query, datetime.strftime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ'), datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ'), "1m")

    response = requests.get(url)
    data = response.json()
    return data

# Main function
def main():

    # fetch datasources
    datasources = fetch_datasources()
    prometheus_datasources = []
    for ds in datasources:
        if ds['type'] == 'prometheus':
            prometheus_datasources.append(ds['uid'])

    data_source_metrics_exprs_dict = {}

    wb = Workbook()
    alerts_ws = wb.active
    alerts_ws.title = "alerts"
    alerts_ws['A1'] = 'UID'
    alerts_ws['B1'] = 'Title'
    alerts_ws['C1'] = 'JSON'

    alert_row_index = 1
    # Fetch alerts from Grafana
    alerts = fetch_alerts()
    # Process each alert
    for alert in alerts:
        alerts_ws[f"A{alert_row_index}"] = alert['uid']
        alerts_ws[f"B{alert_row_index}"] = alert['title']
        alerts_ws[f"C{alert_row_index}"] = json.dumps(alert)

        for data in alert['data']:
            if data.get('datasourceUid') and data.get('datasourceUid') in prometheus_datasources:
                if data.get('datasourceUid') not in data_source_metrics_exprs_dict:
                    data_source_metrics_exprs_dict[data.get('datasourceUid')] = []
                if data['model'].get('expr'):
                    data_source_metrics_exprs_dict[data.get('datasourceUid')].append(data['model'].get('expr'))

    metrics_ws = wb.create_sheet(title="metrics")
    metrics_ws['A1'] = 'Metric Query'
    metrics_ws['B1'] = 'Metric Values'

    metric_row_index = 1

    for ds_id in prometheus_datasources[:1]:
        for metric_query in data_source_metrics_exprs_dict[ds_id][:1]:
            metric_values = query_prometheus(metric_query)
            metrics_ws[f"A{metric_row_index}"] = metric_query
            metrics_ws[f"B{metric_row_index}"] = json.dumps(metric_values)

    wb.save('imported_metrics.xlsx')


if __name__ == "__main__":
    main()
