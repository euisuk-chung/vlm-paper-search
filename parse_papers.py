import re
import os

def parse_eccv_2024(input_file, output_file):
    """Parse ECCV 2024 format"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    papers = []

    # Split by lines and process
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Format 1: Look for lines with paper number and title (has quotes)
        # Format: "number\tTitle"
        match = re.search(r'\t"([^"]+)"$', line)
        if match:
            title = match.group(1)

            # Next line should have authors and presentation info
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Parse authors and presentation type (tab separated)
                parts = next_line.split('\t')
                if len(parts) >= 2:
                    authors = parts[0].strip()
                    presentation = parts[1].strip() if len(parts) > 1 else ''

                    papers.append({
                        'title': title,
                        'authors': authors,
                        'presentation': presentation
                    })
                i += 1  # Skip the author line
        else:
            # Format 2: Look for lines that start with number\tTitle (no quotes)
            # Check if line has a title and next line has authors
            match2 = re.match(r'^\d+\t(.+)$', line)
            if match2:
                title = match2.group(1).strip()

                # Next line should have authors and presentation info
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Check if next line contains author info (has semicolons or tabs but not starting with number\t)
                    if not re.match(r'^\d+\t', next_line) and next_line.strip():
                        parts = next_line.split('\t')
                        if len(parts) >= 2:
                            authors = parts[0].strip()
                            presentation = parts[1].strip() if len(parts) > 1 else ''

                            papers.append({
                                'title': title,
                                'authors': authors,
                                'presentation': presentation
                            })
                        i += 1  # Skip the author line
        i += 1

    # Write formatted output
    with open(output_file, 'w', encoding='utf-8') as f:
        year = '2024' if '2024' in input_file else '2022'
        f.write(f"# ECCV {year} Accepted Papers ({len(papers)} papers)\n\n")
        for idx, paper in enumerate(papers, 1):
            f.write(f"## {idx}. {paper['title']}\n")
            f.write(f"**Authors:** {paper['authors']}\n")
            if paper['presentation']:
                f.write(f"**Presentation:** {paper['presentation']}\n")
            f.write("\n")

def parse_eccv_2022(input_file, output_file):
    """Parse ECCV 2022 format (similar to 2024)"""
    parse_eccv_2024(input_file, output_file)

def parse_iccv_2023(input_file, output_file):
    """Parse ICCV 2023 format"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    papers = []
    lines = content.split('\n')
    i = 2  # Skip header

    while i < len(lines):
        line = lines[i]

        # Look for lines that start with a number and tab (paper entry)
        match = re.match(r'^(\d+)\t(.+)$', line)
        if match:
            paper_num = match.group(1)
            title = match.group(2).strip()

            # Move to next line
            i += 1

            # Skip short identifier lines (like "HCL", "Github", "SAGA", "3Dsketch2shape" etc.)
            while i < len(lines):
                next_line = lines[i]

                # Check if it's an identifier line (short text without tabs or semicolons)
                # These lines don't start with a number
                if not re.match(r'^\d+\t', next_line) and next_line.strip():
                    # Check if it's a category line (contains "3D from" or similar patterns)
                    if '3D from' in next_line or 'shape-from-x' in next_line:
                        # This is a category, skip it
                        i += 1
                        if i < len(lines):
                            next_line = lines[i]
                        else:
                            break
                    # Check if it's a short identifier (< 100 chars, no tabs, no semicolons)
                    elif len(next_line.strip()) < 100 and '\t' not in next_line and ';' not in next_line:
                        # This is an identifier like "HCL", "Github", etc., skip it
                        i += 1
                        if i < len(lines):
                            next_line = lines[i]
                        else:
                            break
                    else:
                        # This might be the author line
                        break
                else:
                    # This is the next paper entry
                    break

            # Now parse the author/details line if it exists
            if i < len(lines) and not re.match(r'^\d+\t', lines[i]):
                details = lines[i].strip()

                if details:  # Make sure it's not empty
                    # First split by tab to separate authors from other info
                    tab_parts = details.split('\t')

                    # Authors are in the first part, separated by semicolons
                    authors_part = tab_parts[0] if len(tab_parts) > 0 else ''
                    authors = authors_part  # Keep all authors together

                    # Affiliation is usually in the second tab-separated part
                    affiliation = tab_parts[1].strip() if len(tab_parts) > 1 and tab_parts[1].strip() else ''

                    # Find presentation type (Poster or Oral) in the remaining parts
                    presentation = 'Poster'
                    for part in tab_parts:
                        if 'Poster' in part or 'Oral' in part:
                            presentation = part.strip()
                            break

                    papers.append({
                        'title': title,
                        'authors': authors,
                        'affiliation': affiliation,
                        'presentation': presentation
                    })
                    i += 1  # Move past the author line
            else:
                # No author line found, just add with title
                papers.append({
                    'title': title,
                    'authors': '',
                    'affiliation': '',
                    'presentation': 'Poster'
                })
        else:
            i += 1

    # Write formatted output
    with open(output_file, 'w', encoding='utf-8') as f:
        year = '2023' if '2023' in input_file else '2025'
        f.write(f"# ICCV {year} Accepted Papers ({len(papers)} papers)\n\n")
        for idx, paper in enumerate(papers, 1):
            f.write(f"## {idx}. {paper['title']}\n")
            if paper['authors']:
                f.write(f"**Authors:** {paper['authors']}\n")
            if paper.get('affiliation'):
                f.write(f"**Affiliation:** {paper['affiliation']}\n")
            if paper.get('presentation'):
                f.write(f"**Presentation:** {paper['presentation']}\n")
            f.write("\n")

