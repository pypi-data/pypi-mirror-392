#!/usr/bin/env python3

"""Canadian ACB calculator - symbol to name servce"""


class NameServer(dict):
    """Might be a real thing one day but just a dictionary for now"""

    def __init__(self, *args):
        super().__init__(*args)
        self._dirty = False

    def __setitem__(self, key, value):
        """Monitors creation/setting of elements"""
        if key in self and self[key] == value:
            return
        super().__setitem__(key, value)
        self.mark_dirty()

    def is_dirty(self):
        """Returns True if server contents have been altered"""
        return self._dirty

    def mark_clean(self):
        """Marks the server clean"""
        self._dirty = False

    def mark_dirty(self):
        """Marks the server dirty"""
        self._dirty = True
