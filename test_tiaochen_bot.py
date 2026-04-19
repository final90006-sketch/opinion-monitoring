import unittest

from tiaochen_bot import ReportRequest, TiaochenBot


class TiaochenBotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = TiaochenBot()

    def test_default_two_versions_only(self):
        reports = self.bot.generate(ReportRequest(raw_text="民眾遭詐欺匯款"))
        self.assertEqual(list(reports.keys()), ["康定所報告", "萬華分局報告"])

    def test_optional_versions(self):
        reports = self.bot.generate(
            ReportRequest(raw_text="民眾遭詐欺匯款", include_chief_version=True, include_council_version=True)
        )
        self.assertIn("報局長版本", reports)
        self.assertIn("回覆議座版本", reports)

    def test_fraud_template_priority(self):
        # 同時有「投資」與「監視器」時，應優先走詐欺模板
        reports = self.bot.generate(ReportRequest(raw_text="投資廣告詐騙並調閱監視器"))
        self.assertIn("案由：詐欺案（偵辦中）", reports["康定所報告"])

    def test_time_normalization_no_leading_zero(self):
        text = "115年04月02日23時05分於現場查獲"
        reports = self.bot.generate(ReportRequest(raw_text=text, force_template="dui"))
        self.assertIn("115年4月2日23時5分", reports["康定所報告"])

    def test_banned_word_replacement(self):
        text = "然後員警帶回去做筆錄，後來看到沒有異狀"
        reports = self.bot.generate(ReportRequest(raw_text=text, force_template="fight"))
        station = reports["康定所報告"]
        self.assertIn("嗣經", station)
        self.assertIn("帶返所", station)
        self.assertIn("製作筆錄", station)
        self.assertNotIn("然後", station)
        self.assertNotIn("後來", station)

    def test_verbatim_keeps_original(self):
        raw = "A\n\nB"
        reports = self.bot.generate(ReportRequest(raw_text=raw, preserve_verbatim=True))
        self.assertIn("A\nB", reports["康定所報告"])


if __name__ == "__main__":
    unittest.main()
