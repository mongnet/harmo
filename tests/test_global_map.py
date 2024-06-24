import allure
import pytest
from harmo.global_map import Global_Map


class TestGlobal_Map():
    gl = Global_Map()
    def test_set(self):
        self.gl.set("name","hubiao")

    def test_sets(self):
        self.gl.sets({"公众号":"彪哥的测试之路"})

    def test_del_key(self):
        self.gl.del_key("del_key_name")

class Test_get():
    gl = Global_Map()
    @allure.title("获取全部")
    def test_get(self):
        self.gl.get()
    @allure.title("获取全部")
    def test_get(self):
        self.gl.get("all")

