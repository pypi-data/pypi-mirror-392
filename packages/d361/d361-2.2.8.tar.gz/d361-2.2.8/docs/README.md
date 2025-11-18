# Markdown Summarizer

A tool that splits Markdown files at H2 headings and summarizes each section using an LLM.

## 1. Features

- Splits Markdown documents at H2 headings  
- Summarizes each section with an LLM  
- Preserves key information and technical details  
- Outputs a new Markdown file containing the summaries  
- Supports multiple LLM providers with automatic fallback  
- Tracks progress via console output  
- Saves intermediate results to resume processing if interrupted  

## 2. Usage

The tool is broken into three commands for flexible workflows:

### 2.1. Load Command

Splits a Markdown file into sections (at H2 headings) and saves them to a JSON file:

```bash
# Basic usage
python summarize.py load input.md

# Specify output JSON file
python summarize.py load input.md --output_file=sections.json

# Enable verbose output
python summarize.py load input.md --verbose
```

### 2.2. Process Command

Processes the JSON file, generating summaries for each section and saving progress after each:

```bash
# Basic usage
python summarize.py process sections.json

# Use a specific LLM model
python summarize.py process sections.json --model=gpt-4o-mini

# Enable verbose output
python summarize.py process sections.json --verbose
```

### 2.3. Save Command

Converts the processed JSON back into a summarized Markdown file:

```bash
# Basic usage
python summarize.py save sections.json

# Specify output Markdown file
python summarize.py save sections.json --output_file=summary.md

# Enable verbose output
python summarize.py save sections.json --verbose
```

### 2.4. All-in-One Command

Runs all steps in sequence:

```bash
# Basic usage
python summarize.py all input.md

# Specify output file and model
python summarize.py all input.md --output_file=summary.md --model=gpt-4o-mini

# Enable verbose output
python summarize.py all input.md --verbose
```

### 2.5. Using with uv

Thanks to a built-in shebang line, you can also run the script directly with `uv`:

```bash
uv run summarize.py load input.md
```

## 3. Workflow Benefits

Splitting the process into steps helps with:

1. **Resumable runs**: If something crashes, pick up where you left off  
2. **Selective edits**: Manually clear individual summaries in the JSON to reprocess only those  
3. **Progress tracking**: JSON acts as a checkpoint during long jobs  
4. **Output control**: Tweak the JSON before generating the final Markdown  

## 4. LLM Support

Uses the `llm` library to connect to various providers. Tries these models in order:

1. `gpt-4o-mini` (OpenAI)  
2. `openrouter/google/gemini-flash-1.5`  
3. `openrouter/openai/gpt-4o-mini`  
4. `haiku` (Claude 3 Haiku)  

Override the default with the `--model` flag.

## 5. Requirements

- Python 3.9+  
- Dependencies: fire, rich, llm, tenacity, pathos  

## 6. Example

Input:

```markdown
# My Document

## 7. Introduction
This is an introduction to my document.

## 8. Section 1
This is the first section with important details.

## 9. Section 2
This is the second section with more information.
```

Output:

```markdown
# My Document

## 7. Introduction
Summary of the introduction...

## 8. Section 1
Summary of section 1...

## 