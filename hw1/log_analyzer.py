#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import argparse
import json
import itertools
from collections import namedtuple

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

    urls = []
    with gzip.open(filename, "rt") if logfile.ext == ".gz" else open(filename) as file:
        for line in file:
            urls.append([line.split()[6], line.split()[-1]])

    return sorted(urls)


def calc_report_values(urls):
    count = len(urls)
    print("count: " + str(count))

    group_urls = []
    for k, g in itertools.groupby(urls):
        group_urls.append([k[0], (float(k[1]) * len(list(g)))])

    [print(group_urls[i]) for i in range(5)]


def main():
    parser = argparse.ArgumentParser(description="nginx log analyzer")
    parser.add_argument("-c", "--config", default="config.json", help="log and reports directories")
    args = parser.parse_args()

    main_config = parse_config(args.config)

    #merge with default config
    main_config = config | main_config

    Logfile = namedtuple('Logfile', 'path date ext')
    calc_report_values(parse_log(Logfile(str(main_config['LOG_DIR']) + '/nginx-access-ui.log-', '20170630', '.gz')))


if __name__ == "__main__":
    main()
