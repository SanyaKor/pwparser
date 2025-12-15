# Amazon Search Parser (Playwright)

This project was created as a **test assignment** for the company **Dresden Medicine Consulting GmbH**.

It demonstrates a basic approach to collecting Amazon search results using
**Python** and **Playwright**, and is intended solely for **evaluation and review purposes**.

---

## Overview

The goal of this test assignment is to:
- demonstrate familiarity with Python
- show basic web automation and parsing skills
- implement pagination handling
- structure data collection and export results in JSON format
- apply logging and configuration best practices

---

## Features

- Search Amazon by query
- Collect items from multiple result pages
- Skip sponsored items
- Extract product:
  - title
  - price (if available)
  - ... any other things if needed?
- Export collected data to JSON
- Configurable logging via environment variables
- Simple CLI interface
- CI for build

---

## Requirements

- Python **3.10+**
- Playwright
- python-dotenv

---

## Installation

```bash
pip install -r requirements.txt
playwright install
```

## Usage

### Command-Line Arguments

The script supports the following command-line options:

| Argument | Description | Default                  |
|--------|-------------|--------------------------|
| `--website` | Target website URL | `https://www.amazon.com` |
| `--query` | Search query | 'harry potter buch'      |
| `--n` | Number of items to collect (1–100) | `50`                     |
| `--out` | Output JSON file name | `collected_items.json`   |
| `--silent` | Run browser in headless (silent) mode | `True`                   |

---

### Examples


```bash
python main.py --query "harry potter book"
```

## Output Example

```bash
[
  {
    "title": "Harry Potter and the Philosopher's Stone",
    "price": "$19.99999999",
    ...
  },
  ...
]
```

## Logging Configuration

The logging level can be controlled via an environment variable.

Set the desired log level before running the script:

```bash
export LOG_LEVEL=DEBUG
python main.py --query "harry potter book"
```
