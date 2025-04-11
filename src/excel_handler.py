"""Excel interaction for Bowens Island Private Parties connector."""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Optional: Use xlwings for more advanced Excel interaction if needed
try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False


class ExcelHandler:
    """Handler for Excel file operations."""

    def __init__(self, file_path: str, main_sheet: str = "MainData"):
        """Initialize the Excel handler.

        Args:
            file_path: Path to the Excel file
            main_sheet: Name of the main data sheet
        """
        self.file_path = file_path
        self.main_sheet = main_sheet
        self.metadata_sheet = "Metadata"
        
    def file_exists(self) -> bool:
        """Check if the Excel file exists.

        Returns:
            True if the file exists, False otherwise
        """
        return os.path.exists(self.file_path)
    
    def create_template(self, schema: Dict[str, Any]) -> None:
        """Create a new Excel template based on the form schema.

        Args:
            schema: The Cognito Forms schema
        """
        # Extract field definitions from schema
        fields = self._extract_fields_from_schema(schema)
        
        # Create a DataFrame with the fields as columns
        df = pd.DataFrame(columns=fields)
        
        # Add metadata columns
        df.insert(0, "ID", None)
        df.insert(1, "Last Updated", None)
        df.insert(2, "Status", None)
        
        # Save to Excel
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=self.main_sheet, index=False)
            
            # Create a metadata sheet
            pd.DataFrame({
                "Key": ["LastSync", "FormID"],
                "Value": [datetime.now().isoformat(), ""],
            }).to_excel(writer, sheet_name=self.metadata_sheet, index=False)
            
            # Apply protection to the main sheet if xlwings is available
            if XLWINGS_AVAILABLE:
                try:
                    book = xw.Book(self.file_path)
                    sheet = book.sheets[self.main_sheet]
                    sheet.api.Protect(Password="")
                    book.save()
                    book.close()
                except Exception as e:
                    print(f"Warning: Could not protect sheet: {e}")
    
    def read_data(self) -> pd.DataFrame:
        """Read data from the Excel file.

        Returns:
            DataFrame containing the Excel data
        """
        return pd.read_excel(self.file_path, sheet_name=self.main_sheet)
    
    def write_data(self, data: pd.DataFrame) -> None:
        """Write data to the Excel file.

        Args:
            data: DataFrame to write to Excel
        """
        # If using xlwings, we can update without closing the file
        if XLWINGS_AVAILABLE and os.path.exists(self.file_path):
            try:
                # Try to use xlwings for in-place update
                app = xw.App(visible=False)
                book = app.books.open(self.file_path)
                
                # Unprotect sheet if needed
                try:
                    sheet = book.sheets[self.main_sheet]
                    sheet.api.Unprotect()
                except Exception:
                    pass
                
                # Clear existing data and write new data
                sheet = book.sheets[self.main_sheet]
                current_range = sheet.used_range
                current_range.clear_contents()
                sheet.range("A1").value = data.columns.tolist()
                
                # Convert NaN values to None for Excel
                excel_data = data.values.tolist()
                for i, row in enumerate(excel_data):
                    for j, cell in enumerate(row):
                        if isinstance(cell, float) and np.isnan(cell):
                            excel_data[i][j] = None
                
                sheet.range("A2").value = excel_data
                
                # Update last sync time
                metadata_sheet = book.sheets[self.metadata_sheet]
                metadata_sheet.range("B1").value = datetime.now().isoformat()
                
                # Re-protect sheet
                try:
                    sheet.api.Protect(Password="")
                except Exception:
                    pass
                
                book.save()
                book.close()
                app.quit()
                return
            except Exception as e:
                print(f"Warning: Could not use xlwings: {e}")
                # Fallback to pandas if xlwings fails
        
        # Use pandas to write the file
        mode = 'a' if os.path.exists(self.file_path) else 'w'
        with pd.ExcelWriter(self.file_path, mode=mode, engine='openpyxl', 
                           if_sheet_exists='replace') as writer:
            data.to_excel(writer, sheet_name=self.main_sheet, index=False)
            
            # Update metadata
            try:
                metadata = pd.read_excel(self.file_path, sheet_name=self.metadata_sheet)
                sync_idx = metadata.index[metadata["Key"] == "LastSync"].tolist()
                if sync_idx:
                    metadata.loc[sync_idx[0], "Value"] = datetime.now().isoformat()
                else:
                    metadata = pd.concat([metadata, pd.DataFrame({
                        "Key": ["LastSync"],
                        "Value": [datetime.now().isoformat()]
                    })], ignore_index=True)
                metadata.to_excel(writer, sheet_name=self.metadata_sheet, index=False)
            except Exception:
                # Create metadata sheet if it doesn't exist
                pd.DataFrame({
                    "Key": ["LastSync", "FormID"],
                    "Value": [datetime.now().isoformat(), ""],
                }).to_excel(writer, sheet_name=self.metadata_sheet, index=False)
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Get the timestamp of the last synchronization.

        Returns:
            Datetime of last sync or None if not available
        """
        try:
            metadata = pd.read_excel(self.file_path, sheet_name=self.metadata_sheet)
            last_sync = metadata.loc[metadata["Key"] == "LastSync", "Value"].values
            if len(last_sync) > 0 and last_sync[0] and not pd.isna(last_sync[0]):
                return datetime.fromisoformat(last_sync[0])
        except Exception:
            pass
        return None
    
    def set_last_sync_time(self, sync_time: Optional[datetime] = None) -> None:
        """Set the timestamp of the last synchronization.

        Args:
            sync_time: Datetime to set as last sync time (defaults to now)
        """
        if sync_time is None:
            sync_time = datetime.now()
            
        try:
            # Try to read existing metadata
            metadata = pd.read_excel(self.file_path, sheet_name=self.metadata_sheet)
            sync_idx = metadata.index[metadata["Key"] == "LastSync"].tolist()
            if sync_idx:
                metadata.loc[sync_idx[0], "Value"] = sync_time.isoformat()
            else:
                metadata = pd.concat([metadata, pd.DataFrame({
                    "Key": ["LastSync"],
                    "Value": [sync_time.isoformat()]
                })], ignore_index=True)
            
            # Write updated metadata
            with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl',
                               if_sheet_exists='replace') as writer:
                metadata.to_excel(writer, sheet_name=self.metadata_sheet, index=False)
        except Exception:
            # Create metadata sheet if it doesn't exist
            with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl') as writer:
                pd.DataFrame({
                    "Key": ["LastSync", "FormID"],
                    "Value": [sync_time.isoformat(), ""],
                }).to_excel(writer, sheet_name=self.metadata_sheet, index=False)
    
    def detect_changes(self, new_data: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
        """Detect changes between the Excel file and new data.

        Args:
            new_data: New data to compare with Excel data

        Returns:
            Tuple containing (updated_entries, deleted_entry_ids, new_entries)
        """
        try:
            # Read current data from Excel
            current_data = self.read_data()
            
            # Find updated entries (entries that exist in both but have changes)
            updated_entries = []
            for _, new_row in new_data.iterrows():
                entry_id = new_row.get("ID")
                if entry_id and not pd.isna(entry_id):
                    # Find corresponding row in current data
                    current_rows = current_data[current_data["ID"] == entry_id]
                    if not current_rows.empty:
                        # Compare values
                        current_row = current_rows.iloc[0]
                        changes = {}
                        for col in new_row.index:
                            # Special handling for NaN values
                            new_val = new_row[col]
                            cur_val = current_row[col]
                            
                            # Both NaN means no change
                            if pd.isna(new_val) and pd.isna(cur_val):
                                continue
                                
                            # One NaN and one not NaN means change
                            if pd.isna(new_val) != pd.isna(cur_val):
                                changes[col] = new_val
                                continue
                                
                            # Otherwise compare normally
                            if new_val != cur_val:
                                changes[col] = new_val
                        
                        if changes:
                            changes["ID"] = entry_id
                            updated_entries.append(changes)
            
            # Find deleted entries (entries in current_data but not in new_data)
            current_ids = set(current_data["ID"].dropna())
            new_ids = set(new_data["ID"].dropna())
            deleted_ids = list(current_ids - new_ids)
            
            # Find new entries (entries in new_data but not in current_data)
            new_entries = []
            for _, new_row in new_data.iterrows():
                entry_id = new_row.get("ID")
                if pd.isna(entry_id) or (entry_id and entry_id not in current_ids):
                    # Remove NaN values
                    row_dict = {}
                    for key, value in new_row.items():
                        if not pd.isna(value):
                            row_dict[key] = value
                    new_entries.append(row_dict)
            
            return updated_entries, deleted_ids, new_entries
        except Exception as e:
            print(f"Error detecting changes: {e}")
            # If we can't read the file or there's any error, return empty results
            return [], [], []
    
    def _extract_fields_from_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Extract field names from the Cognito Forms schema.

        Args:
            schema: The Cognito Forms schema

        Returns:
            List of field names
        """
        # This is a placeholder - actual implementation would need to parse the schema
        # based on the specific structure of the Cognito Forms schema
        fields = []
        
        # Example logic - would need to be adapted to actual schema format
        if "properties" in schema:
            for prop_name, prop_data in schema["properties"].items():
                if prop_name != "Entry":  # Skip metadata
                    fields.append(prop_name)
        
        return fields
