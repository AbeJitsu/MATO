#!/usr/bin/env python3
"""
Simple CSV Content Hasher
Generates content hash from original CSV files for validation tracking
"""

import sys
from pathlib import Path
from content_validator import extract_csv_content, generate_content_hash
import json
import datetime

def main():
    if len(sys.argv) != 3:
        print("Usage: python hash_csv.py <input_csv> <hash_output_file>")
        sys.exit(1)
    
    input_csv = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_csv.exists():
        print(f"Error: Input file {input_csv} not found")
        sys.exit(1)
    
    print(f"Generating hash for: {input_csv}")
    
    try:
        questions = extract_csv_content(input_csv)
        content_hash = generate_content_hash(questions)
        
        hash_data = {
            'file': str(input_csv),
            'question_count': len(questions),
            'content_hash': content_hash,
            'timestamp': str(datetime.datetime.now())
        }
        
        with open(output_file, 'w') as f:
            json.dump(hash_data, f, indent=2)
        
        print(f"✅ Hash generated for {len(questions)} questions")
        print(f"Hash: {content_hash}")
        print(f"Saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()