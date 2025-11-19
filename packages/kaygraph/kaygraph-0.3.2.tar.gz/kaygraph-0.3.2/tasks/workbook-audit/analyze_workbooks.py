#!/usr/bin/env python3
"""
Workbook Analysis Script
Analyzes all KayGraph workbooks to determine quality, complexity, and value.
"""

import os
import json
from pathlib import Path
from datetime import datetime

def get_file_size(filepath):
    """Get file size in bytes, return 0 if not exists."""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def get_line_count(filepath):
    """Count lines in file, return 0 if not exists."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0

def get_last_modified(filepath):
    """Get last modified timestamp."""
    try:
        return datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
    except:
        return None

def extract_description(readme_path):
    """Extract first meaningful description from README."""
    try:
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 20:
                    return line[:200]
        return "No description found"
    except:
        return "README not found"

def categorize_workbook(name):
    """Categorize workbook by name."""
    if 'agent' in name:
        return 'AI/Agent'
    elif 'workflow' in name:
        return 'Workflow'
    elif 'chat' in name or 'voice' in name:
        return 'Chat/Conversation'
    elif 'memory' in name:
        return 'Memory'
    elif 'batch' in name or 'parallel' in name:
        return 'Batch Processing'
    elif 'tool' in name:
        return 'Tools/Integration'
    elif 'rag' in name or 'retrieval' in name:
        return 'RAG'
    elif any(x in name for x in ['fastapi', 'api', 'production', 'monitoring', 'tracing']):
        return 'Production'
    elif any(x in name for x in ['gradio', 'streamlit', 'human', 'visualization']):
        return 'UI/UX'
    elif name in ['kaygraph-hello-world', 'kaygraph-complete-example']:
        return 'Getting Started'
    elif 'async' in name or 'basic' in name:
        return 'Core Patterns'
    else:
        return 'Other'

def analyze_workbook(workbook_path):
    """Analyze a single workbook."""
    name = workbook_path.name

    # Key files to check
    readme_path = workbook_path / 'README.md'
    main_path = workbook_path / 'main.py'
    nodes_path = workbook_path / 'nodes.py'
    requirements_path = workbook_path / 'requirements.txt'

    # Gather metrics
    analysis = {
        'name': name,
        'category': categorize_workbook(name),
        'has_readme': readme_path.exists(),
        'has_main': main_path.exists(),
        'has_nodes': nodes_path.exists(),
        'has_requirements': requirements_path.exists(),
        'main_lines': get_line_count(main_path),
        'nodes_lines': get_line_count(nodes_path),
        'readme_size': get_file_size(readme_path),
        'last_modified': get_last_modified(main_path),
        'description': extract_description(readme_path),
        'total_files': len(list(workbook_path.glob('*.py'))),
    }

    # Calculate complexity score (0-10)
    complexity = 0
    if analysis['main_lines'] > 500:
        complexity += 4
    elif analysis['main_lines'] > 200:
        complexity += 3
    elif analysis['main_lines'] > 100:
        complexity += 2
    else:
        complexity += 1

    if analysis['nodes_lines'] > 300:
        complexity += 3
    elif analysis['nodes_lines'] > 100:
        complexity += 2
    elif analysis['nodes_lines'] > 0:
        complexity += 1

    if analysis['total_files'] > 5:
        complexity += 3
    elif analysis['total_files'] > 3:
        complexity += 2
    elif analysis['total_files'] > 1:
        complexity += 1

    analysis['complexity_score'] = min(complexity, 10)

    # Calculate quality score (0-10)
    quality = 0
    if analysis['has_readme']:
        quality += 3
    if analysis['readme_size'] > 2000:
        quality += 2
    if analysis['has_main']:
        quality += 2
    if analysis['has_requirements']:
        quality += 1
    if analysis['main_lines'] > 50:  # Not a stub
        quality += 2

    analysis['quality_score'] = min(quality, 10)

    return analysis

def main():
    """Run analysis on all workbooks."""
    workbooks_dir = Path('workbooks')

    # Find all kaygraph workbooks
    workbook_dirs = sorted(workbooks_dir.glob('kaygraph-*'))

    print(f"Found {len(workbook_dirs)} workbooks")
    print("Analyzing...\n")

    results = []

    for wb_path in workbook_dirs:
        if wb_path.is_dir():
            analysis = analyze_workbook(wb_path)
            results.append(analysis)

            # Print progress
            status = "✓" if analysis['quality_score'] >= 7 else "⚠" if analysis['quality_score'] >= 5 else "✗"
            print(f"{status} {analysis['name']:50} Quality: {analysis['quality_score']}/10  Complexity: {analysis['complexity_score']}/10")

    # Save results
    output_file = Path('tasks/workbook-audit/analysis_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Analysis complete. Results saved to {output_file}")

    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    total = len(results)
    high_quality = len([r for r in results if r['quality_score'] >= 7])
    medium_quality = len([r for r in results if 5 <= r['quality_score'] < 7])
    low_quality = len([r for r in results if r['quality_score'] < 5])

    print(f"\nTotal workbooks: {total}")
    print(f"High quality (7-10): {high_quality} ({high_quality*100//total}%)")
    print(f"Medium quality (5-6): {medium_quality} ({medium_quality*100//total}%)")
    print(f"Low quality (0-4): {low_quality} ({low_quality*100//total}%)")

    # Category breakdown
    print("\nBy Category:")
    categories = {}
    for r in results:
        cat = r['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat:25} {count:3} workbooks")

    # Missing README
    no_readme = [r['name'] for r in results if not r['has_readme']]
    if no_readme:
        print(f"\nMissing README ({len(no_readme)}):")
        for name in no_readme:
            print(f"  - {name}")

    # Small/stub workbooks
    stubs = [r['name'] for r in results if r['main_lines'] < 50]
    if stubs:
        print(f"\nPotential stubs (< 50 lines main.py) ({len(stubs)}):")
        for name in stubs:
            print(f"  - {name}")

if __name__ == '__main__':
    main()