def parse_iccv_2025(input_file, output_file):
    """Parse ICCV 2025 format (similar to 2023)"""
    parse_iccv_2023(input_file, output_file)

def parse_aaai(input_file, output_file):
    """Parse AAAI format"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    papers = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for lines that start with a number and tab (paper entry)
        match = re.match(r'^(\d+)\t(.+)$', line)
        if match:
            paper_num = match.group(1)
            title = match.group(2).strip()

            # Move to next line
            i += 1

            # Skip short identifier lines (like "Github", project names, etc.)
            while i < len(lines):
                next_line = lines[i]

                # Check if it's an identifier line (short text without tabs)
                if not re.match(r'^\d+\t', next_line) and next_line.strip():
                    # Check if it contains tabs (likely the details line)
                    if '\t' in next_line:
                        # This is the details line
                        break
                    else:
                        # This is a short identifier, skip it
                        i += 1
                        if i < len(lines):
                            next_line = lines[i]
                        else:
                            break
                else:
                    # This is the next paper entry
                    break

            # Now parse the details line if it exists
            if i < len(lines) and not re.match(r'^\d+\t', lines[i]):
                details = lines[i].strip()

                if details:  # Make sure it's not empty
                    # Split by tab
                    tab_parts = details.split('\t')

                    # Parse different parts
                    # Format: track \t authors \t affiliation \t country \t type \t number
                    track = tab_parts[0] if len(tab_parts) > 0 else ''
                    authors = tab_parts[1] if len(tab_parts) > 1 else ''
                    affiliation = tab_parts[2] if len(tab_parts) > 2 else ''
                    country = tab_parts[3] if len(tab_parts) > 3 else ''
                    paper_type = tab_parts[4] if len(tab_parts) > 4 else ''

                    papers.append({
                        'title': title,
                        'track': track,
                        'authors': authors,
                        'affiliation': affiliation,
                        'country': country,
                        'type': paper_type
                    })
                    i += 1  # Move past the details line
            else:
                # No details line found, just add with title
                papers.append({
                    'title': title,
                    'track': '',
                    'authors': '',
                    'affiliation': '',
                    'country': '',
                    'type': 'Technical'
                })
        else:
            i += 1

    # Write formatted output
    with open(output_file, 'w', encoding='utf-8') as f:
        year = '2023' if '2023' in input_file else ('2024' if '2024' in input_file else '2025')
        f.write(f"# AAAI {year} Accepted Papers ({len(papers)} papers)\n\n")
        for idx, paper in enumerate(papers, 1):
            f.write(f"## {idx}. {paper['title']}\n")
            if paper.get('track'):
                f.write(f"**Track:** {paper['track']}\n")
            if paper['authors']:
                f.write(f"**Authors:** {paper['authors']}\n")
            if paper.get('affiliation'):
                f.write(f"**Affiliation:** {paper['affiliation']}\n")
            if paper.get('country'):
                f.write(f"**Country:** {paper['country']}\n")
            if paper.get('type'):
                f.write(f"**Type:** {paper['type']}\n")
            f.write("\n")

def parse_neurips(input_file, output_file):
    """Parse NeurIPS format (similar to ICCV but with OR identifier)"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    papers = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for lines that start with a number and tab (paper entry)
        match = re.match(r'^(\d+)\t(.+)$', line)
        if match:
            paper_num = match.group(1)
            title = match.group(2).strip()

            # Move to next line
            i += 1

            # Skip short identifier lines (like "OR")
            while i < len(lines):
                next_line = lines[i]

                # Check if it's an identifier line (short text without tabs or semicolons)
                if not re.match(r'^\d+\t', next_line) and next_line.strip():
                    # Check if it's a short identifier (< 10 chars, no tabs, no semicolons)
                    if len(next_line.strip()) < 10 and '\t' not in next_line and ';' not in next_line:
                        # This is an identifier like "OR", skip it
                        i += 1
                        if i < len(lines):
                            next_line = lines[i]
                        else:
                            break
                    else:
                        # This might be the author line
                        break
                else:
                    # This is the next paper entry
                    break

            # Now parse the author/details line if it exists
            if i < len(lines) and not re.match(r'^\d+\t', lines[i]):
                details = lines[i].strip()

                if details:  # Make sure it's not empty
                    # First split by tab to separate authors from other info
                    tab_parts = details.split('\t')

                    # Authors are in the first part, separated by semicolons
                    authors_part = tab_parts[0] if len(tab_parts) > 0 else ''
                    authors = authors_part  # Keep all authors together

                    # Affiliation is usually in the second tab-separated part
                    affiliation = tab_parts[1].strip() if len(tab_parts) > 1 and tab_parts[1].strip() else ''

                    # Find presentation type (Oral, Spotlight, Poster) in the remaining parts
                    presentation = 'Poster'
                    for part in tab_parts:
                        if 'Oral' in part or 'Spotlight' in part or 'Poster' in part:
                            presentation = part.strip()
                            break

                    papers.append({
                        'title': title,
                        'authors': authors,
                        'affiliation': affiliation,
                        'presentation': presentation
                    })
                    i += 1  # Move past the author line
            else:
                # No author line found, just add with title
                papers.append({
                    'title': title,
                    'authors': '',
                    'affiliation': '',
                    'presentation': 'Poster'
                })
        else:
            i += 1

    # Write formatted output
    with open(output_file, 'w', encoding='utf-8') as f:
        year = '2023' if '2023' in input_file else ('2024' if '2024' in input_file else '2025')
        f.write(f"# NeurIPS {year} Accepted Papers ({len(papers)} papers)\n\n")
        for idx, paper in enumerate(papers, 1):
            f.write(f"## {idx}. {paper['title']}\n")
            if paper['authors']:
                f.write(f"**Authors:** {paper['authors']}\n")
            if paper.get('affiliation'):
                f.write(f"**Affiliation:** {paper['affiliation']}\n")
            if paper.get('presentation'):
                f.write(f"**Presentation:** {paper['presentation']}\n")
            f.write("\n")

