from aws_cert_manager import AWSCredentialManager
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# HOST = "https://test.public-api.orcatech.org:8087"
HOST = "https://test.c4.orcatech.org:8080/api/public"

SCOPE = "study"
SCOPE_ID = "1"
ITEM_ID = 1
SCHEMA = "com.orcatech.inventory.item"

AUTH_TOKEN = "your-auth-token-here"

with open("aws_cert.pem", "r") as cert_file:
    CERT_PEM = cert_file.read()

with open("aws_key.pem", "r") as key_file:
    KEY_PEM = key_file.read()


combined_pem = CERT_PEM.strip() + "\n" + KEY_PEM.strip()

manager = AWSCredentialManager(
    host=HOST,
    scope=SCOPE,
    scope_id=SCOPE_ID,
    auth_token=AUTH_TOKEN,
    demo_mode=False,
    insecure_ssl=True,
    schema=SCHEMA,
)

manager.create_aws_credentials(item_id=ITEM_ID, combined_pem=combined_pem)

# manager.update_aws_credentials(item_id=ITEM_ID, combined_pem=combined_pem)
