# Utility Scripts

This directory contains utility scripts for working with the Bowens Island Private Parties connector.

## get_form_schema.py

This script retrieves the schema for a Cognito Form and saves it to a JSON file. The schema provides a detailed structure of the form, including all fields, their types, validation rules, and other properties.

### Usage

```bash
# Basic usage (uses configuration file for API key and form ID)
python scripts/get_form_schema.py

# Specify API key and form ID directly
python scripts/get_form_schema.py --api-key YOUR_API_KEY --form-id 17

# Save to a specific file
python scripts/get_form_schema.py --output schema/bowens_island_form.json

# Format the JSON for readability
python scripts/get_form_schema.py --pretty
```

### Command-line Options

- `--api-key`: Your Cognito Forms API key. If not provided, it will be read from the configuration file.
- `--form-id`: The ID of the form to get the schema for. Defaults to "17".
- `--output`: Output file path. Defaults to "form_schema.json".
- `--pretty`: Format the JSON output for readability.

### Example Output

The script will save the form schema to a JSON file and print a brief summary:

```
Getting schema for form ID: 17
Schema saved to: form_schema.json
Form Title: Bowens Island Private Party
Fields: 25
Field Names: Name, Email, Phone, EventDate, GuestCount, MenuSelection, BarService, ...
```

### Understanding the Schema

The schema provides detailed information about the form, including:

1. **General Form Properties**: Title, description, etc.
2. **Fields**: Name, type, validation rules, options, etc.
3. **Sections**: Grouping of fields
4. **Conditional Logic**: Rules for showing/hiding fields
5. **Calculation Fields**: Formulas for calculated values

This information is essential for developing features that interact with the form data, such as:

- Creating Excel templates with matching columns
- Validating data before submission
- Building custom interfaces
- Implementing form-specific business logic
