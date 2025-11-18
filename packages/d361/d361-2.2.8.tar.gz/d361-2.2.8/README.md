# D361: Robust Offline Documentation Generator

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/d361.svg)](https://badge.fury.io/py/d361)
[![Python Versions](https://img.shields.io/pypi/pyversions/d361.svg)](https://pypi.org/project/d361/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with MyPy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Tests Passing](https://github.com/twardoch/d361/actions/workflows/push.yml/badge.svg)](https://github.com/twardoch/d361/actions/workflows/push.yml)

## TL;DR

D361 creates offline versions of Document360 knowledge bases and other sitemap-based documentation sites. It's the foundation of the Document360 unified toolkit, designed for reliability and performance.

**Quick Start:**
```bash
# Install and generate offline docs in one command
pip install d361 && playwright install chromium
d361-offline all --map-url="https://docs.example.com/sitemap-en.xml" --output-dir="offline_docs"

# Or use the standalone binary (no Python required)
curl -L -o d361-offline https://github.com/twardoch/d361/releases/latest/download/d361-offline-ubuntu-latest
chmod +x d361-offline && ./d361-offline all --map-url="https://docs.example.com/sitemap-en.xml"
```

**Key Features:**
- Complete documentation capture
- Multi-strategy sitemap parsing with fallbacks
- Browser automation for dynamic content
- HTML and Markdown output formats
- Concurrent downloads with retry logic
- Preserved navigation structure

---

## What is D361?

D361 is an offline documentation generator that extracts, processes, and organizes content from Document360 and similar sites for offline access.

**Core Purpose:**
Automate downloading of entire documentation sites and converting them into offline formats. Handles dynamic content, virtual scrolling, and complex navigation.

**The D361 Workflow:**

1. Multi-strategy sitemap discovery
2. Navigation structure extraction
3. Concurrent content fetching
4. Multi-format processing
5. Structured organization

**Result:** A complete, self-contained documentation snapshot that works offline.

## Who Uses D361?

**Enterprise Documentation Teams:**
- **Technical Writers** - Archive versions, offline reviews, distribution packages
- **DevOps Engineers** - Integration into deployment pipelines
- **Support Engineers** - Instant access to knowledge bases
- **Compliance Teams** - Immutable snapshots for regulatory requirements

**Development & Integration:**
- **Software Developers** - Bundle documentation with applications
- **System Integrators** - Deploy in air-gapped environments
- **CI/CD Pipelines** - Automated documentation processing
- **Documentation Toolkit Builders** - Foundation component (used in `vexy-help`)

**Specialized Use Cases:**
- **Industrial/Manufacturing** - Factory floor access
- **Healthcare/Government** - Regulated environments
- **Field Service** - Remote locations with limited connectivity
- **Training & Education** - Portable learning packages

## Why Choose D361?

**Technical Excellence:**
- Handles complex documentation sites with dynamic content
- Concurrent processing with intelligent retries
- Multiple fallback strategies for content extraction
- Outputs HTML, Markdown, and combined formats

**Real-World Reliability:**
- Tested on large-scale sites with thousands of pages
- Playwright techniques handle cookie banners and virtual scrolling
- Preserves navigation structure, styling, and cross-references
- Comprehensive error handling for partial success

**Integration-Friendly:**
- Works independently
- Clean programmatic interface
- Docker-friendly with minimal resource requirements
- Cross-platform support for Linux, macOS, and Windows

## Core Features & Capabilities

### Complete Documentation Extraction
D361 captures entire documentation ecosystems:

```python
# Advanced content discovery with multiple fallback strategies
from d361.offline.parser import parse_sitemap

# Strategy 1: Direct sitemap parsing
urls = await parse_sitemap("https://docs.example.com/sitemap-en.xml")

# Strategy 2: Robots.txt discovery + parsing  
urls = await parse_sitemap("https://docs.example.com/robots.txt", strategy="robots")

# Strategy 3: Stealth browser automation for protected sites
urls = await parse_sitemap("https://docs.example.com", strategy="stealth")
```

**What gets captured:**
- All article content (HTML + Markdown)
- Complete navigation hierarchy
- Referenced images and media
- Cross-references and internal links
- Original styling and CSS (optional)

### Multi-Strategy Sitemap Parsing
Robust discovery mechanisms ensure content extraction:

```python
from d361.offline.d361_offline import D361Offline
from d361.offline.config import Config

config = Config(
    map_url="https://docs.example.com/sitemap-en.xml",
    effort=True,  # Enable additional discovery strategies
    max_concurrent=8,  # Concurrent parsing attempts
    retries=3  # Per-strategy retry attempts
)

offline_gen = D361Offline(config)
await offline_gen.prep()  # Intelligent sitemap discovery and parsing
```

**Parsing Strategies:**
1. Direct navigation via HTTP GET
2. Stealth browser automation
3. aiohttp-based lightweight parsing
4. Robots.txt discovery
5. Google cache fallback

### Advanced Browser Automation
Playwright handles modern web complexity:

```python
from d361.offline.browser import setup_browser, expand_all_items

# Configure stealth browser
browser_config = {
    'headless': True,
    'user_agent': 'Mozilla/5.0 (compatible; D361 Documentation Archiver)',
    'viewport': {'width': 1920, 'height': 1080},
    'extra_http_headers': {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    }
}

async with setup_browser(**browser_config) as browser:
    page = await browser.new_page()
    await page.goto("https://docs.example.com")
    
    # Handle dynamic content loading
    navigation_tree = await page.locator('#left-panel d360-data-list-tree-view').first
    await expand_all_items(navigation_tree, page)  # Recursively expand all navigation
    
    # Extract complete navigation structure
    nav_data = await extract_tree_structure(navigation_tree)
```

**Capabilities:**
- Cookie banner dismissal
- Virtual scrolling content loading
- Dynamic tree expansion
- Network idle detection
- Retry logic for failures

### Multi-Format Output Generation
Flexible output formats for different needs:

```python
# Configure output formats
config = Config(
    map_url="https://docs.example.com/sitemap-en.xml",
    output_dir=Path("./offline_docs"),
    css_file=Path("./custom-styling.css"),
    
    # File naming
    all_docs_html_filename="complete_documentation.html",
    all_docs_md_filename="complete_documentation.md",
    
    # Processing options
    test=False,
    verbose=True
)

offline_gen = D361Offline(config)
await offline_gen.all()  # Generate all formats
```

**Generated Output Structure:**
```
offline_docs/docs.example.com/
├── prep.json              # Sitemap discovery metadata
├── fetch.json             # Content extraction results  
├── nav.json               # Navigation structure data
├── nav.html               # Standalone navigation menu
├── nav.md                 # Markdown navigation index
├── all_docs.html          # Complete HTML with embedded navigation
├── all_docs.md            # Complete Markdown with TOC
├── html/                  # Individual HTML pages
│   ├── getting-started.html
│   ├── api-reference.html
│   └── ...
└── md/                    # Individual Markdown pages
    ├── getting-started.md
    ├── api-reference.md
    └── ...
```

### Performance-Optimized Processing
Enterprise-grade performance with intelligent resource management:

```python
from d361.offline.config import Config

# Performance-tuned configuration
config = Config(
    map_url="https://docs.example.com/sitemap-en.xml",
    max_concurrent=12,        # Concurrent page fetching
    timeout=60,              # Per-page timeout (seconds)
    retries=5,               # Retry attempts for failed pages  
    pause=0                  # No artificial delays
)

offline_gen = D361Offline(config)
start_time = time.time()
result = await offline_gen.all()
processing_time = time.time() - start_time

print(f"Processed {len(result['content'])} pages in {processing_time:.2f}s")
```

**Performance Features:**
- Concurrent downloads (default: 5 concurrent)
- Exponential backoff with `tenacity`
- Memory-efficient streaming processing
- Progress tracking and metrics
- Connection pooling for HTTP efficiency

### Installation

D361 can be installed in multiple ways:

#### Quick Installation
```bash
curl -sSL https://raw.githubusercontent.com/twardoch/d361/main/scripts/install.sh | bash
```

#### Manual Installation

**Via pip:**
```bash
pip install d361
playwright install chromium
```

**Via uv:**
```bash
uv pip install d361
playwright install chromium
```

**Binary Download:**
```bash
# Linux
curl -L -o d361-offline https://github.com/twardoch/d361/releases/latest/download/d361-offline-ubuntu-latest
chmod +x d361-offline

# macOS
curl -L -o d361-offline https://github.com/twardoch/d361/releases/latest/download/d361-offline-macos-latest
chmod +x d361-offline

# Windows
curl -L -o d361-offline.exe https://github.com/twardoch/d361/releases/latest/download/d361-offline-windows-latest.exe
```

#### Installation Options

The installation script supports various options:

```bash
# Install specific version
./scripts/install.sh --version 1.0.0

# Install via specific method
./scripts/install.sh --method binary

# Install with Playwright browsers
./scripts/install.sh --install-browsers

# Install to custom directory
./scripts/install.sh --install-dir ~/.local/bin

# See all options
./scripts/install.sh --help
```

### Command Line Usage

The package provides a command-line interface `d361-offline` with several operations: `prep`, `fetch`, `build`, and `all`.

**1. `all` (Recommended):**
Runs the entire process: preparation, fetching, and building.
```bash
d361-offline all --map-url="https://docs.example.com/sitemap-en.xml" --output-dir="my_offline_docs"
```
*   `--map-url`: (Required) Documentation sitemap URL.
*   `--output-dir`: (Optional) Output directory. Defaults to domain-named folder.
*   `--style`: (Optional) Custom CSS file for HTML output.
*   `--nav-url`: (Optional) Page to extract navigation from.

**2. Individual Steps:**

*   **`prep`**: Parses sitemap and extracts navigation.
    ```bash
    d361-offline prep --map-url="https://docs.example.com/sitemap-en.xml" --output-dir="my_docs"
    ```
    Creates `prep.json`.

*   **`fetch`**: Downloads content for all URLs.
    ```bash
    d361-offline fetch --prep-file="my_docs/prep.json" --output-dir="my_docs"
    ```
    Creates `fetch.json` and saves individual pages.

*   **`build`**: Generates combined documentation files.
    ```bash
    d361-offline build --fetch-file="my_docs/fetch.json" --output-dir="my_docs" --style="path/to/custom.css"
    ```

**Getting Help:**
Use `d361-offline <command> --help` for options.
Example: `d361-offline all --help`.

### Programmatic Usage

Use D361 from Python scripts:

```python
import asyncio
from pathlib import Path
from d361.offline.config import Config
from d361.offline.d361_offline import D361Offline

async def generate_my_docs():
    sitemap_url = "https://docs.example.com/sitemap-en.xml"
    if not sitemap_url:
        raise ValueError("map_url must be set")

    config = Config(
        map_url=sitemap_url,
        output_dir=Path("custom_offline_docs"),
        css_file=Path("styles/my_custom_style.css") if Path("styles/my_custom_style.css").exists() else None,
        max_concurrent=5,
        retries=3,
        timeout=60,
        verbose=False,
        test=False
    )

    offline_generator = D361Offline(config)

    try:
        print(f"Starting offline generation for {config.map_url}...")
        print(f"Output will be saved to: {config.output_dir.resolve()}")
        await offline_generator.all()
        print("Offline documentation generated successfully!")
        print(f"Combined HTML: {config.output_dir / config.all_docs_html_filename}")
        print(f"Combined Markdown: {config.output_dir / config.all_docs_md_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run `playwright install` if browsers aren't installed
    asyncio.run(generate_my_docs())
```

### Configuration Options

Behavior controlled by `Config` model (see `src/d361/offline/config.py`):

| Option | CLI Argument | Description | Default |
|--------|-------------|-------------|---------|
| `map_url` | `--map-url` | Sitemap URL | Required |
| `nav_url` | `--nav-url` | Navigation extraction URL | None |
| `output_dir` | `--output-dir` | Base output directory | Current directory |
| `css_file` | `--style` | Custom CSS file | None |
| `effort` | `--effort` | Aggressive sitemap mapping | `False` |
| `max_concurrent` | `--parallel` | Concurrent downloads | 5 |
| `retries` | `--retries` | Retry attempts | 3 |
| `timeout` | `--timeout` | Page load timeout | 60 |
| `verbose` | `--verbose` | Verbose logging | `False` |
| `test` | `--test` | Test mode (5 items) | `False` |
| `pause` | `--wait` | Navigation extraction pause | `False` |

*Note: Output directory behavior - if `map_url` is `https://docs.example.com/...` and `output_dir` is `my_docs`, actual path becomes `my_docs/docs.example.com/`.*

### Output Structure

Generated documentation organized as follows:

```
output_dir/your_domain_com/
├── prep.json          # Preparation data (URLs, navigation)
├── fetch.json         # Fetched content map
├── nav.json           # Navigation structure
├── nav.html           # Navigation menu (HTML)
├── nav.md             # Navigation menu (Markdown)
├── all_docs.html      # Combined HTML documentation
├── all_docs.md        # Combined Markdown documentation
├── html/              # Individual HTML pages
│   ├── page-slug-1.html
│   ├── page-slug-2.html
│   └── ...
└── md/                # Individual Markdown pages
    ├── page-slug-1.md
    ├── page-slug-2.md
    └── ...
```
Custom CSS copied to `html/assets/` and linked in `all_docs.html`.

## Part 2: Technical Deep-Dive

This section describes D361's internal architecture and contribution guidelines.

### How the Code Works

D361 operates in three asynchronous phases: **Prep**, **Fetch**, and **Build**.

**Core Workflow:**

1.  **Prep Phase:**
    *   Parses sitemap to get unique page URLs
    *   Extracts navigation structure
    *   Saves data to `prep.json`
    *   Generates `nav.json`, `nav.html`, and `nav.md`

2.  **Fetch Phase:**
    *   Reads `prep.json`
    *   Fetches content for each URL (title, HTML, Markdown)
    *   Saves individual pages to `html/<slug>.html` and `md/<slug>.md`
    *   Saves all content to `fetch.json`

3.  **Build Phase:**
    *   Reads `fetch.json`
    *   Generates `all_docs.html`: single HTML file with navigation and styling
    *   Generates `all_docs.md`: single Markdown file with table of contents

**Key Components:**

*   **Configuration (`src/d361/offline/config.py`):**
    *   `Config` class manages settings with Pydantic validation
    *   Computes defaults and provides output file paths

*   **Main Orchestrator (`src/d361/offline/d361_offline.py`):**
    *   `D361Offline` class coordinates all operations
    *   Methods: `prep()`, `fetch()`, `build()`, `all()`

*   **Command Line Interface (`src/d361/offline/__main__.py`):**
    *   Exposes `D361Offline` methods via `fire` library
    *   CLI commands: `prep`, `fetch`, `build`, `all`

*   **Sitemap Parsing (`src/d361/offline/parser.py`):**
    *   `parse_sitemap` extracts URLs from sitemap.xml
    *   Multiple strategies for robustness:
        1.  Direct Playwright navigation
        2.  Playwright with stealth techniques
        3.  Direct HTTP GET with `aiohttp`
        4.  Robots.txt discovery
        5.  Google cache fallback
    *   Uses `BeautifulSoup` with `lxml` parser

*   **Navigation Extraction (`src/d361/offline/navigation.py`):**
    *   `extract_navigation` uses Playwright to load navigation page
    *   Complex interaction due to Document360's dynamic UI:
        *   Cookie/consent banner dismissal
        *   Tree expansion via `expand_navigation_tree`
        *   `expand_all_items` scrolls and clicks expand icons recursively
        *   Structure parsing with `extract_tree_structure`
    *   Fallback mechanisms for non-standard selectors

*   **Content Processing (`src/d361/offline/content.py`, `D361Offline.process_url`):**
    *   `process_url` launches Playwright page for each URL
    *   `extract_page_content`:
        *   Navigates to URL
        *   Dismisses cookie banners
        *   Waits for network idle and rendering
        *   Extracts title and content
        *   Converts HTML to Markdown with `markdownify`
    *   Saves content to `html/<slug>.html` and `md/<slug>.md`

*   **Browser Automation (`src/d361/offline/browser.py`):**
    *   `setup_browser`: Configures Playwright with realistic arguments
    *   `scroll_to_bottom`: Handles virtual scrolling
    *   `expand_all_items`: Recursively expands tree nodes

*   **Output Generation (`D361Offline._generate_combined_files`, `src/d361/offline/generator.py`):**
    *   `_generate_combined_files` creates `all_docs.html` and `all_docs.md`
    *   HTML includes navigation and custom/default CSS
    *   Markdown includes table of contents and article content
    *   `generator.py` handles directory creation

*   **Error Handling:**
    *   `tenacity` library provides exponential backoff retries
    *   Individual URL errors don't stop entire batch processing

### Development Environment

Project uses [Hatch](https://hatch.pypa.io/) for dependency management and [uv](https://github.com/astral-sh/uv) for speed.

**Setup:**

1.  **Install Hatch and uv**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv pip install hatch
    ```

2.  **Create/Activate Environment**:
    ```bash
    hatch shell
    ```
    *   Creates isolated virtual environment
    *   Installs dependencies using `uv`

3.  **Install Playwright Browsers**:
    ```bash
    playwright install
    ```

**Running Tasks:**

*   **Run Tests**:
    ```bash
    hatch run test:test-cov    # With coverage
    hatch run test:test        # Without coverage
    ```

*   **Linting and Formatting**:
    ```bash
    hatch run lint:fix         # Format and fix
    hatch run lint:style       # Check style
    hatch run lint:typing      # Type checking
    hatch run lint:all         # All checks
    ```

*   **Pre-commit Hooks**:
    ```bash
    pre-commit install
    ```

### Coding and Contribution Guidelines

Contributions welcome. Follow these guidelines:

1.  **Branching:**
    *   Create branches from `main` (e.g., `feat/add-feature`, `fix/bug-name`)

2.  **Code Quality:**
    *   Format with Ruff: `hatch run lint:fix`
    *   Lint with Ruff: `hatch run lint:style`
    *   Type check with MyPy: `hatch run lint:typing`
    *   Write idiomatic Python with docstrings and comments

3.  **Commit Messages:**
    *   Follow [Conventional Commits](https://www.conventionalcommits.org/)
    *   Examples:
        *   `feat: add support for Confluence sitemap parsing`
        *   `fix: improve resilience of cookie banner dismissal`
        *   `docs: update README with advanced usage examples`
        *   `refactor: simplify content extraction logic`
        *   `test: add unit tests for slug generation`

4.  **Testing:**
    *   Write `pytest` tests for new features
    *   Place tests in `tests/` directory
    *   Check coverage: `hatch run test:test-cov`
    *   Ensure all tests pass locally

5.  **Pull Requests:**
    *   Submit against `main` branch
    *   Provide clear title and description
    *   Explain changes and link issues
    *   Ensure CI checks pass

6.  **Dependencies:**
    *   Minimize new dependencies
    *   Add to `pyproject.toml` under appropriate section

### Releases

D361 follows [Semantic Versioning](https://semver.org/) with multiple distribution formats:

- **PyPI Package**: For `pip` and `uv` installation
- **Binary Releases**: Pre-built executables for all platforms
- **Source Code**: Available on GitHub

Each release includes:
- Source distribution
- Wheel distribution
- Standalone binaries
- Automated testing across Python 3.10-3.12

#### Release Process

Automatic releases triggered by version tags:

```bash
git tag v1.0.0
git push origin v1.0.0
```

CI/CD pipeline:
1. Runs comprehensive tests
2. Builds packages and binaries
3. Publishes to PyPI
4. Creates GitHub release

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed guidelines.

### License

D361 is licensed under the MIT License. See [LICENSE](LICENSE) for details.