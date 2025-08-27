#!/usr/bin/env python3
"""
CSV Format Preprocessor
Transforms quiz CSV files to match the format expected by csv_to_xlsx_converter.py
"""

import csv
import sys
from pathlib import Path

def format_csv_for_converter(input_csv_path, output_csv_path, question_type=None):
    """
    Transform CSV from original format to converter-expected format
    
    Original format: Book Name,Question #,Question Stem,Answer A,Answer B,Answer C,Answer D,Correct Answer
    Target format: Question,Choice 1,Choice 2,Choice 3,Choice 4,Correct Answer,Explanation,Source
    
    Args:
        question_type: 'Quiz' or 'Final' to distinguish source types
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
            
            # Auto-detect question type from file path if not provided
            if question_type is None:
                if 'Quiz' in str(input_csv_path):
                    detected_type = 'Quiz'
                elif 'Final' in str(input_csv_path):
                    detected_type = 'Final'
                else:
                    detected_type = ''
            else:
                detected_type = question_type
            
            # Build source ID with quiz/final distinction
            type_prefix = f" {detected_type}" if detected_type else ""
            
            if question_number.startswith('P') and len(question_number) > 1:
                # P-series questions: "P4" -> "PREP FL Quiz P.4." or "PREP FL Final P.4."
                source_id = f"PREP FL{type_prefix} P.{question_number[1:]}."
            elif question_number:
                # Regular questions: "1.1" -> "PREP FL Quiz 1.1." or "PREP FL Final 1.1."
                source_id = f"PREP FL{type_prefix} {question_number}."
            else:
                source_id = f"PREP FL{type_prefix}."
            
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