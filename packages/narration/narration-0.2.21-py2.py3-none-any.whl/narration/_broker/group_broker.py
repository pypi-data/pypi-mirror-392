import secrets
import threading

GROUPID_PREFIX = "urn:ugid"


class GroupIdBroker:
    def __init__(self):
        self._mutex = threading.RLock()
        self._key_to_group_ids = {}

    def is_ugid(self, value: str = None) -> bool:
        return value.startswith(GROUPID_PREFIX) if value is not None else False

    def get_ugid(self, key: str) -> str:
        """Get a short unique human *un*friendly group id

        :param key: str:

        """
        with self._mutex:
            group_id = self._key_to_group_ids.get(key, None)
            if group_id is None:
                group_id = f"{GROUPID_PREFIX}:{secrets.token_hex(15)}"
                self._key_to_group_ids[key] = group_id
            return group_id

    def pop_ugid(self, key):
        with self._mutex:
            group_id = self._key_to_group_ids.get(key, None)
            self._key_to_group_ids.pop(group_id, None)


GROUPIDBROKER = GroupIdBroker()
