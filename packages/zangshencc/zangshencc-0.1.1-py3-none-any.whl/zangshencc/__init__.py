from .browser import Browser
from .element import Element
from .wait import Wait


class Utils:
    page = None

    def __init__(self, page):
        self.page = page
        self._wait = None
        self._element = None
        self._browser = None

    @property
    def wait(self):
        if self._wait is None:
            self._wait = Wait(self.page)
        return self._wait

    @property
    def element(self):
        if self._element is None:
            self._element = Element(self.page)
        return self._element

    @property
    def browser(self):
        if self._browser is None:
            self._browser = Browser(self.page)
        return self._browser
