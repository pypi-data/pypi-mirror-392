import datetime
import copy
import sys
import projectal
from projectal.entity import Entity
from projectal.enums import DateLimit
from projectal.linkers import *


class Task(
    Entity,
    ResourceLinker,
    SkillLinker,
    FileLinker,
    StageLinker,
    StaffLinker,
    RebateLinker,
    NoteLinker,
    TagLinker,
    PredecessorTaskLinker,
):
    """
    Implementation of the [Task](https://projectal.com/docs/latest/#tag/Task) API.
    """

    _path = "task"
    _name = "task"
    _links = [
        ResourceLinker,
        SkillLinker,
        FileLinker,
        StageLinker,
        StaffLinker,
        RebateLinker,
        NoteLinker,
        TagLinker,
    ]
    _links_reverse = [
        PredecessorTaskLinker,
    ]

    def _add_link_def(self, cls, reverse=False):
        """
        Each entity is accompanied by a dict with details about how to
        get access to the data of the link within the object. Subclasses
        can pass in customizations to this dict when their APIs differ.

        reverse denotes a reverse linker, where extra work is done to
        reverse the relationship of the link internally so that it works.
        The backend only offers one side of the relationship.
        """
        d = {
            "name": cls._link_name,
            "link_key": cls._link_key or cls._link_name + "List",
            "data_name": cls._link_data_name,
            "type": cls._link_type,
            "entity": cls._link_entity or cls._link_name.capitalize(),
            "reverse": reverse,
        }
        self._link_def_by_key[d["link_key"]] = d
        self._link_def_by_name[d["name"]] = d
        if cls._link_name == "predecessor_task":
            d_after_reverse = copy.deepcopy(d)
            d_after_reverse["reverse"] = False
            self._link_def_by_name["task"] = d_after_reverse
            # We need this to be present in the link def so that
            # returned predecessor tasks can be typed as Tasks
            d_for_pred_link_typing = copy.deepcopy(d)
            d_for_pred_link_typing["link_key"] = "planList"
            self._link_def_by_key[
                d_for_pred_link_typing["link_key"]
            ] = d_for_pred_link_typing

    @classmethod
    def create(
        cls,
        holder,
        entities,
        batch_linking=True,
        disable_system_features=True,
        enable_system_features_on_exit=True,
    ):
        """Create a Task

        `holder`: An instance or the `uuId` of the owner

        `entities`: `dict` containing the fields of the entity to be created,
        or a list of such `dict`s to create in bulk.
        """
        holder_id = holder["uuId"] if isinstance(holder, dict) else holder
        params = "?holder=" + holder_id
        out = super().create(
            entities,
            params,
            batch_linking,
            disable_system_features,
            enable_system_features_on_exit,
        )

        # Tasks should always refer to their parent and project. We don't get this information
        # from the creation api method, but we can insert them ourselves because we know what
        # they are.
        def add_fields(obj):
            obj.set_readonly("projectRef", holder_id)
            obj.set_readonly("parent", obj.get("parent", holder_id))

        if isinstance(out, dict):
            add_fields(out)
        if isinstance(out, list):
            for obj in out:
                add_fields(obj)
        return out

    @classmethod
    def get(cls, entities, links=None, deleted_at=None):
        r = super().get(entities, links, deleted_at)
        if not links:
            return r
        # When Predecessor Task links are fetched,
        # make sure the key matches the name expected
        # by the predecessor linking REST end point
        if PredecessorTaskLinker._link_name.casefold() in (
            link.casefold() for link in links
        ):
            if isinstance(r, dict):
                r["taskList"] = r.pop("planList", [])
                r._Entity__old = copy.deepcopy(r)
            else:
                for entity in r:
                    entity["taskList"] = entity.pop("planList", [])
                    entity._Entity__old = copy.deepcopy(entity)
        return r

    # Override here to correctly format the URL for the Predecessor Task link case
    def _link(
        self, to_entity_name, to_link, operation, update_cache=True, batch_linking=True
    ):
        """
        `to_entity_name`: Destination entity name (e.g. 'staff')

        `to_link`: List of Entities of the same type (and optional data) to link to

        `operation`: `add`, `update`, `delete`

        'update_cache': also modify the entity's internal representation of the links
        to match the operation that was done. Set this to False when replacing the
        list with a new one (i.e., when calling save() instead of a linker method).

        'batch_linking': Enabled by default, batches any link
        updates required into composite API requests. If disabled
        a request will be executed for each link update.
        Recommended to leave enabled to increase performance.
        """

        link_def = self._link_def_by_name[to_entity_name]
        to_key = link_def["link_key"]

        if isinstance(to_link, dict) and link_def["type"] == list:
            # Convert input dict to list when link type is a list (we allow linking to single entity for convenience)
            to_link = [to_link]

            # For cases where user passed in dict instead of Entity, we turn them into
            # Entity on their behalf.
            typed_list = []
            target_cls = getattr(sys.modules["projectal.entities"], link_def["entity"])
            for link in to_link:
                if not isinstance(link, target_cls):
                    typed_list.append(target_cls(link))
                else:
                    typed_list.append(link)
            to_link = typed_list
        else:
            # For everything else, we expect types to match.
            if not isinstance(to_link, link_def["type"]):
                raise api.UsageException(
                    "Expected link type to be {}. Got {}.".format(
                        link_def["type"], type(to_link)
                    )
                )

        if not to_link:
            return

        url = ""
        payload = {}
        request_list = []
        # Is it a reverse linker? If so, invert the relationship
        if link_def["reverse"]:
            for link in to_link:
                # Sets the data attribute on the correct
                # link entity
                if link_def["name"] == "predecessor_task":
                    data_name = link_def.get("data_name")
                    self[data_name] = copy.deepcopy(link[data_name])
                request_list.extend(
                    link._link(
                        self._name,
                        self,
                        operation,
                        update_cache,
                        batch_linking=batch_linking,
                    )
                )
        else:
            # Only keep UUID and the data attribute, if it has one
            def strip_payload(link):
                single = {"uuId": link["uuId"]}
                data_name = link_def.get("data_name")
                if data_name and data_name in link:
                    single[data_name] = copy.deepcopy(link[data_name])
                    # limiting data attribute removal to only planLink
                    # in case of side effects
                    if data_name == "planLink":
                        del link[data_name]
                return single

            # If batch linking is enabled and the entity to link is a list of entities,
            # a separate request must be constructed for each one because the final composite
            # request permits only one input per call
            if to_entity_name == "predecessor_task" or to_entity_name == "task":
                url = "/api/{}/plan/TASK/{}".format(self._path, operation)
            else:
                url = "/api/{}/link/{}/{}".format(self._path, to_entity_name, operation)
            to_link_payload = None
            if isinstance(to_link, list):
                to_link_payload = []
                for link in to_link:
                    if batch_linking:
                        request_list.append(
                            {
                                "method": "POST",
                                "invoke": url,
                                "body": {
                                    "uuId": self["uuId"],
                                    to_key: [strip_payload(link)],
                                },
                            }
                        )
                    else:
                        to_link_payload.append(strip_payload(link))
            if isinstance(to_link, dict):
                if batch_linking:
                    request_list.append(
                        {
                            "method": "POST",
                            "invoke": url,
                            "body": {
                                "uuId": self["uuId"],
                                to_key: strip_payload(to_link),
                            },
                        }
                    )
                else:
                    to_link_payload = strip_payload(to_link)

            if not batch_linking:
                payload = {"uuId": self["uuId"], to_key: to_link_payload}
                api.post(url, payload=payload)

        if not update_cache:
            return request_list

        # Set the initial state if first add. We need the type to be set to correctly update the cache
        if operation == "add" and self.get(to_key, None) is None:
            if link_def.get("type") == dict:
                self[to_key] = {}
            elif link_def.get("type") == list:
                self[to_key] = []

        # Modify the entity object's cache of links to match the changes we pushed to the server.
        if isinstance(self.get(to_key, []), list):
            if operation == "add":
                # Sometimes the backend doesn't return a list when it has none. Create it.
                if to_key not in self:
                    self[to_key] = []

                for to_entity in to_link:
                    self[to_key].append(to_entity)
            else:
                for to_entity in to_link:
                    # Find it in original list
                    for i, old in enumerate(self.get(to_key, [])):
                        if old["uuId"] == to_entity["uuId"]:
                            if operation == "update":
                                self[to_key][i] = to_entity
                            elif operation == "delete":
                                del self[to_key][i]
        if isinstance(self.get(to_key, None), dict):
            if operation in ["add", "update"]:
                self[to_key] = to_link
            elif operation == "delete":
                self[to_key] = None

        # Update the "old" record of the link on the entity to avoid
        # flagging it for changes (link lists are not meant to be user editable).
        if to_key in self:
            self._Entity__old[to_key] = self[to_key]

        return request_list

    def update_order(self, order_at_uuId, order_as=True):
        url = "/api/task/update?order-at={}&order-as={}".format(
            order_at_uuId, "true" if order_as else "false"
        )
        return api.put(url, [{"uuId": self["uuId"]}])

    def link_predecessor_task(self, predecessor_task):
        return self.__plan(self, predecessor_task, "add")

    def relink_predecessor_task(self, predecessor_task):
        return self.__plan(self, predecessor_task, "update")

    def unlink_predecessor_task(self, predecessor_task):
        return self.__plan(self, predecessor_task, "delete")

    @classmethod
    def __plan(cls, from_task, to_task, operation):
        url = "/api/task/plan/task/{}".format(operation)
        # Invert the link relationship to match the linker
        if isinstance(to_task, dict):
            from_task_copy = copy.deepcopy(from_task)
            from_task_copy[PredecessorTaskLinker._link_data_name] = copy.deepcopy(
                to_task[PredecessorTaskLinker._link_data_name]
            )
            payload = {"uuId": to_task["uuId"], "taskList": [from_task_copy]}
            api.post(url, payload=payload)
        elif isinstance(to_task, list):
            for task in to_task:
                from_task_copy = copy.deepcopy(from_task)
                from_task_copy[PredecessorTaskLinker._link_data_name] = copy.deepcopy(
                    task[PredecessorTaskLinker._link_data_name]
                )
                payload = {"uuId": task["uuId"], "taskList": [from_task_copy]}
                api.post(url, payload=payload)
        return True

    def parents(self):
        """
        Return an ordered list of [name, uuId] pairs of this task's parents, up to
        (but not including) the root of the project.
        """
        payload = {
            "name": "Task Parents",
            "type": "msql",
            "start": 0,
            "limit": -1,
            "holder": "{}".format(self["uuId"]),
            "select": [
                ["TASK(one).PARENT_ALL_TASK.name"],
                ["TASK(one).PARENT_ALL_TASK.uuId"],
            ],
        }
        list = api.query(payload)
        # Results come back in reverse order. Flip them around
        list.reverse()
        return list

    def project_uuId(self):
        """Return the `uuId` of the Project that holds this Task."""
        payload = {
            "name": "Project that holds this task",
            "type": "msql",
            "start": 0,
            "limit": 1,
            "holder": "{}".format(self["uuId"]),
            "select": [["TASK.PROJECT.uuId"]],
        }
        projects = api.query(payload)
        for t in projects:
            return t[0]
        return None

    @classmethod
    def add_task_template(cls, project, template):
        """Insert TaskTemplate `template` into Project `project`"""
        url = "/api/task/task_template/add?override=false&group=false"
        payload = {"uuId": project["uuId"], "templateList": [template]}
        api.post(url, payload)

    def reset_duration(self, calendars=None):
        """Set this task's duration based on its start and end dates while
        taking into account the calendar for weekends and scheduled time off.

        calendars is expected to be the list of calendar objects for the
        location of the project that holds this task. You may provide this
        list yourself for efficiency (recommended) - if not provided, it
        will be fetched for you by issuing requests to the server.
        """
        if not calendars:
            if "projectRef" not in self:
                task = projectal.Task.get(self)
                project_ref = task["projectRef"]
            else:
                project_ref = self["projectRef"]
            project = projectal.Project.get(project_ref, links=["LOCATION"])
            for location in project.get("locationList", []):
                calendars = location.calendar()
                break

        start = self.get("startTime")
        end = self.get("closeTime")
        if not start or start == DateLimit.Min:
            return 0
        if not end or end == DateLimit.Max:
            return 0

        # Build a list of weekday names that are non-working
        base_non_working = set()
        location_non_working = {}
        location_working = set()
        for calendar in calendars:
            if calendar["name"] == "base_calendar":
                for item in calendar["calendarList"]:
                    if not item["isWorking"]:
                        base_non_working.add(item["type"])

            if calendar["name"] == "location":
                for item in calendar["calendarList"]:
                    start_date = datetime.date.fromisoformat(item["startDate"])
                    end_date = datetime.date.fromisoformat(item["endDate"])
                    if not item["isWorking"]:
                        delta = start_date - end_date
                        location_non_working[item["startDate"]] = delta.days + 1
                    else:
                        location_working = {
                            (start_date + datetime.timedelta(days=x)).strftime(
                                "%Y-%m-%d"
                            )
                            for x in range((end_date - start_date).days + 1)
                        }

        start = datetime.datetime.fromtimestamp(start / 1000)
        end = datetime.datetime.fromtimestamp(end / 1000)
        minutes = 0
        current = start
        while current <= end:
            if (
                current.strftime("%A") in base_non_working
                and current.strftime("%Y-%m-%d") not in location_working
            ):
                current += datetime.timedelta(days=1)
                continue
            if current.strftime("%Y-%m-%d") in location_non_working:
                days = location_non_working[current.strftime("%Y-%m-%d")]
                current += datetime.timedelta(days=days)
                continue
            minutes += 8 * 60
            current += datetime.timedelta(days=1)

        self["duration"] = minutes
