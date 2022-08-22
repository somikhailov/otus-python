#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
from collections import namedtuple

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def parse_log(logfile: namedtuple):
    filename = logfile.path + logfile.date + logfile.ext
    with gzip.open(filename) if logfile.ext == ".gz" else open(filename) as file:
        for line in file:
            print(line)


def main():
    Logfile = namedtuple('Logfile', 'path date ext')
    parse_log(Logfile('log/nginx-access-ui.log-', '20170630', '.gz'))


if __name__ == "__main__":
    main()