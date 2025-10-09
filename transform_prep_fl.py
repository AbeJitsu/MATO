#!/usr/bin/env python3
"""
PREP-FL CSV Transformer

What: Transforms PREP-FL CSV format to intermediate format for csv_to_xlsx_converter
Why: Standardizes question format for consistent processing
How: Reads PREP-FL format, restructures columns, and exports to intermediate CSV
"""

import csv
import pandas as pd

# Input and output paths
INPUT_CSV = "Input/PREP-FL 2nd Ed Final Question Excel Database 8-10-23.xlsx - Sheet1 (2).csv"
OUTPUT_CSV = "Input/PREP-FL_intermediate.csv"

def transform_prep_fl_csv():
    """
    Transform PREP-FL CSV format to intermediate format

    Fixes numbering errors: 1.2 appears twice (should be 1.2 and 1.20),
    same for 1.3-1.9 and 2.2-2.9

    Input format:
    - Book Name, Question #, Question Stem, Answer A, Answer B, Answer C, Answer D, Correct Answer, Meta Key, Meta Value

    Output format:
    - Question, Choice 1, Choice 2, Choice 3, Choice 4, Correct Answer, Source, Explanation
    """

    questions = []
    seen_numbers = {}  # Track which numbers we've seen

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        # Skip first 2 rows (title and blank)
        next(reader)
        next(reader)

        # Read header row
        headers = next(reader)

        for row in reader:
            # Skip empty rows
            if not row or len(row) < 8:
                continue

            # Skip exam divider rows
            if len(row) > 1 and row[1].startswith('Final Exam'):
                continue

            # Extract question data by column index
            question_stem = row[2].strip() if len(row) > 2 else ''
            if not question_stem:
                continue

            answer_a = row[3].strip() if len(row) > 3 else ''
            answer_b = row[4].strip() if len(row) > 4 else ''
            answer_c = row[5].strip() if len(row) > 5 else ''
            answer_d = row[6].strip() if len(row) > 6 else ''
            correct_answer = row[7].strip() if len(row) > 7 else ''
            question_number = row[1].strip() if len(row) > 1 else ''

            # Fix duplicate question numbers
            # If we've seen this number before and it's in the pattern X.2 through X.9
            if question_number in seen_numbers:
                # Check if it matches the pattern that needs fixing (X.2 - X.9)
                parts = question_number.split('.')
                if len(parts) == 2 and parts[1] in ['2', '3', '4', '5', '6', '7', '8', '9']:
                    # Add a trailing 0: 1.2 -> 1.20, 1.3 -> 1.30, etc.
                    question_number = f"{parts[0]}.{parts[1]}0"

            seen_numbers[question_number] = True

            # Generate Source ID with trailing period (PREP-FL-FINAL-1.1.)
            source_id = f"PREP-FL-FINAL-{question_number}."

            # Create intermediate format row
            intermediate_row = {
                'Question': question_stem,
                'Choice 1': answer_a,
                'Choice 2': answer_b,
                'Choice 3': answer_c,
                'Choice 4': answer_d,
                'Correct Answer': correct_answer,
                'Source': source_id,
                'Explanation': ''  # No explanations in source data
            }

            questions.append(intermediate_row)

    return questions

def main():
    """Main transformation function"""

    print("=" * 60)
    print("PREP-FL CSV Transformation")
    print("=" * 60)

    print(f"\nReading: {INPUT_CSV}")
    questions = transform_prep_fl_csv()

    print(f"Found: {questions} questions")

    # Create DataFrame
    df = pd.DataFrame(questions)

    # Save to intermediate CSV
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Saved: {OUTPUT_CSV}")
    print(f"\n✅ Transformation complete!")
    print(f"   Total questions: {len(questions)}")
    print(f"\nNext step: Run the converter tool")
    print(f"   python Tools/csv_to_xlsx_converter.py {OUTPUT_CSV} Output/prep_fl_questions.xlsx")
    print("=" * 60)

if __name__ == "__main__":
    main()
