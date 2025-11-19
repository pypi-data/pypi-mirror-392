import requests
import urllib3
from typing import Optional, Dict, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIError(Exception):
    pass


class APIClient:
    def __init__(self, host: str, token: str):
        self.host = host
        self.base_headers = {"Authorization": f"Bearer {token}"}
        self.json_headers = {**self.base_headers, "Content-Type": "application/json"}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        url = f"{self.host}{endpoint}/1"
        response = requests.get(
            url, headers=self.base_headers, params=params, verify=False
        )
        if response.status_code == 200:
            return response.json()
        print(f"Error: {response.status_code} - {response.text}")
        return None

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        verify: bool = True,
    ):
        url = f"{endpoint}"
        if files:
            response = requests.post(
                url, headers=self.base_headers, files=files, verify=verify
            )
        else:
            response = requests.post(
                url, headers=self.json_headers, json=data, verify=verify
            )

        if response.status_code in (200, 201):
            return response.json() if response.content else response.text
        print(f"Error: {response.status_code} - {response.text}")
        return None


class RecordCertificateClient:
    def __init__(self, host: str, demo_mode: bool = False, insecure_ssl: bool = False):
        if not host.startswith("http"):
            raise ValueError("Host must include scheme, e.g. https://example.com")
        self.host = host.rstrip("/")
        self.demo_mode = demo_mode
        self.insecure_ssl = insecure_ssl
        # Extract base origin (scheme + host without path/port) for CSRF headers
        from urllib.parse import urlparse
        parsed = urlparse(self.host)
        # Strip port from hostname for CSRF validation
        hostname = parsed.hostname
        self.origin = f"{parsed.scheme}://{hostname}"

    def get_record_certificates(self, scope: str, scope_id: str, schema: str) -> Any:
        if self.demo_mode:
            return {
                "scope": scope,
                "scope_id": scope_id,
                "schema": schema,
                "certificates": ["demo_cert_1"],
            }

        url = f"{self.host}/scopes/{scope}/{scope_id}/records/{schema}/certificates"
        response = requests.get(url, verify=not self.insecure_ssl)
        if response.ok:
            return response.json()
        raise APIError(f"Error fetching certificates: {response.text}")

    def get_record_certificate(
        self, scope: str, scope_id: str, schema: str, record_id: str, name: str
    ) -> str:
        if self.demo_mode:
            return f"Demo cert for {record_id}/{name}"
        url = f"{self.host}/scopes/{scope}/{scope_id}/records/{schema}/{record_id}/certificates/{name}"
        response = requests.get(url, verify=not self.insecure_ssl)
        if response.ok:
            return response.text
        raise APIError(f"Error fetching certificate: {response.text}")

    def create_record_certificate(
        self,
        scope: str,
        scope_id: str,
        schema: str,
        record_id: str,
        name: str,
        pem_string: str,
        auth_token: str,
    ) -> str:
        if self.demo_mode:
            return f"Created demo cert {name} for {record_id}"

        url = f"{self.host}/scopes/{scope}/{scope_id}/records/{schema}/{record_id}/certificates/{name}"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Origin": self.origin,
            "Referer": self.origin,
        }

        files = {"file": ("cert.pem", pem_string, "application/x-pem-file")}

        extra = requests.options if isinstance(requests.options, dict) else {}

        response = requests.post(
            url,
            headers=headers,
            files=files,
            verify=not self.insecure_ssl,
            **extra,
        )

        if response.ok:
            return response.text
        raise APIError(f"Error creating certificate: {response.text}")

    def update_record_certificate(
        self,
        scope: str,
        scope_id: str,
        schema: str,
        record_id: str,
        name: str,
        pem_string: str,
        auth_token: str,
    ) -> str:
        """
        Overwrites the existing certificate for the record.
        """
        if self.demo_mode:
            return f"Updated demo cert {name} for {record_id}"

        url = f"{self.host}/scopes/{scope}/{scope_id}/records/{schema}/{record_id}/certificates/{name}"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Origin": self.origin,
            "Referer": self.origin,
        }

        files = {"file": ("cert.pem", pem_string, "application/x-pem-file")}

        extra = requests.options if isinstance(requests.options, dict) else {}

        response = requests.post(
            url,
            headers=headers,
            files=files,
            verify=not self.insecure_ssl,
            **extra,
        )

        if response.ok:
            return response.text or f"Certificate {name} updated for record {record_id}"
        raise APIError(
            f"Error updating certificate: {response.status_code} - {response.text}"
        )


class AWSCredentialManager:
    def __init__(
        self,
        host: str,
        scope: str,
        scope_id: str,
        auth_token: str,
        schema: str,
        demo_mode: bool = False,
        insecure_ssl: bool = False,
    ):
        self.scope = scope
        self.scope_id = scope_id
        self.cert_client = RecordCertificateClient(host, demo_mode, insecure_ssl)
        self.auth_token = auth_token
        self.schema = schema

    def create_aws_credentials(self, item_id: int, combined_pem: str):
        try:
            self.cert_client.create_record_certificate(
                self.scope,
                self.scope_id,
                self.schema,
                item_id,
                "aws",
                combined_pem,
                auth_token=self.auth_token,
            )
            print("Certificate record created.")
        except APIError as e:
            print("Failed to create certificate:", e)
            raise

    def update_aws_credentials(self, item_id: str, combined_pem: str):
        try:
            self.cert_client.update_record_certificate(
                self.scope,
                self.scope_id,
                self.schema,
                item_id,
                "aws",
                combined_pem,
                auth_token=self.auth_token,
            )
            print("Certificate record updated.")

        except APIError as e:
            print("Failed to update certificate:", e)
            raise
