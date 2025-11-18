"""
A python client for the [Projectal API](https://projectal.com/docs/latest).

## Getting started

```
import projectal
import os

# Supply your Projectal server URL and account credentials
projectal.api_base = 'https://yourcompany.projectal.com'
projectal.api_username = os.environ.get('PROJECTAL_USERNAME')
projectal.api_password = os.environ.get('PROJECTAL_PASSWORD')

# Test communication with server
status = projectal.status()

# Test account credentials
projectal.login()
details = projectal.auth_details()
```

----

## Changelog

### 5.3.2
- Added batch_linking, disable_system_features, enable_system_features_on_exit parameters for Entity.save().
- Added request chunking for Entity.query() using projectal.query_chunk_size, default value is 10000.

### 5.3.1
- Add Entity.create flag parameters to overriding methods.

### 5.3.0
- parameters: disable_system_features(Default: True), enable_system_features_on_exit(Default: True)
  for Entity.create() and Entity.update().
  Allows for better performance during entity linking steps. With default flags, system features will be disabled
  and re-enabled after each internal query chunk. Better performance can be achieved by setting
  enable_system_features_on_exit to false, but system features must be manually re-enabled afterwards.
- Parameter for Entity.query() to configure request timeout, default is 30 seconds.

### 5.2.0
- Supported handling for new Projectal API rate limiting. When a request is rate limited,
  will pause for the required waiting period before retrying the request.

### 5.1.0
- Added new Staff function: `projectal.Staff.create_contract()`.
  Allows creation of a new contract for the given Staff uuId. It's recommended to set a different
  Department, Position, Start/End Date or Pay Amount for new Contracts to differentiate them.

  Parameters:
  - UUID: uuId of the Source Staff
  - payload: Optional payload to specify updated fields for the new Staff contract
  - end_current_contract (Default=False): Source Staff Contract will have its End Date set to Current Date.
    Source Staff Start Date must be before Current Date.
  - start_new_contract (Default=False): New Staff Contract will have its Start Date set to Current Date.

- Allow fetching Staff entities with "CONTRACT" link. Will return list of all Contracts for each Staff.

### 5.0.0
- Updated `projectal.login()` to use a basic Dict to store the login cookie instead of an instance
  of the RequestsCookieJar object from the Python Requests library. This fixes an issue where an
  indefinite loop can occur when the stored cookie is cleared unexpectedly after attempting to login
  again after a token expired.
- Update the stored cookie whenever a new cookie is returned by a successful request. This takes
  advantage of an updated Projectal implementation that refreshes the login cookie periodically.
  This should avoid the re-authentication procedure in most cases for scripts with long execution
  times.

### 4.3.2
- Added CompanyType.Division enum, matching new system defaults.

### 4.3.1
- Fixed typo in "Getting started" example.
- Fixed typo in 4.3.0 Changelog.

### 4.3.0

**Breaking changes:**

- Added "PREDECESSOR_TASK" option when fetching projectal.Task with links
- Predecessor tasks will be returned as a list of tasks under the taskList attribute
- This attribute name is different to what you would see when using the REST API directly
  (planList). This change was necessary to allow for directly manipulating
  the list of links and then saving the task entity to commit any changes,
  since the REST API is expecting a different key for linking calls (taskList).
- Existing Predecessor Task linking methods were also updated to match the new linking functionality.
  They now work as a reverse linker, automatically inverting the link relationship between
  the task entities. This more closely matches what you would expect to see based on the Web UI.
  I.e. When previously calling `some_task.link_predecessor_task(another_task)`,
  some_task would be set as a predecessor for another_task instead of the other way around.
  Now another_task would be set as the predecessor for some_task.

### 4.2.2
- `projectal.User.current_user_permissions()` fixed incorrect query.
- `projectal.Webhook.list()` default limit increased to 1000.

### 4.2.1
- Added classes allowing for the management of dynamic enums. The user must have the "List Management"
  permission to update enums.

  New classes:
  - `projectal.CompanyTypes`
  - `projectal.SkillLevels`
  - `projectal.StaffTypes`
  - `projectal.PriorityLevels`
  - `projectal.ComplexityLevels`
  - `projectal.CurrencyList`

  The current enum can be retrieved with get(), and updated with set().
  For example, to return the current SkillLevels enum:

  ```
  projectal.SkillLevels.get()
  ```

  For each enum the entire list of key value pairs must be provided when calling set(),
  any existing values that are omitted from the dictionary will be removed,
  and any additional values will be added.

  To update the SkillLevels enum with a new value:

  ```
  new_value_added = {
      "Senior": 10,
      "Mid": 20,
      "Junior": 30,
      # new SkillLevel value "Beginner"
      "Beginner": 40,
  }
  projectal.SkillLevels.set(new_value_added)
  ```

  To change the name of a value, set a new key name for the original value:

  ```
  updated_value_name = {
      # changing "Senior" SkillLevel to "Expert"
      "Expert": 10,
      "Mid": 20,
      "Junior": 30,
  }
  projectal.SkillLevels.set(updated_value_name)
  ```

  To remove an existing value, call set on a dictionary with that value removed:

  ```
  value_removed = {
      "Senior": 10,
      "Mid": 20,
      # "Junior" SkillLevel removed
  }
  projectal.SkillLevels.set(new_value_added)
  ```

  Updating the CurrencyList works differently to the other enums, since the
  names of values must match the alphabetic currency code and the value must
  match the numeric currency code.
  This will cause an exception if you try to change the name for any values.

  Adding a new currency:

  ```
  new_currency_added = {
    "AED": 784
    ...
    # rest of the existing currencies
    ...
    # new currency to add with the alphabetic and numeric code
    "ZWL": 932,
  }
  projectal.CurrencyList.set(new_currency_added)
  ```

  Removing an existing currency requires you to provide the numeric code for
  the currency as a negative value.

  ```
  currency_removed = {
    # this currency will be removed
    "AED": -784
    ...
    # rest of the existing currencies
    ...
  }
  projectal.CurrencyList.set(currency_removed)
  ```

### 4.2.0
Version 4.2.0 accompanies the release of Projectal 4.1.0

- Minimum Projectal version is now 4.1.0.

- Changed order of applying link types when an entity is initialized,
prevents a type error with reverse linking in certain situations.

- `projectal.Task.reset_duration()` now supports adjustments with multi day calendar exceptions.

- `projectal.Task.reset_duration()` location working days override base exceptions.

- `projectal.TaskTemplate.list()` fixed incorrect query when using inherited method.

### 4.1.0
- DateLimit.Max enum value changed from "9999-12-31" to "3000-01-01". This reflects changes to the Projectal
backend that defines this as the maximum allowable date value. The front end typically considers this value as
equivalent with having no end date.

- Updated requirements.txt version for requests package

- Minimum Projectal version is now 4.0.40

### 4.0.3
- When a dict object is passed to the update class method, it will be converted to the corresponding Entity type.
  Allows for proper handling of keys that require being treated as links.

### 4.0.2
- Booking entity is now fetched with project field and either staff or resource field.

- Added missing link methods for 'Booking' entity (Note, File)

- Added missing link methods for 'Activity' entity (Booking, Note, File, Rebate)

- Reduced maximum number of link methods to 100 for a single batch request to prevent timeouts
under heavy load.

### 4.0.1
- Minimum Projectal version is now 4.0.0.

### 4.0.0

Version 4.0.0 accompanies the release of Projectal 4.0.

- Added the `Activity` entity, new in Projectal 4.0.

- Added the `Booking` entity, new in Projectal 4.0.

### 3.1.1
- Link requests generated by 'projectal.Entity.create()' and 'projectal.Entity.update()' are now
  executed in batches. This is enabled by default with the 'batch_linking=True' parameter and can
  be disabled to execute each link request individually. It is recommended to leave this parameter
  enabled as this can greatly reduce the number of network requests.

### 3.1.0
- Minimum Projectal version is now 3.1.5.

- Added `projectal.Webhook.list_events()`. See API doc for details on how to use.

- Added `deleted_at` parameter to `projectal.Entity.get()`. This value should be a UTC timestamp
  from a webhook delete event.

- Added `projectal.ldap_sync()` to initiate a user sync with the LDAP/AD service configured in
  the Projectal server settings.

- Enhanced output of `projectal.Entity.changes()` function when reporting link changes.
  It no longer dumps the entire before-and-after list with the full content of each linked entity.
  Now reports three lists: `added`, `updated`, `removed`. Entities within the `updated` list
  follow the same `old` vs `new` dictionary model for the data attributes within them. E.g:

    ```
    resourceList: [
        'added': [],
        'updated': [
            {'uuId': '14eb4c31-0f92-49d1-8b4d-507ab939003e', 'resourceLink': {'utilization': {'old': 0.1, 'new': 0.9}}},
        ],
        'removed': []
    ]
    ```
  This should result in slimmer logs that are much easier to understand as the changes are
  clearly indicated.

### 3.0.2
- Added `projectal.Entity.get_link_definitions()`. Exposes entity link definition dictionary.
  Consumers can inspect which links an Entity knows about and their internal settings.
  Link definitions that appear here are the links valid for `links=[]` parameters.

### 3.0.1
- Fixed fetching project with links=['task'] not being available.

- Improved Permission.list(). Now returns a dict with the permission name as
  key with Permission objects as the value (instead of list of uuIds).

- Added a way to use the aliasing feature of the API (new in Projectal 3.0).
Set `projectal.api_alias = 'uuid'` to the UUID of a User object and all
requests made will be done as that user. Restore this value to None to resume
normal operation. (Some rules and limitations apply. See API for more details.)

- Added complete support for the Tags entity (including linkers).

### 3.0

Version 3.0 accompanies the release of Projectal 3.0.

**Breaking changes**:

- The `links` parameter on `Entity` functions now consumes a list of entity
  names instead of a comma-separated string. For example:

    ```
    # Before:
    projectal.Staff.get('<uuid>', links='skill,location')  # No longer valid
    # Now:
    projectal.Staff.get('<uuid>', links=['skill', 'location'])
    ```

- The `projectal.enums.SkillLevel` enum has had all values renamed to match the new values
  used in Projectal (Junior, Mid, Senior). This includes the properties on
  Skill entities indicating work time for auto-scheduling (now `juniorLevel`,
  `midLevel`, `seniorLevel`).

**Other changes**:

- Working with entity links has changed in this release. The previous methods
  are still available and continue to work as before, but there is no need
  to interact with the `projectal.linkers` methods yourself anymore.

  You can now modify the list of links within an entity and save the entity
  directly. The library will automatically determine how the links have been
  modified and issue the correct linker methods on your behalf. E.g.,
  you can now do:

    ```
    staff = projectal.Staff.get('<uuid>', links=['skill'])
    staff['firstName'] = "New name"  # Field update
    staff['skillList'] = [skill1, skill2, skill3]  # Link update
    staff.save()  # Both changes are saved

    task = projectal.Task.get('<uuid>', links=['stage'])
    task['stage'] = stage1  # Uses a single object instead of list
    task.save()
    ```

  See `examples/linking.py` for a more complete demonstration of linking
  capabilities and limitations.

- Linkers (`projectal.linkers`) can now be given a list of Entities (of one
 type) to link/unlink/relink in bulk. E.g:
    ```
    staff.unlink_skill(skill1)  # Before
    staff.unlink_skill([skill1, skill2, skill3])  # This works now too
    ```

- Linkers now strip the payload to only the required fields instead of passing
  on the entire Entity object. This cuts down on network traffic significantly.

- Linkers now also work in reverse. The Projectal server currently only supports
  linking entities in one direction (e.g., Company to Staff), which often means
  writing something like:
    ```
    staff.link_location(location)
    company.link_staff(staff)
    ```
  The change in direction is not very intuitive and would require you to constantly
  verify which direction is the one available to you in the documentation.

  Reverse linkers hide this from you and figure out the direction of the relationship
  for you behind the scenes. So now this is possible, even though the API doesn't
  strictly support it:
    ```
    staff.link_location(location)
    staff.link_company(company)
    ```
    Caveat: the documentation for Staff will not list Company links. You will still
    have to look up the Company documentation for the link description.

- Requesting entity links with the `links=` parameter will now always ensure the
  link field (e.g., `taskList`) exists in the result, even if there are no links.
  The server may not always return a value, but we can use a default value ([] for
  lists, None for dicts).

- Added a `Permission` entity to correctly type Permissions in responses.

- Added a `Tag` entity, new in Projectal 3.0.

- Added `links` parameter to `Company.get_primary_company()`

- `Department.tree()`: now consumes a `holder` Entity object instead
  of a uuId.

- `Department.tree()`: added `generic_staff` parameter, new in
  Projectal 3.0.

- Don't break on trailing slash in Projectal URL

- When creating tasks, populate the `projectRef` and `parent` fields in the
  returned Task object.

- Added convenience functions for matching on fields where you only want
  one result (e.g match_one()) which return the first match found.

- Update the entity `history()` method for Projectal 3.0. Some new parameters
  allow you to restrict the history to a particular range or to get only the
  changes for a webhook timestamp.

- Entity objects can call `.history()` on themselves.

- The library now keeps a reference to the User account that is currently logged
  in and using the API: `projectal.api_auth_details`.

**Known issues**:
- You cannot save changes to Notes or Calendars via their holding entity. You
  must save the changes on the Note or Calendar directly. To illustrate:
  ```
  staff = projectal.Staff.get(<uuid>, links=['calendar'])
  calendar = staff['calendarList'][0]
  calendar['name'] = 'Calendar 2'

  # Cannot do this - will not pick up the changes
  staff.save()

  # You must do this for now
  calendar.save()
  ```
  This will be resolved in a future release.

- When creating Notes, the `created` and `modified` values may differ by
  1ms in the object you have a reference to compared to what is actually
  stored in the database.

- Duration calculation is not precise yet (mentioned in 2.1.0)

### 2.1.0
**Breaking changes**:
- Getting location calendar is now done on an instance instead of class. So
  `projectal.Location.calendar(uuid)` is now simply `location.calendar()`
- The `CompanyType.Master` enum has been replaced with `CompanyType.Primary`.
  This was a leftover reference to the Master Company which was renamed in
  Projectal several versions ago.

**Other changes**:
- Date conversion functions return None when given None or empty string
- Added `Task.reset_duration()` as a basic duration calculator for tasks.
  This is a work-in-progress and will be gradually improved. The duration
  calculator takes into consideration the location to remove non-work
  days from the estimate of working duration. It currently does not work
  for the time component or `isWorking=True` exceptions.
- Change detection in `Entity.changes()` now excludes cases where the
  server has no value and the new value is None. Saving this change has
  no effect and would always detect a change until a non-None value is
  set, which is noisy and generates more network activity.

### 2.0.3
- Better support for calendars.
  - Distinguish between calendar containers ("Calendar") and the
    calendar items within them ("CalendarItem").
  - Allow CalendarItems to be saved directly. E.G item.save()
- Fix 'holder' parameter in contact/staff/location/task_template not
  permitting object type. Now consumes uuId or object to match rest of
  the library.
- `Entity.changes()` has been extended with an `old=True` flag. When
  this flag is true, the set of changes will now return both the original
  and the new values. E.g.
```
task.changes()
# {'name': 'current'}
task.changes(old=True)
# {'name': {'old': 'original', 'new': 'current'}}
```
- Fixed entity link cache causing errors when deleting a link from an entity
  which has not been fetched with links (deleting from empty list).

### 2.0.2
- Fixed updating Webhook entities

### 2.0.1
- Fixed application ID not being used correctly.

### 2.0.0
- Version 2.0 accompanies the release of Projectal 2.0. There are no major changes
  since the previous release.
- Expose `Entity.changes()` function. It returns a list of fields on an entity that
  have changed since fetching it. These are the changes that will be sent over to the
  server when an update request is made.
- Added missing 'packaging' dependency to requirements.

### 1.2.0

**Breaking changes**:

- Renamed `request_timestamp` to `response_timestamp` to better reflect its purpose.
- Automatic timestamp conversion into dates (introduced in `1.1.0`) has been reverted.
  All date fields returned from the server remain as UTC timestamps.

  The reason is that date fields on tasks contain a time component and converting them
  into date strings was erasing the time, resulting in a value that does not match
  the database.

  Note: the server supports setting date fields using a date string like `2022-04-05`.
  You may use this if you prefer but the server will always return a timestamp.

  Note: we provide utility functions for easily converting dates from/to
  timestamps expected by the Projectal server. See:
  `projectal.date_from_timestamp()`,`projectal.timestamp_from_date()`, and
  `projectal.timestamp_from_datetime()`.

**Other changes**:
- Implement request chunking - for methods that consume a list of entities, we now
  automatically batch them up into multiple requests to prevent timeouts on really
  large request. Values are configurable through
  `projectal.chunk_size_read` and `projectal.chunk_size_write`.
  Default values: Read: 1000 items. Write: 200 items.
- Added profile get/set functions on entities for easier use. Now you only need to supply
  the key and the data. E.g:

```
key = 'hr_connector'
data = {'staff_source': 'company_z'}
task.profile_set(key, data)
```

- Entity link methods now automatically update the entity's cached list of links. E.g:
  a task fetched with staff links will have `task['staffList'] = [Staff1,Staff2]`.
  Before, doing a `task.link_staff(staff)` did not modify the list to reflect the
  addition. Now, it will turn into `[Staff1,Staff2,Staff3]`. The same applies for update
  and delete.

  This allows you to modify links and continue working with that object without having
  to fetch it again to obtain the most recent link data. Be aware that if you acquire
  the object without requesting the link data as well
  (e.g: `projectal.Task.get(id, links='STAFF')`),
  these lists will not accurately reflect what's in the database, only the changes made
  while the object is held.

- Support new `applicationId` property on login. Set with: `projectal.api_application_id`.
  The application ID is sent back to you in webhooks so you know which application was
  the source of the event (and you can choose to filter them accordingly).
- Added `Entity.set_readonly()` to allow setting values on entities that will not
  be sent over to the server when updating/saving the entity.

  The main use case for this is to populate cached entities which you have just created
  with values you already know about. This is mainly a workaround for the limitation of
  the server not sending the full object back after creating it, resulting in the client
  needing to fetch the object in full again if it needs some of the fields set by the
  server after creation.

  Additionally, some read-only fields will generate an error on the server if
  included in the update request. This method lets you set these values on newly
  created objects without triggering this error.

  A common example is setting the `projectRef` of a task you just created.


### 1.1.1
- Add support for 'profiles' API. Profiles are a type of key-value storage that target
  any entity. Not currently documented.
- Fix handling error message parsing in ProjectalException for batch create operation
- Add `Task.update_order()` to set task order
- Return empty list when GETing empty list instead of failing (no request to server)
- Expose the timestamp returned by requests that modify the database. Use
  `projectal.request_timestamp` to get the value of the most recent request (None
  if no timestamp in response)

### 1.1.0
- Minimum Projectal version is now 1.9.4.

**Breaking changes**:
- Entity `list()` now returns a list of UUIDs instead of full objects. You may provide
  an `expand` parameter to restore the previous behavior: `Entity.list(expand=True)`.
  This change is made for performance reasons where you may have thousands of tasks
  and getting them all may time out. For those cases, we suggest writing a query to filter
  down to only the tasks and fields you need.
- `Company.get_master_company()` has been renamed to `Company.get_primary_company()`
  to match the server.
- The following date fields are converted into date strings upon fetch:
  `startTime`, `closeTime`, `scheduleStart`, `scheduleFinish`.
  These fields are added or updated using date strings (like `2022-03-02`), but the
  server returns timestamps (e.g: 1646006400000) upon fetch, which is confusing. This
  change ensures they are always date strings for consistency.

**Other changes**:
- When updating an entity, only the fields that have changed are sent to the server. When
  updating a list of entities, unmodified entities are not sent to the server at all. This
  dramatically reduces the payload size and should speed things up.
- When fetching entities, entity links are now typed as well. E.g. `project['rebateList']`
  contains a list of `Rebate` instead of `dict`.
- Added `date_from_timestamp()` and `timestamp_from_date()` functions to help with
  converting to/from dates and Projectal timestamps.
- Entity history now uses `desc` by default (index 0 is newest)
- Added `Project.tasks()` to list all task UUIDs within a project.

### 1.0.3
- Fix another case of automatic JWT refresh not working

### 1.0.2
- Entity instances can `save()` or `delete()` on themselves
- Fix broken `dict` methods (`get()` and `update()`) when called from Entity instances
- Fix automatic JWT refresh only working in some cases

### 1.0.1
- Added `list()` function for all entities
- Added search functions for all entities (match-, search, query)
- Added `Company.get_master_company()`
- Fixed adding template tasks

"""

import logging
import os

from projectal.entities import *
from projectal.dynamic_enums import *
from .api import *
from . import profile

api_base = os.getenv("PROJECTAL_URL")
api_username = os.getenv("PROJECTAL_USERNAME")
api_password = os.getenv("PROJECTAL_PASSWORD")
api_application_id = None
api_auth_details = None
api_alias = None
cookies = None
chunk_size_read = 1000
chunk_size_write = 200
query_chunk_size = 10000

# Records the timestamp generated by the last request (database
# event time). These are reported on add or updates; if there is
# no timestamp in the response, this is set to None.
response_timestamp = None


# The minimum version number of the Projectal instance that this
# API client targets. Lower versions are not supported and will
# raise an exception.
MIN_PROJECTAL_VERSION = "5.3.0"

__verify = True

logging.getLogger("projectal-api-client").addHandler(logging.NullHandler())