def parse_ijcai(input_file, output_file):
    """Parse IJCAI format"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    papers = []
    lines = content.split('\n')

    # Skip header lines until we reach "Content" or "Main Track"
    i = 0
    while i < len(lines):
        if 'Content' in lines[i] or 'Main Track' in lines[i]:
            i += 1
            break
        i += 1

    current_track = ''

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Check if this is a track/section header (single line, not followed by authors)
        # Track headers are lines that don't have authors on the next line
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            # If next line is empty or looks like another section, this is likely a track header
            # Track headers typically don't have comma-separated names
            if not next_line or (next_line and not any(char in next_line for char in [',', ';'])):
                # Check if current line might be a track header
                # Track headers are usually short and don't contain author-like patterns
                if len(line.split()) < 15 and ',' not in line:
                    # This might be a track header, but let's verify
                    # by checking if it's not an author line (no comma pattern)
                    potential_track = line

                    # Look ahead to see if there's a title-author pattern following
                    if i + 2 < len(lines) and lines[i + 2].strip():
                        # If line after next has commas, current line is likely a track
                        if ',' in lines[i + 2].strip():
                            current_track = potential_track
                            i += 1
                            continue

        # Check if this line is a title (followed by authors on next line)
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            # If next line has commas or semicolons, it's likely authors
            if next_line and (',' in next_line or ';' in next_line):
                title = line
                authors = next_line

                papers.append({
                    'title': title,
                    'authors': authors,
                    'track': current_track
                })

                i += 2  # Skip title and authors
                continue

        i += 1

    # Write formatted output
    with open(output_file, 'w', encoding='utf-8') as f:
        year = '2023' if '2023' in input_file else ('2024' if '2024' in input_file else '2025')
        f.write(f"# IJCAI {year} Accepted Papers ({len(papers)} papers)\n\n")

        current_track_output = ''
        for idx, paper in enumerate(papers, 1):
            # Add track header if it changed
            if paper['track'] and paper['track'] != current_track_output:
                f.write(f"### {paper['track']}\n\n")
                current_track_output = paper['track']

            f.write(f"## {idx}. {paper['title']}\n")
            if paper['authors']:
                f.write(f"**Authors:** {paper['authors']}\n")
            if paper.get('track') and paper['track'] != current_track_output:
                f.write(f"**Track:** {paper['track']}\n")
            f.write("\n")

def parse_iclr(input_file, output_file):
    """Parse ICLR format (similar to NeurIPS but with different metadata)"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    papers = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for lines that start with a number and tab (paper entry)
        match = re.match(r'^(\d+)\t(.+)$', line)
        if match:
            paper_num = match.group(1)
            title = match.group(2).strip()

            # Move to next line
            i += 1

            # Skip short identifier lines (like "OR")
            while i < len(lines):
                next_line = lines[i]

                # Check if it's an identifier line (short text without tabs or semicolons)
                if not re.match(r'^\d+\t', next_line) and next_line.strip():
                    # Check if it's a short identifier (< 10 chars, no tabs, no semicolons)
                    if len(next_line.strip()) < 10 and '\t' not in next_line and ';' not in next_line:
                        # This is an identifier like "OR", skip it
                        i += 1
                        if i < len(lines):
                            next_line = lines[i]
                        else:
                            break
                    else:
                        # This might be the details line
                        break
                else:
                    # This is the next paper entry
                    break

            # Now parse the details line if it exists
            if i < len(lines) and not re.match(r'^\d+\t', lines[i]):
                details = lines[i].strip()

                if details:  # Make sure it's not empty
                    # Split by tab
                    tab_parts = details.split('\t')

                    # Format: authors \t affiliation \t country \t rating/tier \t number
                    authors = tab_parts[0] if len(tab_parts) > 0 else ''
                    affiliation = tab_parts[1] if len(tab_parts) > 1 else ''
                    country = tab_parts[2] if len(tab_parts) > 2 else ''
                    rating = tab_parts[3] if len(tab_parts) > 3 else ''

                    papers.append({
                        'title': title,
                        'authors': authors,
                        'affiliation': affiliation,
                        'country': country,
                        'rating': rating
                    })
                    i += 1  # Move past the details line
            else:
                # No details line found, just add with title
                papers.append({
                    'title': title,
                    'authors': '',
                    'affiliation': '',
                    'country': '',
                    'rating': ''
                })
        else:
            i += 1

    # Write formatted output
    with open(output_file, 'w', encoding='utf-8') as f:
        year = '2023' if '2023' in input_file else ('2024' if '2024' in input_file else '2025')
        f.write(f"# ICLR {year} Accepted Papers ({len(papers)} papers)\n\n")
        for idx, paper in enumerate(papers, 1):
            f.write(f"## {idx}. {paper['title']}\n")
            if paper['authors']:
                f.write(f"**Authors:** {paper['authors']}\n")
            if paper.get('affiliation'):
                f.write(f"**Affiliation:** {paper['affiliation']}\n")
            if paper.get('country'):
                f.write(f"**Country:** {paper['country']}\n")
            if paper.get('rating'):
                f.write(f"**Rating:** {paper['rating']}\n")
            f.write("\n")

