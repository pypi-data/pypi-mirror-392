# Test Fixtures

This directory contains test data migrated from legacy Document360 implementations during Phase 9 consolidation (2025-08-08).

## Directory Structure

### `vexy-lines-archive/`
Full Document360 archive from Vexy Lines documentation:
- **`Vexy-Lines-2025-Mar-12-04-42-07.zip`**: Production archive with 1000+ files
- Use for integration testing, archive parsing, and performance benchmarking

### `markdown_samples/`
Markdown articles from the Vexy Lines archive:
- **`about-this-guide.md`**: Introduction/guide article
- **`adding-a-fill.md`**: How-to tutorial  
- **`actions-6.md`**: Feature documentation
- Use for markdown parsing and content conversion testing

## Data Directory

### `../data/`
- **`v1_categories_articles.json`**: 532KB JSON metadata from Vexy Lines export
- Includes categories hierarchy and article metadata
- Use for performance testing and parser benchmarking

## Schemas Directory

### `../schemas/`
- **`d361.schema.json`**: JSON schema for d361 configuration
- Use for configuration validation

## Templates Directory

### `../templates/`
Configuration templates from legacy implementations:
- **`d361.toml.example`**: Project configuration template
- **`d361api.toml.example`**: API client configuration
- Use for setup documentation

## Usage Notes

This test data includes:
- **Production content** from FontLab's Vexy Lines documentation
- **Complete Document360 structure** with metadata
- **Multiple content types**: guides, tutorials, API docs, feature docs
- **Large-scale dataset** for performance testing

## Migration Source

Migrated from:
- `external/int_folders/d362c/example/` (archive and samples)
- `external/int_folders/d362c/` (configuration templates)

Moved during Phase 9 consolidation to preserve test data before cleanup.