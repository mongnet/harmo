from unittest import TestCase

from luban_common.operation.yaml_file import get_yaml_data


class TestGet_yaml_data(TestCase):
    def test_get_yaml_data(self):
        yamldate = get_yaml_data("../data/config1.yaml")
        assert type(yamldate) == dict
        assert yamldate["centerProductid"] == 100
        assert "User-Agent" in yamldate["headers"]["multipart_header"]
