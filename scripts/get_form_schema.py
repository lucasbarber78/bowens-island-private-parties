#!/usr/bin/env python3
"""Script to get and save the schema for a Cognito Form."""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from src.config import Config


def get_form_schema(api_key, form_id):
    """Get the schema for a Cognito Form.
    
    Args:
        api_key: Your Cognito Forms API key
        form_id: The ID of the form to get the schema for
        
    Returns:
        The form schema as a dictionary
    """
    # Set up the request headers with authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make the request to the API
    url = f"https://www.cognitoforms.com/api/forms/{form_id}/schema"
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Return the schema as a dictionary
    return response.json()


def main():
    """Main entry point for the script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Get and save the schema for a Cognito Form"
    )
    parser.add_argument(
        "--api-key", help="Cognito Forms API key"
    )
    parser.add_argument(
        "--form-id", help="Cognito Forms form ID", default="17"
    )
    parser.add_argument(
        "--output", help="Output file path", default="form_schema.json"
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Format the JSON output for readability"
    )
    
    args = parser.parse_args()
    
    # Try to get API key from config if not provided
    api_key = args.api_key
    if not api_key:
        config = Config()
        api_key = config.get("cognito.api_key")
        if not api_key:
            print("Error: No API key provided.")
            print("Use --api-key or configure it in the settings.")
            sys.exit(1)
    
    # Try to get form ID from config if not provided
    form_id = args.form_id
    if not form_id:
        config = Config()
        form_id = config.get("cognito.form_id")
        if not form_id:
            print("Error: No form ID provided.")
            print("Use --form-id or configure it in the settings.")
            sys.exit(1)
    
    # Get the form schema
    try:
        print(f"Getting schema for form ID: {form_id}")
        schema = get_form_schema(api_key, form_id)
        
        # Save the schema to a file
        indent = 2 if args.pretty else None
        with open(args.output, 'w') as f:
            json.dump(schema, f, indent=indent)
        
        print(f"Schema saved to: {args.output}")
        
        # Print schema summary
        if 'title' in schema:
            print(f"Form Title: {schema['title']}")
        
        if 'properties' in schema:
            fields = [prop for prop in schema.get('properties', {}).keys() if prop != 'Entry']
            print(f"Fields: {len(fields)}")
            print(f"Field Names: {', '.join(fields[:10])}{'...' if len(fields) > 10 else ''}")
    
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Connection error occurred. Check your internet connection.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
