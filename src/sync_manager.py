"""Synchronization manager for Bowens Island Private Parties connector."""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .cognito_api import CognitoFormsClient
from .excel_handler import ExcelHandler
from .config import Config


class SyncManager:
    """Manager for synchronizing between Cognito Forms and Excel."""

    def __init__(self, config: Config):
        """Initialize the sync manager.

        Args:
            config: Configuration for the sync manager
        """
        self.config = config
        
        # Initialize Cognito Forms client
        cognito_config = config.get("cognito", {})
        self.cognito_client = CognitoFormsClient(
            api_key=cognito_config.get("api_key", ""),
            form_id=cognito_config.get("form_id", ""),
            base_url=cognito_config.get("base_url", "https://www.cognitoforms.com/api")
        )
        
        # Initialize Excel handler
        excel_config = config.get("excel", {})
        self.excel_handler = ExcelHandler(
            file_path=excel_config.get("template_path", ""),
            main_sheet=excel_config.get("main_sheet", "MainData")
        )
    
    def sync_to_excel(self) -> Tuple[int, int, int]:
        """Synchronize data from Cognito Forms to Excel.

        Returns:
            Tuple containing (updated_count, added_count, deleted_count)
        """
        # Get form schema if needed
        schema = self.cognito_client.get_form_schema()
        
        # Create Excel template if it doesn't exist
        if not self.excel_handler.file_exists():
            self.excel_handler.create_template(schema)
        
        # Get last sync time
        last_sync = self.excel_handler.get_last_sync_time()
        
        # Fetch entries from Cognito Forms
        entries = self.cognito_client.get_entries(since=last_sync)
        
        # Transform entries to DataFrame
        df = self._transform_entries_to_dataframe(entries, schema)
        
        # If the Excel file exists, detect changes
        if self.excel_handler.file_exists():
            updated, deleted, added = self.excel_handler.detect_changes(df)
            updated_count, added_count, deleted_count = len(updated), len(added), len(deleted)
        else:
            # First sync
            updated_count, added_count, deleted_count = 0, len(df), 0
        
        # Write data to Excel
        self.excel_handler.write_data(df)
        
        # Update last sync time
        self.excel_handler.set_last_sync_time()
        
        return updated_count, added_count, deleted_count
    
    def sync_to_cognito(self) -> Tuple[int, int, int]:
        """Synchronize changes from Excel to Cognito Forms.

        Returns:
            Tuple containing (updated_count, added_count, deleted_count)
        """
        if not self.excel_handler.file_exists():
            return 0, 0, 0
        
        # Get current data from Excel
        excel_data = self.excel_handler.read_data()
        
        # Get all entries from Cognito Forms
        cognito_entries = self.cognito_client.get_entries()
        
        # Transform to DataFrame for comparison
        cognito_df = self._transform_entries_to_dataframe(
            cognito_entries, self.cognito_client.get_form_schema()
        )
        
        # Detect changes
        updated, deleted, added = self._detect_changes_for_cognito(
            excel_data, cognito_df
        )
        
        # Apply changes to Cognito
        updated_count, added_count, deleted_count = self._apply_changes_to_cognito(
            updated, deleted, added
        )
        
        # Update last sync time
        self.excel_handler.set_last_sync_time()
        
        return updated_count, added_count, deleted_count
    
    def _transform_entries_to_dataframe(self, entries: List[Dict[str, Any]], schema: Dict[str, Any]) -> pd.DataFrame:
        """Transform Cognito Forms entries to a pandas DataFrame.

        Args:
            entries: List of entries from Cognito Forms
            schema: The form schema from Cognito Forms

        Returns:
            DataFrame containing the transformed entries
        """
        # This is a placeholder - actual implementation would depend on the schema
        rows = []
        
        for entry in entries:
            # Extract ID and metadata
            entry_id = entry.get("Id")
            entry_meta = entry.get("Entry", {})
            
            # Build row with all fields
            row = {
                "ID": entry_id,
                "Last Updated": entry_meta.get("DateUpdated"),
                "Status": entry_meta.get("Status")
            }
            
            # Add all other fields (excluding metadata)
            for key, value in entry.items():
                if key not in ["Id", "Entry"]:
                    row[key] = value
            
            rows.append(row)
        
        # Create DataFrame
        if not rows:
            # Create empty DataFrame with appropriate columns
            columns = ["ID", "Last Updated", "Status"]
            # Add columns from schema
            for field in self._extract_fields_from_schema(schema):
                if field not in columns:
                    columns.append(field)
            
            df = pd.DataFrame(columns=columns)
        else:
            df = pd.DataFrame(rows)
        
        return df
    
    def _extract_fields_from_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Extract field names from the Cognito Forms schema.

        Args:
            schema: The Cognito Forms schema

        Returns:
            List of field names
        """
        # Same implementation as in excel_handler.py
        fields = []
        
        # Example logic - would need to be adapted to actual schema format
        if "properties" in schema:
            for prop_name, prop_data in schema["properties"].items():
                if prop_name != "Entry":  # Skip metadata
                    fields.append(prop_name)
        
        return fields
    
    def _detect_changes_for_cognito(self, excel_df: pd.DataFrame, cognito_df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
        """Detect changes from Excel to sync to Cognito Forms.

        Args:
            excel_df: DataFrame from Excel
            cognito_df: DataFrame from Cognito Forms

        Returns:
            Tuple containing (updated_entries, deleted_entry_ids, new_entries)
        """
        # Find updated entries (entries that exist in both but have changes in Excel)
        updated_entries = []
        for _, excel_row in excel_df.iterrows():
            entry_id = excel_row.get("ID")
            if entry_id and not pd.isna(entry_id):
                # Find corresponding row in Cognito data
                cognito_rows = cognito_df[cognito_df["ID"] == entry_id]
                if not cognito_rows.empty:
                    # Compare values
                    cognito_row = cognito_rows.iloc[0]
                    changes = {}
                    for col in excel_row.index:
                        if col not in ["ID", "Last Updated", "Status"]:
                            # Special handling for NaN values
                            excel_val = excel_row[col]
                            cognito_val = cognito_row.get(col)
                            
                            # Both NaN means no change
                            if pd.isna(excel_val) and pd.isna(cognito_val):
                                continue
                                
                            # One NaN and one not NaN means change
                            if pd.isna(excel_val) != pd.isna(cognito_val):
                                changes[col] = None if pd.isna(excel_val) else excel_val
                                continue
                                
                            # Otherwise compare normally
                            if excel_val != cognito_val:
                                changes[col] = excel_val
                    
                    if changes:
                        changes["ID"] = entry_id
                        updated_entries.append(changes)
        
        # Find deleted entries (entries in Cognito but marked for deletion in Excel)
        # For now, we'll assume a "Status" column with "Deleted" indicates deletion
        deleted_ids = []
        for _, excel_row in excel_df.iterrows():
            if excel_row.get("Status") == "Deleted" and excel_row.get("ID") and not pd.isna(excel_row.get("ID")):
                deleted_ids.append(excel_row.get("ID"))
        
        # Find new entries (entries in Excel that don't have an ID yet)
        new_entries = []
        for _, excel_row in excel_df.iterrows():
            entry_id = excel_row.get("ID")
            if pd.isna(entry_id) or not entry_id:
                # Skip rows that are empty (all values are NaN)
                if not all(pd.isna(excel_row[col]) for col in excel_row.index if col != "ID"):
                    # Convert row to dict and filter out NaN values
                    row_dict = {}
                    for key, val in excel_row.items():
                        if key not in ["ID", "Last Updated"] and not pd.isna(val):
                            row_dict[key] = val
                    
                    if row_dict:
                        new_entries.append(row_dict)
        
        return updated_entries, deleted_ids, new_entries
    
    def _apply_changes_to_cognito(self, updated: List[Dict[str, Any]], deleted: List[str], added: List[Dict[str, Any]]) -> Tuple[int, int, int]:
        """Apply changes to Cognito Forms.

        Args:
            updated: List of entries to update
            deleted: List of entry IDs to delete
            added: List of entries to add

        Returns:
            Tuple containing (updated_count, added_count, deleted_count)
        """
        updated_count = 0
        for entry in updated:
            try:
                entry_id = entry.pop("ID")
                
                # Prepare entry data for Cognito Forms API
                entry_data = {
                    "Entry": {
                        "Action": "Update",
                        "Role": "Internal"
                    }
                }
                
                # Add all other fields
                for key, value in entry.items():
                    if key not in ["Last Updated", "Status"]:
                        entry_data[key] = value
                
                self.cognito_client.update_entry(entry_id, entry_data)
                updated_count += 1
            except Exception as e:
                print(f"Error updating entry: {e}")
        
        deleted_count = 0
        for entry_id in deleted:
            try:
                self.cognito_client.delete_entry(entry_id)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting entry: {e}")
        
        added_count = 0
        for entry in added:
            try:
                # Prepare entry data for Cognito Forms API
                entry_data = {
                    "Entry": {
                        "Action": "Submit",
                        "Role": "Internal"
                    }
                }
                
                # Add all other fields
                for key, value in entry.items():
                    if key not in ["ID", "Last Updated", "Status"]:
                        entry_data[key] = value
                
                self.cognito_client.create_entry(entry_data)
                added_count += 1
            except Exception as e:
                print(f"Error creating entry: {e}")
        
        return updated_count, added_count, deleted_count
        
    def get_status(self) -> Dict[str, Any]:
        """Get the current synchronization status.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "last_sync": None,
            "excel_file_exists": False,
            "excel_row_count": 0,
            "cognito_connected": False,
            "cognito_form_name": "",
            "cognito_entry_count": 0
        }
        
        # Check Excel file
        if self.excel_handler.file_exists():
            status["excel_file_exists"] = True
            status["last_sync"] = self.excel_handler.get_last_sync_time()
            
            try:
                df = self.excel_handler.read_data()
                status["excel_row_count"] = len(df)
            except Exception:
                pass
        
        # Check Cognito connection
        try:
            # Try to get form schema
            schema = self.cognito_client.get_form_schema()
            status["cognito_connected"] = True
            
            # Try to get form name
            if schema and "title" in schema:
                status["cognito_form_name"] = schema["title"]
            
            # Try to get entry count
            try:
                entries = self.cognito_client.get_entries()
                status["cognito_entry_count"] = len(entries)
            except Exception:
                pass
        except Exception:
            pass
        
        return status
