# D361: From Document360 to Offline Documentation

*A story of automated documentation tools, featuring humans, LLMs, and offline access*

---

## Chapter 1: The Beginning (February 27, 2025)

On a cold February evening, Adam Twardoch decided that Document360's online-only format was too limiting. The problem was clear: you're on a plane, the WiFi is unreliable, and you need access to documentation that’s only available online.

```python
# The start of d361.py
class D361:
    """Foundation for offline documentation"""
    def __init__(self):
        self.ambition = "unlimited"
        self.patience_with_online_only_docs = 0
```

The first commit (`a6070ce`) on February 27th was unexpectedly complete – 925 lines across 11 files, with GitHub Actions workflows and a proper Python package structure. This wasn’t just a prototype; it had real intent behind it.

Key features from the start:
- **GitHub Workflows**: Automated CI/CD setup.
- **Python Packaging**: `pyproject.toml` with standard configurations.
- **Pre-commit Hooks**: Basic code formatting and linting checks.

The structure showed early planning for enterprise-grade documentation processing.

---

## Chapter 2: Major Improvements (February 28, 2025)

One day later, commit `3051861` added **61,739 lines of code**. It wasn’t an incremental update – it was a major overhaul focused on navigation extraction, content processing, and file generation.

```python
# Simple sitemap parsing...
urls = await parse_sitemap("https://docs.example.com/sitemap-en.xml")

# Became full browser automation:
async with setup_browser(headless=False) as browser:
    page = await browser.new_page()
    await expand_all_items(navigation_tree, page)
    nav_data = await extract_tree_structure(navigation_tree)
```

This update introduced the **Three-Phase Approach**:

1. **PREP**: Parse sitemaps to find documentation structure.
2. **FETCH**: Download content using browser automation.
3. **BUILD**: Generate unified offline documentation.

### Browser Automation

The standout feature was Playwright-powered navigation extraction. This wasn’t basic web scraping – it handled modern web complexities like cookie banners, virtual scrolling, and dynamic content loading.

```python
async def expand_all_items(tree_element, page):
    """Expand navigation nodes in Document360 UI"""
    
    # Scroll to load dynamically rendered items
    await scroll_to_bottom(tree_element, page)
    
    # Click expand buttons with fallback strategies
```

---

## Chapter 3: System Updates (June-July 2025)

### Documentation Overhaul (June 29, 2025)

On June 29th, a bot (`google-labs-jules[bot]`) updated the README.md. The result was a detailed 692-line document with:

- Working usage examples
- Clear architecture descriptions
- Performance benchmarks
- Troubleshooting steps

> "D361 is a **robust offline documentation generator** and part of the Document360 unified toolkit."

### Build System Upgrade (July 17, 2025)

Commits `e68ad95` and `a52edd6` introduced enterprise-grade tooling:

```yaml
# Multi-platform testing
strategy:
  matrix:
    python: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

New features:
- **PyInstaller support** for standalone binaries
- **Semantic versioning** via git tags
- **Cross-platform releases**
- **Reliable installation scripts**

---

## Chapter 4: Plugin System Development (March-August 2025)

### Code Structure

By March 2025, D361 had evolved beyond a simple offline generator. The project adopted a **hexagonal architecture**:

```
d361/
├── api/              # Document360 API integration
├── archive/          # Archive processing
├── scraping/         # Content extraction
├── providers/        # Data source abstraction
├── config/          # Configuration management
├── core/            # Core logic
└── offline/         # Offline documentation generation
```

### MkDocs Integration Plan

The `PLAN.md` outlined a vision: transform D361 into a **Document360 → MkDocs conversion toolkit**.

Planned enhancements over 10 weeks:
- Material theme support
- Plugin architecture
- Template system
- Performance improvements

### Human-AI Collaboration

Development followed a clear pattern:

**Humans handled**: Vision, architecture, real-world requirements  
**AI assisted with**: Implementation, documentation, code organization  

Example commit messages:
```bash
# Human
"Enhance navigation extraction, content processing, and file generation"

# AI-assisted
"feat(build): add build system, testing, and release automation"
```

---

## Chapter 5: Technical Features

### Sitemap Parsing Strategies

D361 uses a **five-strategy approach** for parsing sitemaps:

1. **Direct Navigation**
2. **Stealth Browser**
3. **HTTP Direct**
4. **Robots.txt Discovery**
5. **Google Cache**

```python
urls = await parse_sitemap(
    "https://docs.example.com/sitemap-en.xml",
    strategy="stealth"
)
```

### Performance Configuration

The system is designed for speed and reliability:

```python
config = Config(
    max_concurrent=12,  # Parallel processing
    timeout=60,        # Per-page limit
    retries=5,         # Retry failed requests
    pause=0            # No artificial delays
)
```

### Content Extraction Pipeline

The pipeline handles modern web challenges:

```python
async def extract_page_content(page, url):
    """Extract page content and convert to Markdown"""
    
    await dismiss_cookie_banners(page)
    await page.wait_for_load_state("networkidle")
    
    title = await extract_title(page)
    content = await extract_article_content(page)
    markdown = markdownify(content)
    
    return {"title": title, "content": content, "markdown": markdown}
```

---

## Chapter 6: Current Status and Future Goals

### As of Version 2.2.3

D361 now includes:
- 25+ Python modules in a clean architecture
- Multi-format output (HTML, Markdown, combined)
- Browser automation for complex UIs
- Plugin-ready design
- Automated tests for reliability

### MkDocs Transformation Plan

The `TODO.md` lists 75 items for improving Document360 → MkDocs conversion:

```markdown
## Success Criteria

- [ ] Export 1000+ pages in <5 minutes
- [ ] >95% link resolution accuracy
- [ ] >90% test coverage
```

These are measurable engineering goals, not vague ideas.

---

## Epilogue: Human-AI Software Development

### What D361 Shows Us

1. **Architecture First**: Clean structure from the start.
2. **Documentation Matters**: README and guides are part of the process.
3. **AI as Assistant**: Automates repetitive tasks; humans guide direction.
4. **Performance Built-In**: Designed for speed, not patched later.
5. **Real-World Focus**: Handles browser quirks and network issues.

### Human Decisions

Despite AI help, the core design choices were human:

- Three-phase processing workflow
- Fallback strategies for failures
- Flexible configuration options
- Plugin system for future growth

### Next Steps

D361 is moving toward becoming a **complete documentation ecosystem**.

Goal: **Convert any Document360 site into a fast, offline-capable documentation site with minimal effort.**

With its track record, that goal is likely within reach.

---

*The development of D361 continues with each commit, test, and user. It’s software built to solve real problems, combining human planning with AI assistance to make documentation more accessible.*

**Current Version**: `v2.2.3`  
**Next Milestone**: MkDocs support  
**Goal**: Reliable offline documentation for everyone