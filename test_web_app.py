import threading
import unittest
from http.server import HTTPServer
from urllib.request import Request, urlopen

from web_app import Handler


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_homepage_contains_manifest(self):
        data = urlopen(f"http://127.0.0.1:{self.port}/", timeout=5).read().decode("utf-8")
        self.assertIn('rel="manifest"', data)
        self.assertIn("serviceWorker", data)

    def test_manifest_served(self):
        data = urlopen(f"http://127.0.0.1:{self.port}/manifest.webmanifest", timeout=5).read().decode("utf-8")
        self.assertIn('"display": "standalone"', data)

    def test_post_generate(self):
        payload = "raw_text=%E6%B0%91%E7%9C%BE%E9%81%AD%E8%A9%90%E9%A8%99%E5%8C%AF%E6%AC%BE50%E8%90%AC&template=fraud".encode("utf-8")
        req = Request(
            f"http://127.0.0.1:{self.port}/",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = urlopen(req, timeout=5).read().decode("utf-8")
        self.assertIn("康定所報告", data)
        self.assertIn("萬華分局報告", data)


if __name__ == "__main__":
    unittest.main()
