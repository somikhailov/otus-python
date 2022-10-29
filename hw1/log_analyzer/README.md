# hw1 - Log Analyzer

This project contains code for analyze nginx log and create html report.

## Installation

> for linux
```bash
npm install -g tablesorter
```

## Usage

set your config parameters in your `config.json`

| Name         | Description                                            | Example     |
|--------------|--------------------------------------------------------|-------------|
| REPORT_SIZE  | count of report lines with max sum request time by url | 100         |
| REPORT_DIR   | where writes your report                               | /reports    |
| LOG_DIR      | where stores your log                                  | .log        |
| OUTPUT_FILE  | where writes information's about working this script   | /output.txt |
| ERRORS_LIMIT | max fraction wrong lines in log                        | 0.5         |

run script
```bash
python3 log_analyzer.py --config config.json
```

## Test
```bash
python3 test_log_analyzer.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)