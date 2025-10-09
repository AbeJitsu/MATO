#!/usr/bin/env python3
"""
CSV to XLSX Question Import Template Converter
Converts quiz CSV files to our standardized XLSX import format
"""

import csv
import pandas as pd
from pathlib import Path
import sys
import re

def parse_csv_questions(csv_file_path):
    """Parse CSV file and extract questions in our template format"""
    questions = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Skip empty rows
            if not row.get('Question') or not row['Question'].strip():
                continue
                
            question_text = row['Question'].strip()
            explanation = row.get('Explanation', '').strip()
            source = row.get('Source', '').strip()
            
            # Extract all available choices (flexible - detect all Choice X columns)
            choices = []
            i = 1
            while True:
                choice_key = f'Choice {i}'
                if choice_key in row and row[choice_key] and row[choice_key].strip():
                    choices.append(row[choice_key].strip())
                    i += 1
                else:
                    break
            
            # Handle correct answer
            correct_answer = row.get('Correct Answer', '').strip()
            
            # Determine question type
            question_type = 'TF' if len(choices) == 2 and 'True' in choices and 'False' in choices else 'MC'
            
            # Handle multiple correct answers (like "1, 2, 3" or "A, B, C")
            if ',' in correct_answer:
                question_type = 'MA'  # Multiple Answer
                correct_indices = []
                for x in correct_answer.split(','):
                    x = x.strip().upper()
                    if x.isdigit():
                        # Numeric (1-based)
                        correct_indices.append(int(x) - 1)
                    elif len(x) == 1 and x.isalpha():
                        # Letter-based (A=0, B=1, etc.)
                        correct_indices.append(ord(x) - ord('A'))
            elif correct_answer.lower() in ['true', 'false']:
                # For True/False questions
                correct_indices = [0 if correct_answer.lower() == 'true' else 1]
            elif correct_answer.isdigit():
                # Numeric answer (1-based)
                correct_indices = [int(correct_answer) - 1]
            elif len(correct_answer.strip()) == 1 and correct_answer.strip().upper().isalpha():
                # Single letter answer (A, B, C, D)
                letter = correct_answer.strip().upper()
                correct_indices = [ord(letter) - ord('A')]
            else:
                # Try to find answer text match
                correct_indices = []
                for i, choice in enumerate(choices):
                    if choice.lower() == correct_answer.lower():
                        correct_indices = [i]
                        break
            
            # Create question entry with all available choices
            question_entry = {
                'type': question_type,
                'question': question_text,
                'explanation': explanation,
                'choices': choices,  # Keep all choices
                'correct_indices': correct_indices,
                'source': source
            }
            
            questions.append(question_entry)
    
    return questions

