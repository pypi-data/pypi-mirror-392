from projectal.entity import Entity
from projectal import api
from projectal.linkers import *


class Contact(Entity, CompanyLinker, CustomerLinker, NoteLinker, TagLinker):
    """
    Implementation of the [Contact](https://projectal.com/docs/latest/#tag/Contact) API.
    """

    _path = "contact"
    _name = "contact"
    _links = [NoteLinker, TagLinker]
    _links_reverse = [CompanyLinker, CustomerLinker]

    @classmethod
    def create(
        cls,
        holder,
        entity,
        batch_linking=True,
        disable_system_features=True,
        enable_system_features_on_exit=True,
    ):
        """Create a Contact

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
    def clone(cls, uuId, holder, entity):
        url = "/api/contact/clone?holder={}&reference={}".format(holder, uuId)
        response = api.post(url, entity)
        return response["jobClue"]["uuId"]
