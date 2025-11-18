from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.enums.status import (
    ListOfDataStatuses,
    OptListOfDataStatuses,
    SimpleDataStatusesMixin,
    FULL_DATA_STATUSES,
)
from maleo.types.enum import OptListOfStrEnumsT
from maleo.types.string import OptStr


class OptionalSimpleDataStatusesMixin(SimpleDataStatusesMixin[OptListOfDataStatuses]):
    statuses: Annotated[
        OptListOfDataStatuses,
        Field(None, description="Data statuses", min_length=1),
    ] = None


class MandatorySimpleDataStatusesMixin(SimpleDataStatusesMixin[ListOfDataStatuses]):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(FULL_DATA_STATUSES, description="Data statuses", min_length=1),
    ] = FULL_DATA_STATUSES


class Search(BaseModel):
    search: Annotated[OptStr, Field(None, description="Search string")] = None


class UseCache(BaseModel):
    use_cache: Annotated[bool, Field(True, description="Whether to use cache")] = True


class Include(BaseModel, Generic[OptListOfStrEnumsT]):
    include: OptListOfStrEnumsT = Field(..., description="Included field(s)")


class Exclude(BaseModel, Generic[OptListOfStrEnumsT]):
    exclude: OptListOfStrEnumsT = Field(..., description="Excluded field(s)")


class Expand(BaseModel, Generic[OptListOfStrEnumsT]):
    expand: OptListOfStrEnumsT = Field(..., description="Expanded field(s)")
