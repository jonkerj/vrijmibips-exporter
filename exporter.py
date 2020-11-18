#!/usr/bin/env python

import argparse
import re
import time
import requests
from bs4 import BeautifulSoup
from prometheus_client import start_http_server, Gauge


def scrape_value(url, select, regex):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	r = re.compile(regex)
	value = '0'
	for element in soup.select(select):
		m = r.match(element.text)
		if m:
			try:
				v = int(m.group(1))
				value = v
			except (ValueError, IndexError):
				pass
	return value
	

if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument('--url', help='URL of the item to watch', required=True)
	p.add_argument('--select', dest='select', help='CSS selector to find element', default='body p.in-stock')
	p.add_argument('--regex', dest='regex', help='Regex to extract value', default='^(\d+).*$')
	p.add_argument('--metric', dest='metric', help='Name of the metric', default='stock')
	p.add_argument('--description', dest='description', help='Description of the metric', default='Items in stock')
	p.add_argument('--port', dest='port', help='Port to run the metrics server on', type=int, default=8000)
	args = p.parse_args()

	p = Gauge(args.metric, args.description)
	p.set_function(lambda: scrape_value(args.url, args.select, args.regex))
	start_http_server(args.port)
	while True:
		time.sleep(1)
