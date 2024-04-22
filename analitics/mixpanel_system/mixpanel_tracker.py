from mixpanel import Mixpanel
from mixpanel_async import AsyncBufferedConsumer

from analitics.event_enteties import BaseEvent, UserEvent
from analitics.system_interface import AnalyticsSystem


class MixpanelAnalyticsSystem(AnalyticsSystem):
    def __init__(self, mixpanel_token):
        self.mp = Mixpanel(mixpanel_token, consumer=AsyncBufferedConsumer())

    def send_event(self, event: BaseEvent):
        try:
            self.mp.track(distinct_id=str(event.user_id), event_name=event.event_name, properties=event.dict())
        except Exception as e:
            print(e)

    def register_new_user(self, user: UserEvent):
        try:
            self.mp.people_set(distinct_id=str(user.user_id), properties=user.dict())
        except Exception as e:
            print(e)
