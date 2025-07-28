import random
import os

class ProxyRoundRobin:
    def __init__(self, proxies_file='proxies.txt'):
        """
        Initialize with proxies loaded from a file.
        Each line in the file should be a proxy string.
        """
        self.proxies = self._load_proxies(proxies_file)
        self._last_index = -1
        self._order = []
        if self.proxies:
            self._shuffle_order()

    def _load_proxies(self, proxies_file):
        proxies_path = proxies_file
        if not os.path.isabs(proxies_file):
            proxies_path = os.path.join(os.path.dirname(__file__), proxies_file)
        if not os.path.exists(proxies_path):
            return []
        with open(proxies_path, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies

    def _shuffle_order(self):
        self._order = list(range(len(self.proxies)))
        random.shuffle(self._order)
        self._last_index = -1

    def get_proxy(self):
        """
        Return a proxy in round robin order, but randomly shuffle the order at each full cycle.
        """
        if not self.proxies:
            return None
        if not self._order or len(self._order) != len(self.proxies):
            self._shuffle_order()
        self._last_index = (self._last_index + 1) % len(self.proxies)
        if self._last_index == 0:
            self._shuffle_order()
        return self.proxies[self._order[self._last_index]]


