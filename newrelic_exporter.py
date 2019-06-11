#!/usr/bin/python

import time
import requests
import click

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY


class NewrelicCollector(object):
  def __init__(self, apikey):
    self.api_base_url = 'https://api.newrelic.com/'
    self.api_key = apikey

  def collect(self):

    headers = {'X-Api-Key': self.api_key  }
    resp  = requests.get(self.api_base_url + 'v2/applications.json', headers=headers)

    # The metrics we want to export.
    metrics = {'response_time': GaugeMetricFamily('newrelic_application_response_time',' newrelic application response in sec', labels=["appname"]),
    'throughput': GaugeMetricFamily('newrelic_application_throughput',' newrelic application throughput',labels=["appname"]),
    'error_rate': GaugeMetricFamily('newrelic_application_error_rate',' newrelic application error_rate', labels=["appname"]),
    'apdex_target': GaugeMetricFamily('newrelic_application_apdex_target',' newrelic application apdex_target', labels=["appname"]),
    'apdex_score': GaugeMetricFamily('newrelic_application_apdex_score',' newrelic application apdex_score', labels=["appname"]),
    }

    for metric in metrics:
      for app in resp.json().get('applications',{}):
        if app.get('application_summary'):
          metrics[metric].add_metric([app['name']], app['application_summary'][metric])
      yield metrics[metric]

@click.command()
@click.option('--api-key', '-a', envvar='APIKEY', help='API key for newrelic', required=True)
def main(api_key):
  REGISTRY.register(NewrelicCollector(api_key))
  start_http_server(9126)
  while True: 
    time.sleep(1)
if __name__ == "__main__":
  main()


