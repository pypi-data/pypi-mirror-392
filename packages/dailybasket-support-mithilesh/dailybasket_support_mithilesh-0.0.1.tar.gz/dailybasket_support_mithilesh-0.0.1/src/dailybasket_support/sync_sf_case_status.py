import os
import json
import boto3
from datetime import datetime, timezone

from support_bridge import SupportBridge

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ITEMS_TABLE = os.getenv("ITEMS_TABLE", "DailyBasketItems")

dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamo.Table(ITEMS_TABLE)

bridge = SupportBridge(table=table, aws_region=AWS_REGION)


def handler(event, context):
    updated = 0
    skipped = 0
    start_key = None

    while True:
        scan_kwargs = {
            "FilterExpression": "attribute_exists(sf_case_id)"
        }
        if start_key:
            scan_kwargs["ExclusiveStartKey"] = start_key

        resp = table.scan(**scan_kwargs)
        items = resp.get("Items", [])

        for item in items:
            order_id = item.get("id")
            case_id = item.get("sf_case_id")

            if not case_id or not order_id:
                skipped += 1
                continue

            try:
                status = bridge.get_case_status(case_id)
            except Exception as e:
                print(f"[sync] error fetching case {case_id} for order {order_id}: {e}")
                skipped += 1
                continue

            if not status:
                skipped += 1
                continue

            status = str(status)
            existing = item.get("sf_case_status")

            if existing == status:
                skipped += 1
                continue

            try:
                table.update_item(
                    Key={"id": order_id},
                    UpdateExpression="SET sf_case_status = :st, sf_case_last_sync_at = :ts",
                    ExpressionAttributeValues={
                        ":st": status,
                        ":ts": datetime.now(timezone.utc).isoformat(),
                    },
                )
                updated += 1
                print(f"[sync] updated order {order_id}: {existing} -> {status}")
            except Exception as e:
                print(f"[sync] failed update for order {order_id}: {e}")
                skipped += 1

        start_key = resp.get("LastEvaluatedKey")
        if not start_key:
            break

    summary = {"updated": updated, "skipped": skipped}
    print("[sync] summary:", json.dumps(summary))
    return summary