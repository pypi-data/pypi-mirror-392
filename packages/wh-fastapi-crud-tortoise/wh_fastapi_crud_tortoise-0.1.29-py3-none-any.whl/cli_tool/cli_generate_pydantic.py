import argparse
import importlib
import os
from fastapi_crud_tortoise import CrudModel
from tortoise import Model, fields


def generate_pydantic_classes(model_class):
    """
    根据 Tortoise ORM 模型类生成 Pydantic DTO 类代码
    """

    model_name = model_class.__name__
    if model_name.endswith("Model"):
        model_name = model_name[:-5]  # 去掉最后的 'Model'

    # 获取字段定义，排除 CrudModel 中的字段
    base_fields = {field for field in CrudModel._meta.fields_map}  # 获取 CrudModel 中的字段
    model_fields = model_class._meta.fields_map.items()

    # 生成 CustomerCreateDTO
    create_dto_class_name = f"{model_name}CreateDTO"
    create_dto_code = f"class {create_dto_class_name}(BaseModel):\n"

    # 遍历模型的字段并生成 Pydantic 字段
    for field_name, field_obj in model_fields:
        if field_name not in base_fields:  # 排除 CrudModel 的字段
            field_type = field_obj.__class__

            # 识别字段类型并映射到 Pydantic 类型
            if field_type == fields.CharField:
                pydantic_type = "str"
            elif field_type == fields.IntField:
                pydantic_type = "int"
            elif field_type == fields.BooleanField:
                pydantic_type = "bool"
            elif field_type == fields.FloatField:
                pydantic_type = "float"
            elif field_type == fields.UUIDField:
                pydantic_type = "uuid.UUID"
            elif field_type == fields.DatetimeField:
                pydantic_type = "datetime.datetime"
            else:
                pydantic_type = "str"  # 默认类型为str

            # 添加字段
            create_dto_code += f"    {field_name}: {pydantic_type}\n"

    # 生成 CustomerDTO
    dto_class_name = f"{model_name}DTO"
    dto_code = f"\nclass {dto_class_name}(BaseModel):\n"
    dto_code += f"    id: Optional[uuid.UUID] = None\n"  # 添加id字段，默认可选

    # 遍历模型的字段并生成 Pydantic 字段
    for field_name, field_obj in model_fields:
        if field_name not in base_fields:  # 排除 CrudModel 的字段
            field_type = field_obj.__class__

            # 识别字段类型并映射到 Pydantic 类型
            if field_type == fields.CharField:
                pydantic_type = "Optional[str]"
            elif field_type == fields.IntField:
                pydantic_type = "Optional[int]"
            elif field_type == fields.BooleanField:
                pydantic_type = "Optional[bool]"
            elif field_type == fields.FloatField:
                pydantic_type = "Optional[float]"
            elif field_type == fields.UUIDField:
                pydantic_type = "Optional[uuid.UUID]"
            elif field_type == fields.DatetimeField:
                pydantic_type = "Optional[datetime.datetime]"
            else:
                pydantic_type = "Optional[str]"  # 默认类型为str

            # 添加字段
            dto_code += f"    {field_name}: {pydantic_type} = None\n"

    # 配置类配置（Pydantic的orm_mode）
    dto_code += f"\n    model_config = ConfigDict(from_attributes=True)\n"

    return create_dto_code, dto_code


def main():
    parser = argparse.ArgumentParser(description="生成Pydantic代码")
    parser.add_argument("module_or_file", help="模块路径（例如 models.customer）或Python文件路径（例如 path/to/model.py）")
    parser.add_argument("model", help="要处理的模型类名（例如 CustomerModel）")

    args = parser.parse_args()

    try:
        # 检查是否是文件路径
        if args.module_or_file.endswith('.py'):
            # 处理文件路径
            file_path = os.path.abspath(args.module_or_file)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 将文件所在目录添加到 Python 路径
            import sys
            sys.path.insert(0, os.path.dirname(file_path))
            
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            # 处理模块路径
            module = importlib.import_module(args.module_or_file)
            
        model_class = getattr(module, args.model)

        # 调用生成 Pydantic 类的函数
        create_dto_code, dto_code = generate_pydantic_classes(model_class)

        # 打印结果
        print(f"生成的 {args.model} Create DTO 类：\n")
        print(create_dto_code)

        print(f"\n生成的 {args.model} DTO 类：\n")
        print(dto_code)

    except (ModuleNotFoundError, AttributeError) as e:
        print(f"错误：模块或模型类未找到。请确保模块路径和类名正确。")
        print(f"错误详情: {e}")


if __name__ == "__main__":
    main()


# python cli_generate_pydantic.py app.models.fishery CustomerModel
# python cli_generate_pydantic.py models.daq CustomerModel
