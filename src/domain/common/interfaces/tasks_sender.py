from abc import ABC, abstractmethod


class TasksSender(ABC):
    @abstractmethod
    def collect_menu_data(self):
        pass