# Parse all files
print("Parsing ECCV 2024...")
parse_eccv_2024(r'd:\repo\vlm-paper-search\eccv\2024-eccv-text.txt',
                r'd:\repo\vlm-paper-search\eccv\2024-eccv-formatted.md')

print("Parsing ECCV 2022...")
parse_eccv_2022(r'd:\repo\vlm-paper-search\eccv\2022-eccv-text.txt',
                r'd:\repo\vlm-paper-search\eccv\2022-eccv-formatted.md')

print("Parsing ICCV 2023...")
parse_iccv_2023(r'd:\repo\vlm-paper-search\iccv\2023-iccv-text.txt',
                r'd:\repo\vlm-paper-search\iccv\2023-iccv-formatted.md')

print("Parsing ICCV 2025...")
parse_iccv_2025(r'd:\repo\vlm-paper-search\iccv\2025-iccv-text.txt',
                r'd:\repo\vlm-paper-search\iccv\2025-iccv-formatted.md')

print("Parsing NeurIPS 2023...")
parse_neurips(r'd:\repo\vlm-paper-search\neurips\2023-neurips-text.txt',
              r'd:\repo\vlm-paper-search\neurips\2023-neurips-formatted.md')

print("Parsing NeurIPS 2024...")
parse_neurips(r'd:\repo\vlm-paper-search\neurips\2024-neurips-text.txt',
              r'd:\repo\vlm-paper-search\neurips\2024-neurips-formatted.md')

