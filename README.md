# DRD-installer
Repository with script and instructions

Run these commands to share with our script the endpoints and keys to Grafana & Prometheus:

```
export GRAFANA_HOST=http://localhost:3000
export GRAFANA_API_KEY=YOUR_KEY_HERE
```

For the API key, create a service account in Grafana with admin access and create a service account token.
After the variables are setup, run the script (needs python3):

```
pip install openpyxl requests
python3 import_alert_metrics.py
```

Please note: In this script, it is assumed that you have a datasource by the name, 'prometheus', which is the source of metrics used for alerts.
