import json
import unittest
import datetime
from unittest.mock import patch, mock_open
from collections import namedtuple
import log_analyzer as log_analyzer
from log_analyzer import TEMPLATE_LOG_FILE


class LogAnalyzerTest(unittest.TestCase):
    def test_read_config(self):
        fake_file_path = "fake/file/path"
        file_content_mock = "{\"REPORT_SIZE\": \"1000\"}"

        with patch('log_analyzer.open'.format(__name__), new=mock_open(read_data=file_content_mock)) as mock_file:
            actual = log_analyzer.read_config(fake_file_path)
            mock_file.assert_called_once_with(fake_file_path)

        expected = json.loads('{"REPORT_SIZE": "1000"}')
        self.assertEqual(expected, actual)

    def test_get_latest_log(self):
        with patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = ['nginx-access-ui.log-20221015', 'nginx-access-ui.log-20170630.gz']
            actual = log_analyzer.get_latest_log(mocked_listdir, TEMPLATE_LOG_FILE)

        Logfile = namedtuple('Logfile', 'path date ext')
        expected = Logfile(
            path='MagicMock/listdir/140669534053584/nginx-access-ui.log-20221015',
            date=datetime.date(2022, 10, 15),
            ext=''
        )

        self.assertEqual(expected.path.split('/')[3], actual.path.split('/')[3])
        self.assertEqual(expected.date, actual.date)
        self.assertEqual(expected.ext, actual.ext)

if __name__ == '__main__':
    unittest.main()