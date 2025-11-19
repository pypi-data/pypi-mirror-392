from typing import Optional
from vtl_serializable import VTLSerializable


class TestEvent(VTLSerializable):
    origin: str
    project: str
    session: str
    timestamp: int
    user_agent: Optional[str] = None
    source_ip: Optional[str] = None
    ttl: Optional[int] = None
    action: str


def test_vtl_field_resolution():
    obj = TestEvent(
        origin="example.com",
        project="test",
        session="abc123",
        timestamp=1234567890,
        action="click"
    )

    assert obj.vtl_field("origin") == "$input.params('origin')"
    assert obj.vtl_field("timestamp") == "$context.requestTimeEpoch"
    assert obj.vtl_field("source_ip") == "$context.identity.sourceIp"
    assert obj.vtl_field("user_agent") == "$context.identity.userAgent"
    assert obj.vtl_field("ttl") == "$expiration"
    assert obj.vtl_field("action") == "$body.action"

def test_vtl_type_inference():
    obj = TestEvent(
        origin="example.com",
        project="test",
        session="abc123",
        timestamp=1234567890,
        action="click"
    )

    assert obj.vtl_type(int) == "N"
    assert obj.vtl_type(str) == "S"
    assert obj.vtl_type(Optional[int]) == "N"
    assert obj.vtl_type(Optional[str]) == "S"

def test_vtl_item_block():
    obj = TestEvent(
        origin="example.com",
        project="test",
        session="abc123",
        timestamp=1234567890,
        action="click"
    )
    result = obj.vtl_item_block("EXPR#PK", "EXPR#SK")
    assert '"PK": { "S": "EXPR#PK" }' in result
    assert '"SK": { "S": "EXPR#SK" }' in result
    assert '"action": { "S": "$body.action" }' in result
