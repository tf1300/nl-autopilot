#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import time

# Create a metric to track sandbox application success.
sandbox_apply_success = Gauge('sandbox_apply_success', 'Sandbox application success', ['ats'])

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9464)
    # Set the gauge to 1 to simulate a successful run.
    sandbox_apply_success.labels(ats='greenhouse').set(1)
    # Keep the script running.
    while True:
        time.sleep(1)
