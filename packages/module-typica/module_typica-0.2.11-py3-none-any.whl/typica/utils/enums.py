from enum import Enum

from deprecated import deprecated


class EnumDetails(Enum):
    @classmethod
    def list(cls):
        """
        Return a list of all Enum values.

        :return: A list of all Enum values.
        """
        return list(map(lambda c: c.value, cls))

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the Enum.

        :param args: The first argument will be used as the value for the Enum.
        :param kwargs: The description keyword argument can be used to set a description for the Enum.
        :return: The new Enum instance.
        """
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, value, description: str | None = None):
        """
        Initialize an EnumDetails instance.

        :param value: The value of the Enum.
        :param description: The description of the Enum.
        """
        self._value_ = value
        self._description_ = description

    @property
    def description(self):
        """
        Get the description of the Enum value.

        :return: The description associated with the Enum value.
        """
        return self._description_


@deprecated(
    version="0.2.0", reason="EnumV2 is deprecated, use EnumDetails instead"
)
class EnumV2(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Operator(EnumDetails):
    equal = ("eq", "value is equals to")
    unequal = ("ne", "value isn't equals to")
    regex = ("re", "regex match")
    gte = ("gte", "value is greater equals to")
    gt = ("gt", "value is greater to")
    lte = ("lte", "value is lower equals to")
    lt = ("lt", "value is lower to")
    include = ("in", "values that must exist")
    exclude = ("nin", "values that don't exist")
    exist = ("exist", "value is exist")
    not_exist = ("exist", "value is exist")


class FilterOption(EnumDetails):
    must = ("must", "List of filter must exact")
    mustnt = ("mustnt", "List of filter mustn't exact")
    should = ("should", "List of filter should exact")
    shouldnt = ("shouldnt", "List of filter shouldn't exact")


class LocationLevel(EnumDetails):
    CONTINENT = ("continent", "Continent level data")
    COUNTRY = ("country", "Country level data")
    PROVINCE = ("province", "Province level data")
    CITY = ("city", "City level data")
    DISTRICT = ("district", "District level data")
    SUBDISTRICT = ("subdistrict", "Subdistrict level data")


class MedallionTypes(EnumDetails):
    LAKE = ("lake", "Lake data")
    BRONZE = ("bronze", "bronze level Medallion")
    SILVER = ("silver", "silver level Medallion")
    GOLD = ("gold", "gold level Medallion")
    OTHER = ("other", "other than any level Medallion")


class DataStatus(str, EnumV2):
    """
    Default status of data
    """

    active = "active"
    archive = "archive"
    deleted = "deleted"
    success = "success"
    failed = "failed"
    published = "published"
    unpublished = "unpublished"


class ConnectionTypes(str, EnumV2):
    """
    Connection types supported on ConnectionUriMeta
    """

    clickhouse = "clickhouse"
    elastic = "elasticsearch"
    mongo = "mongo"
    postgre = "postgresql"
    mysql = "mysql"
    redis = "redis"
    s3aws = "s3aws"


class ResponseMessage(str, EnumV2):
    """
    Base response service
    """

    ok = "OK"
    failed = "Failed"
    success = "Success"
    update = "Updated"
    delete = "Deleted"
    archive = "Archived"


class ErrorResponseMessage(str, EnumV2):
    """
    Base error response service
    """

    # * base
    alreadyExist = "is already exist"
    isNotExist = "isn't exist"
    isInvalid = "is invalid"
    notFound = "isn't found"
    expired = "is expired"

    # * with sub/ob-ject
    dataAlreadyExist = "Data is already exist"
    dataIsNotExist = "Data isn't exist"
    dataIsInvalid = "Data is invalid"
    dataNotFound = "Data isn't found"
    tokenExpired = "Token is expired"

    # * others
    forbidden = "Forbidden access"
    unAuthz = "Unathorized"
    wentWrong = "Service error, please tell admin"
