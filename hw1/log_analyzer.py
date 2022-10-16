#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import argparse
import os
import re
import json
import logging
import statistics
import datetime
from collections import namedtuple, defaultdict
from string import Template

DEFAULT_CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "OUTPUT_FILE": None
}

TEMPLATE_LOG_FILE = re.compile(r"^nginx-access-ui\.log-(?P<date>\d{8})(?P<ext>\.gz|)?$")

TEMPLATE_LOG = re.compile(
    r'(?P<remote_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(?P<remote_user>.*?)\s+'
    r'(?P<http_x_real_ip>.*?)\s+\[(?P<time_local>.*?)\]\s+\"(?P<request_method>.*?)\s+'
    r'(?P<url>.*?)(?P<request_version>\s+HTTP/.*)?\"\s+(?P<status>.*?)\s+'
    r'(?P<body_bytes_sent>.*?)\s+\"(?P<http_referer>.*?)\"\s+\"(?P<http_user_agent>.*?)\"\s+'
    r'\"(?P<http_x_forwarded_for>.*?)\"\s+\"(?P<http_X_REQUEST_ID>.*?)\"\s+'
    r'\"(?P<http_X_RB_USER>.*)\"\s+(?P<request_time>\d+\.?\d*)'
)


def parse_config(configfile) -> json:
    with open(configfile) as file:
        return json.load(file)


def get_latest_log(logdir: str, template: str) -> namedtuple('Logfile', 'path date ext'):
    Logfile = namedtuple('Logfile', 'path date ext')
    last_logfile = None

    for logfile in os.listdir(logdir):
        match = re.match(template, logfile)
        if match:
            log_date = datetime.datetime.strptime(match.groupdict()['date'], '%Y%m%d').date()
            ext = match.groupdict()['ext']

            if not last_logfile or log_date > last_logfile.date:
                last_logfile = Logfile(os.path.join(logdir, logfile), log_date, ext)

    return last_logfile


def parse_log(logfile: namedtuple('Logfile', 'path date ext'), template):
    filename = logfile.path
    counter = 0
    with gzip.open(filename, "rt") if logfile.ext == ".gz" else open(filename) as file:
        for line in file:
            counter += 1
            parse_line = template.match(line)
            if parse_line:
                yield [parse_line.group('url'), float(parse_line.group('request_time'))]
            else:
                logging.error('line №{} not from template'.format(counter))


def get_report(log_data, report_size: int):
    url_data = defaultdict(list)
    count_total, time_total = 0, 0

    for url, req_time in log_data:
        url_data[url].append(float(req_time))
        count_total += 1
        time_total += float(req_time)

    report_values = []
    for url, req_times in url_data.items():
        count = len(req_times)
        time_sum = sum(req_times)
        report_values.append({
            "url": url,
            "count": count,
            "count_perc": round(count / count_total * 100, 3),
            "time_sum": round(time_sum, 3),
            "time_perc": round(time_sum / time_total * 100, 3),
            "time_avg": round(time_sum / count, 3),
            "time_max": round(max(req_times), 3),
            "time_med": round(statistics.median(req_times), 3)
        })

    return sorted(report_values, key=lambda item: item["time_sum"], reverse=True)[:report_size]


def write_report(report_values, report_filename: str):
    with open("report.html", "rt") as file:
        report_file = Template(file.read())
        report_file = report_file.safe_substitute(table_json=json.dumps(report_values))

    with open(report_filename, 'w') as file:
        file.write(report_file)


def main():
    parser = argparse.ArgumentParser(description="nginx log analyzer")
    parser.add_argument("-c", "--config", default="config.json", help="log and reports directories")
    args = parser.parse_args()
    config = DEFAULT_CONFIG | parse_config(args.config)

    logging.basicConfig(
        format=u"[%(asctime)s] %(levelname).1s %(message)s",
        filename=config["OUTPUT_FILE"],
        level=logging.INFO,
        datefmt='%Y.%m.%d %H:%M:%S'
    )

    logfile = get_latest_log(config["LOG_DIR"], TEMPLATE_LOG_FILE)
    report_filename = "{}/report-{}.html".format(config["REPORT_DIR"], logfile.date.strftime('%Y.%m.%d'))

    if not os.path.isfile(report_filename):
        report_values = get_report(parse_log(logfile, TEMPLATE_LOG), config["REPORT_SIZE"])
        write_report(report_values, report_filename)
    # else:
    #     logging.info('{} exists'.format(report_filename))


if __name__ == "__main__":
    main()
