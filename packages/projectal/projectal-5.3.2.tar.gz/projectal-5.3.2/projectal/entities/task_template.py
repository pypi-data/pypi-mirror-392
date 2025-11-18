from projectal.entity import Entity
from projectal.linkers import *


class TaskTemplate(
    Entity,
    ResourceLinker,
    SkillLinker,
    FileLinker,
    StaffLinker,
    RebateLinker,
    NoteLinker,
    TagLinker,
):
    """
    Implementation of the
    [Task Template](https://projectal.com/docs/latest/#tag/Task-Template) API.
    """

    _path = "template/task"
    _name = "task_template"
    _links = [
        ResourceLinker,
        SkillLinker,
        FileLinker,
        StaffLinker,
        RebateLinker,
        NoteLinker,
        TagLinker,
    ]

    def clone(self, holder, entity):
        url = "/api/template/task/clone?holder={}&reference={}".format(
            holder["uuId"], self["uuId"]
        )
        response = api.post(url, entity)
        return response["jobClue"]["uuId"]

    @classmethod
    def create(
        cls,
        holder,
        entity,
        batch_linking=True,
        disable_system_features=True,
        enable_system_features_on_exit=True,
    ):
        """Create a Task Template

        `holder`: `uuId` of the owner

        `entity`: The fields of the entity to be created
        """
        holder = holder["uuId"] if isinstance(holder, dict) else holder
        params = "?holder=" + holder
        return super().create(
            entity,
            params,
            batch_linking,
            disable_system_features,
            enable_system_features_on_exit,
        )

    @classmethod
    def list(cls, expand=False, links=None):
        """Return a list of all entity UUIDs of this type.

        You may pass in `expand=True` to get full Entity objects
        instead, but be aware this may be very slow if you have
        thousands of objects.

        If you are expanding the objects, you may further expand
        the results with `links`.
        """

        payload = {
            "name": "List all entities of type {}".format(cls._name.upper()),
            "type": "msql",
            "start": 0,
            "limit": -1,
            "select": [["PROJECT_TEMPLATE.{}.uuId".format(cls._name.upper())]],
        }
        ids = api.query(payload)
        ids = [id_[0] for id_ in ids]
        if ids:
            return cls.get(ids, links=links) if expand else ids
        return []

    @classmethod
    def link_predecessor_task(cls, task, predecessor_task):
        return cls.__plan(task, predecessor_task, "add")

    @classmethod
    def relink_predecessor_task(cls, task, predecessor_task):
        return cls.__plan(task, predecessor_task, "update")

    @classmethod
    def unlink_predecessor_task(cls, task, predecessor_task):
        return cls.__plan(task, predecessor_task, "delete")

    @classmethod
    def __plan(cls, from_task, to_task, operation):
        url = "/api/template/task/plan/task/{}".format(operation)
        payload = {"uuId": from_task["uuId"], "taskList": [to_task]}
        api.post(url, payload=payload)
        return True
