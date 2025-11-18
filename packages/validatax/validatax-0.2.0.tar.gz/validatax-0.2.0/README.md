# validata

`validata` is a lightweight data-quality toolkit for validating tabular data stored in CSV and Excel files.
It provides a set of focused, practical checks commonly required in data engineering, reporting, and ETL pipelines.

The library is designed to be simple, predictable, and easy to integrate into existing workflows.

## Features

* Compare column structures between files

* Validate required columns

* Check missing values for key fields

* Detect new distinct values between file versions

* Validate that a date column belongs to a specific month

* Extract the list of months present in a dataset

* Produce value counts for a column

* Clear all rows while preserving file structure

* All functions operate on CSV, XLSX, and XLS formats.

## Installation

```bash
pip install validata

