from typing import List, Dict

from aleph_message.models import Message, ProgramMessage
from vm_supervisor.pubsub import PubSub
from vm_supervisor.run import run_code_on_event


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

    pubsub: PubSub
    listeners: List[ProgramMessage]

    def __init__(self, pubsub: PubSub):
        self.pubsub = pubsub
        self.listeners = []

    async def trigger(self, message: Message):
        for listener in self.listeners:
            if not listener.content.on.message:
                continue
            for entrypoint in listener.content.on.message:
                for subscription in listener.content.on.message[entrypoint]:
                    if subscription_matches(subscription, message):
                        vm_hash = listener.item_hash
                        event = message.json()
                        # TODO: Run in parallel / asynchronously
                        await run_code_on_event(vm_hash, event, self.pubsub)
                        break

    def register(self, message: ProgramMessage):
        raise NotImplementedError()
