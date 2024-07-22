import logging
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableServiceClient
from msal import ConfidentialClientApplication
import jwt 
from jwt.algorithms import RSAAlgorithm
import requests

# Environment variables or configurations
STORAGE_ACCOUNT_NAME = "afasstorage001"
TABLE_NAME = "afas001tablestorage"
CLIENT_ID = "99fbd4f5-fc2f-40c1-95fa-f8bcae8e8d94"
TENANT_ID = "a3b7e820-e897-498d-a4bf-c723c6f52ab6"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

def get_email_from_token(token):
    try:
        # Fetch the public keys from Microsoft identity platform
        jwks_url = f"{AUTHORITY}/discovery/v2.0/keys"
        jwks_response = requests.get(jwks_url)
        jwks = jwks_response.json()
        
        # Decode the token header to get the kid
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            # Validate the token and decode the payload
            payload = jwt.decode(token, key=RSAAlgorithm.from_jwk(json.dumps(rsa_key)), algorithms=["RS256"], audience=f"api://{CLIENT_ID}")
            logging.info(f"Payload: {payload}")
            email = payload.get("preferred_username") or payload.get("email") or payload.get("upn")
            logging.info(f"Email: {email}")
            return email
        else:
            raise ValueError("Unable to find appropriate key")
    except Exception as e:
        logging.error(f"Token validation error: {e}")
        return None
    

def get_company_from_email(email):
    try:
        # Extract company name from email (assuming email format is user@company.com)
        company_name = email.split('@')[1].split('.')[0]
        logging.info(f'Company name: {company_name}')
        return company_name
    except Exception as e:
        logging.error(f"Error extracting company name from email: {e}")
        return None

def query_pipelines(company_name):
    try:
        credential = DefaultAzureCredential()
        table_service = TableServiceClient(endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net", credential=credential)
        table_client = table_service.get_table_client(table_name=TABLE_NAME)

        query_filter = f"PartitionKey eq '{company_name}'"
        entities = table_client.query_entities(query_filter=query_filter)

        pipelines = []
        for entity in entities:
            pipelines.append({
                "name": entity.get("PipelineName"),
                "link": entity.get("PipelineLink"),
                "description": entity.get("PipelineDescription"),
                "inputFieldInstructions": json.loads(entity.get("InputFieldInstructions", "{}"))
            })

        logging.info(f"Pipelines: {pipelines}")
        return pipelines
    except Exception as e:
        logging.error(f"Error querying pipelines: {e}")
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get the access token from the request header
        auth_header = req.headers.get('Authorization')
        if not auth_header:
            raise ValueError("Missing Authorization header")
        
        token = auth_header.split(' ')[1]
        
        # Validate token and get email
        email = get_email_from_token(token)
        if not email:
            raise ValueError("Invalid token or email extraction failed.")
        
        # Get company name from email
        company_name = get_company_from_email(email)
        if not company_name:
            raise ValueError("Failed to extract company name from email.")
        
        # Query pipelines from Azure Table Storage
        pipelines = query_pipelines(company_name)
        if pipelines is None:
            raise ValueError("Failed to query pipelines.")
        
        return func.HttpResponse(
            body=json.dumps(pipelines),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            body=f"An error occurred: {str(e)}",
            status_code=500
        )
