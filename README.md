# Inventory Data Validation

This repository contains scripts and tools for validating inventory, cobbler, and puppet data. The goal is to ensure that the data is accurate, consistent, and complete before it is used in any downstream processes.

## Features

- **Data Integrity Checks**: Verify that the data meets predefined integrity constraints.
- **Completeness Checks**: Confirm that all required data fields are populated.
- **Consistency Checks**: Ensure that the data is consistent across different datasets.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (listed in `requirements.txt`)


### Usage

1. Place your asset_data and puppet_data in the same directory as this repository (TODO: implement specifying path in command line)
2. Run the validation script:
    ```sh
    python3 main.py
    ```
3. Check the output for any cross-validation errors.

The main script compares data from all three sources.  Each of the individual (asset, cobbler, puppet) runs different checks for validity and completeness on its own source.
