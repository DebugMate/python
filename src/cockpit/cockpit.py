import sys
import requests


class Occurrence:
    def __init__(self, hook, type, value, traceback):
        self.hook = hook
        self.type = type
        self.value = value
        self.traceback = traceback  # not sending for now

    # @staticmethod
    def from_excepthook(args):
        (hook, type, value, traceback) = args

        return Occurrence(hook, type, value, traceback)

    def to_form_data(self):
        return {
            'exception': self.type,
            'message': self.value,
            'file': self.hook,
            'type': 'cli',
        }


class Cockpit:
    def __init__(self, enabled, domain, token):
        self.enabled = enabled
        self.domain = domain
        self.token = token

        sys.addaudithook(self.audit)  # >= python 3.8

    def audit(self, event, args):
        if 'sys.excepthook' in event:
            self.publish(Occurrence.from_excepthook(args))

    def publish(self, occurrence: Occurrence):
        response = requests.post(
            self.domain,
            headers={
                'X-COCKPIT-TOKEN': self.token,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            data=occurrence.to_form_data()
        )

        # print(response.content)
