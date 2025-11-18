# D361Offline

A tool for generating offline documentation from Document360 sites.

## Features

- Extract URLs from a sitemap
- Extract navigation structure from Document360 pages
- Fetch and process HTML content
- Generate static HTML and Markdown documentation

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Usage

### Command Line Interface

```bash
# Extract sitemap and navigation
d361-offline prep --map-url=https://docs.document360.com/sitemap-en.xml --output-dir=docs

# Download content for all URLs
d361-offline fetch --prep-file=docs/prep.json

# Build HTML and Markdown files
d361-offline build --fetch-file=docs/fetch.json

# Run all steps at once
d361-offline all --map-url=https://docs.document360.com/sitemap-en.xml --output-dir=docs
```

### Python API

```python
import asyncio
from d361_offline import D361Offline
from d361_offline.config import Config

# Configure
config = Config(
    map_url="https://docs.document360.com/sitemap-en.xml",
    output_dir="docs"
)

# Initialize
offline = D361Offline(config)

# Run the process
async def main():
    # Step by step
    await offline.prep()
    await offline.fetch()
    await offline.build()
    
    # Or all at once
    # await offline.all()

# Execute
asyncio.run(main())
```

## Options

| Option | Description |
|--------|-------------|
| `--map-url` | URL of the sitemap.xml file |
| `--nav-url` | Navigation page URL (if different from sitemap URLs) |
| `--output-dir` | Output directory (defaults to domain name) |
| `--css-file` | Custom CSS file path |
| `--effort` | Processing level (1-3, higher = more aggressive) |
| `--max-concurrent` | Maximum concurrent requests |
| `--retries` | Retry attempts for failed requests |
| `--timeout` | Page load timeout in seconds |
| `--verbose` | Enable verbose logging |
| `--test` | Test mode with limited output |
| `--pause` | Delay between requests in seconds |

## Development

Requires Python 3.11+ and Playwright.

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Run tests
pytest

# Format code
ruff check --fix . && ruff format .
```

## License

MIT