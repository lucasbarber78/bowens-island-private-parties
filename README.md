# Bowens Island Private Parties

A Python-based connector for syncing Bowens Island Private Party data between Cognito Forms and Excel.

## Overview

This project provides a two-way synchronization between Cognito Forms and Excel for managing Bowens Island Private Party bookings. It allows you to:

- Pull the latest booking data from Cognito Forms into Excel
- Make changes to data via Excel and Power Query
- Push changes back to Cognito Forms

## Features

- **Two-way synchronization**: Keep Cognito Forms and Excel in sync
- **Read-only main data table**: Prevent accidental edits to source data
- **Power Query integration**: Create custom views with Power Query
- **Change detection**: Intelligent tracking of changes
- **Flexible UI options**: Both GUI and command-line interfaces
- **Configurable sync options**: Control when and how synchronization happens

## Requirements

- Python 3.8+
- Excel (with Power Query)
- Cognito Forms API access (Pro, Team, or Enterprise plan)

## Installation

### From GitHub

```bash
# Clone the repository
git clone https://github.com/lucasbarber78/bowens-island-private-parties.git

# Navigate to the project directory
cd bowens-island-private-parties

# Install dependencies
pip install -r requirements.txt
```

### As a Package

```bash
# Install directly from GitHub
pip install git+https://github.com/lucasbarber78/bowens-island-private-parties.git

# Or, after cloning
pip install -e .
```

## Configuration

Before using the connector, you need to configure it with your Cognito Forms API key and form ID:

### Using the GUI

1. Run the application with `python -m src`
2. Go to the Settings tab
3. Enter your Cognito Forms API key and form ID
4. Set the path to your Excel file
5. Configure other settings as needed
6. Click "Save Settings"

### Using the CLI

```bash
# Setup the connector with basic configuration
python -m src --cli --command setup --api-key YOUR_API_KEY --form-id 17 --excel-path path/to/your/excel/file.xlsx
```

## Usage

### GUI Mode

```bash
# Run the application in GUI mode (default)
python -m src
```

The GUI provides:
- Sync operations between Cognito Forms and Excel
- Settings configuration
- Status monitoring

### CLI Mode

```bash
# Synchronize from Cognito Forms to Excel
python -m src --cli --command sync-to-excel

# Synchronize from Excel to Cognito Forms
python -m src --cli --command sync-to-cognito

# Show current status
python -m src --cli --command status

# Show help
python -m src --cli --help
```

## Excel Integration

The connector creates a main data table in Excel with all entries from the Cognito Forms API. This table serves as a read-only source for Power Query views.

### Creating Power Query Views

1. Open the Excel file
2. Go to the Data tab
3. Select "Get Data" > "From Other Sources" > "From Table/Range"
4. Select the main data table
5. Use the Power Query Editor to create your custom view
6. Load the view to a new worksheet

### Making Changes

1. Make changes in the Power Query views
2. Save the Excel file
3. Use the connector to sync changes back to Cognito Forms

## Advanced Usage

### Automatic Synchronization

The connector can automatically synchronize when the Excel file is opened or saved:

1. Enable "Auto-sync when Excel file is opened" in settings
2. Enable "Auto-sync when Excel file is saved" in settings

Note: This requires appropriate Excel VBA integration (future feature).

### Custom Field Mapping

For advanced users, you can modify the field mapping by editing the Cognito Forms schema interpretation in the code:

1. Examine the schema returned by `GET /forms/{formId}/schema`
2. Update the `_extract_fields_from_schema` method in `excel_handler.py`

## Troubleshooting

### Common Issues

- **API Authentication Errors**: Verify your API key is correct and has appropriate permissions
- **Excel File Access Issues**: Ensure Excel is not locking the file during sync
- **Missing Data**: Check if the form schema changed and fields were added/removed

### Logging

The connector logs all activities to the status display in GUI mode, or to the console in CLI mode.

## Development

### Project Structure

```
/
├── src/                  # Source code
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Entry point
│   ├── config.py         # Configuration management
│   ├── cognito_api.py    # Cognito Forms API client
│   ├── excel_handler.py  # Excel file operations
│   ├── sync_manager.py   # Synchronization logic
│   ├── cli.py            # Command-line interface
│   └── gui.py            # Graphical user interface
├── docs/                 # Documentation
├── setup.py              # Package setup
└── requirements.txt      # Dependencies
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License

## Acknowledgements

- [Cognito Forms](https://www.cognitoforms.com/)
- [pandas](https://pandas.pydata.org/)
- [openpyxl](https://openpyxl.readthedocs.io/)
- [xlwings](https://www.xlwings.org/)
