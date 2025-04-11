"""Basic example of using the Bowens Island Private Parties connector."""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.sync_manager import SyncManager


def main():
    """Run a basic synchronization example."""
    # Create configuration
    config = Config()
    
    # Set configuration values
    config.set("cognito.api_key", os.environ.get("COGNITO_API_KEY", ""))
    config.set("cognito.form_id", os.environ.get("COGNITO_FORM_ID", "17"))
    
    excel_path = os.environ.get("EXCEL_PATH", "bowens_island_bookings.xlsx")
    config.set("excel.template_path", excel_path)
    
    # Create sync manager
    sync_manager = SyncManager(config)
    
    # Perform sync from Cognito to Excel
    print(f"Syncing from Cognito Forms to Excel file: {excel_path}")
    updated, added, deleted = sync_manager.sync_to_excel()
    
    print(f"Synchronization complete:")
    print(f"  - {updated} entries updated")
    print(f"  - {added} entries added")
    print(f"  - {deleted} entries deleted")
    
    # Check if any changes were made to the Excel file
    print("\nChecking for changes to sync back to Cognito Forms...")
    status = sync_manager.get_status()
    
    print(f"Excel file exists: {status['excel_file_exists']}")
    print(f"Cognito connected: {status['cognito_connected']}")
    print(f"Last sync time: {status['last_sync']}")
    
    # Note: In a real application, you would make changes to the Excel file
    # and then run sync_to_cognito() to push changes back to Cognito Forms


if __name__ == "__main__":
    main()