print("Parsing NeurIPS 2025...")
parse_neurips(r'd:\repo\vlm-paper-search\neurips\2025-neurips-text.txt',
              r'd:\repo\vlm-paper-search\neurips\2025-neurips-formatted.md')

print("Parsing AAAI 2023...")
parse_aaai(r'd:\repo\vlm-paper-search\aaai\2023-aaai-text.txt',
           r'd:\repo\vlm-paper-search\aaai\2023-aaai-formatted.md')

print("Parsing AAAI 2024...")
parse_aaai(r'd:\repo\vlm-paper-search\aaai\2024-aaai-text.txt',
           r'd:\repo\vlm-paper-search\aaai\2024-aaai-formatted.md')

print("Parsing AAAI 2025...")
parse_aaai(r'd:\repo\vlm-paper-search\aaai\2025-aaai-text.txt',
           r'd:\repo\vlm-paper-search\aaai\2025-aaai-formatted.md')

print("Parsing ICLR 2023...")
parse_iclr(r'd:\repo\vlm-paper-search\iclr\2023-iclr-text.txt',
           r'd:\repo\vlm-paper-search\iclr\2023-iclr-formatted.md')

print("Parsing ICLR 2024...")
parse_iclr(r'd:\repo\vlm-paper-search\iclr\2024-iclr-text.txt',
           r'd:\repo\vlm-paper-search\iclr\2024-iclr-formatted.md')

print("Parsing ICLR 2025...")
parse_iclr(r'd:\repo\vlm-paper-search\iclr\2025-iclr-text.txt',
           r'd:\repo\vlm-paper-search\iclr\2025-iclr-formatted.md')

print("Parsing IJCAI 2023...")
parse_ijcai(r'd:\repo\vlm-paper-search\IJCAI\2023-ijcai-text.txt',
            r'd:\repo\vlm-paper-search\IJCAI\2023-ijcai-formatted.md')

print("Parsing IJCAI 2024...")
parse_ijcai(r'd:\repo\vlm-paper-search\IJCAI\2024-ijcai-text.txt',
            r'd:\repo\vlm-paper-search\IJCAI\2024-ijcai-formatted.md')

print("Parsing IJCAI 2025...")
parse_ijcai(r'd:\repo\vlm-paper-search\IJCAI\2025-ijcai-text.txt',
            r'd:\repo\vlm-paper-search\IJCAI\2025-ijcai-formatted.md')

print("Done! All files have been formatted.")
