import time
from DrissionPage import ChromiumPage


class Browser:
    def __init__(self, page: ChromiumPage):
        self.page = page

    """页面操作"""

    def get(self, url: str, close_others: bool = True):
        """打开页面"""
        try:
            self.page.get(url)
            self.page.wait.doc_loaded()
            self.page.wait(1)
            if close_others:
                self.close_other_tabs()
            self.page.wait(1)
        except TimeoutError:
            self.page.run_js('window.stop()')
        except Exception as e:
            print(f'发生异常：浏览器打开超时 - {e}')

    """关闭其他tab"""

    def close_other_tabs(self):
        # 获取所有标签页
        all_tabs = self.page.get_tabs()
        # 遍历所有标签页并关闭非当前页
        for tab in all_tabs:
            if self.page.url != tab.url:  # 排除当前标签页
                tab.close()  # 关闭其他标签页

    def quit(self):
        """关闭浏览器"""
        self.page.quit()

    def back(self, steps: int = 1):
        """在浏览历史中后退若干步（默认后退1步）"""
        self.page.back(steps)
        self.page.wait.doc_loaded()

    def forward(self, steps: int = 1):
        """在浏览历史中前进若干步（默认前进1步）"""
        self.page.forward(steps)
        self.page.wait.doc_loaded()

    def refresh(self, ignore_cache: bool = False):
        """刷新页面（新增缓存控制参数）
        :param ignore_cache: 是否忽略缓存
        """
        self.page.refresh(ignore_cache=ignore_cache)
        self.page.wait.doc_loaded()
        self.page.wait(3)

    def stop_loading(self):
        """强制停止当前页面加载"""
        self.page.stop_loading()

    def run_js(self, js: str):
        """执行 JavaScript 脚本"""
        return self.page.run_js(js)

    def clear_cache(self):
        """清除缓存"""
        self.page.clear_cache()

    def reconnect(self):
        """重新连接"""
        self.page.reconnect()

    def process_id(self):
        """返回浏览器进程 pid"""
        return self.page.process_id

    """标签页操作"""

    def get_current_tabs(self) -> set:
        """获取当前所有标签页ID（兼容4.1语法）"""
        return {tab.tab_id for tab in self.page.get_tabs()}

    def has_new_tab(self, timeout=5) -> bool:
        """等待新标签页出现（使用4.1原生等待方法）"""
        try:
            new_tab = self.page.wait.new_tab(timeout=timeout)
            return new_tab is not None
        except TimeoutError:
            return False

    def switch_to_new_tab(self, timeout=10) -> bool:
        """切换到最新标签页（4.1优化方法）"""
        try:
            new_tab = self.page.wait.new_tab(timeout=timeout)
            if new_tab:
                self.page.get_tab(new_tab)
                return True
            return False
        except Exception as e:
            raise RuntimeError(f"切换标签页失败: {str(e)}")

    def new_tab(self, url: str = None):
        """新建标签页"""
        if url:
            return self.page.new_tab(url)
        return self.page.new_tab()

    def close(self):
        """关闭当前标签页"""
        self.page.close()

    def close_tabs(self):
        """此方法用于关闭除当前激活外的标签页。"""
        self.page.wait(3)
        tabs_count = self.tabs_count()
        if tabs_count > 1:
            self.page.close_tabs(self.page.latest_tab)
        self.page.wait(3)

    def latest_tab(self, timeout: int = 40):
        """返回最新的标签页对象或 id，最新标签页指最后创建或最后被激活的"""
        times = 0
        while True:
            self.page.wait(1)
            tabs_count = self.tabs_count()
            if times > timeout:
                return False
            if tabs_count > 1:
                return self.page.latest_tab
            else:
                time.sleep(1)
                times = times + 1

    def tabs_count(self):
        """返回标签页数量"""
        return self.page.tabs_count

    def get_tab(self, id_or_num=None, title=None):
        """获取指定标签页对象"""
        return self.page.get_tab(id_or_num=id_or_num, title=title)

    def get_tabs(self, title=None):
        """获取所有标签页对象"""
        return self.page.get_tabs(title)

    def find_tab(self, **kwargs):
        """查找符合条件的标签页, 支持传入 title、url、tab_type 等条件"""
        return self.page.get_tab(**kwargs)

    def get_latest_tab(self):
        """获取最新标签页"""
        return self.page.get_tab(self.page.latest_tab)

    def get_url(self):
        """获取当前页面 URL"""
        return self.page.url

    def tab_id(self):
        """获取当前标签页 ID"""
        return self.page.tab_id

    def set_windows_size(self, width, height):
        """设置浏览器窗口大小"""
        self.page.set.window.size(width, height)

    """页面滚动"""

    def scroll_to_location(self, x: int, y: int):
        """滚动页面到指定坐标"""
        self.page.scroll.to_location(x, y)

    def scroll_to_see(self, loc_or_ele):
        """滚动页面直到元素可见"""
        self.page.scroll.to_see(loc_or_ele)

    def scroll_up(self, pixel: int):
        """向上滚动指定像素"""
        self.page.scroll.up(pixel)

    def scroll_down(self, pixel: int):
        """向下滚动指定像素"""
        self.page.scroll.down(pixel)

    def scroll_right(self, pixel: int):
        """向右滚动指定像素"""
        self.page.scroll.right(pixel)

    def scroll_left(self, pixel: int):
        """向左滚动指定像素"""
        self.page.scroll.left(pixel)

    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.page.scroll.to_top()

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.page.scroll.to_bottom()

    def scroll_to_half(self):
        """滚动到页面垂直中间位置"""
        self.page.scroll.to_half()

    def scroll_to_rightmost(self):
        """滚动到页面最右边"""
        self.page.scroll.to_rightmost()

    def scroll_to_leftmost(self):
        """滚动到页面最左边"""
        self.page.scroll.to_leftmost()

    """页面弹窗处理"""

    def handle_alert(self):
        """返回提示框内容文本"""
        return self.page.handle_alert(accept=None)

    def alert_cancel(self):
        """取消弹出框"""
        self.page.handle_alert(accept=False)

    def alert_input_and_confirm(self, text: str):
        """在弹出框输入文本并确认"""
        self.page.handle_alert(accept=True, send=text)

    def auto_handle_alert(self, accept: bool = True):
        """自动处理弹出框, 默认为接受弹出框"""
        self.page.set.auto_handle_alert(accept)

    def get_shadow_root(self, xpath):
        sr_ele = self.page.ele(xpath).shadow_root
        return sr_ele
