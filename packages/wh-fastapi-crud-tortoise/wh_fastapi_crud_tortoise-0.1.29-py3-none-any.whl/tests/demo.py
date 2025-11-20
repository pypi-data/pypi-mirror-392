"""
Descripttion:
version: 0.x
Author: zhai
Date: 2025-01-16 19:56:59
LastEditors: zhai
LastEditTime: 2025-02-23 09:57:03
"""

import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import List, Optional
import uvicorn


sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # 添加父目录到系统路径
from fastapi_crud_tortoise import (
    CrudModel,
    TortoiseCRUDRouter,
    resp_success,
    resp_fail,
    MODEL_ID_TYPE,
    FileField,
)
from tortoise.contrib.fastapi import register_tortoise
from tests.models.dummy import DepartmentModel, DummyModel, EmployeeModel, TeamModel


class DummyCreateDTO(BaseModel):
    name: str
    age: int
    salary: float
    is_active: bool
    birthdate: date
    created_at: datetime
    notes: str
    # json_data: Optional[dict] = None
    json_data: Optional[FileField] = None


class DummyDTO(BaseModel):
    id: Optional[MODEL_ID_TYPE] = None
    name: Optional[str] = None
    age: Optional[int] = None
    salary: Optional[float] = None
    is_active: Optional[bool] = None
    birthdate: Optional[date] = None
    created_at: Optional[datetime] = None
    notes: Optional[str] = None
    # json_data: Optional[dict] = None
    json_data: Optional[FileField] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreateDTO(BaseModel):
    number: str
    name: str
    retire: bool
    retire_date: Optional[datetime] = None
    department_id: Optional[MODEL_ID_TYPE] = None
    teams_refids: Optional[List[MODEL_ID_TYPE]] = None


class Ref_DepartmentDTO(BaseModel):
    id: Optional[MODEL_ID_TYPE] = None
    name: Optional[str] = None
    factor: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class Ref_TeamDTO(BaseModel):
    id: Optional[MODEL_ID_TYPE] = None
    name: Optional[str] = None


class EmployeeDTO(BaseModel):
    id: Optional[MODEL_ID_TYPE] = None
    number: Optional[str] = None
    name: Optional[str] = None
    retire: Optional[bool] = None
    retire_date: Optional[datetime] = None
    department: Optional[Ref_DepartmentDTO] = None
    department_id: Optional[MODEL_ID_TYPE] = None
    teams: Optional[List[Ref_TeamDTO]] = None
    teams_refids: Optional[List[MODEL_ID_TYPE]] = None

    model_config = ConfigDict(from_attributes=True)


###################################################################################


class DepartmentCreateDTO(BaseModel):
    name: str
    factor: float


class DepartmentDTO(BaseModel):
    id: Optional[MODEL_ID_TYPE] = None
    name: Optional[str] = None
    factor: Optional[float] = None
    employees: Optional[List[EmployeeDTO]] = None
    employees_refids: Optional[List[MODEL_ID_TYPE]] = None

    model_config = ConfigDict(from_attributes=True)


###################################################################################


class TeamCreateDTO(BaseModel):
    name: str
    # employees


class TeamDTO(BaseModel):
    id: Optional[MODEL_ID_TYPE] = None
    name: Optional[str] = None
    employees: Optional[List[EmployeeDTO]] = None
    employees_refids: Optional[List[MODEL_ID_TYPE]] = None

    model_config = ConfigDict(from_attributes=True)


dummy_router = TortoiseCRUDRouter(
    schema=DummyDTO,
    create_schema=DummyCreateDTO,
    db_model=DummyModel,
    prefix="dummy",
    kupload_file_route=True,
    kupdate_file_route=True,
)


employee_router = TortoiseCRUDRouter(
    schema=EmployeeDTO,
    create_schema=EmployeeCreateDTO,
    db_model=EmployeeModel,
    prefix="employee",
)

team_router = TortoiseCRUDRouter(
    schema=TeamDTO,
    create_schema=TeamCreateDTO,
    db_model=TeamModel,
    prefix="team",
)

department_router = TortoiseCRUDRouter(
    schema=DepartmentDTO,
    create_schema=DepartmentCreateDTO,
    db_model=DepartmentModel,
    prefix="department",
)

"""
  "columns": [
    {"name": "工号", "field": "number"},
    {"name": "部门", "field": "department.name", "default": "未分配"},
    {"name": "退休日期", "field": "retire_date", "formatter": "date:%Y-%m-%d"}
  ]
"""


@dummy_router.post("/custom_router")
async def test(para1: int, para2: str):
    return resp_success(data="test custom router")


app = FastAPI(title="FastapiCrudPro")
register_tortoise(
    app,
    config={
        "connections": {
            # If an error occurs, you can try to delete the "migrations/app_system" folder and all tables, and then run the project again
            "sqlite": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": "./tortoise.sqlite3"},
            },
        },
        "apps": {
            # don't modify `app_system`, otherwise you will need to modify all `app_systems` in app/models/admin.py
            "app_system": {
                "models": [
                    "tests.models.dummy",
                ],
                "default_connection": "sqlite",
            },
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    },
    generate_schemas=True,
    # db_url="sqlite://tortoise.sqlite3",
    # modules={
    #     "app_system": {"demo": ["demo"]},
    #     },
    # generate_schemas=True,
    # add_exception_handlers=True,
)


app.include_router(dummy_router)
app.include_router(employee_router)
app.include_router(team_router)
app.include_router(department_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


def main():
    """
    Command line entry point for running the demo server.

    Usage:
        crud-run-demo [--host HOST] [--port PORT] [--reload]
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the FastAPI CRUD Tortoise demo server"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8010, help="Port to bind the server to"
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    print(f"Starting demo server on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "tests.demo:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
