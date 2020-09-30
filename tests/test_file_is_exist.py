from unittest import TestCase

from luban_common import base_utils


class TestFile_is_exist(TestCase):
    def test_file_is_exist(self):
        base_utils.file_is_exist("../data/config.yaml")
