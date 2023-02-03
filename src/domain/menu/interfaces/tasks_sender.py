from asyncio import Protocol


class IMenuTasksSender(Protocol):
    def collect_menu_data(self):
        pass
