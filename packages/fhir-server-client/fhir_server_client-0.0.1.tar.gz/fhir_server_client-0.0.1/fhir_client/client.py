import requests
from requests.auth import HTTPBasicAuth
from typing import Optional


class FhirClient:
    def __init__(self, url: str, auth: Optional[dict] = None):
        """
        Initializes the FHIR client.

        :param url: URL of the FHIR server.
        :param auth: Dictionary containing 'username' and 'password' for Basic Authentication.
        """
        self.url = url
        if auth:
            self.auth = HTTPBasicAuth(auth["username"], auth["password"])
        else:
            self.auth = None

    def get(self, resource: str):
        """
        Get a FHIR resource from the server.

        :param resource: The resource to retrieve (e.g., "Patient/123").
        :return: Response from the server.
        """
        response = requests.get(f"{self.url}/{resource}", auth=self.auth)
        return response.json()

    def post(self, resource: str, data: dict):
        """
        Add a new resource to the FHIR server.

        :param resource: The resource to post to (e.g., "Patient").
        :param data: The data to post (in JSON format).
        :return: Response from the server.
        """
        response = requests.post(f"{self.url}/{resource}", json=data, auth=self.auth)
        return response.json()

    def put(self, resource: str, data: dict):
        """
        Update an existing resource on the FHIR server.

        :param resource: The resource to update (e.g., "Patient/123").
        :param data: The updated data to put.
        :return: Response from the server.
        """
        response = requests.put(f"{self.url}/{resource}", json=data, auth=self.auth)
        return response.json()

    def delete(self, resource: str):
        """
        Delete a resource from the FHIR server.

        :param resource: The resource to delete (e.g., "Patient/123").
        :return: Response from the server.
        """
        response = requests.delete(f"{self.url}/{resource}", auth=self.auth)
        return response.status_code
