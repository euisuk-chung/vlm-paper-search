"""
Paper Filtering System
Filters papers from formatted markdown files based on topics and keywords defined in filter_config.yaml
"""

import os
import re
import yaml
import json
import argparse
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class PaperFilter:
    def __init__(self, config_path: str = "filter_config.yaml"):
        """Initialize the paper filter with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.options = self.config.get('options', {})
        self.case_sensitive = self.options.get('case_sensitive', False)
        self.min_keyword_matches = self.options.get('min_keyword_matches', 1)
        self.output_dir = self.options.get('output_dir', '_filtered')

        # Map conference names to directory names
        self.conference_map = {
            'AAAI': 'AAAI',
            'ECCV': 'ECCV',
            'ICCV': 'ICCV',
            'ICLR': 'ICLR',
            'IJCAI': 'IJCAI',
            'NEURIPS': 'NeurIPS',
            'CVPR': 'ECCV'  # CVPR papers might be in ECCV folder, adjust as needed
        }

    def parse_markdown_file(self, file_path: str) -> List[Dict]:
        """Parse a formatted markdown file and extract paper information"""
        papers = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract conference and year from filename
        filename = Path(file_path).stem
        match = re.match(r'(\d{4})-(\w+)-formatted', filename)
        if match:
            year = int(match.group(1))
            conference = match.group(2).upper()
        else:
            return papers

        # Split by paper sections (## number. Title)
        paper_sections = re.split(r'\n## \d+\. ', content)

        for section in paper_sections[1:]:  # Skip header
            lines = section.split('\n')
            if not lines:
                continue

            title = lines[0].strip()

            # Extract metadata
            authors = ''
            affiliation = ''
            country = ''
            rating = ''
            presentation = ''
            track = ''

            for line in lines[1:]:
                if line.startswith('**Authors:**'):
                    authors = line.replace('**Authors:**', '').strip()
                elif line.startswith('**Affiliation:**'):
                    affiliation = line.replace('**Affiliation:**', '').strip()
                elif line.startswith('**Country:**'):
                    country = line.replace('**Country:**', '').strip()
                elif line.startswith('**Rating:**'):
                    rating = line.replace('**Rating:**', '').strip()
                elif line.startswith('**Presentation:**'):
                    presentation = line.replace('**Presentation:**', '').strip()
                elif line.startswith('**Track:**'):
                    track = line.replace('**Track:**', '').strip()

            papers.append({
                'title': title,
                'authors': authors,
                'affiliation': affiliation,
                'country': country,
                'rating': rating,
                'presentation': presentation,
                'track': track,
                'conference': conference,
                'year': year,
                'source_file': file_path
            })

        return papers

    def match_keywords(self, text: str, keywords: List[str]) -> tuple[int, List[str]]:
        """
        Check if text matches keywords
        Returns: (number of matches, list of matched keywords)
        """
        if not self.case_sensitive:
            text = text.lower()
            keywords = [k.lower() for k in keywords]

        matched = []
        for keyword in keywords:
            if keyword in text:
                matched.append(keyword)

        return len(matched), matched

    def filter_papers_by_topic(self, topic_key: str, topic_config: Dict) -> tuple[List[Dict], Dict]:
        """Filter papers for a specific topic"""
        keywords = topic_config.get('keywords', [])
        conferences = topic_config.get('conferences', [])
        years = topic_config.get('years')

        # Convert conferences to uppercase for matching
        conferences = [c.upper() for c in conferences]

        all_papers = []
        stats = {
            'total': 0,
            'by_conference': {},
            'by_year': {},
            'keyword_matches': {}
        }

        # Scan all conference directories
        for conf_dir in os.listdir('.'):
            if not os.path.isdir(conf_dir):
                continue

            conf_upper = conf_dir.upper()

            # Skip if not in the conference list
            if conferences and conf_upper not in conferences:
                continue

            # Find all formatted markdown files
            for filename in os.listdir(conf_dir):
                if not filename.endswith('-formatted.md'):
                    continue

                # Extract year from filename
                match = re.match(r'(\d{4})-', filename)
                if not match:
                    continue

                file_year = int(match.group(1))

                # Check year filter
                if years is not None and file_year not in years:
                    continue

                # Parse the file
                file_path = os.path.join(conf_dir, filename)
                papers = self.parse_markdown_file(file_path)

                # Filter papers by keywords
                for paper in papers:
                    match_count, matched_keywords = self.match_keywords(
                        paper['title'], keywords
                    )

                    if match_count >= self.min_keyword_matches:
                        paper['matched_keywords'] = matched_keywords
                        paper['match_count'] = match_count
                        all_papers.append(paper)

                        # Update stats
                        conf_year_key = f"{paper['conference']} {paper['year']}"
                        stats['by_conference'][conf_year_key] = stats['by_conference'].get(conf_year_key, 0) + 1
                        stats['by_year'][paper['year']] = stats['by_year'].get(paper['year'], 0) + 1

                        for kw in matched_keywords:
                            stats['keyword_matches'][kw] = stats['keyword_matches'].get(kw, 0) + 1

        stats['total'] = len(all_papers)

        # Sort papers by conference and year
        all_papers.sort(key=lambda p: (p['conference'], p['year'], p['title']))

        return all_papers, stats

    def generate_papers_md(self, topic_key: str, topic_config: Dict, papers: List[Dict], stats: Dict, output_dir: str):
        """Generate the papers.md file for reading"""
        topic_name = topic_config.get('name', topic_key)
        description = topic_config.get('description', '')
        keywords = topic_config.get('keywords', [])
        conferences = topic_config.get('conferences', [])
        years = topic_config.get('years')

        year_str = f"{min(years)}-{max(years)}" if years else "all years"

        output = []
        output.append(f"# {topic_name}\n")
        output.append(f"**Filtered on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.append(f"**Description:** {description}\n")
        output.append(f"**Keywords:** {', '.join(keywords)}\n")
        output.append(f"**Conferences:** {', '.join(conferences)} ({year_str})\n")
        output.append(f"**Total Papers:** {stats['total']}\n")
        output.append("\n---\n\n")

        # Quick Stats
        output.append("## Quick Stats\n\n")
        for conf_year, count in sorted(stats['by_conference'].items()):
            output.append(f"- {conf_year}: {count} papers\n")
        output.append("\n---\n\n")

        # Group papers by conference/year
        conf_groups = {}
        for paper in papers:
            conf_year = f"{paper['conference']} {paper['year']}"
            if conf_year not in conf_groups:
                conf_groups[conf_year] = []
            conf_groups[conf_year].append(paper)

        # Sort papers within each conference by priority (HIGH > MED > LOW)
        def get_priority_score(paper):
            if paper['match_count'] >= 3 or (paper.get('rating') and 'Top-5' in paper.get('rating', '')):
                return 3  # HIGH
            elif paper['match_count'] >= 2 or (paper.get('rating') and 'Top' in paper.get('rating', '')):
                return 2  # MED
            else:
                return 1  # LOW

        # Papers by Conference
        output.append("## Papers by Conference\n\n")
        output.append("_Papers within each conference are sorted by priority (HIGH → MED → LOW)_\n\n")

        paper_num = 1
        for conf_year in sorted(conf_groups.keys()):
            conf_paper_list = conf_groups[conf_year]
            # Sort by priority (descending) then by match_count (descending)
            conf_paper_list.sort(key=lambda p: (get_priority_score(p), p['match_count']), reverse=True)

            count = len(conf_paper_list)
            output.append(f"### {conf_year} ({count} papers)\n\n")

            for paper in conf_paper_list:
                # Calculate priority for display
                priority = "[LOW]"
                if paper['match_count'] >= 3 or (paper.get('rating') and 'Top-5' in paper.get('rating', '')):
                    priority = "[HIGH]"
                elif paper['match_count'] >= 2 or (paper.get('rating') and 'Top' in paper.get('rating', '')):
                    priority = "[MED]"

                output.append(f"#### {paper_num}. {priority} {paper['title']}\n\n")

                if paper['authors']:
                    output.append(f"**Authors:** {paper['authors']}  \n")
                if paper['affiliation']:
                    output.append(f"**Affiliation:** {paper['affiliation']}  \n")
                if paper['country']:
                    output.append(f"**Country:** {paper['country']}  \n")
                if paper['rating']:
                    output.append(f"**Rating:** {paper['rating']}  \n")
                if paper['presentation']:
                    output.append(f"**Presentation:** {paper['presentation']}  \n")
                if paper['track']:
                    output.append(f"**Track:** {paper['track']}  \n")

                output.append(f"**Keywords Matched:** {', '.join(paper['matched_keywords'])}  \n")
                output.append(f"**Match Count:** {paper['match_count']}  \n\n")

                # Why this paper
                output.append("**Why this paper:**\n")
                reasons = []
                if paper['match_count'] >= 2:
                    reasons.append(f"Matches {paper['match_count']} keywords")
                if paper.get('rating') and 'Top' in paper.get('rating', ''):
                    reasons.append(f"High rating: {paper['rating']}")
                if paper['year'] >= 2024:
                    reasons.append(f"Recent ({paper['year']})")

                for reason in reasons:
                    output.append(f"- {reason}\n")
                output.append("\n")

                # Source and Links
                source_file = Path(paper['source_file']).name
                output.append(f"**Original Source:** {paper['conference']}/{source_file}\n\n")

                # arXiv search link
                search_query = urllib.parse.quote(paper['title'])
                output.append(f"**Links:**\n")
                output.append(f"- [Search on arXiv](https://arxiv.org/search/?query={search_query}&searchtype=title)\n")
                output.append(f"- [Search on Google Scholar](https://scholar.google.com/scholar?q={search_query})\n\n")

                output.append("---\n\n")

                paper_num += 1

        # Write to file
        with open(os.path.join(output_dir, 'papers.md'), 'w', encoding='utf-8') as f:
            f.write(''.join(output))

    def generate_checklist_md(self, topic_key: str, topic_config: Dict, papers: List[Dict], output_dir: str):
        """Generate the reading checklist"""
        topic_name = topic_config.get('name', topic_key)

        output = []
        output.append(f"# Reading Checklist - {topic_name}\n")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        output.append("## How to use\n")
        output.append("- [ ] Check papers as you read them\n")
        output.append("- Update notes in the \"Notes\" column\n")
        output.append("- Priority levels:\n")
        output.append("  - **[HIGH]**: 3+ keyword matches OR Top-5% rated papers\n")
        output.append("  - **[MED]**: 2+ keyword matches OR Top-rated papers\n")
        output.append("  - **[LOW]**: 1 keyword match\n\n")
        output.append("---\n\n")

        output.append("| Status | Priority | Paper | Conference | Keywords | Notes |\n")
        output.append("|--------|----------|-------|------------|----------|-------|\n")

        for paper in papers:
            # Auto-assign priority based on criteria
            priority = "[LOW]"
            if paper['match_count'] >= 3 or (paper.get('rating') and 'Top-5' in paper.get('rating', '')):
                priority = "[HIGH]"
            elif paper['match_count'] >= 2 or (paper.get('rating') and 'Top' in paper.get('rating', '')):
                priority = "[MED]"

            conf_year = f"{paper['conference']} {paper['year']}"
            title = paper['title'][:50] + '...' if len(paper['title']) > 50 else paper['title']
            keywords = f"{paper['match_count']}x"

            output.append(f"| [ ] | {priority} | {title} | {conf_year} | {keywords} | |\n")

        output.append(f"\n**Progress:** 0 / {len(papers)} papers read\n")
        output.append(f"\n**Priority Distribution:**\n")
        high = sum(1 for p in papers if p['match_count'] >= 3 or (p.get('rating') and 'Top-5' in p.get('rating', '')))
        med = sum(1 for p in papers if (p['match_count'] >= 2 or (p.get('rating') and 'Top' in p.get('rating', ''))) and p['match_count'] < 3)
        low = len(papers) - high - med
        output.append(f"- [HIGH]: {high} papers\n")
        output.append(f"- [MED]: {med} papers\n")
        output.append(f"- [LOW]: {low} papers\n")

        with open(os.path.join(output_dir, 'reading_checklist.md'), 'w', encoding='utf-8') as f:
            f.write(''.join(output))

    def generate_excel_file(self, papers: List[Dict], output_dir: str):
        """Generate Excel file with papers organized in a table"""
        try:
            import pandas as pd
        except ImportError:
            print("  [SKIP] Excel file - pandas not installed (run: uv pip install pandas openpyxl)")
            return

        # Prepare data for DataFrame
        data = []
        for paper in papers:
            # Calculate priority
            priority = "LOW"
            if paper['match_count'] >= 3 or (paper.get('rating') and 'Top-5' in paper.get('rating', '')):
                priority = "HIGH"
            elif paper['match_count'] >= 2 or (paper.get('rating') and 'Top' in paper.get('rating', '')):
                priority = "MED"

            # Create arXiv and Google Scholar URLs
            search_query = urllib.parse.quote(paper['title'])
            arxiv_url = f"https://arxiv.org/search/?query={search_query}&searchtype=title"
            scholar_url = f"https://scholar.google.com/scholar?q={search_query}"

            data.append({
                'Conference': paper['conference'],
                'Year': paper['year'],
                'Priority': priority,
                'Title': paper['title'],
                'Authors': paper.get('authors', ''),
                'Keywords Matched': ', '.join(paper['matched_keywords']),
                'Match Count': paper['match_count'],
                'Rating': paper.get('rating', ''),
                'arXiv Search': arxiv_url,
                'Google Scholar': scholar_url
            })

        # Create DataFrame
        df = pd.DataFrame(data)

        # Sort by Conference, Year, then Priority (HIGH > MED > LOW)
        priority_order = {'HIGH': 3, 'MED': 2, 'LOW': 1}
        df['Priority_Num'] = df['Priority'].map(priority_order)
        df = df.sort_values(['Conference', 'Year', 'Priority_Num', 'Match Count'],
                           ascending=[True, True, False, False])
        df = df.drop('Priority_Num', axis=1)

        # Write to Excel
        excel_path = os.path.join(output_dir, 'papers.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Papers', index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets['All Papers']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                # Limit URL columns width
                if 'URL' in col or 'Search' in col or 'Scholar' in col or 'arXiv' in col:
                    max_length = min(max_length, 50)
                # Limit Title column width
                elif col == 'Title':
                    max_length = min(max_length, 80)
                else:
                    max_length = min(max_length, 40)

                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

    def generate_by_conference_files(self, papers: List[Dict], stats: Dict, output_dir: str):
        """Generate individual files for each conference/year combination"""
        by_conf_dir = os.path.join(output_dir, 'by_conference')
        os.makedirs(by_conf_dir, exist_ok=True)

        # Group papers by conference/year
        conf_papers = {}
        for paper in papers:
            conf_year = f"{paper['conference']}_{paper['year']}"
            if conf_year not in conf_papers:
                conf_papers[conf_year] = []
            conf_papers[conf_year].append(paper)

        # Sort papers within each conference by priority (HIGH > MED > LOW)
        def get_priority_score(paper):
            if paper['match_count'] >= 3 or (paper.get('rating') and 'Top-5' in paper.get('rating', '')):
                return 3  # HIGH
            elif paper['match_count'] >= 2 or (paper.get('rating') and 'Top' in paper.get('rating', '')):
                return 2  # MED
            else:
                return 1  # LOW

        # Generate a file for each conference/year
        for conf_year, conf_paper_list in conf_papers.items():
            # Sort by priority (descending) then by match_count (descending)
            conf_paper_list.sort(key=lambda p: (get_priority_score(p), p['match_count']), reverse=True)

            output = []
            conf, year = conf_year.rsplit('_', 1)

            # Count papers by priority
            high_count = sum(1 for p in conf_paper_list if get_priority_score(p) == 3)
            med_count = sum(1 for p in conf_paper_list if get_priority_score(p) == 2)
            low_count = sum(1 for p in conf_paper_list if get_priority_score(p) == 1)

            output.append(f"# {conf} {year}\n")
            output.append(f"**Total Papers:** {len(conf_paper_list)}\n\n")
            output.append(f"**Priority Distribution:**\n")
            output.append(f"- [HIGH]: {high_count} papers\n")
            output.append(f"- [MED]: {med_count} papers\n")
            output.append(f"- [LOW]: {low_count} papers\n\n")
            output.append("_Papers are sorted by priority (HIGH → MED → LOW)_\n\n")
            output.append("---\n\n")

            for idx, paper in enumerate(conf_paper_list, 1):
                # Priority indicator
                priority = "[LOW]"
                if paper['match_count'] >= 3 or (paper.get('rating') and 'Top-5' in paper.get('rating', '')):
                    priority = "[HIGH]"
                elif paper['match_count'] >= 2 or (paper.get('rating') and 'Top' in paper.get('rating', '')):
                    priority = "[MED]"

                output.append(f"## {idx}. {priority} {paper['title']}\n\n")

                if paper['authors']:
                    output.append(f"**Authors:** {paper['authors']}  \n")
                if paper['affiliation']:
                    output.append(f"**Affiliation:** {paper['affiliation']}  \n")
                if paper['country']:
                    output.append(f"**Country:** {paper['country']}  \n")
                if paper['rating']:
                    output.append(f"**Rating:** {paper['rating']}  \n")
                if paper['presentation']:
                    output.append(f"**Presentation:** {paper['presentation']}  \n")
                if paper['track']:
                    output.append(f"**Track:** {paper['track']}  \n")

                output.append(f"**Keywords Matched:** {', '.join(paper['matched_keywords'])}  \n")
                output.append(f"**Match Count:** {paper['match_count']}  \n")
                output.append(f"**Priority:** {priority}\n\n")

                # arXiv and Google Scholar search links
                search_query = urllib.parse.quote(paper['title'])
                output.append(f"**Links:**\n")
                output.append(f"- [Search on arXiv](https://arxiv.org/search/?query={search_query}&searchtype=title)\n")
                output.append(f"- [Search on Google Scholar](https://scholar.google.com/scholar?q={search_query})\n\n")

                output.append("---\n\n")

            # Write file
            filename = f"{conf_year}.md"
            with open(os.path.join(by_conf_dir, filename), 'w', encoding='utf-8') as f:
                f.write(''.join(output))

    def generate_metadata_json(self, topic_key: str, topic_config: Dict, stats: Dict, output_dir: str, timestamp: str):
        """Generate metadata JSON file"""
        metadata = {
            'topic': topic_key,
            'topic_name': topic_config.get('name', topic_key),
            'timestamp': timestamp,
            'config': {
                'keywords': topic_config.get('keywords', []),
                'conferences': topic_config.get('conferences', []),
                'years': topic_config.get('years')
            },
            'results': stats,
            'priority_criteria': {
                'HIGH': '3+ keyword matches OR Top-5% rated papers',
                'MED': '2+ keyword matches OR Top-rated papers',
                'LOW': '1 keyword match'
            }
        }

        with open(os.path.join(output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def update_index(self, topic_key: str, topic_config: Dict, stats: Dict, output_subdir: str):
        """Update the index.md file with filtering history"""
        index_path = os.path.join(self.output_dir, 'index.md')

        # Read existing index if it exists
        entries = []
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse existing entries (simple approach)
                if '## Recent Searches' in content:
                    entries_section = content.split('## Recent Searches')[1]
                    # Keep existing entries
                    entries = [e.strip() for e in entries_section.split('\n###') if e.strip()]

        # Create new entry
        topic_name = topic_config.get('name', topic_key)
        conferences = topic_config.get('conferences', [])
        years = topic_config.get('years')
        year_str = ', '.join(map(str, years)) if years else 'all years'

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        new_entry = f"""### {timestamp} - {topic_name}
- **Papers Found:** {stats['total']}
- **Conferences:** {', '.join(conferences)} ({year_str})
- **Folder:** [{output_subdir}](./{output_subdir}/)
"""

        # Write index
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Paper Filtering History\n\n")
            f.write("## Recent Searches\n\n")
            f.write(new_entry + "\n")

            # Add existing entries (limit to 20)
            for entry in entries[:20]:
                if entry and not entry.startswith('#'):
                    f.write(f"### {entry}\n")

    def filter_topic(self, topic_key: str):
        """Filter papers for a single topic"""
        topic_config = self.config['topics'].get(topic_key)
        if not topic_config:
            print(f"Error: Topic '{topic_key}' not found in config")
            return

        topic_name = topic_config.get('name', topic_key)
        print(f"\nFiltering: {topic_name}")
        print("=" * 60)

        # Filter papers
        papers, stats = self.filter_papers_by_topic(topic_key, topic_config)

        if stats['total'] == 0:
            print(f"  No papers found matching criteria")
            return

        # Create output directory with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_subdir = f"{timestamp}_{topic_key}"
        output_dir = os.path.join(self.output_dir, output_subdir)
        os.makedirs(output_dir, exist_ok=True)

        # Generate output files
        print(f"\nGenerating output files...")
        self.generate_papers_md(topic_key, topic_config, papers, stats, output_dir)
        print(f"  [OK] papers.md - All papers in one file")

        self.generate_by_conference_files(papers, stats, output_dir)
        print(f"  [OK] by_conference/ - Individual files per conference/year")

        self.generate_checklist_md(topic_key, topic_config, papers, output_dir)
        print(f"  [OK] reading_checklist.md")

        self.generate_excel_file(papers, output_dir)
        print(f"  [OK] papers.xlsx - Excel file with all papers")

        self.generate_metadata_json(topic_key, topic_config, stats, output_dir, timestamp)
        print(f"  [OK] metadata.json")

        # Update index
        self.update_index(topic_key, topic_config, stats, output_subdir)
        print(f"  [OK] index.md updated")

        # Print stats
        print(f"\nResults:")
        print(f"  Total: {stats['total']} papers")
        print(f"\n  By Conference:")
        for conf_year, count in sorted(stats['by_conference'].items()):
            print(f"    {conf_year}: {count} papers")

        print(f"\nResults saved to: {output_dir}/")
        print(f"\nHappy reading!\n")

    def filter_all_topics(self):
        """Filter papers for all topics in config"""
        topics = self.config.get('topics', {})

        if not topics:
            print("No topics found in config")
            return

        for topic_key in topics:
            self.filter_topic(topic_key)


def main():
    parser = argparse.ArgumentParser(
        description='Filter papers by topics and keywords',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Filter all topics
  python filter_papers.py

  # Filter specific topic
  python filter_papers.py --topic vlm_pruning

  # Filter multiple topics
  python filter_papers.py --topics vlm_pruning llm_efficiency
        '''
    )

    parser.add_argument(
        '--topic',
        type=str,
        help='Filter a specific topic'
    )

    parser.add_argument(
        '--topics',
        type=str,
        nargs='+',
        help='Filter multiple topics'
    )

    args = parser.parse_args()

    # Initialize filter
    filter_system = PaperFilter()

    # Determine which topics to filter
    if args.topic:
        filter_system.filter_topic(args.topic)
    elif args.topics:
        for topic in args.topics:
            filter_system.filter_topic(topic)
    else:
        # Filter all topics
        filter_system.filter_all_topics()


if __name__ == '__main__':
    main()
