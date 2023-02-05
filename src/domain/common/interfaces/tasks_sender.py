from abc import ABC, abstractmethod

from src.domain.menu.dto.menu import OutputMenu


class TasksSender(ABC):
    @abstractmethod
    def collect_menu_data(self, menu: OutputMenu):
        pass
