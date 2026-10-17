import os
import unittest

# Chạy test không cần BOT_TOKEN/Redis thật.
os.environ.pop("BOT_TOKEN", None)
os.environ.pop("UPSTASH_URL", None)
os.environ.pop("UPSTASH_TOKEN", None)
os.environ["SECRET_TOKEN"] = "test-secret"
os.environ["ADMIN_ID"] = "admin-1"

import FAQ
import admin
import storage


class BotMVPTest(unittest.TestCase):
    def setUp(self):
        storage._memory.clear()

    def send_admin(self, text):
        sent = []
        admin.handle_admin(text, "admin-1", "admin-chat", lambda chat, msg: sent.append(msg))
        return sent

    def test_admin_can_create_and_customer_can_view_product(self):
        sent = self.send_admin("/themsp TM01 | Áo Tân Minh | 120000 | Áo mặc hằng ngày | https://example.com/tm01")
        self.assertIn("TM01", sent[0])
        self.assertIn("Áo Tân Minh", "\n".join(FAQ.handle_message("sanpham")))
        detail = "\n".join(FAQ.handle_message("sp tm01"))
        self.assertIn("120000", detail)
        self.assertIn("https://example.com/tm01", detail)

    def test_admin_can_hide_product(self):
        self.send_admin("/themsp TM02 | Túi Tân Minh | 90000 | Túi tiện dụng | https://example.com/tm02")
        self.send_admin("/xoasp TM02")
        self.assertIn("chưa tìm thấy", FAQ.handle_message("sp tm02")[0].lower())

    def test_unknown_question_has_fallback(self):
        self.assertIn("tt1", FAQ.handle_message("xin abc")[0])


if __name__ == "__main__":
    unittest.main()
