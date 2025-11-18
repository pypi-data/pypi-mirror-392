from projectal.entity import Entity
from projectal.linkers import *


class Activity(
    Entity,
    BookingLinker,
    ContactLinker,
    LocationLinker,
    NoteLinker,
    FileLinker,
    RebateLinker,
    ResourceLinker,
    StaffLinker,
    StageLinker,
    TagLinker,
):
    """
    Implementation of the [Activity](https://projectal.com/docs/latest/#tag/Activity) API.
    """

    _path = "activity"
    _name = "activity"
    _links = [
        BookingLinker,
        ContactLinker,
        LocationLinker,
        NoteLinker,
        FileLinker,
        RebateLinker,
        ResourceLinker,
        StaffLinker,
        StageLinker,
        TagLinker,
    ]
