#!/usr/bin/env python3
"""
CSV Format Preprocessor
Transforms quiz CSV files to match the format expected by csv_to_xlsx_converter.py
"""

import csv
import sys
from pathlib import Path

def format_csv_for_converter(input_csv_path, output_csv_path):
    """
    Transform CSV from original format to converter-expected format
    
    Original format: Book Name,Question #,Question Stem,Answer A,Answer B,Answer C,Answer D,Correct Answer
    Target format: Question,Choice 1,Choice 2,Choice 3,Choice 4,Correct Answer,Explanation,Source
    """
    
    questions_processed = 0
    
    with open(input_csv_path, 'r', encoding='utf-8') as infile, \
         open(output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
        
        # Skip the first two rows (title and blank row)
        next(infile)  # Skip title row
        next(infile)  # Skip blank row
        
        reader = csv.DictReader(infile)
        
        # Define target fieldnames for the converter
        target_fieldnames = ['Question', 'Choice 1', 'Choice 2', 'Choice 3', 'Choice 4', 
                           'Correct Answer', 'Explanation', 'Source']
        
        writer = csv.DictWriter(outfile, fieldnames=target_fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Skip empty rows or rows without question stems
            if not row.get('Question Stem') or not row['Question Stem'].strip():
                continue
                
            question_stem = row['Question Stem'].strip()
            
            # Skip header repetitions, section headers, and metadata
            if (question_stem == 'Question Stem' or 
                'Final Exam' in question_stem or 
                'Quiz' in question_stem or
                not any(row.get(f'Answer {letter}', '').strip() for letter in ['A', 'B', 'C', 'D'])):
                continue
            
            # Transform the row to target format
            question_number = row.get('Question #', '').strip()
            source_id = f"PREP FL {question_number}" if question_number else "PREP FL"
            
            formatted_row = {
                'Question': question_stem,
                'Choice 1': row.get('Answer A', '').strip(),
                'Choice 2': row.get('Answer B', '').strip(), 
                'Choice 3': row.get('Answer C', '').strip(),
                'Choice 4': row.get('Answer D', '').strip(),
                'Correct Answer': row.get('Correct Answer', '').strip(),
                'Explanation': '',  # Empty - not available in source
                'Source': source_id  # Use PREP FL + question number
            }
            
            # Only write rows that have actual question content
            if formatted_row['Question'] and any(formatted_row[f'Choice {i}'] for i in range(1, 5)):
                writer.writerow(formatted_row)
                questions_processed += 1
    
    return questions_processed

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_formatter.py <input_csv> <output_csv>")
        sys.exit(1)
    
    input_csv = Path(sys.argv[1])
    output_csv = Path(sys.argv[2])
    
    if not input_csv.exists():
        print(f"Error: Input file {input_csv} not found")
        sys.exit(1)
    
    print(f"Formatting CSV: {input_csv} -> {output_csv}")
    
    try:
        questions_count = format_csv_for_converter(input_csv, output_csv)
        print(f"✅ Successfully formatted {questions_count} questions")
        print(f"Output saved to: {output_csv}")
        
    except Exception as e:
        print(f"❌ Error during formatting: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()