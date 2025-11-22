# VLM Paper Search

A comprehensive collection of accepted papers from major computer vision and machine learning conferences (2022-2025).

## Overview

This repository aggregates and formats paper lists from top-tier AI/ML conferences, making it easier to search and browse through thousands of research papers. Each conference's papers are available in both raw text format and formatted markdown for better readability.

## Conferences Included

### Computer Vision
- **ECCV** (European Conference on Computer Vision)
  - 2022, 2024
- **ICCV** (International Conference on Computer Vision)
  - 2023, 2025

### Machine Learning & Artificial Intelligence
- **NeurIPS** (Conference on Neural Information Processing Systems)
  - 2023, 2024, 2025
- **ICLR** (International Conference on Learning Representations)
  - 2023, 2024, 2025
- **AAAI** (Association for the Advancement of Artificial Intelligence)
  - 2023, 2024, 2025
- **IJCAI** (International Joint Conference on Artificial Intelligence)
  - 2023, 2024, 2025

## Repository Structure

```
.
├── AAAI/
│   ├── 2023-aaai-formatted.md
│   ├── 2024-aaai-formatted.md
│   └── 2025-aaai-formatted.md
├── ECCV/
│   ├── 2022-eccv-formatted.md
│   └── 2024-eccv-formatted.md
├── ICCV/
│   ├── 2023-iccv-formatted.md
│   └── 2025-iccv-formatted.md
├── ICLR/
│   ├── 2023-iclr-formatted.md
│   ├── 2024-iclr-formatted.md
│   └── 2025-iclr-formatted.md
├── IJCAI/
│   ├── 2023-ijcai-formatted.md
│   ├── 2024-ijcai-formatted.md
│   └── 2025-ijcai-formatted.md
├── NeurIPS/
│   ├── 2023-neurips-formatted.md
│   ├── 2024-neurips-formatted.md
│   └── 2025-neurips-formatted.md
└── parse_papers.py
```

**Note:** Raw text files (`*-text.txt`) are excluded from the repository via `.gitignore` to keep the repo clean. Only formatted markdown files are committed.

## File Formats

### Raw Text Files (`*-text.txt`) - Not in Repository
Original data extracted from conference websites, containing:
- Paper titles
- Author names
- Affiliations
- Additional metadata (presentation type, ratings, countries, etc.)

**Note:** These files are not committed to the repository (excluded via `.gitignore`). They are used locally to generate the formatted markdown files using `parse_papers.py`.

### Formatted Markdown Files (`*-formatted.md`) - Committed to Repository
Clean, readable markdown format with:
- Numbered paper listings
- Structured metadata fields
- Easy navigation and search

These are the only files committed to the repository for easy browsing and searching.

## Paper Information

Each formatted paper entry includes (when available):
- **Title**: Full paper title
- **Authors**: List of all authors
- **Affiliation**: Author institutions
- **Country**: Geographic locations
- **Presentation Type**: Oral, Poster, Spotlight (for applicable conferences)
- **Rating/Track**: Quality tier or conference track (for applicable conferences)

## Usage

### Browsing Papers
Simply open the formatted markdown files (`.md`) in any text editor or markdown viewer to browse papers from a specific conference and year.

### Searching Papers
Use your text editor's search function or command-line tools:

```bash
# Search for papers about "vision language" in ICLR 2024
grep -i "vision language" ICLR/2024-iclr-formatted.md

# Search across all conferences
grep -r -i "transformer" */\*-formatted.md
```

### Filtering Papers by Topic (NEW!)

The repository includes an intelligent filtering system to help you find relevant papers based on your research interests.

#### Quick Start

1. **Set up your configuration file**:
   ```bash
   # Copy the example configuration file
   cp filter_config.yaml.example filter_config.yaml

   # Edit filter_config.yaml to define your research topics and keywords
   # The example file includes topics like: Graph Neural Networks, Reinforcement Learning, NLP
   ```

2. **Filter papers**:
   ```bash
   # Filter all topics in config
   uv run filter_papers.py

   # Filter specific topic
   uv run filter_papers.py --topic vlm_pruning

   # Filter multiple topics
   uv run filter_papers.py --topics vlm_pruning llm_efficiency
   ```

3. **Review results**:
   - Results are saved in `_filtered/{timestamp}_{topic_name}/`
   - Each run creates a new timestamped folder so you can compare different searches
   - Files generated:
     - `papers.md` - Full paper list organized by conference
     - `reading_checklist.md` - Track your reading progress
     - `metadata.json` - Search criteria and statistics
     - `index.md` - History of all your searches

#### Filter Configuration

The repository includes `filter_config.yaml.example` as a template. Copy it to create your own configuration:

```bash
cp filter_config.yaml.example filter_config.yaml
```

Then customize `filter_config.yaml` for your research interests:

```yaml
topics:
  my_research:
    name: "My Research Topic"
    description: "Papers related to my research"
    keywords:
      - keyword1
      - keyword2
      - model_name
    conferences:
      - ICLR
      - NeurIPS
      - CVPR
    years:
      - 2024
      - 2025
    # Or use null for all available years
```

**Note**: Your personal `filter_config.yaml` is excluded from git (via `.gitignore`) to keep your research interests private. Only the example file is shared in the repository.

#### Output Structure

```
_filtered/
├── 2025-11-22_10-30-15_vlm_pruning/    # Timestamped results
│   ├── papers.md                        # Reading material
│   ├── reading_checklist.md             # Progress tracker
│   └── metadata.json                    # Search metadata
├── 2025-11-22_14-20-05_llm_efficiency/
│   └── ...
└── index.md                             # Search history
```

#### Features

- **Smart keyword matching**: Case-insensitive, matches partial words
- **Automatic prioritization**: Papers ranked by keyword matches and quality ratings
- **Reading checklist**: Track which papers you've read
- **Search history**: Keep track of all your filtering sessions
- **Timestamped results**: Each search creates a unique folder for easy comparison

### Regenerating Formatted Files
If you need to regenerate the formatted markdown files:

```bash
uv run parse_papers.py
```

or

```bash
python parse_papers.py
```

## Statistics

Total papers across all conferences: **15,000+**

## Use Cases

- Research literature review
- Finding papers by topic, author, or institution
- Tracking conference acceptance trends
- Building paper recommendation systems
- Dataset creation for meta-research

## Contributing

To add new conferences or years:
1. Add raw text file (`*-text.txt`) to the appropriate directory (this will remain local only)
2. Update `parse_papers.py` with the appropriate parser function if needed
3. Run the parser to generate formatted markdown files: `uv run parse_papers.py`
4. Commit only the generated `*-formatted.md` files to the repository

The raw text files are excluded from version control to keep the repository clean and focused on the formatted, searchable content.

## License

This repository contains publicly available information from conference websites. Please refer to individual conference policies for paper usage rights.