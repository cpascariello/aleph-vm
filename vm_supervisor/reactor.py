from typing import List, Dict

from aleph_message.models import Message, ProgramMessage


def is_equal_or_includes(value, compare_to) -> bool:
    if isinstance(value, str):
        return value == compare_to
    elif isinstance(value, dict):
        for subkey, subvalue in value.items():
            if not is_equal_or_includes(subvalue, getattr(compare_to, subkey)):
                return False
        return True
    else:
        raise ValueError("Unsupported value")


def subscription_matches(subscription: Dict, message: ProgramMessage) -> bool:
    if not subscription:
        # Require at least one value to match
        return False
    for key, value in subscription.items():
        if not is_equal_or_includes(value, getattr(message, key)):
            return False
    return True


class Reactor:

    listeners: List[ProgramMessage]

    def __init__(self):
        self.listeners = []

    def trigger(self, message: Message):
        for listener in self.listeners:
            if not listener.content.on.message:
                continue
            for subscription in listener.content.on.message:
                if subscription_matches(subscription, message):
                    run_vm(...)
                    break
