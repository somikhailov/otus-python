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
import statistics
import datetime
from collections import namedtuple, defaultdict
from string import Template

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def parse_config(configfile) -> json:
    with open(configfile) as file:
        return json.load(file)


def get_latest_log(logdir: str) -> namedtuple('Logfile', 'path date ext'):
    Logfile = namedtuple('Logfile', 'path date ext')
    template = re.compile(r"^nginx-access-ui\.log-(?P<date>\d{8})(?P<ext>\.gz|)?$")
    last_logfile = None

    for logfile in os.listdir(logdir):
        match = re.match(template, logfile)
        if match:
            log_date = datetime.datetime.strptime(match.groupdict()['date'], '%Y%m%d').date()
            ext = match.groupdict()['ext']

            if not last_logfile or log_date > last_logfile.date:
                last_logfile = Logfile(os.path.join(logdir, logfile), log_date, ext)

    return last_logfile


def parse_log(logfile: namedtuple('Logfile', 'path date ext')):
    filename = logfile.path
    with gzip.open(filename, "rt") if logfile.ext == ".gz" else open(filename) as file:
        for line in file:
            yield [line.split()[6], line.split()[-1]]


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
    main_config = config | parse_config(args.config)

    logfile = get_latest_log(main_config["LOG_DIR"])
    report_filename = "{}/report-{}.html".format(main_config["REPORT_DIR"], logfile.date.strftime('%Y.%m.%d'))

    if not os.path.isfile(report_filename):
        report_values = get_report(parse_log(logfile), main_config["REPORT_SIZE"])
        write_report(report_values, report_filename)


if __name__ == "__main__":
    main()
