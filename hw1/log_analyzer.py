#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import argparse
import os
import json
import statistics
from collections import namedtuple, defaultdict

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def parse_config(configfile):
    with open(configfile) as json_file:
        data = json.load(json_file)
    return data


def parse_log(logfile: namedtuple):
    filename = logfile.path + logfile.date + logfile.ext
    with gzip.open(filename, "rt") if logfile.ext == ".gz" else open(filename) as file:
        for line in file:
            yield [line.split()[6], line.split()[-1]]


def get_report(log_data: list):
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

    with open("report.html", "rt")  as file:
        file_data = file.read()

    file_data = file_data.replace(
        '$table_json',
        json.dumps(sorted(report_values, key=lambda item: item["time_sum"], reverse=True)[:1000])
    )
    with open("reports/report-1.html", 'w') as file:
        file.write(file_data)


def main():
    parser = argparse.ArgumentParser(description="nginx log analyzer")
    parser.add_argument("-c", "--config", default="config.json", help="log and reports directories")
    args = parser.parse_args()

    main_config = parse_config(args.config)

    #merge with default config
    main_config = config | main_config

    # Logfile = namedtuple('Logfile', 'path date ext')
    # get_report(parse_log(Logfile(str(main_config['LOG_DIR']) + '/nginx-access-ui.log-', '20170630', '.gz')))

    print(os.listdir(main_config["LOG_DIR"]))

if __name__ == "__main__":
    main()
