from datetime import datetime
from tortoise import fields
from fastapi_crud_tortoise import CrudModel, TortoiseCRUDRouter, resp_success, resp_fail

from fastapi_crud_tortoise import TenantModel, OperationsModel, TenantCrudModel

class DummyModel(CrudModel):
    """记录表"""

    name = fields.CharField(max_length=255, null=False)
    age = fields.IntField()
    salary = fields.FloatField()
    is_active = fields.BooleanField(default=True)
    birthdate = fields.DateField()
    created_at = fields.DatetimeField()
    notes = fields.TextField()
    json_data = fields.JSONField(null=True, default=None)

    class Meta:
        table = "dummy"


class DepartmentModel(CrudModel):
    # id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    factor = fields.FloatField()
    employees = fields.ReverseRelation["EmployeeModel"]

    class Meta:
        table = "department"


class TeamModel(CrudModel):
    name = fields.CharField(max_length=255)
    employees = fields.ReverseRelation["EmployeeModel"]
    # employees = fields.ManyToManyField(
    #     "app_system.EmployeeModel", related_name="teams", through="team_employee"
    # )

    class Meta:
        table = "team"


class EmployeeModel(CrudModel):
    # id = fields.IntField(pk=True)
    number = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255)
    retire = fields.BooleanField(default=False)
    retire_date = fields.DatetimeField(default=datetime.now)
    department = fields.ForeignKeyField("app_system.DepartmentModel", related_name="employees", null=True)
    teams = fields.ManyToManyField("app_system.TeamModel", related_name="employees", through="team_employee")

    class Meta:
        table = "employee"


__all__ = ["DummyModel", "DepartmentModel", "TeamModel", "EmployeeModel", "TenantModel", "OperationsModel"]
