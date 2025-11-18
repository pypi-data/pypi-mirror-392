"""
Enums use readable names for string values expected by the Projectal
API.

```
# Example usage
from projectal.enums import ConstraintType

task = projectal.Task.create(project, {
    'name': 'Example Task',
    'constraintType': ConstraintType.ASAP,
    'taskType': TaskType.Task
})
```
"""


class Currency:
    AED = "AED"
    ARS = "ARS"
    AUD = "AUD"
    BGN = "BGN"
    BRL = "BRL"
    CAD = "CAD"
    CHF = "CHF"
    CLP = "CLP"
    CNY = "CNY"
    COP = "COP"
    CZK = "CZK"
    DKK = "DKK"
    EUR = "EUR"
    GBP = "GBP"
    HKD = "HKD"
    HUF = "HUF"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    JPY = "JPY"
    KRW = "KRW"
    MXN = "MXN"
    MYR = "MYR"
    NOK = "NOK"
    NZD = "NZD"
    PEN = "PEN"
    PHP = "PHP"
    PKR = "PKR"
    PLN = "PLN"
    RON = "RON"
    RUB = "RUB"
    SAR = "SAR"
    SEK = "SEK"
    SGD = "SGD"
    THB = "THB"
    TRY = "TRY"
    TWD = "TWD"
    UAH = "UAH"
    USD = "USD"
    ZAR = "ZAR"


class TaskType:
    Project = "Project"
    Task = "Task"
    Milestone = "Milestone"


class ConstraintType:
    ASAP = "As_soon_as_possible"
    ALAP = "As_late_as_possible"
    SNET = "Start_no_earlier_than"
    SNLT = "Start_no_later_than"
    FNET = "Finish_no_earlier_than"
    FNLT = "Finish_no_later_than"
    MSO = "Must_start_on"
    MFO = "Must_finish_on"


class StaffType:
    Casual = "Casual"
    Contractor = "Contractor"
    Consultant = "Consultant"
    Freelance = "Freelance"
    Intern = "Intern"
    FullTime = "Full_Time"
    PartTime = "Part_Time"


class PayFrequency:
    # OneShot = "One_shot"
    Annually = "Annually"
    Monthly = "Monthly"
    Hourly = "Hourly"
    Daily = "Daily"
    Weekly = "Weekly"


class DateLimit:
    Min = "1970-01-01"
    Max = "3000-01-01"


class CompanyType:
    Primary = "Primary"
    Subsidiary = "Subsidiary"
    Contractor = "Contractor"
    Partner = "Partner"
    Affiliate = "Affiliate"
    Office = "Office"
    Division = "Division"


class CalendarType:
    Leave = "Leave"
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Working = "Working"


class SkillLevel:
    Junior = "Junior"
    Mid = "Mid"
    Senior = "Senior"


class GanttLinkType:
    FinishToStart = "Finish_to_start"
    StartToStart = "Start_to_start"
    FinishToFinish = "Finish_to_finish"
    StartToFinish = "Start_to_finish"


class ComplexityLevel:
    Low = "Low"
    Medium = "Medium"
    High = "High"


class PriorityLevel:
    Low = "Low"
    Normal = "Normal"
    High = "High"
