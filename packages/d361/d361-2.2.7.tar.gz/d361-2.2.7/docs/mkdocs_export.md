# MkDocs Export Documentation

**Document360 → MkDocs Export System**

The d361 MkDocs export system converts Document360 archives or API data to modern MkDocs documentation sites, supporting Material theme, popular plugins, and advanced features.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Templates](#templates)
5. [Content Processing](#content-processing)
6. [Asset Management](#asset-management)
7. [Navigation](#navigation)
8. [Advanced Features](#advanced-features)
9. [API Reference](#api-reference)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

## Overview

The MkDocs export system processes Document360 content through multiple specialized components:

### Core Components

- **MkDocsExporter**: Main orchestrator for the complete export process
- **ConfigGenerator**: Dynamic MkDocs YAML configuration generation with template support
- **NavigationBuilder**: Navigation structure creation from Document360 hierarchy
- **ContentEnhancer**: Content optimization with frontmatter, quality assessment, and SEO
- **AssetManager**: Image processing, CDN optimization, and responsive asset handling
- **CrossReferenceResolver**: Internal link resolution and validation

### Supported Features

- Archive and API Sources: Works with Document360 archives (.zip) and live API
- Modern Themes: Full Material for MkDocs integration with all features
- Popular Plugins: autorefs, section-index, redirects, social cards, minify
- Advanced Markdown: SuperFences, tabbed content, admonitions, math expressions
- Performance: Parallel processing, intelligent caching, optimization
- Quality Control: Content validation, broken link detection, SEO optimization
- Template System: Jinja2 templates for customization

## Quick Start

### Basic Export from Archive

```python
import asyncio
from pathlib import Path
from d361.mkdocs import MkDocsExporter

async def export_documentation():
    # Create exporter instance
    exporter = MkDocsExporter(
        source="archive",
        archive_path=Path("my-docs-archive.zip"),
        output_path=Path("mkdocs_site"),
        theme="material",
        enable_plugins=True
    )
    
    # Run export
    results = await exporter.export()
    
    # Check results
    if results["success"]:
        print(f"Export successful!")
        print(f"Output: {results['output_path']}")
        print(f"Config: {results['config_path']}")
        print(f"Processed {results['statistics']['articles_processed']} articles")
    else:
        print("Export failed")
        for error in results["validation"]["errors"]:
            print(f"Error: {error}")

# Run the export
asyncio.run(export_documentation())
```

### Export from API

```python
from d361.mkdocs import MkDocsExporter

async def export_from_api():
    exporter = MkDocsExporter(
        source="api",
        api_token="your-document360-api-token",
        api_base_url="https://apidocs.document360.com",
        output_path=Path("api_mkdocs_site"),
        theme="material"
    )
    
    results = await exporter.export()
    return results

# For hybrid mode (archive + API)
async def export_hybrid():
    exporter = MkDocsExporter(
        source="hybrid",
        archive_path=Path("base-archive.zip"),
        api_token="your-api-token",
        output_path=Path("hybrid_site"),
        theme="material",
        parallel_processing=True,
        max_workers=6
    )
    
    results = await exporter.export()
    return results
```

### Generated Directory Structure

After export:

```
mkdocs_site/
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── guides/
│   │   ├── index.md
│   │   ├── getting-started.md
│   │   └── advanced-guide.md
│   ├── reference/
│   │   └── api-docs.md
│   └── assets/
│       ├── images/
│       └── stylesheets/
└── site/
```

## Configuration

### MkDocsExporter Options

```python
exporter = MkDocsExporter(
    # Data Source Configuration
    source="archive",                    # "archive", "api", or "hybrid"
    archive_path=Path("archive.zip"),    # Path to Document360 archive
    api_token="your-token",              # Document360 API token
    api_base_url="https://api.url",      # API base URL
    
    # Output Configuration  
    output_path=Path("output"),          # Output directory
    theme="material",                    # MkDocs theme
    enable_plugins=True,                 # Enable popular MkDocs plugins
    
    # Performance Configuration
    parallel_processing=True,            # Enable parallel processing
    max_workers=4,                       # Number of parallel workers
    
    # Advanced Configuration
    config_path=Path("d361.toml")       # Path to d361 configuration file
)
```

### ConfigGenerator Customization

```python
from d361.mkdocs import ConfigGenerator

# Create config generator
generator = ConfigGenerator(
    theme="material",
    enable_plugins=True
)

# Generate configuration programmatically
config_yaml = await generator.generate_config(
    site_name="My Documentation",
    site_url="https://docs.example.com",
    site_description="Comprehensive project documentation",
    repo_url="https://github.com/user/project",
    navigation=[
        {"Home": "index.md"},
        {
            "User Guide": [
                "guide/getting-started.md",
                "guide/advanced.md"
            ]
        },
        {"API Reference": "api/index.md"}
    ]
)

# Generate from template
config_content = await generator.generate_config_from_template(
    template_name="material_theme.yml.j2",
    context={
        "site_name": "Custom Site",
        "primary_color": "teal",
        "accent_color": "orange",
        "enable_social_cards": True,
        "analytics": {
            "provider": "google",
            "property": "G-XXXXXXXXXX"
        }
    }
)

# Validate configuration
validation_results = generator.validate_final_config(config_yaml)
if not validation_results["valid"]:
    print("Configuration errors:")
    for error in validation_results["errors"]:
        print(f"  - {error}")
```

### Theme-Specific Configuration

#### Material Theme

```python
# Material theme configuration
material_context = {
    "site_name": "Material Documentation",
    "site_url": "https://docs.example.com",
    
    # Color scheme
    "color_scheme": "auto",          # "auto", "light", "dark"
    "primary_color": "indigo",       # Material color palette
    "accent_color": "blue",
    
    # Typography
    "text_font": "Roboto",
    "code_font": "Roboto Mono",
    
    # Features
    "enable_tabs": True,
    "enable_instant": True,
    "enable_social_cards": True,
    "enable_feedback": True,
    
    # Search
    "enable_offline_search": True,
    
    # Analytics
    "analytics": {
        "provider": "google",
        "property": "G-XXXXXXXXXX",
        "feedback": {
            "title": "Was this page helpful?",
            "ratings": [
                {"icon": "material/emoticon-happy-outline", "name": "Yes", "data": 1},
                {"icon": "material/emoticon-sad-outline", "name": "No", "data": 0}
            ]
        }
    }
}
```

#### Read the Docs Theme

```python
# RTD theme configuration
rtd_context = {
    "site_name": "RTD Documentation",
    "theme_name": "readthedocs",
    "highlightjs": True,
    "hljs_languages": ["python", "javascript", "yaml", "bash"]
}
```

## Templates

The system includes three main Jinja2 templates:

### 1. Base Template (`mkdocs_base.yml.j2`)

Basic MkDocs configuration:

```yaml
# Example usage
await generator.generate_config_from_template(
    "mkdocs_base.yml.j2",
    {
        "site_name": "Basic Documentation",
        "theme_name": "mkdocs",
        "navigation": [{"Home": "index.md"}],
        "enable_task_lists": True,
        "enable_superfences": True
    }
)
```

### 2. Material Theme Template (`material_theme.yml.j2`)

Comprehensive Material theme configuration:

```yaml
# Full Material theme example
material_config = await generator.generate_config_from_template(
    "material_theme.yml.j2",
    {
        "site_name": "Advanced Material Site",
        "site_url": "https://docs.example.com",
        "primary_color": "deep purple",
        "accent_color": "pink",
        "color_scheme": "auto",
        "enable_social_cards": True,
        "enable_tags": True,
        "enable_feedback": True,
        "social": [
            {"icon": "fontawesome/brands/github", "link": "https://github.com/user/repo"},
            {"icon": "fontawesome/brands/twitter", "link": "https://twitter.com/user"}
        ]
    }
)
```

### 3. Plugin Configuration Template (`plugin_configs.yml.j2`)

Plugin configuration focused:

```yaml
plugin_config = await generator.generate_config_from_template(
    "plugin_configs.yml.j2",
    {
        "site_name": "Plugin-Rich Site",
        "enable_autorefs": True,
        "enable_section_index": True,
        "enable_redirects": True,
        "redirects": {
            "old-page.html": "new-page.md",
            "legacy/": "current/"
        }
    }
)
```

### Custom Templates

Create templates for specialized use cases:

```yaml
# custom_enterprise.yml.j2
site_name: {{ site_name }}
site_url: {{ site_url }}

theme:
  name: material
  custom_dir: {{ custom_dir | default('theme') }}
  features:
    - navigation.instant
    - navigation.tracking
    {% if enable_enterprise_features %}
    - content.action.edit
    - content.feedback.general
    {% endif %}

plugins:
  - search
  {% if enable_enterprise_auth %}
  - auth:
      providers:
        - saml: {{ saml_config | to_yaml }}
        - oauth: {{ oauth_config | to_yaml }}
  {% endif %}
```

## Content Processing

### ContentEnhancer Features

The ContentEnhancer optimizes Document360 content for MkDocs:

```python
from d361.mkdocs.processors import ContentEnhancer

# Create content enhancer
enhancer = ContentEnhancer(
    site_url="https://docs.example.com",
    enable_seo=True,
    validate_links=True,
    add_edit_links=True,
    enable_social_cards=True,
    custom_css_classes={
        "tables": "data-table",
        "blockquotes": "callout"
    }
)

# Enhance article content
enhanced = await enhancer.enhance_article(article)

# Access enhanced components
frontmatter = enhanced["frontmatter"]      # YAML frontmatter
content = enhanced["content"]              # Processed markdown
quality = enhanced["quality_metrics"]     # Quality assessment
nav_hints = enhanced["navigation_hints"]  # Navigation suggestions
```

### Content Transformations

#### 1. Heading Normalization

```markdown
# Input (Document360)
# Main Title
## Section
### Subsection

# Output (MkDocs)
## Main Title {: #main-title }
## Section {: #section }
### Subsection {: #subsection }
```

#### 2. Link Processing

```markdown
# Internal links
[Guide](../docs/user-guide.html) → [Guide](../docs/user-guide.md)

# External links  
[Example](https://example.com) → [Example](https://example.com){: target="_blank" rel="noopener noreferrer" }
```

#### 3. Image Enhancement

```markdown
# Document360 CDN URLs are optimized
![Diagram](https://d360-cdn.com/image.png) → ![Diagram](assets/images/optimized-image.png)

# Responsive images
![Large Image](big-image.jpg) → ![Large Image](big-image.jpg){: .responsive-image loading="lazy" }
```

#### 4. Code Block Enhancement

```markdown
# Language detection and line numbers
```
def example():
    return "hello world"
```

# Becomes:
```python linenums="1"
def example():
    return "hello world"
```

### Quality Assessment

The system provides quality metrics:

```python
quality_metrics = {
    "word_count": 450,
    "heading_count": 5,
    "link_count": 8,
    "image_count": 3,
    "code_block_count": 2,
    "estimated_reading_time": 3,  # minutes
    "overall_score": 85,          # 0-100
    "quality_level": "excellent"  # needs_improvement, fair, good, excellent
}
```

## Asset Management

### AssetManager Configuration

```python
from d361.mkdocs.processors import AssetManager

# Configure asset processing
manager = AssetManager(
    output_dir=Path("docs/assets"),
    enable_optimization=True,
    generate_responsive=True,
    max_image_width=1200,
    image_quality=85,
    convert_to_webp=True,
    enable_lazy_loading=True,
    download_external_assets=True
)

# Process assets in content
processed_content = await manager.process_assets(content, article_id)

# Copy all assets to output directory
assets_copied = await manager.copy_assets(docs_dir)
```

### Supported Asset Types

- Images: PNG, JPG, WebP, GIF, SVG
- Documents: PDF, DOCX, XLSX
- Code: JSON, XML, CSV
- Media: MP4, WebM

### CDN Optimization

```python
# Document360 CDN URLs are automatically optimized
original_url = "https://document360.com/wp-content/uploads/2023/image.png"
optimized_url = manager.optimize_cdn_url(original_url)
# Result: "assets/images/document360-image-optimized.webp"
```

## Navigation

### NavigationBuilder Features

```python
from d361.mkdocs.exporters import NavigationBuilder

builder = NavigationBuilder()

# Build navigation from Document360 structure
navigation = await builder.build_navigation(articles, categories)

# Example output:
[
    {"Home": "index.md"},
    {
        "Getting Started": [
            "guides/index.md",
            "guides/installation.md",
            "guides/quick-start.md"
        ]
    },
    {
        "API Reference": [
            "api/index.md",
            "api/authentication.md",
            "api/endpoints.md"
        ]
    },
    {"FAQ": "help/faq.md"}
]
```

### Hierarchical Categories

The system handles nested categories:

```python
# Document360 categories
parent_category = Category(id="guides", name="User Guides", parent_id=None)
child_category = Category(id="advanced", name="Advanced Topics", parent_id="guides")

# Generates nested navigation:
{
    "User Guides": [
        "guides/index.md",
        "guides/basic-guide.md",
        {
            "Advanced Topics": [
                "guides/advanced/index.md",
                "guides/advanced/expert-tips.md"
            ]
        }
    ]
}
```

## Advanced Features

### Cross-Reference Resolution

```python
from d361.mkdocs.processors import CrossReferenceResolver

resolver = CrossReferenceResolver(
    articles=all_articles,
    categories=all_categories,
    base_url="https://docs.example.com",
    validate_external=True,
    generate_autorefs=True
)

# Resolve references in content
resolved_content = await resolver.resolve_content_references(content, current_article_id)

# Generate link report
link_report = resolver.generate_link_report()
```

### Template Validation

```python
# Comprehensive template validation
validation_results = generator.validate_final_config(config_yaml)

print(f"Valid: {validation_results['valid']}")
print(f"Errors: {len(validation_results['errors'])}")
print(f"Warnings: {len(validation_results['warnings'])}")
print(f"Suggestions: {len(validation_results['suggestions'])}")

for error in validation_results['errors']:
    print(f"{error}")

for warning in validation_results['warnings']:
    print(f"{warning}")

for suggestion in validation_results['suggestions']:
    print(f"{suggestion}")
```

### Performance Optimization

```python
# Enable parallel processing for large archives
exporter = MkDocsExporter(
    source="archive",
    archive_path=large_archive,
    output_path=output_dir,
    parallel_processing=True,
    max_workers=8
)

# Monitor performance
results = await exporter.export()
performance_metrics = results["performance"]

print(f"Total time: {performance_metrics['total_export']}s")
print(f"Content loading: {performance_metrics['content_loading']}s")  
print(f"Content processing: {performance_metrics['content_processing']}s")
```

## API Reference

### MkDocsExporter

#### Constructor

```python
MkDocsExporter(
    source: str = "archive",
    archive_path: Optional[Path] = None,
    api_token: Optional[str] = None,
    api_base_url: Optional[str] = None,
    output_path: Path = Path("mkdocs_output"),
    theme: str = "material",
    enable_plugins: bool = True,
    parallel_processing: bool = True,
    max_workers: int = 4,
    config_path: Optional[Path] = None
)
```

#### Methods

```python
async def export() -> Dict[str, Any]:
    """Execute complete MkDocs export process."""
    
async def _load_content() -> Tuple[List[Article], List[Category]]:
    """Load content from configured data source."""
    
async def _validate_export() -> Dict[str, Any]:
    """Validate the generated MkDocs export."""
```

### ConfigGenerator

#### Constructor

```python
ConfigGenerator(
    theme: str = "material",
    enable_plugins: bool = True,
    template_dir: Optional[Path] = None
)
```

#### Methods

```python
async def generate_config(
    site_name: str,
    navigation: List[Dict[str, Any]],
    output_path: Path,
    **kwargs
) -> str:
    """Generate MkDocs configuration YAML."""

async def generate_config_from_template(
    template_name: str,
    context: Dict[str, Any],
    validate_output: bool = True
) -> str:
    """Generate configuration from Jinja2 template."""

def validate_final_config(config_yaml: str) -> Dict[str, Any]:
    """Validate MkDocs configuration."""
```

### ContentEnhancer

#### Constructor

```python
ContentEnhancer(
    site_url: Optional[str] = None,
    enable_seo: bool = True,
    validate_links: bool = True,
    add_edit_links: bool = True,
    enable_social_cards: bool = False,
    custom_css_classes: Optional[Dict] = None
)
```

#### Methods

```python
async def enhance_article(article: Article) -> Dict[str, Any]:
    """Enhance single article for MkDocs."""
```

## Examples

### Complete Enterprise Setup

```python
import asyncio
from pathlib import Path
from d361.mkdocs import MkDocsExporter, ConfigGenerator

async def enterprise_documentation_setup():
    """Complete enterprise documentation setup example."""
    
    # Step 1: Create custom configuration
    generator = ConfigGenerator(theme="material", enable_plugins=True)
    
    enterprise_context = {
        "site_name": "Enterprise Documentation Portal",
        "site_url": "https://docs.company.com",
        "site_description": "Comprehensive enterprise documentation",
        "repo_url": "https://github.com/company/docs",
        "copyright": "Copyright &copy; 2025 Company Inc.",
        
        "primary_color": "blue grey",
        "accent_color": "deep orange",
        "color_scheme": "auto",
        "logo": "assets/company-logo.svg",
        "favicon": "assets/favicon.ico",
        
        "enable_social_cards": True,
        "enable_feedback": True,
        "enable_tags": True,
        "enable_offline_search": True,
        
        "analytics": {
            "provider": "google",
            "property": "G-COMPANY123",
            "feedback": {
                "title": "How was this page?",
                "ratings": [
                    {"icon": "material/thumb-up", "name": "Helpful", "data": 1},
                    {"icon": "material/thumb-down", "name": "Not helpful", "data": 0}
                ]
            }
        },
        
        "social": [
            {"icon": "fontawesome/brands/github", "link": "https://github.com/company"},
            {"icon": "fontawesome/brands/linkedin", "link": "https://linkedin.com/company/company"},
            {"icon": "fontawesome/solid/envelope", "link": "mailto:docs@company.com"}
        ],
        
        "navigation": [
            {"Home": "index.md"},
            {
                "Getting Started": [
                    "getting-started/index.md",
                    "getting-started/installation.md",
                    "getting-started/authentication.md",
                    "getting-started/first-steps.md"
                ]
            },
            {
                "User Guides": [
                    "guides/index.md",
                    "guides/basic-usage.md",
                    "guides/advanced-features.md",
                    "guides/integrations.md"
                ]
            },
            {
                "API Reference": [
                    "api/index.md",
                    "api/authentication.md",
                    "api/users.md",
                    "api/projects.md",
                    "api/webhooks.md"
                ]
            },
            {
                "Administration": [
                    "admin/index.md",
                    "admin/user-management.md",
                    "admin/system-configuration.md",
                    "admin/monitoring.md"
                ]
            },
            {"Support": "support/index.md"},
            {"Changelog": "changelog.md"}
        ]
    }
    
    # Step 2: Set up exporter with enterprise configuration
    exporter = MkDocsExporter(
        source="hybrid",
        archive_path=Path("enterprise-docs-archive.zip"),
        api_token="your-enterprise-api-token",
        output_path=Path("enterprise_docs_site"),
        theme="material",
        enable_plugins=True,
        parallel_processing=True,
        max_workers=6
    )
    
    # Step 3: Run export
    print("Starting enterprise documentation export...")
    results = await exporter.export()
    
    # Step 4: Generate custom configuration
    if results["success"]:
        print("Basic export completed successfully!")
        
        # Generate enterprise configuration
        enterprise_config = await generator.generate_config_from_template(
            "material_theme.yml.j2",
            enterprise_context
        )
        
        # Save custom configuration
        config_path = Path(results["output_path"]) / "mkdocs-enterprise.yml"
        config_path.write_text(enterprise_config)
        
        print(f"Enterprise configuration saved: {config_path}")
        print(f"Statistics:")
        print(f"   Articles: {results['statistics']['articles_processed']}")
        print(f"   Categories: {results['statistics']['categories_processed']}")
        print(f"   Assets: {results['statistics']['assets_processed']}")
        print(f"   Links resolved: {results['statistics']['links_resolved']}")
        
        # Validation report
        validation = results["validation"]
        if validation["errors"]:
            print("Validation issues found:")
            for error in validation["errors"]:
                print(f"   {error}")
        
        if validation["warnings"]:
            print("Suggestions:")
            for warning in validation["warnings"]:
                print(f"   {warning}")
    
    else:
        print("Export failed!")
        for error in results["validation"]["errors"]:
            print(f"   Error: {error}")
    
    return results

# Run the enterprise setup
if __name__ == "__main__":
    asyncio.run(enterprise_documentation_setup())
```

### Multi-Site Documentation

```python
async def multi_site_documentation():
    """Generate multiple documentation sites from single source."""
    
    base_archive = Path("complete-documentation.zip")
    
    # Site configurations
    sites = {
        "public": {
            "output": "public_docs",
            "theme": "material",
            "name": "Public Documentation",
            "url": "https://docs.example.com"
        },
        "internal": {
            "output": "internal_docs", 
            "theme": "material",
            "name": "Internal Documentation",
            "url": "https://internal-docs.company.com"
        },
        "api": {
            "output": "api_docs",
            "theme": "material", 
            "name": "API Documentation",
            "url": "https://api-docs.example.com"
        }
    }
    
    results = {}
    
    for site_type, config in sites.items():
        print(f"Generating {site_type} documentation...")
        
        exporter = MkDocsExporter(
            source="archive",
            archive_path=base_archive,
            output_path=Path(config["output"]),
            theme=config["theme"]
        )
        
        result = await exporter.export()
        results[site_type] = result
        
        if result["success"]:
            print(f"{site_type.title()} site generated successfully")
        else:
            print(f"{site_type.title()} site generation failed")
    
    return results
```

## Troubleshooting

### Common Issues

#### 1. Template Not Found

```python
# Error: Template 'custom_template.j2' not found
# Solution: Check template path and ensure it exists
generator = ConfigGenerator(template_dir=Path("custom_templates"))
```

#### 2. Invalid Configuration

```python
# Error: YAML syntax error in generated config
# Solution: Validate template context
validation = generator.validate_final_config(config_yaml)
if not validation["valid"]:
    for error in validation["errors"]:
        print(f"Config error: {error}")
```

#### 3. Asset Processing Issues

```python
# Error: Cannot process external assets
# Solution: Enable external asset downloading
manager = AssetManager(
    output_dir=Path("assets"),
    download_external_assets=True
)
```

#### 4. Performance Issues

```python
# Issue: Slow export for large archives
# Solution: Enable parallel processing
exporter = MkDocsExporter(
    parallel_processing=True,
    max_workers=8
)
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailed error information
try:
    results = await exporter.export()
except Exception as e:
    logger.error(f"Export failed: {e}", exc_info=True)
```

### Validation Tools

```python
# Comprehensive validation
def validate_export_results(results):
    """Validate export results comprehensively."""
    
    issues = []
    
    # Check basic success
    if not results.get("success"):
        issues.append("Export marked as failed")
    
    # Check output structure
    output_path = Path(results["output_path"])
    if not output_path.exists():
        issues.append(f"Output directory not found: {output_path}")
    
    # Check configuration
    config_path = Path(results["config_path"])  
    if not config_path.exists():
        issues.append(f"Configuration file not found: {config_path}")
    else:
        try:
            import yaml
            yaml.safe_load(config_path.read_text())
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML configuration: {e}")
    
    # Check docs directory
    docs_dir = output_path / "docs"
    if not docs_dir.exists():
        issues.append("Docs directory not found")
    elif not any(docs_dir.glob("*.md")):
        issues.append("No markdown files found in docs directory")
    
    # Report issues
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("Export validation passed")
        return True
```

---

**Need Help?**

- [API Reference](#api-reference)
- [Report Issues](https://github.com/d361/issues)
- [Community Support](https://discord.gg/d361)
- [Contact Support](mailto:support@d361.com)

This documentation covers the MkDocs export capabilities of d361. For updates and examples, check the official repository.