"""
The base DynamicEnum class that all dynamic enums inherit from.
"""
from projectal import api


class DynamicEnum:
    _name = None

    @classmethod
    def get(cls):
        if not cls._name:
            raise NotImplementedError
        url = f"/api/system/schema?type=enum&object={cls._name}"
        return api.get(url)

    @classmethod
    def set(cls, payload):
        if not cls._name:
            raise NotImplementedError
        url = (
            f"/api/system/schema?type=enum&object={cls._name}"
            "&opts=allowDisable,allowAdding,allowRename,allowDelete,allowCleanup"
        )
        return api.put(endpoint=url, payload=payload)
