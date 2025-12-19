import math
class Menu:
    def __init__(self, *, items: list, items_per_page: int = 4):
        self.items = items
        self.items_per_page = items_per_page
        self.page = 1

    @property
    def total_page(self) -> int:
        return max(1, math.ceil(len(self.items) / self.items_per_page))

    def next_page(self):
        if self.page < self.total_page:
            self.page += 1

    def prev_page(self):
        if self.page > 1:
            self.page -= 1

    def get_visible_items(self) -> list:
        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def reset(self, new_items: list):
        self.items = new_items
        self.page = 1
