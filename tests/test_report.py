import unittest
from sim_progress import Report


class TestReport(unittest.TestCase):
    def test_report_to_log(self):
        Report.report_to_log("test")
        Report.report_to_log("test", 1)
        Report.report_to_log()

    def test_get_result_id(self):
        id = Report.get_result_id()