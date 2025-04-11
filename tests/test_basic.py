"""Basic tests for the Bowens Island Private Parties connector."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.cognito_api import CognitoFormsClient
from src.excel_handler import ExcelHandler
from src.sync_manager import SyncManager


class TestConfig(unittest.TestCase):
    """Tests for the Config class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary config file path
        self.temp_config_path = "test_config.yaml"
        # Create a Config instance with the test path
        self.config = Config(self.temp_config_path)

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary config file
        if os.path.exists(self.temp_config_path):
            os.remove(self.temp_config_path)

    def test_get_set(self):
        """Test getting and setting configuration values."""
        # Test setting a value
        self.config.set("test.key", "value")
        # Test getting the value
        self.assertEqual(self.config.get("test.key"), "value")
        # Test getting a value with a default
        self.assertEqual(self.config.get("nonexistent.key", "default"), "default")

    def test_nested_get_set(self):
        """Test getting and setting nested configuration values."""
        # Test setting a nested value
        self.config.set("cognito.api_key", "test_api_key")
        # Test getting the nested value
        self.assertEqual(self.config.get("cognito.api_key"), "test_api_key")


class TestCognitoFormsClient(unittest.TestCase):
    """Tests for the CognitoFormsClient class."""

    def setUp(self):
        """Set up test environment."""
        # Create a CognitoFormsClient instance with test values
        self.client = CognitoFormsClient(
            api_key="test_api_key",
            form_id="17",
            base_url="https://example.com/api"
        )

    @patch("requests.get")
    def test_get_form_schema(self, mock_get):
        """Test getting a form schema."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "schema"}
        mock_get.return_value = mock_response
        # Call the method
        result = self.client.get_form_schema()
        # Check the result
        self.assertEqual(result, {"test": "schema"})
        # Check the request
        mock_get.assert_called_once_with(
            "https://example.com/api/forms/17/schema",
            headers={
                "Authorization": "Bearer test_api_key",
                "Content-Type": "application/json",
            }
        )

    @patch("requests.get")
    def test_get_entries(self, mock_get):
        """Test getting entries."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"test": "entry"}]
        mock_get.return_value = mock_response
        # Call the method
        result = self.client.get_entries()
        # Check the result
        self.assertEqual(result, [{"test": "entry"}])
        # Check the request
        mock_get.assert_called_once_with(
            "https://example.com/api/forms/17/entries",
            headers={
                "Authorization": "Bearer test_api_key",
                "Content-Type": "application/json",
            }
        )


class TestSyncManager(unittest.TestCase):
    """Tests for the SyncManager class."""

    def setUp(self):
        """Set up test environment."""
        # Create a Config instance with test values
        self.config = MagicMock()
        self.config.get.return_value = {"api_key": "test_api_key", "form_id": "17"}
        
        # Create a SyncManager instance with the mock config
        self.sync_manager = SyncManager(self.config)
        
        # Mock the SyncManager's dependencies
        self.sync_manager.cognito_client = MagicMock()
        self.sync_manager.excel_handler = MagicMock()

    def test_sync_to_excel(self):
        """Test syncing from Cognito Forms to Excel."""
        # Mock dependency behavior
        self.sync_manager.cognito_client.get_form_schema.return_value = {"test": "schema"}
        self.sync_manager.cognito_client.get_entries.return_value = [{"test": "entry"}]
        self.sync_manager.excel_handler.file_exists.return_value = True
        self.sync_manager.excel_handler.detect_changes.return_value = ([], [], [])
        self.sync_manager._transform_entries_to_dataframe = MagicMock(return_value="df")
        
        # Call the method
        result = self.sync_manager.sync_to_excel()
        
        # Check dependencies were called
        self.sync_manager.cognito_client.get_form_schema.assert_called_once()
        self.sync_manager.cognito_client.get_entries.assert_called_once()
        self.sync_manager.excel_handler.detect_changes.assert_called_once_with("df")
        self.sync_manager.excel_handler.write_data.assert_called_once_with("df")
        self.sync_manager.excel_handler.set_last_sync_time.assert_called_once()
        
        # Check the result
        self.assertEqual(result, (0, 0, 0))  # No changes


if __name__ == "__main__":
    unittest.main()