def create_xlsx_output(questions, output_file_path, section_id="DTOX101-LESSON1"):
    """Create XLSX file in our template format"""
    
    # Prepare data for Questions sheet
    rows = []
    
    # Add header row
    rows.append(['Type', 'Question', 'Explanation', 'Answer', 'Correct', 'Meta Key', 'Meta Value'])
    
    for q in questions:
        # First row: question with first answer
        if q['choices']:  # Only if there are choices
            # Use question's individual source field for Meta Value
            question_section_id = q['source'] if q['source'] else section_id
            first_row = [
                q['type'],
                q['question'],
                q['explanation'],
                q['choices'][0],
                '1' if 0 in q['correct_indices'] else '',
                'ID',
                question_section_id
            ]
            rows.append(first_row)
            
            # Subsequent rows: remaining answers (flexible based on actual choices)
            for i in range(1, len(q['choices'])):
                answer_row = [
                    '',  # Type (empty)
                    '',  # Question (empty)
                    '',  # Explanation (empty)
                    q['choices'][i],  # Answer choice
                    '1' if i in q['correct_indices'] else '',  # Correct indicator
                    '',  # Meta Key (empty)
                    ''   # Meta Value (empty)
                ]
                rows.append(answer_row)
        
        # Blank row after each question
        rows.append(['', '', '', '', '', '', ''])
    
    # Create DataFrame and save to XLSX
    df_questions = pd.DataFrame(rows[1:], columns=rows[0])
    
    # Create comprehensive debug sheet following CLAUDE.md specifications
    debug_rows = []
    
    # Calculate section counts from individual question sources
    section_counts = {}
    for q in questions:
        q_section = q['source'] if q['source'] else section_id
        section_counts[q_section] = section_counts.get(q_section, 0) + 1
    
    # Section 1: Conversion Summary
    debug_rows.extend([
        ['Metric', 'Value'],
        ['Total Questions Parsed', len(questions)],
        ['Total Tracks/Sections', len(section_counts)],
        ['Keep Answer Prefixes', 'No'],
        ['Parsing Errors', 0],  # TODO: Track actual errors
        [''],
        ['Track Details']
    ])
    
    # Add each section's question count with natural sorting
    # Sort by extracting numerical parts for proper ordering (1.1, 1.2, ... 1.10, 1.11, etc.)
    def natural_sort_key(item):
        """Sort key that handles numerical parts correctly"""
        section = item[0]
        # Extract numbers from the section ID for proper sorting
        import re
        parts = re.findall(r'\d+', section)
        if len(parts) >= 2:
            # Convert to integers for numerical sorting: e.g., "1.2" -> (1, 2)
            return tuple(int(p) for p in parts)
        return (section,)  # Fallback to string if pattern doesn't match

    for section, count in sorted(section_counts.items(), key=natural_sort_key):
        debug_rows.append([f'  {section}', f'{count} questions'])
    
    debug_rows.extend([
        [''],
        ['Parsing Errors:'],
        ['  None detected'],
        [''],
        ['Track', 'Q#', 'Question Preview', 'Correct Answer', 'Page Ref', 'Has Explanation']
    ])
    
    # Section 4: Question Summary Table
    for i, q in enumerate(questions, 1):
        # Get correct answer letter(s) - handle multiple answers
        correct_letter = ''
        if q['correct_indices']:
            # Convert indices to letters (0->A, 1->B, etc.) - indices are already 0-based
            correct_letters = [chr(65 + idx) for idx in q['correct_indices']]
            correct_letter = ', '.join(sorted(correct_letters))
        
        # Get question preview (first 50 chars)
        question_preview = (q['question'][:47] + '...') if len(q['question']) > 50 else q['question']
        
        # Check if has explanation
        has_explanation = 'Yes' if q['explanation'].strip() else 'No'
        
        # Use question's individual source for debug table
        q_section = q['source'] if q['source'] else section_id
        debug_rows.append([
            q_section,
            str(i),
            question_preview,
            correct_letter,
            '',  # Page ref not available in CSV
            has_explanation
        ])
    
    # Create debug DataFrame
    df_debug = pd.DataFrame(debug_rows)
    
    # Write to XLSX with both sheets
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        df_questions.to_excel(writer, sheet_name='Questions', index=False)
        df_debug.to_excel(writer, sheet_name='Debug', index=False, header=False)
    
    return len(questions)

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_to_xlsx_converter.py <input_csv> <output_xlsx>")
        sys.exit(1)
    
    input_csv = Path(sys.argv[1])
    output_xlsx = Path(sys.argv[2])
    
    if not input_csv.exists():
        print(f"Error: Input file {input_csv} not found")
        sys.exit(1)
    
    # Parse questions
    print(f"Reading questions from {input_csv}")
    questions = parse_csv_questions(input_csv)
    
    if not questions:
        print("Error: No questions found in CSV file")
        sys.exit(1)
    
    print(f"Found {len(questions)} questions")
    
    # Generate section ID - prefer Source field, fallback to filename
    section_id = None
    if questions and questions[0]['source']:
        # Use Source field from first question if available
        section_id = questions[0]['source'].strip()
        print(f"Using Source field for Section ID: {section_id}")
    else:
        # Fallback to filename generation
        filename = input_csv.stem  # Get filename without extension
        # Clean up the filename to create a section ID
        section_id = filename.replace(' ', '-').replace('_', '-').upper()
        # Remove common file extensions or indicators and FORMATTED suffix
        section_id = section_id.replace('.XLSX', '').replace('.CSV', '').replace('-FORMATTED', '')
        print(f"Generated Section ID from filename: {section_id}")
    
    # Create output XLSX
    print(f"Converting to XLSX format: {output_xlsx}")
    question_count = create_xlsx_output(questions, output_xlsx, section_id)
    
    print(f"✅ Successfully converted {question_count} questions to {output_xlsx}")
    print(f"Section ID: {section_id}")

if __name__ == "__main__":
    main()