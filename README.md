# Inventory Data Validation

This repository contains scripts and tools for validating inventory data. The goal is to ensure that the data is accurate, consistent, and complete before it is used in any downstream processes.

## Features

- **Data Integrity Checks**: Verify that the data meets predefined integrity constraints.
- **Consistency Checks**: Ensure that the data is consistent across different datasets.
- **Completeness Checks**: Confirm that all required data fields are populated.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (listed in `requirements.txt`)


### Usage

1. Place your asset_data and puppet_data in the same directory as this repository (TODO: implement specifying path in command line)
2. Run the validation script:
    ```sh
    python3 validate_inventory.py
    ```
3. Check the output for any validation errors.

### TODO:
 - puppet_data_formatter does not read el7 nodefiles
 - how are we going to present the data?