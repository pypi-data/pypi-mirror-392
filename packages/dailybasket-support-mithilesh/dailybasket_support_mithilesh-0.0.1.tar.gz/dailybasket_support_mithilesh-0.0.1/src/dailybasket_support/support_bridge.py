import os
import base64
import boto3
import requests
from typing import Any, Dict, Optional

class SalesforceRefreshClient:
    def __init__(
            self,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            refresh_token: Optional[str] = None,
            login_base_url: Optional[str] = None,
            api_version: str = "v61.0",
    ) -> None:
        self.client_id = (
                client_id
                or "3MVG9Y6d_Btp4xp74w_wPm7MaCvchYo814IX.BXUTYK_3gQqiLOWtj2TcKAspSI_QbehRmfb.Vozr9uM3soT7"
        )
        self.client_secret = (
                client_secret
                or "C5D80F58D89F183272F0A5749BB7E31901F7CC36C6639B759E27D6E77B9E1342"
        )
        self.refresh_token = (
                refresh_token
                or "5Aep8617VFpoP.M.4sDE1_BycnwBVjqNim.CNGQMLsYobTZQoiv_dKPIW1hgA4htlz8CTu6fjrYNGNdAMvb_cL8"
        )
        self.login_base_url = login_base_url or "https://login.salesforce.com"
        self.api_version = api_version or "v61.0"

        if not self.client_id or not self.client_secret or not self.refresh_token:
            raise RuntimeError("Missing Salesforce OAuth configuration")

        self.access_token: Optional[str] = None
        self.instance_url: Optional[str] = None

    def refresh(self) -> Dict[str, Any]:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        resp = requests.post(
            f"{self.login_base_url}/services/oauth2/token",
            data=data,
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()
        self.access_token = payload.get("access_token")
        self.instance_url = payload.get("instance_url")
        if not self.access_token or not self.instance_url:
            raise RuntimeError("Salesforce token response missing fields")
        return payload

    def ensure_token(self) -> None:
        if not self.access_token or not self.instance_url:
            self.refresh()

    def request(
            self,
            method: str,
            path: str,
            json_body: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        self.ensure_token()
        url = self.instance_url.rstrip("/") + path
        headers = {"Authorization": f"Bearer {self.access_token}"}
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        if extra_headers:
            headers.update(extra_headers)

        resp = requests.request(
            method=method.upper(),
            url=url,
            json=json_body,
            params=params,
            headers=headers,
            timeout=20,
        )

        if resp.status_code == 401:
            self.refresh()
            headers["Authorization"] = f"Bearer {self.access_token}"
            resp = requests.request(
                method=method.upper(),
                url=url,
                json=json_body,
                params=params,
                headers=headers,
                timeout=20,
            )

        resp.raise_for_status()
        if not resp.text.strip():
            return {}
        return resp.json()

    def create_case(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/services/data/{self.api_version}/sobjects/Case"
        return self.request("POST", path, json_body=fields)

    def create_attachment(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/services/data/{self.api_version}/sobjects/Attachment"
        return self.request("POST", path, json_body=fields)

    def get_case(self, case_id: str) -> Dict[str, Any]:
        path = f"/services/data/{self.api_version}/sobjects/Case/{case_id}"
        return self.request("GET", path)

    def get_case_status(self, case_id: str) -> Optional[str]:
        data = self.get_case(case_id)
        return data.get("Status")


class SupportBridge:
    def __init__(self, table=None, aws_region: Optional[str] = None) -> None:
        self.sf = SalesforceRefreshClient()
        if table is not None:
            self.table = table
        else:
            region = aws_region or os.getenv("AWS_REGION", "us-east-1")
            table_name = os.getenv("ITEMS_TABLE", "DailyBasketItems")
            dynamo = boto3.resource("dynamodb", region_name=region)
            self.table = dynamo.Table(table_name)

    def create_support_case(
            self,
            order_id: Optional[str],
            name: str,
            email: str,
            description: str,
            attachment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        subject = "DailyBasket support request"
        if order_id:
            subject = f"Order support for {order_id}"

        fields: Dict[str, Any] = {
            "Subject": subject,
            "Origin": "Web",
            "Status": "New",
            "SuppliedName": name,
            "SuppliedEmail": email,
            "Description": description,
        }

        if order_id:
            fields["mks1__OrderId__c"] = order_id

        result = self.sf.create_case(fields)
        case_id = result.get("id")

        if case_id and attachment:
            self._attach_file(case_id, attachment)

        if order_id and self.table and case_id:
            try:
                self.table.update_item(
                    Key={"id": order_id},
                    UpdateExpression="SET sf_case_status = :st, sf_case_id = :cid",
                    ExpressionAttributeValues={
                        ":st": "Open",
                        ":cid": case_id,
                    },
                    ConditionExpression="attribute_exists(#items) AND attribute_exists(#t)",
                    ExpressionAttributeNames={
                        "#items": "items",
                        "#t": "type",
                    },
                )
            except self.table.meta.client.exceptions.ConditionalCheckFailedException:
                pass

        return {"case_id": case_id, "raw": result}

    def _attach_file(self, case_id: str, attachment: Dict[str, Any]) -> None:
        content = attachment.get("content_bytes")
        if not content:
            return
        if isinstance(content, str):
            content = content.encode("utf-8")
        body_b64 = base64.b64encode(content).decode("ascii")
        fields = {
            "ParentId": case_id,
            "Name": attachment.get("filename") or "attachment",
            "Body": body_b64,
        }
        content_type = attachment.get("content_type")
        if content_type:
            fields["ContentType"] = content_type
        self.sf.create_attachment(fields)

    def get_case_status(self, case_id: str) -> Optional[str]:
        if not case_id:
            return None
        data = self.sf.get_case(case_id)
        return data.get("Status")