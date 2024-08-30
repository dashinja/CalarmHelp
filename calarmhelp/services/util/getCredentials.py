import os

from dotenv import load_dotenv
from google.auth import default, identity_pool, impersonated_credentials
from google.auth.transport.requests import Request
from google.cloud import storage
from google.oauth2 import id_token

load_dotenv()


class CredentialService:
    def getEnv(self, env):
        return os.environ.get(env)

    def getCredential(self):
        # Assuming you have obtained an OIDC token from your external identity provider
        oidc_token = self.getEnv("CLIENT_SECRET")
        request = Request()

        # Configure the Workload Identity Pool and Provider IDs
        workload_identity_pool_id = self.getEnv("WORKLOAD_IDENTITY_POOL_ID")
        provider_id = self.getEnv("WORKLOAD_IDENTITY_PROVIDER_ID")
        service_account_email = self.getEnv("SERVICE_ACCOUNT_EMAIL")
        service_account_email_dev = self.getEnv("SERVICE_ACCOUNT_EMAIL_DEV")
        project_id = self.getEnv("PROJECT_ID")
        audience = f"//iam.googleapis.com/projects/{project_id}/locations/global/workloadIdentityPools/{workload_identity_pool_id}/providers/{provider_id}"

        # print all environmental variables
        print("oidc_token: ", oidc_token)
        print("workload_identity_pool_id: ", workload_identity_pool_id)
        print("provider_id: ", provider_id)
        print("service_account_email: ", service_account_email)
        print("audience: ", audience)

        print("before google.auth.defualt()")

        credentials, project_id = default()
        # print("credentials: ", credentials)
        # print("project_id: ", project_id)

        print("BEFORE fetch_id_token_credentials")

        google_oidc_token = id_token.fetch_id_token(request, audience)

        # Generate a Google-signed OIDC token
        # google_oidc_token = id_token.fetch_id_token_credentials(audience=audience, request=request)

        print("google_oidc_token: ", google_oidc_token)

        # google_oidc_token = id_token.IDTokenCredentials.from_service_account_info(
        #   info={},  # No need to provide service account info
        #   target_audience=workload_identity_pool_id,
        #   token_url=f'https://sts.googleapis.com/v1/token',
        #   additional_claims={
        #     "target_audience": f'//iam.googleapis.com/projects/-/locations/global/workloadIdentityPools/{workload_identity_pool_id}/providers/{provider_id}'
        #   }
        # )

        # Use the Google Auth library to exchange the external OIDC token for a Google Cloud access token
        # request = Request()

        print("BEFORE federated_credentials")
        federated_credentials = impersonated_credentials.Credentials(
            source_credentials=google_oidc_token,
            target_principal=service_account_email,
            target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
            lifetime=3600,  # Token lifetime in seconds
            delegates=[],
        )

        # Refresh the credentials to obtain the access token
        federated_credentials.refresh(request)

        # Now you can use federated_credentials to authenticate your requests
        print(federated_credentials.token)
        return federated_credentials
