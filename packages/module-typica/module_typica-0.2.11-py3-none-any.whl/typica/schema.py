from typing import Any, Optional

from pydantic import BaseModel, Field


class PaginationSchema(BaseModel):
    page: Optional[int] = Field(1, gt=0, description="Page number")
    size: Optional[int] = Field(10, ge=0, description="Page size")


class OrderSchema(BaseModel):
    order_by: Optional[str] = Field(None, description="Order by field")
    order_type: Optional[str | int] = Field(
        None, description="Order type", examples=[1, "asc", "desc"]
    )


class FilterValueSchema(BaseModel):
    filter_value: Optional[Any] = Field(None, description="Filter value")


class FilterSchema(FilterValueSchema):
    filter_by: Optional[str] = Field(None, description="Filter by field")


class FilterOpsSchema(FilterSchema):
    filter_op: Optional[str] = Field(None, description="Filter operation")
