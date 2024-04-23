

from enum import Enum

class EventsNames(Enum):
    START_COMMAND = 'Push Start Command'
    REGISTRATION = 'New Registration'
    ASSISTANT_CHOSEN = 'Assistant Chosen'
    FILE_UPLOADED = 'File Upload'
    YOUTUBE_LINK_UPLOADED = 'YouTube Link Upload'
    RECOGNIZED_TEXT_RECEIVED = 'Recognized  Text Received'
    SUMMARY_RECEIVED = 'Summary Received'
    PAYMENT_SCENARIO_STARTED = 'Start Payment Scenario'
    PAYMENT_COMPLETED = 'Successful Payment'
    OUT_OF_FUNDS = 'Out of Funds'
    VIEWED_HISTORY = 'Viewed History'
    ERROR_RECEIVED = 'Error'


