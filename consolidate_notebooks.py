"""
Master Notebook Consolidation Script
Scans Google Drive for related notebooks and merges them into a structured master notebook.

Usage:
    python consolidate_notebooks.py --search-dir "/content/drive/MyDrive" --output master_notebook.ipynb
"""

import os
import json
import argparse
import nbformat
from pathlib import Path
from typing import List, Dict, Tuple


class NotebookConsolidator:
    """Consolidates multiple .ipynb files into a single master notebook with metadata."""

    def __init__(self, search_dir: str):
        self.search_dir = search_dir
        self.notebooks: Dict[str, str] = {}

    def find_notebooks(self, keywords: List[str] = None) -> Dict[str, str]:
        """
        Find all .ipynb files in search_dir, optionally filtered by keywords.
        
        Args:
            keywords: List of keywords to filter notebooks (e.g., ['legal', 'hallucination'])
        
        Returns:
            Dict mapping notebook name to file path
        """
        found = {}
        keywords = keywords or []
        
        for root, dirs, files in os.walk(self.search_dir):
            for file in files:
                if file.endswith('.ipynb'):
                    full_path = os.path.join(root, file)
                    
                    # Filter by keywords if provided
                    if keywords:
                        if any(kw.lower() in file.lower() for kw in keywords):
                            found[file] = full_path
                    else:
                        found[file] = full_path
        
        self.notebooks = found
        return found

    def merge_notebooks(self, notebook_paths: List[str], output_path: str) -> None:
        """
        Merge multiple notebooks into a single master notebook.
        
        Args:
            notebook_paths: List of notebook file paths to merge
            output_path: Path to write consolidated notebook
        """
        merged_nb = nbformat.v4.new_notebook()
        merged_nb.metadata['consolidated'] = True
        merged_nb.metadata['source_notebooks'] = notebook_paths

        # Add title cell
        title_cell = nbformat.v4.new_markdown_cell(
            "# Master Research Notebook\n"
            "Auto-consolidated from multiple source notebooks.\n"
            f"Sources: {len(notebook_paths)} notebooks"
        )
        merged_nb.cells.append(title_cell)

        for file_path in notebook_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    nb = nbformat.read(f, as_version=4)
                    
                    # Add source notebook marker
                    source_marker = nbformat.v4.new_markdown_cell(
                        f"\n---\n## Source: {Path(file_path).name}\n"
                    )
                    merged_nb.cells.append(source_marker)
                    merged_nb.cells.extend(nb.cells)
                    
            except Exception as e:
                print(f"ERROR reading {file_path}: {e}")

        # Write consolidated notebook
        with open(output_path, "w", encoding="utf-8") as f:
            nbformat.write(merged_nb, f)
        
        print(f"✓ Consolidated notebook written to: {output_path}")

    def print_inventory(self) -> None:
        """Print inventory of found notebooks."""
        print("\n=== Found Notebooks ===")
        for name, path in self.notebooks.items():
            print(f"  {name}")
            print(f"    → {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate multiple Colab notebooks")
    parser.add_argument("--search-dir", type=str, required=True, help="Directory to search for notebooks")
    parser.add_argument("--keywords", type=str, nargs="+", help="Keywords to filter notebooks")
    parser.add_argument("--output", type=str, default="master_notebook.ipynb", help="Output path")
    
    args = parser.parse_args()
    
    consolidator = NotebookConsolidator(args.search_dir)
    found = consolidator.find_notebooks(keywords=args.keywords)
    
    consolidator.print_inventory()
    
    if found:
        notebook_paths = list(found.values())
        consolidator.merge_notebooks(notebook_paths, args.output)
    else:
        print("No notebooks found matching criteria.")
