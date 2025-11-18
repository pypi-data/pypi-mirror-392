import random
import time

from DrissionPage._elements.none_element import NoneElement
from DrissionPage import ChromiumPage
from DrissionPage.common import Keys


class Element:
	def __init__(self, page: ChromiumPage):
		self.page = page

	@staticmethod
	def _random_delay(base=0.5):
		"""生成随机延迟时间，base为基准秒数"""
		return base + random.uniform(-0.3, 1.2)

	def find(self, locators, timeout: int = 10, random_delay=True):
		"""一个定位符或多个组成的列表, 任何一个定位符找到结果即返回"""
		if random_delay:
			self.page.wait(self._random_delay())
		return self.page.find(locators, any_one=True, timeout=timeout)[0]

	def find_ele(self, xpath, timeout: int = 10, index: int = 1, random_delay=True):
		if random_delay:
			self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, index=index, timeout=timeout)
		if ele is None or isinstance(ele, NoneElement):
			return False
		else:
			return ele

	def find_eles(self, xpath, timeout: int = 10):
		self.page.wait(self._random_delay())
		eles = self.page.eles(xpath, timeout=timeout)
		if eles is None or isinstance(eles, NoneElement):
			return False
		else:
			return eles

	def find_ele_xpath(self, xpath, timeout: int = 10):
		self.page.wait(self._random_delay())
		ele = self.page.ele('x:' + xpath, timeout=timeout)
		return ele

	"""元素交互"""

	def click(self, xpath, timeout: int = 10):
		"""对ele元素进行模拟点击，强制模拟点击，被遮挡也会进行点击"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click(by_js=False)

	def click_min(self, xpath, timeout: int = 10):
		"""对ele元素进行模拟点击，强制模拟点击，被遮挡也会进行点击"""
		self.page.wait(0.2)
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click(by_js=False)

	def click_js(self, xpath, timeout: int = 10):
		"""对ele元素进行模拟点击，直接用 js 点击"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click(by_js=True)

	def click_xpath(self, xpath, timeout: int = 10):
		"""对ele元素进行模拟点击，如判断会被遮挡点击"""
		self.page.wait(self._random_delay())
		ele = self.page.ele('x:' + xpath, timeout=timeout)
		ele.click(by_js=False)

	def click_right(self, xpath, timeout: int = 10):
		"""此方法实现右键单击元素"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click.right()

	def click_multi(self, xpath, timeout: int = 10, times: int = 2):
		"""此方法实现左键多次点击元素, 默认为2次"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click.multi(times)

	def click_to_upload(self, xpath, file_paths, timeout: int = 10):
		"""此方法用于点击元素，触发文件选择框并把指定的文件路径添加到网页"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click.to_upload(file_paths)

	def click_to_download(self, xpath, save_path, timeout: int = 10):
		"""此方法用于点击元素，触发文件下载"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.click.to_download(save_path=save_path)

	def click_for_new_tab(self, xpath, timeout: int = 30):
		"""此方法用于点击元素，触发新标签页"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.wait.clickable(timeout=timeout)
		return ele.click.for_new_tab()

	def clear(self, xpath, timeout: int = 10):
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.clear(by_js=False)

	def input(self, xpath, text, timeout: int = 10):
		"""此方法用于向元素输入文本或组合键(有些文本框可以接收回车代替点击按钮，可以直接在文本末尾加上'\n')"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.clear(by_js=False)
		ele.input(vals=text)

	def input_no_clear(self, xpath, text, timeout: int = 10):
		"""此方法用于向元素输入文本或组合键(有些文本框可以接收回车代替点击按钮，可以直接在文本末尾加上'\n')"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.input(vals=text, clear=False)

	def input_xpath(self, xpath, text, timeout: int = 10):
		"""此方法用于向元素输入文本或组合键(有些文本框可以接收回车代替点击按钮，可以直接在文本末尾加上'\n')"""
		self.page.wait(self._random_delay())
		ele = self.page.ele('x:' + xpath, timeout=timeout)
		ele.input(vals=text)

	def text(self, xpath, timeout: int = 10):
		"""此方法用于获取元素文本"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		return ele.text

	def text_xpath(self, xpath, timeout: int = 10):
		self.page.wait(self._random_delay())
		ele = self.page.ele('x:' + xpath, timeout=timeout)
		return ele.text

	def ele_check(self, xpath, timeout: int = 10):
		"""此方法用于选中或取消选中元素"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.check()

	def set_value(self, xpath, value, timeout: int = 10):
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.set.value(value)

	def set_attr(self, xpath, name, value, timeout: int = 10):
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.set.attr(name, value)

	def ele_run_js(self, xpath, js, timeout: int = 10):
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.run_js(js)

	"""元素滚动功能"""

	def ele_scroll_to_bottom(self, xpath, timeout: int = 10):
		self.page.wait(self._random_delay())
		"""此方法用于滚动到元素底部，水平位置不变"""
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.to_bottom()

	def ele_scroll_to_top(self, xpath, timeout: int = 10):
		"""此方法用于滚动到元素顶部，水平位置不变"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.to_top()

	def ele_scroll_to_half(self, xpath, timeout: int = 10):
		"""此方法用于滚动到元素垂直中间位置，水平位置不变"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.to_half()

	def ele_scroll_to_up(self, xpath, pixel, timeout: int = 10):
		"""此方法用于使元素向上滚动若干像素，水平位置不变"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.up(pixel)

	def ele_scroll_to_down(self, xpath, pixel, timeout: int = 10):
		"""此方法用于使元素向下滚动若干像素，水平位置不变"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.down(pixel)

	def ele_scroll_to_right(self, xpath, pixel, timeout: int = 10):
		"""此方法用于使元素向下滚动若干像素，水平位置不变"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.right(pixel)

	def ele_scroll_to_see(self, xpath, timeout: int = 10):
		"""此方法用于滚动页面直到元素可见"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.scroll.to_see()

	"""select列表元素操作"""

	def select_by_text(self, xpath, text, timeout: int = 10):
		"""用于按文本选择列表项。如为多选列表，可多选(传入list或tuple可选择多项)"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.select.by_text(text)

	def select_by_value(self, xpath, value, timeout: int = 10):
		"""此方法用于按value属性选择列表项。如为多选列表，可多选(传入list或tuple可选择多项)"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.select.by_value(value)

	def select_by_index(self, xpath, index, timeout: int = 10):
		"""此方法用于按序号选择列表项，从1开始。如为多选列表，可多选(传入list或tuple可选择多项)"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.select.by_index(index)

	def select_clear(self, xpath, timeout: int = 10):
		"""此方法用于取消所有项选中状态。多选列表才有效"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.select.clear()

	def select_all(self, xpath, timeout: int = 10):
		"""此方法用于全选所有项。多选列表才有效"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.select.all()

	"""元素鼠标操作"""

	def drag(self, xpath, offset_x, offset_y, duration, timeout: int = 10):
		"""此方法用于拖拽元素到相对于当前的一个新位置，可以设置速度(duration为拖拽时间)"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.drag(offset_x, offset_y, duration)

	def drag_to(self, xpath, another_ele, duration, timeout: int = 10):
		"""此方法用于拖拽元素到另一个元素上(duration为拖拽时间)"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.drag_to(another_ele, duration)

	def hover(self, xpath, timeout: int = 10):
		"""此方法用于模拟鼠标悬停在元素上，可接受偏移量"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		ele.hover()

	def move(self, offset_x, offset_y, duration: int = 1):
		"""此方法用于使鼠标相对当前位置移动若干距离"""
		self.page.wait(self._random_delay())
		self.page.actions.move(offset_x=offset_x, offset_y=offset_y, duration=duration)

	def move_to(self, xpath, timeout: int = 10):
		"""此方法用于模拟鼠标移动到元素上，可接受偏移量"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		self.page.actions.move_to(ele, duration=1)

	def move_to_offset_click(self, x, y, duration: int = 1):
		"""此方法用于模拟鼠标移动到元页面上的某个绝对坐标，可接受偏移量"""
		self.page.wait(self._random_delay())
		offset = (x, y)
		self.page.actions.move_to(ele_or_loc=offset, duration=duration).click()

	def move_up(self, pixel):
		"""此方法用于使鼠标相对当前位置向上移动若干距离"""
		self.page.wait(self._random_delay())
		self.page.actions.up(pixel=pixel)

	def move_down(self, pixel):
		"""此方法用于使鼠标相对当前位置向下移动若干距离"""
		self.page.wait(self._random_delay())
		self.page.actions.down(pixel=pixel)

	def move_left(self, pixel):
		"""此方法用于使鼠标相对当前位置向左移动若干距离"""
		self.page.wait(self._random_delay())
		self.page.actions.left(pixel=pixel)

	def move_right(self, pixel):
		"""此方法用于使鼠标相对当前位置向右移动若干距离"""
		self.page.wait(self._random_delay())
		self.page.actions.right(pixel=pixel)

	def mouse_click(self, xpath, times: int = 1, random_delay=True):
		"""此方法用于模拟鼠标单击元素，times:点击次数"""
		if random_delay:
			self.page.wait(0.1)
		self.page.actions.click(xpath, times=times)

	def key_down(self, key):
		"""此方法用于模拟键盘按下某个键"""
		self.page.wait(self._random_delay())
		self.page.actions.key_down(key)

	def ctrl_a(self):
		"""此方法用于模拟键盘按下Ctrl+A"""
		self.page.wait(self._random_delay())
		self.page.actions.key_down(Keys.CTRL)
		self.page.actions.type('a')
		self.page.actions.key_up(Keys.CTRL)

	def ctrl_c(self):
		"""此方法用于模拟键盘按下Ctrl+C"""
		self.page.wait(self._random_delay())
		self.page.actions.key_down(Keys.CTRL)
		self.page.actions.type('c')
		self.page.actions.key_up(Keys.CTRL)

	def ctrl_v(self):
		"""此方法用于模拟键盘按下Ctrl+C"""
		self.page.wait(self._random_delay())
		self.page.actions.key_down(Keys.CTRL)
		self.page.actions.type('v')
		self.page.actions.key_up(Keys.CTRL)

	def key_up(self, key):
		"""此方法用于模拟键盘松开某个键"""
		self.page.wait(self._random_delay())
		self.page.actions.key_up(key)

	def key_type(self, xpath, key, timeout: int = 10):
		"""此方法用于将文本复制进输入框"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		self.page.actions.click(ele).type(key)

	"""获取元素信息"""

	def get_attr(self, xpath, name, timeout: int = 10):
		"""此方法返回元素某个 attribute 属性值"""
		self.page.wait(0.1)
		ele = self.page.ele(xpath, timeout=timeout)
		return ele.attr(name)

	def rect_location(self, xpath, timeout: int = 10):
		"""此属性以元组形式返回元素左上角在整个页面中的坐标"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		location = ele.rect.location
		return location

	def states_is_clickable(self, xpath, timeout: int = 10):
		"""此属性以布尔值返回元素是否可点击"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		return ele.states.is_clickable

	def states_is_displayed(self, xpath, timeout: int = 10):
		"""此属性以布尔值返回元素是否可见"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		return ele.states.is_displayed

	def states_is_enabled(self, xpath, timeout: int = 10):
		"""此属性以布尔值返回元素是否可用"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		return ele.states.is_enabled

	def states_is_checked(self, xpath, timeout: int = 10):
		"""此属性以布尔值返回表单单选或多选元素是否选中"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		state = ele.states.is_checked
		return state

	def states_is_selected(self, xpath, timeout: int = 10):
		"""此属性以布尔值返回<select>元素中的项是否选中"""
		self.page.wait(self._random_delay())
		ele = self.page.ele(xpath, timeout=timeout)
		return ele.states.is_selected

	"""iframe 操作"""

	def iframe_ele_click(self, iframe_xpath, ele_xpath, timeout: int = 10):
		iframe = self.page(iframe_xpath)
		iframe = self.page.get_frame(iframe, timeout=timeout)
		time.sleep(5)
		ele = iframe(ele_xpath, timeout=timeout)
		ele.click(timeout=timeout)

	def get_frame(self, iframe_xpath, timeout: int = 10):
		"""获取iframe元素"""
		self.page.wait(self._random_delay())
		iframe = self.page.ele(iframe_xpath, timeout=timeout)
		return iframe

	def find_in_frame(self, iframe_xpath, ele_xpath, timeout: int = 10):
		"""在iframe中查找元素"""
		self.page.wait(self._random_delay())
		iframe = self.page.ele(iframe_xpath, timeout=timeout)
		iframe = self.page.get_frame(iframe, timeout)
		ele = iframe(ele_xpath)
		return ele
