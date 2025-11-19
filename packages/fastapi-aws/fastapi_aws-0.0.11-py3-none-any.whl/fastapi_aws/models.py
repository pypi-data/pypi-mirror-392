"""Pydantic models for the AWS API integration validation
"""
from pydantic import BaseModel
from typing import get_args, get_origin, List, Dict, Type, Union
import inspect


class IntegrationType(str, Enum):
    AWS_PROXY = "aws_proxy"
    AWS = "aws"
    MOCK = "mock"


class Integration(BaseModel):
    """Baseclass for defining integrations
    TODO: build the integrations with classes and then export to dict.
    """

    type: IntegrationType
    requestTemplates: Dict[str, Any]
    responses: Dict[str, Any]

    def model_dump(self) -> Dict[str, Any]:
        return {"x-amazon-apigateway-integration": super().model_dump()}


class LambdaJSONRequestTemplate(BaseModel):
    body: str
    httpMethod: str = "POST"
    resource: str = "/"
    path: str = "/"
    pathParameters: Optional[Dict[str, str]] = None


class MockIntegration(Integration):
    type: IntegrationType = IntegrationType.MOCK


class ServiceIntegration(Integration):
    uri: str = Field(..., description="arn of the called resource")
    credentials: str = Field(..., description="arn of the IAM used to invoke the resource")
    httpMethod: str = "POST"


class LambdaIntegration(ServiceIntegration):
    type: IntegrationType = IntegrationType.AWS_PROXY
    # uri must be lambda arn


class StepFunctionIntegration(ServiceIntegration):
    type: IntegrationType = IntegrationType.AWS
    # uri: "arn:aws:apigateway:${region}:states:action/StartSyncExecution"


class NotImplementedIntegration(MockIntegration):
    requestTemplates: Dict[str, Any] = {"application/json": {"statusCode": 200}}
    responses: Dict[str, Any] = {
        "default": {
            "statusCode": "200",
            "responseTemplates": {"application/json": '{"status": "not implemented"}'},
        }
    }


class VTLBaseModel(BaseModel):
    """base model which converts itself to a vtl string"""
    def to_vtl(self, root: str = "$data", indent: int = 2) -> str:
        def ind(level): return " " * (level * indent)

        def render_field(name, type_, path, level):
            origin = get_origin(type_)
            args = get_args(type_)

            if inspect.isclass(type_) and issubclass(type_, VTLBaseModel):
                lines = [f'{ind(level)}"{name}": {{']
                lines += render_model(type_, f"{path}.{name}", level + 1)
                lines.append(f'{ind(level)}}}')
                return lines

            elif origin == list and len(args) == 1:
                lines = [f'{ind(level)}"{name}": [']
                lines.append(f'{ind(level + 1)}#foreach($item in {path}.{name})')
                lines.append(f'{ind(level + 2)}"$util.escapeJavaScript($item)"#if($foreach.hasNext),#end')
                lines.append(f'{ind(level + 1)}#end')
                lines.append(f'{ind(level)}]')
                return lines

            elif origin == dict and args[0] == str:
                lines = [f'{ind(level)}"{name}": {{']
                lines.append(f'{ind(level + 1)}#set($keys = {path}.{name}.keySet())')
                lines.append(f'{ind(level + 1)}#foreach($k in $keys)')
                lines.append(f'{ind(level + 2)}"$k": "$util.escapeJavaScript({path}.{name}[$k])"#if($foreach.hasNext),#end')
                lines.append(f'{ind(level + 1)}#end')
                lines.append(f'{ind(level)}}}')
                return lines

            else:
                return [f'{ind(level)}"{name}": "{path}.{name}"']

        def render_model(model_type: Type[BaseModel], path: str, level: int) -> List[str]:
            lines = []
            for field_name, field in model_type.model_fields.items():
                lines += render_field(field_name, field.annotation, path, level)
            return lines

        vtl_lines = ["{"]
        vtl_lines += render_model(self.__class__, root, 1)
        vtl_lines.append("}")
        return "\n".join(vtl_lines)
