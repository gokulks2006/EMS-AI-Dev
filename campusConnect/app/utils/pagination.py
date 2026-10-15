"""
CampusConnect - Pagination Utility
==================================
Pagination container object compatible with Jinja2 templates.
Avoids 'builtin_function_or_method' object is not iterable error when templates
access .items on dictionaries.
"""

class Pagination:
    """
    Pagination wrapper matching Jinja2 template expectations:
    - pagination.items -> list of items on current page
    - pagination.page -> current page number
    - pagination.pages -> total pages
    - pagination.total -> total items count
    - pagination.has_prev, pagination.has_next
    - pagination.prev_num, pagination.next_num
    """

    def __init__(self, items: list, page: int, per_page: int, total: int):
        self.items = list(items)
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max((total + per_page - 1) // per_page, 1) if per_page else 1
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1
        self.next_num = page + 1

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return getattr(self, item)
