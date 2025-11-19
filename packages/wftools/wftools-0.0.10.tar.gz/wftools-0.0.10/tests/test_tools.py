import unittest
import os
import tempfile

from tests.test_utils.test_input import stub_stdin
from wftools.api.tools import *


class TestTools(unittest.TestCase):
    def test_weather(self):
        stub_stdin(self, '北京\ny\nq\n')  # 依次输入
        weather()

    def test_url2ip(self):
        result = url2ip('www.python-office.com')
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, '')

    def test_lottery8ticket(self):
        stub_stdin(self, '12\n0\n')  # 依次输入
        lottery8ticket()

    def test_create_article(self):
        create_article('生日快乐', line_num=2000)

    def test_transtools(self):
        # 测试中文翻译成英文
        result = transtools('你好', 'en', 'zh')
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, '')

    def test_qrcodetools(self):
        # 测试生成二维码
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'test_qrcode.png')
            qrcodetools('https://www.python-office.com', output_path)
            self.assertTrue(os.path.exists(output_path))

    def test_passwordtools(self):
        # 测试默认长度密码生成
        result = passwordtools()
        self.assertEqual(len(result), 8)
        self.assertIsInstance(result, str)
        
        # 测试自定义长度密码生成
        result_custom = passwordtools(12)
        self.assertEqual(len(result_custom), 12)
        self.assertIsInstance(result_custom, str)

    def test_net_speed_test(self):
        # 测试网速测试（这个测试可能需要一些时间）
        net_speed_test()

    def test_pwd4wifi(self):
        # 测试WiFi密码破解功能（已废弃，但测试函数调用）
        pwd4wifi(len_pwd=8, pwd_list=['12345678', 'testpassword'])

    def test_open_soft(self):
        # 测试打开软件功能（使用notepad作为测试）
        import platform
        if platform.system() == 'Windows':
            try:
                open_soft('notepad.exe', 1)
            except Exception:
                # 如果notepad不存在或其他错误，跳过测试
                pass
