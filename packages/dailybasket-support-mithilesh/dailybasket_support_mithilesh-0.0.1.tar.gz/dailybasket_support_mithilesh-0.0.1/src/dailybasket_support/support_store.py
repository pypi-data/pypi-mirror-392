import os
import boto3
from decimal import Decimal
from typing import List, Dict
from boto3.dynamodb.conditions import Attr

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ITEMS_TABLE = os.getenv("ITEMS_TABLE", "DailyBasketItems")

dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamo.Table(ITEMS_TABLE)

OPEN_STATUSES = {"New", "Working", "Escalated"}
CLOSED_STATUSES = {"Closed"}

def _plain(o):
    if isinstance(o, list):
        return [_plain(x) for x in o]
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items()}
    if isinstance(o, Decimal):
        f = float(o)
        return int(f) if f.is_integer() else f
    return o

def list_support_tickets(group: str = "open") -> List[Dict]:
    group = (group or "open").lower()

    filter_expr = Attr("sf_case_id").exists()

    if group == "open":
        filter_expr = filter_expr & Attr("sf_case_status").is_in(list(OPEN_STATUSES))
    elif group == "closed":
        filter_expr = filter_expr & Attr("sf_case_status").is_in(list(CLOSED_STATUSES))

    scan_kwargs = {"FilterExpression": filter_expr}

    items = []
    start_key = None

    while True:
        if start_key:
            scan_kwargs["ExclusiveStartKey"] = start_key

        resp = table.scan(**scan_kwargs)
        batch = resp.get("Items", [])

        if group == "other":
            allowed = OPEN_STATUSES | CLOSED_STATUSES
            batch = [
                it
                for it in batch
                if str(it.get("sf_case_status") or "") not in allowed
            ]

        items.extend(batch)
        start_key = resp.get("LastEvaluatedKey")
        if not start_key:
            break

    out = []
    for raw in items:
        item = _plain(raw)
        out.append(
            {
                "order_id": item.get("id"),
                "sf_case_id": item.get("sf_case_id"),
                "sf_case_status": item.get("sf_case_status"),
                "sf_case_last_sync_at": item.get("sf_case_last_sync_at"),
            }
        )
    return out
