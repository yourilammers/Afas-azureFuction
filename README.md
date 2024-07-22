Azure Function: HTTP Trigger for Pipeline Querying

This Azure Function is designed to authenticate a user via a JWT token, extract the user's email, determine their associated company, and then query Azure Table Storage for pipeline data related to that company. The function returns the pipeline information in a JSON response.
Prerequisites

    Python 3.8 or later
    Azure Functions Core Tools
    An Azure Storage Account with a Table
    Azure AD App Registration

Setup Instructions
Local Development Setup

    Clone the repository

    bash

git clone <repository_url>
cd <repository_directory>


Install the required packages

bash

pip install -r requirements.txt



    func start

    The function should now be running on http://localhost:7071.

Deploy to Azure

    Login to Azure

    bash

az login

Create a Function App in Azure

bash

az functionapp create --resource-group <your_resource_group> --consumption-plan-location <your_location> --runtime python --runtime-version 3.8 --functions-version 3 --name <your_function_app_name> --storage-account <your_storage_account_name>

Deploy the function

bash

    func azure functionapp publish <your_function_app_name>

Environment Variables

    STORAGE_ACCOUNT_NAME: Name of the Azure Storage Account.
    TABLE_NAME: Name of the Azure Table Storage.
    CLIENT_ID: Client ID from Azure AD App Registration.
    TENANT_ID: Tenant ID from Azure AD.

Functionality Overview

    Token Validation: The function validates the JWT token provided in the Authorization header by fetching the public keys from the Microsoft identity platform.

    Email Extraction: Extracts the email from the validated token.

    Company Extraction: Determines the company name from the extracted email.

    Pipeline Query: Queries Azure Table Storage for pipeline information associated with the extracted company name.

    Response: Returns the pipeline information in a JSON format or an error message if any step fails.

Error Handling

If any error occurs during the processing of the request, an appropriate error message will be logged and a 500 HTTP response will be returned with the error details.
Dependencies

All dependencies are listed in the requirements.txt file and can be installed using:

bash

pip install -r requirements.txt

Sample requirements.txt:

kotlin

azure-functions
azure-identity
azure-data-tables
msal
pyjwt
requests

Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your changes or improvements.
License

This project is licensed under the MIT License.
