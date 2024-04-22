from abc import ABC, abstractmethod


class AnalyticsSystem(ABC):
    @abstractmethod
    def send_event(self, *args, **kwargs):
        pass

    @abstractmethod
    def register_new_user(self,*args, **kwargs):
        pass
