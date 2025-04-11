"""Command-line interface for Bowens Island Private Parties connector."""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .config import Config
from .sync_manager import SyncManager


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Bowens Island Private Parties connector for Cognito Forms and Excel"
    )
    
    # Setup commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup the connector")
    setup_parser.add_argument(
        "--api-key", help="Cognito Forms API key"
    )
    setup_parser.add_argument(
        "--form-id", help="Cognito Forms form ID", default="17"
    )
    setup_parser.add_argument(
        "--excel-path", help="Path to Excel file"
    )
    
    # Sync to Excel command
    sync_to_excel_parser = subparsers.add_parser(
        "sync-to-excel", help="Sync from Cognito Forms to Excel"
    )
    sync_to_excel_parser.add_argument(
        "--excel-path", help="Path to Excel file (overrides config)"
    )
    
    # Sync to Cognito command
    sync_to_cognito_parser = subparsers.add_parser(
        "sync-to-cognito", help="Sync from Excel to Cognito Forms"
    )
    sync_to_cognito_parser.add_argument(
        "--excel-path", help="Path to Excel file (overrides config)"
    )
    sync_to_cognito_parser.add_argument(
        "--confirm", action="store_true", help="Confirm changes before syncing"
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Show sync status"
    )
    status_parser.add_argument(
        "--excel-path", help="Path to Excel file (overrides config)"
    )
    
    return parser.parse_args(args)


def setup(args: argparse.Namespace, config: Config) -> None:
    """Setup the connector configuration.

    Args:
        args: Command-line arguments
        config: Configuration manager
    """
    if args.api_key:
        config.set("cognito.api_key", args.api_key)
    
    if args.form_id:
        config.set("cognito.form_id", args.form_id)
    
    if args.excel_path:
        config.set("excel.template_path", args.excel_path)
    
    print(f"Configuration saved to {config.config_path}")


def sync_to_excel(args: argparse.Namespace, config: Config) -> None:
    """Synchronize data from Cognito Forms to Excel.

    Args:
        args: Command-line arguments
        config: Configuration manager
    """
    # Override Excel path if provided
    if args.excel_path:
        config.set("excel.template_path", args.excel_path)
    
    # Check if Excel path is configured
    excel_path = config.get("excel.template_path")
    if not excel_path:
        print("Error: Excel path not configured. Use 'setup --excel-path' to configure.")
        sys.exit(1)
    
    # Check if API key is configured
    api_key = config.get("cognito.api_key")
    if not api_key:
        print("Error: Cognito Forms API key not configured. Use 'setup --api-key' to configure.")
        sys.exit(1)
    
    # Create sync manager
    sync_manager = SyncManager(config)
    
    print("Synchronizing from Cognito Forms to Excel...")
    try:
        updated, added, deleted = sync_manager.sync_to_excel()
        
        print(f"Synchronization complete:")
        print(f"  - {updated} entries updated")
        print(f"  - {added} entries added")
        print(f"  - {deleted} entries deleted")
    except Exception as e:
        print(f"Error synchronizing: {e}")
        sys.exit(1)


def sync_to_cognito(args: argparse.Namespace, config: Config) -> None:
    """Synchronize data from Excel to Cognito Forms.

    Args:
        args: Command-line arguments
        config: Configuration manager
    """
    # Override Excel path if provided
    if args.excel_path:
        config.set("excel.template_path", args.excel_path)
    
    # Check if Excel path is configured and file exists
    excel_path = config.get("excel.template_path")
    if not excel_path:
        print("Error: Excel path not configured. Use 'setup --excel-path' to configure.")
        sys.exit(1)
    
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found at {excel_path}")
        sys.exit(1)
    
    # Check if API key is configured
    api_key = config.get("cognito.api_key")
    if not api_key:
        print("Error: Cognito Forms API key not configured. Use 'setup --api-key' to configure.")
        sys.exit(1)
    
    # Create sync manager
    sync_manager = SyncManager(config)
    
    # Confirm if needed
    if args.confirm:
        confirm = input("Are you sure you want to sync changes from Excel to Cognito Forms? (y/n): ")
        if confirm.lower() != "y":
            print("Sync cancelled.")
            return
    
    print("Synchronizing from Excel to Cognito Forms...")
    try:
        updated, added, deleted = sync_manager.sync_to_cognito()
        
        print(f"Synchronization complete:")
        print(f"  - {updated} entries updated")
        print(f"  - {added} entries added")
        print(f"  - {deleted} entries deleted")
    except Exception as e:
        print(f"Error synchronizing: {e}")
        sys.exit(1)


def show_status(args: argparse.Namespace, config: Config) -> None:
    """Show synchronization status.

    Args:
        args: Command-line arguments
        config: Configuration manager
    """
    # Override Excel path if provided
    if args.excel_path:
        config.set("excel.template_path", args.excel_path)
    
    # Check if Excel path is configured
    excel_path = config.get("excel.template_path")
    if not excel_path:
        print("Error: Excel path not configured. Use 'setup --excel-path' to configure.")
        sys.exit(1)
    
    # Create sync manager
    sync_manager = SyncManager(config)
    
    # Get status
    status = sync_manager.get_status()
    
    print(f"Excel file:        {excel_path}")
    print(f"  - Exists:        {status['excel_file_exists']}")
    if status['excel_file_exists']:
        print(f"  - Row count:     {status['excel_row_count']}")
    
    print(f"Cognito Forms:")
    print(f"  - Connected:     {status['cognito_connected']}")
    if status['cognito_connected']:
        print(f"  - Form name:     {status['cognito_form_name'] or '(unknown)'}")
        print(f"  - Entry count:   {status['cognito_entry_count']}")
    
    print(f"Last synchronized: {status['last_sync'] or 'Never'}")


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    config = Config()
    
    if args.command == "setup":
        setup(args, config)
    elif args.command == "sync-to-excel":
        sync_to_excel(args, config)
    elif args.command == "sync-to-cognito":
        sync_to_cognito(args, config)
    elif args.command == "status":
        show_status(args, config)
    else:
        # No command or unknown command
        print("Error: No command specified.")
        print("Run with --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
