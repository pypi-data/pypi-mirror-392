#!/usr/bin/env python3
"""Command-line interface for kunna."""

import sys
import os
from pathlib import Path


def get_data_dir():
    """Get the path to the data directory containing Q files."""
    return Path(__file__).parent / "data"


def show_question(question_id):
    """Display the content of a specific question file."""
    # Normalize the question ID (handle both q1, Q1, etc.)
    question_id = question_id.upper()
    if not question_id.startswith('Q'):
        question_id = 'Q' + question_id
    
    data_dir = get_data_dir()
    question_file = data_dir / f"{question_id}.md"
    
    if not question_file.exists():
        print(f"Error: Question '{question_id}' not found.")
        print(f"Available questions: Q1-Q15")
        return 1
    
    try:
        with open(question_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content)
        return 0
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 3:
        print("Usage: kunna show <question>")
        print("Example: kunna show q1")
        print("         kunna show Q1")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "show":
        question_id = sys.argv[2]
        return show_question(question_id)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: show")
        return 1


if __name__ == "__main__":
    sys.exit(main())
