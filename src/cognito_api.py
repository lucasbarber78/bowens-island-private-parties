"""Cognito Forms API client for Bowens Island Private Parties."""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime


class CognitoFormsClient:
    """Client for interacting with the Cognito Forms API."""

    def __init__(
        self, api_key: str, form_id: str, base_url: str = "https://www.cognitoforms.com/api"
    ):
        """Initialize the Cognito Forms API client.

        Args:
            api_key: The Cognito Forms API key
            form_id: The ID of the Bowens Island Private Party form
            base_url: The base URL for the Cognito Forms API
        """
        self.api_key = api_key
        self.form_id = form_id
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_form_schema(self) -> Dict[str, Any]:
        """Get the schema for the Bowens Island Private Party form.

        Returns:
            The form schema as a dictionary
        """
        url = f"{self.base_url}/forms/{self.form_id}/schema"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_entries(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get entries from the Bowens Island Private Party form.

        Args:
            since: If provided, only get entries updated since this time

        Returns:
            List of form entries
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries"
        
        # TODO: Implement filtering by date when available in the API
        # This is a placeholder for future enhancement
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Get a specific entry by ID.

        Args:
            entry_id: The ID of the entry to retrieve

        Returns:
            The entry data
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries/{entry_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entry in the form.

        Args:
            entry_data: The data for the new entry

        Returns:
            The created entry data
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries"
        response = requests.post(url, headers=self.headers, json=entry_data)
        response.raise_for_status()
        return response.json()

    def update_entry(self, entry_id: str, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing entry.

        Args:
            entry_id: The ID of the entry to update
            entry_data: The updated data for the entry

        Returns:
            The updated entry data
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries/{entry_id}"
        response = requests.patch(url, headers=self.headers, json=entry_data)
        response.raise_for_status()
        return response.json()

    def delete_entry(self, entry_id: str) -> None:
        """Delete an entry.

        Args:
            entry_id: The ID of the entry to delete
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries/{entry_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        
    def get_document(self, entry_id: str, template_id: int) -> Dict[str, Any]:
        """Get a document for an entry.
        
        Args:
            entry_id: The ID of the entry
            template_id: The ID of the document template
            
        Returns:
            The document data
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries/{entry_id}/documents/{template_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
        
    def get_file(self, entry_id: str, file_id: str) -> Dict[str, Any]:
        """Get a file attached to an entry.
        
        Args:
            entry_id: The ID of the entry
            file_id: The ID of the file
            
        Returns:
            The file data
        """
        url = f"{self.base_url}/forms/{self.form_id}/entries/{entry_id}/files/{file_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
