import random
from DrissionPage import ChromiumPage


class Wait:
    def __init__(self, page: ChromiumPage):
        self.page = page

    @staticmethod
    def _random_delay(base=0.5):
        """生成随机延迟时间，base为基准秒数"""
        return base + random.uniform(-0.3, 1.2)

    def wait(self, second: float = 1):
        self.page.wait(second)

    """元素对象的等待方法"""

    def wait_displayed(self, xpath, timeout: int = 10):
        """此方法用于等待元素从隐藏状态变成显示状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.displayed()

    def wait_hidden(self, xpath, timeout: int = 10):
        """此方法用于等待元素从显示状态变成隐藏状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.hidden()

    def wait_deleted(self, xpath, timeout: int = 10):
        """此方法用于等待元素被从 DOM 删除"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.deleted()

    def wait_enabled(self, xpath, timeout: int = 10):
        """此方法用于等待元素变为可用状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.enabled(timeout=timeout)

    def wait_disabled(self, xpath, timeout: int = 10):
        """此方法用于等待元素变为不可用状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.disabled(timeout=timeout)

    def wait_clickable(self, xpath, timeout: int = 10):
        """此方法用于等待元素变为可点击状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.clickable(timeout=timeout)

    def wait_clickable_and_click(self, xpath, timeout: int = 10):
        """此方法用于等待元素变为可点击状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        ele.wait.clickable(timeout=timeout).click()

    def wait_disable_or_deleted(self, xpath, timeout: int = 10):
        """此方法用于等待元素变为不可用状态"""
        self.page.wait(self._random_delay())
        ele = self.page.ele(xpath, timeout=timeout)
        return ele.wait.disabled_or_deleted(timeout=timeout)

    """页面对象的等待方法"""

    def wait_ele_loaded(self, loc_or_ele, timeout: int = 10):
        """此方法用于等待一个元素被加载到 DOM(loc_or_ele:要等待的元素，可以是元素或定位符)"""
        self.page.wait(self._random_delay())
        return self.page.wait.eles_loaded(loc_or_ele, timeout)

    def wait_ele_displayed(self, loc_or_ele, timeout: int = 10):
        """此方法用于等待一个元素变成显示状态(loc_or_ele:要等待的元素，可以是元素或定位符)"""
        self.page.wait(self._random_delay())
        return self.page.wait.ele_displayed(loc_or_ele, timeout)

    def wait_ele_hidden(self, loc_or_ele, timeout: int = 10):
        """此方法用于等待一个元素变成隐藏状态(loc_or_ele:要等待的元素，可以是元素或定位符)"""
        self.page.wait(self._random_delay())
        return self.page.wait.ele_hidden(loc_or_ele, timeout)

    def wait_ele_deleted(self, loc_or_ele, timeout: int = 10):
        """此方法用于等待一个元素被从 DOM 中删除(loc_or_ele:要等待的元素，可以是元素或定位符)"""
        self.page.wait(self._random_delay())
        return self.page.wait.ele_deleted(loc_or_ele, timeout)

    def wait_load_start(self, timeout: int = 30):
        """此方法用于等待页面进入加载状态"""
        self.page.wait(self._random_delay())
        return self.page.wait.load_start(timeout)

    def wait_new_tab(self, timeout: int = 30):
        """此方法用于等待新标签页出现"""
        self.page.wait(self._random_delay())
        return self.page.wait.new_tab(timeout)

    def wait_title_change(self, text, exclude=False, timeout: int = 30):
        """此方法用于等待 title 变成包含或不包含指定文本"""
        self.page.wait(self._random_delay())
        return self.page.wait.title_change(text=text, exclude=exclude, timeout=timeout)

    def wait_doc_loaded(self, ):
        self.page.wait(self._random_delay())
        return self.page.wait.doc_loaded()
