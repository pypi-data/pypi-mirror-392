# d360_getsitenav

Python Fire CLI tool using Playwright to:

- Navigate to https://docs.document360.com/docs/
- Target the navigation panel: `#left-panel > div.catergory-list > site-category-list-tree-view > d360-data-list-tree-view`
- Recursively expand all collapsible sections by clicking triangle icons
- Scroll to reveal all content
- Extract and collect all navigation links
- Process links upward through the hierarchy until complete
- Include links from https://docs.document360.com/s