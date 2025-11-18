from typing import Optional

from pydantic import BaseModel, Field, RootModel

from .connection import (
    ClusterConnectionMeta,
    DBConnectionMeta,
    S3ConnectionMeta,
)
from .utils import LocationLevel, MedallionTypes


class SchemaMeta(BaseModel):
    field_name: str
    field_type: str
    field_alias: Optional[str] = Field(None, description="Alias name field")
    field_alias_type: Optional[str] = Field(
        None, description="Alias type field"
    )
    field_required: Optional[bool] = Field(False, description="Required field")
    field_hide: Optional[bool] = Field(False, description="Hide field")


class SchemaRawMeta(SchemaMeta):
    regional_field: Optional[str] = Field(None, description="Regional field")
    none_percentage: Optional[float] = Field(
        0.0, description="Percentage of null / none values"
    )
    unique_value: Optional[list[str]] = Field(
        None, description="Unique values in field"
    )
    describe_field: Optional[str] = Field(None, description="Describe field")


class Schemas(RootModel):
    root: list[SchemaMeta]

    def __iter__(self):  # type: ignore
        return self.root.__iter__()

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return self.root.__len__()


class SimplifieMetadata(BaseModel):
    id: str = Field(..., description="Identifier for the metadata")

    # ? basic
    title: str = Field(
        ..., description="Title, name, or label for the metadata"
    )
    source: str = Field(
        ..., description="Source of the metadata, e.g. www.example.com"
    )
    country: str = Field(..., description="Country of origin")
    year: str | int = Field(..., description="Year of the metadata")
    range_data: str = Field(..., description="Range of data, eg. 2021-2022")
    description: Optional[str] = Field(None)

    # ? Category
    category: str = Field(..., description="Category of the metadata")
    sub_category: Optional[str] = Field(None)

    # ? Schemas
    schemas: Schemas = Field(
        ..., description="Description of all fields in data"
    )

    # ? Database
    database_access: DBConnectionMeta | ClusterConnectionMeta
    table_name: str = Field(..., description="Table name in database")


class FullMetadata(SimplifieMetadata):
    # ? Basic
    sub_title: Optional[str] = Field(None)

    # ? Detail data from source
    # * Use case: bronze
    source_desc: Optional[str] = Field(
        None, description="Description from the source of data"
    )
    source_link: Optional[str] = Field(
        None, description="Link to the source of data"
    )

    # ? Medalion & Inheritance data
    # * Use case: silver, gold
    parents_id: Optional[list[str]] = Field([])
    medalion_type: MedallionTypes = Field(
        ..., description="Medalion type, e.g. BRONZE, SILVER, GOLD"
    )
    joined_by: Optional[str] = Field(None)

    # ? Locational
    # * Use case: if the table is a location table
    location_level: Optional[LocationLevel] = Field(None)
    location_field: Optional[str] = Field(None)

    # ? Data lake
    # * Use case: bronze
    lake_access: Optional[
        S3ConnectionMeta | DBConnectionMeta | ClusterConnectionMeta
    ] = Field(None, description="Data lake access")
    lake_meta_path: Optional[str] = Field(
        None, description="Data lake metadata path"
    )
    lake_data_path: Optional[str] = Field(
        None, description="Data lake data path"
    )
    lake_data_format: Optional[str] = Field(
        None, description="Data lake data format"
    )
