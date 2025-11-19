"""Simplist model to VTL conversion

usage:
```python
class UserComment(VTLSerializable):
    event_name: Literal["event.user.comment"] = "event.user.comment"
    username: str
    item_ref: str
    comment: str
    timestamp: int
    trace_id: Optional[str] = None
    ttl: Optional[int] = None
```

```python
model = UserComment(
    username="username",
    item_ref="item_id",
    comment="Some comment",
    timestamp=0,
)

print(model.vtl_item_block("USER#COMMENT", "REF#$body.item_id#USER#$context.authorizer.claims['cognito:username']#TS#$context.requestTimeEpoch"))
```
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

class VTLSerializable(BaseModel):
    def vtl_field(self, field: str) -> str:
        """Guess where to pull the field from in VTL context."""
        if field in ("username",):
            return f"$context.authorizer.claims['cognito:username']"
        elif field == "timestamp":
            return "$context.requestTimeEpoch"
        elif field == "trace_id":
            return "$context.requestId"
        elif field == "ttl":
            return "$expiration"
        elif field == "origin":
            return "$input.params('origin')"
        elif field == "source_ip":
            return "$context.identity.sourceIp"
        elif field == "user_agent":
            return "$context.identity.userAgent"
        else:
            return f"$body.{field}"

    def vtl_type(self, field_type: Any) -> str:
        base_type = get_origin(field_type)
        type_args = get_args(field_type)

        if field_type in (int, float) or base_type in (Optional,) and type_args and type_args[0] in (int, float):
            return "N"
        return "S"

    def vtl_item_block(self, pk_expr: str, sk_expr: str) -> str:
        """Render full VTL item block with PK/SK and fields."""
        lines = [
            f'"PK": {{ "S": "{pk_expr}" }},',
            f'"SK": {{ "S": "{sk_expr}" }},'
        ]

        for field_name, model_field in self.model_fields.items():
            if field_name in ("PK", "SK"):
                continue
            type_code = self.vtl_type(model_field.annotation)
            value_expr = self.vtl_field(field_name)
            lines.append(f'"{field_name}": {{ "{type_code}": "{value_expr}" }},')

        return "\n".join(lines).rstrip(",")
