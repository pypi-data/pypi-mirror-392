import requests
import json


class LarkUtil:
    def __init__(self, webhook: str):
        self.webhook = webhook
        self.headers = {"Content-Type": "application/json"}

    def send_text(self, text: str, at_ids=None):
        data = {
            "msg_type": "text",
            "content": {"text": text},
        }
        if at_ids:
            data["at"] = {"open_ids": at_ids}
        return requests.post(self.webhook, data=json.dumps(data), headers=self.headers)

    def send_markdown(self, title: str, markdown_text: str):
        """发送 Markdown 消息"""

        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "template": "blue",
                    "title": {"tag": "plain_text", "content": title}
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": markdown_text
                    }
                ]
            }
        }

        resp = requests.post(self.webhook, headers=self.headers, data=json.dumps(data))
        return resp.text

    def send_test_report(self, total: int, passed: int, failed: int, skipped: int, report_url: str = None):
        """自动化测试结果消息（Markdown）"""
        try:
            pass_rate = round(passed / (total - skipped) * 100, 2)
        except ZeroDivisionError:
            pass_rate = 0
        markdown = f"""
        **执行统计：**  
        **执行用例总数：** {total}
        **通过用例数：** {passed}
        **失败用例数：** {failed}
        **跳过用例数：** {skipped}
        **用例通过率：** {pass_rate}%
            """
        if report_url:
            markdown += f"\n\t**测试报告：**  👉 [点击查看测试报告]({report_url})"
        return self.send_markdown("自动化测试结果", markdown)


if __name__ == "__main__":
    # 你的飞书群机器人 Webhook URL
    WEBHOOK = "https://open.larksuite.com/open-apis/bot/v2/hook/27de2bf2-fa0d-49e7-8ff3-a3e3ad8cf2d7"
    bot = LarkUtil(WEBHOOK)

    bot.send_test_report(
        total=20,
        passed=18,
        failed=1,
        skipped=1,
        report_url="http://your-report/index.html"
    )
