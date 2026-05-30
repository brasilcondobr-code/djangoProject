from datetime import datetime

class JsonLogBuilder:
    @staticmethod
    def build_event(event, message):
        return {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "message": message
        }
