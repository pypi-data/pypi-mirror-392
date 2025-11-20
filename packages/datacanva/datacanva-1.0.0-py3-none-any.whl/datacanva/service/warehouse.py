from logging import Logger

import pandas
from pandas._typing import DtypeObj

from ..api.warehouse import *
from . import Service


def map_dtype(dtype: DtypeObj):
    if pandas.api.types.is_integer_dtype(dtype):
        return DataType.INT
    elif pandas.api.types.is_float_dtype(dtype):
        return DataType.FLOAT
    elif pandas.api.types.is_string_dtype(dtype):
        return DataType.STRING
    elif pandas.api.types.is_bool_dtype(dtype):
        return DataType.BOOLEAN
    elif pandas.api.types.is_datetime64_any_dtype(dtype):
        return DataType.TIMESTAMP
    else:
        raise ValueError(f"Unsupported type: {dtype}")


def dataframe_to_schema(dataframe: pandas.DataFrame):
    fields: list[SchemaField] = []
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        fields.append(
            SchemaField(
                name=column,
                dataType=map_dtype(dtype),
            )
        )
    return Schema(fields=fields)


class Entity:

    def __init__(self, service: "WarehouseService", data: dict):
        self.service = service
        self.id = int(data["id"])
        self.name = str(data["name"])
        self.creator = str(data["creatorUsername"])

    def __str__(self):
        return f"Warehouse/{self.creator}/{self.name}({self.id})"

    def get_schema(self):
        try:
            res = self.service.crud_api.get(self.id)
            return Schema(res["schema"])
        except Exception as e:
            self.service.logger.error(f"Failed to get entity (id: {self.id}): {e}")
            return None

    def get_items_count(self, criteria: Criteria = None):
        try:
            req = GetDataRequest(
                acquireReadLock=True,
                page=0,
                size=1,
                criteria=criteria,
            )
            res = self.service.api.get_data(self.id, req)
            return res["totalItems"]
        except Exception as e:
            self.service.logger.error(f"Failed to get entity items count: {e}")
            return 0

    def get_data(
        self,
        page=0,
        size=1000,
        sort: list[str] = [],
        criteria: Criteria = None,
        drop_columns: list[str] = ["_id", "_tags"],
    ):
        try:
            req = GetDataRequest(
                acquireReadLock=True,
                page=page,
                size=size,
                criteria=criteria,
                sort=sort,
                description="DataLab User Get Data",
            )
            res = self.service.api.get_data(self.id, req)
            dataframe = pandas.DataFrame(res["items"]).drop(
                columns=drop_columns, errors="ignore"
            )

            # convert datetime columns
            schema = self.get_schema()
            if schema is not None:
                for field in schema["fields"]:
                    if field["dataType"] == "TIMESTAMP":
                        dataframe[field["name"]] = pandas.to_datetime(
                            dataframe[field["name"]]
                        )

            return dataframe
        except Exception as e:
            self.service.logger.error(f"Failed to get entity data: {e}")
            return None

    def write_data(
        self,
        dataframe: pandas.DataFrame,
        write_mode: WriteMode = WriteMode.UPSERT,
        upsert_by: list[str] = None,
    ):
        try:
            schema = dataframe_to_schema(dataframe)

            output_dataframe = dataframe.copy()
            for field in schema["fields"]:
                if field["dataType"] == "TIMESTAMP":
                    output_dataframe[field["name"]] = (
                        output_dataframe[field["name"]].astype(int) // 10**6
                    )

            req = WriteDataRequest(
                schema=schema,
                writeMode=write_mode,
                upsertBy=upsert_by,
                data=output_dataframe.to_dict(orient="records"),
                description="DataLab User Write Data",
            )
            self.service.api.write_data(self.id, req)
        except Exception as e:
            self.service.logger.error(f"Failed to write entity data: {e}")

    def delete_data(
        self,
        dataframe: pandas.DataFrame,
        delete_by: list[str],
    ):
        try:
            output_dataframe = dataframe.copy()
            output_dataframe = output_dataframe.drop(
                columns=output_dataframe.select_dtypes(include=["datetime64", "datetimetz"]).columns
            )

            req = WriteDataRequest(
                writeMode=WriteMode.UPSERT,
                deleteMode=True,
                upsertBy=delete_by,
                data=output_dataframe.to_dict(orient="records"),
                description="DataLab User Delete Data",
            )
            self.service.api.write_data(self.id, req)
        except Exception as e:
            self.service.logger.error(f"Failed to delete entity data: {e}")


class WarehouseService(Service[Entity]):

    def __init__(self, logger: Logger, api: WarehouseApi):
        super().__init__(logger, api, Entity)
        self.api = api
