from projectal.entity import Entity
from projectal.linkers import *
import projectal


class Booking(Entity, NoteLinker, FileLinker, StageLinker, TagLinker):
    """
    Implementation of the [Booking](https://projectal.com/docs/latest/#tag/Booking) API.
    """

    _path = "booking"
    _name = "booking"
    _links = [NoteLinker, FileLinker, StageLinker, TagLinker]

    @classmethod
    def get(cls, entities, links=None, deleted_at=None):
        """
        Get one or more entities of the same type. The entity
        type is determined by the subclass calling this method.

        `entities`: One of several formats containing the `uuId`s
        of the entities you want to get (see bottom for examples):

        - `str` or list of `str`
        - `dict` or list of `dict` (with `uuId` key)

        `links`: A case-insensitive list of entity names to fetch with
        this entity. For performance reasons, links are only returned
        on demand.

        Links follow a common naming convention in the output with
        a *_List* suffix. E.g.:
        `links=['company', 'location']` will appear as `companyList` and
        `locationList` in the response.
        ```
        # Example usage:
        # str
        projectal.Project.get('1b21e445-f29a-4a9f-95ff-fe253a3e1b11')

        # list of str
        ids = ['1b21e445-f29a...', '1b21e445-f29a...', '1b21e445-f29a...']
        projectal.Project.get(ids)

        # dict
        project = project.Project.create({'name': 'MyProject'})
        # project = {'uuId': '1b21e445-f29a...', 'name': 'MyProject', ...}
        projectal.Project.get(project)

        # list of dicts (e.g. from a query)
        # projects = [{'uuId': '1b21e445-f29a...'}, {'uuId': '1b21e445-f29a...'}, ...]
        project.Project.get(projects)

        # str with links
        projectal.Project.get('1b21e445-f29a...', 'links=['company', 'location']')
        ```

        `deleted_at`: Include this parameter to get a deleted entity.
        This value should be a UTC timestamp from a webhook delete event.
        """
        link_set = cls._get_linkset(links)

        if isinstance(entities, str):
            # String input is a uuId
            payload = [{"uuId": entities}]
        elif isinstance(entities, dict):
            # Dict input needs to be a list
            payload = [entities]
        elif isinstance(entities, list):
            # List input can be a list of uuIds or list of dicts
            # If uuIds (strings), convert to list of dicts
            if len(entities) > 0 and isinstance(entities[0], str):
                payload = [{"uuId": uuId} for uuId in entities]
            else:
                # Already expected format
                payload = entities
        else:
            # We have a list of dicts already, the expected format
            payload = entities

        if deleted_at:
            if not isinstance(deleted_at, int):
                raise projectal.UsageException("deleted_at must be a number")

        url = "/api/{}/get".format(cls._path)
        params = []
        # project and staff links need to be included by default for methods that use get
        # they can't be included in the typical way since they aren't compatible with linking methods
        params.append(
            "links=PROJECT,STAFF,RESOURCE{}".format(
                "," + ",".join(links) if links else ""
            )
        )
        params.append("epoch={}".format(deleted_at - 1)) if deleted_at else None
        if len(params) > 0:
            url += "?" + "&".join(params)

        # We only need to send over the uuIds
        payload = [{"uuId": e["uuId"]} for e in payload]
        if not payload:
            return []
        objects = []
        for i in range(0, len(payload), projectal.chunk_size_read):
            chunk = payload[i : i + projectal.chunk_size_read]
            dicts = api.post(url, chunk)
            for d in dicts:
                obj = cls(d)
                obj._with_links.update(link_set)
                obj._is_new = False
                # Create default fields for links we ask for. Workaround for backend
                # sometimes omitting links if no links exist.
                for link_name in link_set:
                    link_def = obj._link_def_by_name[link_name]
                    if link_def["link_key"] not in obj:
                        if link_def["type"] == dict:
                            obj.set_readonly(link_def["link_key"], None)
                        else:
                            obj.set_readonly(link_def["link_key"], link_def["type"]())
                objects.append(obj)

        if not isinstance(entities, list):
            return objects[0]
        return objects
