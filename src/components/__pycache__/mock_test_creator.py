

import streamlit as st
import json
import requests
import re
from datetime import datetime
import os

# Import centralized styles - CSS is handled by main.py
# No CSS imports needed here as styles are centralized

# Configuration
CLAUDE_API_KEY = ""
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# Add these imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def get_board_specific_guidelines(board, grade, subject, topic):
    """Get comprehensive guidelines for ALL boards, grades, subjects, and topics"""
    
    # Universal grade-level cognitive development guidelines
    grade_development = {
        1: "Basic recognition, simple vocabulary, concrete concepts, visual learning",
        2: "Simple sentences, basic operations, pattern recognition, foundational skills",
        3: "Expanded vocabulary, multi-step processes, comparison skills, basic analysis",
        4: "Complex sentences, problem-solving, categorization, logical reasoning",
        5: "Abstract thinking begins, detailed explanations, cause-effect relationships",
        6: "Advanced vocabulary, multi-step problems, analytical thinking, applications",
        7: "Complex concepts, critical thinking, detailed analysis, practical applications",
        8: "Abstract reasoning, sophisticated vocabulary, advanced problem-solving",
        9: "High-level analysis, complex applications, preparation for advanced study",
        10: "Board exam preparation, advanced concepts, comprehensive understanding",
        11: "Pre-university level, specialized knowledge, research-based learning",
        12: "University preparation, expert-level understanding, independent analysis"
    }
    
    # Board-specific educational philosophies and styles
    board_characteristics = {
        "CBSE": {
            "philosophy": "Holistic development, practical application, Indian cultural context",
            "language": "Indian English, Hindi transliterations when relevant",
            "examples": "Indian cities, cultural references, local contexts",
            "assessment": "Application-based, real-world problems, analytical thinking",
            "difficulty": "Balanced approach, comprehensive coverage, skill development"
        },
        "ICSE": {
            "philosophy": "Analytical thinking, detailed study, British educational system",
            "language": "British English spellings and grammar",
            "examples": "International contexts, analytical scenarios",
            "assessment": "Detailed answers, analytical questions, comprehensive evaluation",
            "difficulty": "Higher complexity, detailed explanations, thorough understanding"
        },
        "Cambridge IGCSE": {
            "philosophy": "International perspective, global contexts, academic excellence",
            "language": "International English, academic vocabulary",
            "examples": "Global examples, international case studies, multicultural contexts",
            "assessment": "Cambridge assessment style, structured questions, evidence-based answers",
            "difficulty": "International standards, university preparation, rigorous evaluation"
        },
        "IB": {
            "philosophy": "Inquiry-based learning, international mindedness, critical thinking",
            "language": "Academic English, inquiry-based terminology",
            "examples": "Global perspectives, intercultural understanding, real-world applications",
            "assessment": "Concept-based, inquiry-driven, reflection and analysis",
            "difficulty": "High academic rigor, conceptual understanding, independent thinking"
        },
        "State Board": {
            "philosophy": "Regional relevance, state-specific curriculum, accessible education",
            "language": "Local language influences, regional terminology",
            "examples": "State-specific examples, local geography and culture",
            "assessment": "State pattern questions, curriculum-aligned, practical focus",
            "difficulty": "State standards, accessible to diverse learners, practical applications"
        }
    }
    
    # Generate comprehensive guidelines
    def generate_guidelines(board, grade, subject, topic):
        # Get base characteristics
        board_info = board_characteristics.get(board, board_characteristics["CBSE"])
        grade_level = grade_development.get(grade, f"Grade {grade} cognitive level")
        
        guidelines = f"""
BOARD: {board}
{board_info['philosophy']}
Language: {board_info['language']}
Examples: {board_info['examples']}
Assessment Style: {board_info['assessment']}

GRADE {grade} LEVEL:
Cognitive Development: {grade_level}

TOPIC: "{topic}"
Focus: All questions must be specifically about "{topic}" as taught in {board} Grade {grade} {subject}
Complexity: Match {board} Grade {grade} examination standards
Context: Use {board_info['examples']} where appropriate
Language: {board_info['language']} terminology and style
"""
        return guidelines
    
    return generate_guidelines(board, grade, subject, topic)

def get_ib_grade_options():
    """Return IB grade options with programme labels"""
    return [
        "Grade 1 (PYP)",
        "Grade 2 (PYP)", 
        "Grade 3 (PYP)",
        "Grade 4 (PYP)",
        "Grade 5 (PYP)",
        "Grade 6 (MYP)",
        "Grade 7 (MYP)",
        "Grade 8 (MYP)",
        "Grade 9 (MYP)",
        "Grade 10 (MYP)",
        "Grade 11 (DP)",
        "Grade 12 (DP)"
    ]

def get_paper_types_by_board_and_grade(board, grade):
    """Return comprehensive paper types based on board and grade selection - RESEARCHED DATA"""
    
    # Extract numeric grade for processing
    if isinstance(grade, str) and "Grade" in grade:
        try:
            if "(" in grade:  # IB format like "Grade 5 (PYP)"
                grade_num = int(grade.split()[1])
            else:  # Standard format like "Grade 5"
                grade_num = int(grade.replace("Grade ", ""))
        except (ValueError, IndexError):
            grade_num = 0
    else:
        grade_num = grade if isinstance(grade, int) else grade
    
    if board == "CBSE":
        if grade_num <= 5:  # Primary Classes (1-5)
            return [
                "Formative Assessment Test (20 Mixed Questions)",
                "Summative Assessment Paper (25 Mixed Questions)", 
                "Unit Test Format (15 Questions)",
                "Term Examination Paper (30 Questions)",
                "Activity-Based Assessment (20 Practical Tasks)",
                "Oral Assessment Test (10 Questions)",
                "Project Work Assessment (15 Creative Tasks)"
            ]
        elif grade_num <= 8:  # Middle Classes (6-8)
            return [
                "Periodic Test Paper (35 Mixed Questions)",
                "Term Examination Format (40 Questions)",
                "Unit Assessment Test (30 Questions)",
                "Half-Yearly Examination (45 Questions)",
                "Annual Examination Paper (50 Questions)",
                "Internal Assessment Format (25 Questions)",
                "Practice Test Series (35 Questions)"
            ]
        elif grade_num <= 10:  # Secondary (9-10)
            return [
                "Board Pattern Paper - Theory (25 MCQ + 10 Short + 5 Long)",
                "Sample Paper Format - Full Syllabus (40 Mixed Questions)",
                "Pre-Board Examination Paper (35 Questions)",
                "Mock Board Test (30 MCQ + 15 Short Answers)",
                "Chapter-wise Practice Test (25 Questions)",
                "Competency-Based Question Paper (20 MCQ + 15 Application)",
                "AISSE Pattern Mock Test (Full 80 marks format)"
            ]
        else:  # Senior Secondary (11-12)
            return [
                "Board Examination Pattern (30 Mixed Questions)",
                "AISSCE Sample Paper Format (35 Questions)",
                "Pre-Board Mock Test (40 Questions)",
                "Term-End Examination (45 Questions)",
                "Practice Test Series (30 MCQ + 10 Long)",
                "Chapter-wise Assessment (25 Questions)",
                "Competency-Based Paper (20 MCQ + 15 Application + 5 Case Study)"
            ]
    
    elif board == "ICSE":
        if grade_num <= 5:  # Primary Classes (1-5)
            return [
                "Foundation Assessment Test (20 Mixed Questions)",
                "Term Examination Paper (25 Questions)",
                "Progress Evaluation Test (30 Questions)",
                "Skills Assessment Format (15 Activity-Based)",
                "Continuous Assessment Paper (20 Questions)",
                "Unit Test Format (18 Questions)",
                "Oral Assessment Test (12 Questions)"
            ]
        elif grade_num <= 8:  # Middle Classes (6-8)
            return [
                "Class Test Format (30 Questions)",
                "Term Examination Paper (35 Questions)", 
                "Half-Yearly Assessment (40 Questions)",
                "Annual Examination Format (45 Questions)",
                "Internal Assessment Test (25 Questions)",
                "Chapter-wise Practice (20 Questions)",
                "Skills Evaluation Paper (30 Mixed Questions)"
            ]
        elif grade_num == 10:  # ICSE Board Exam
            return [
                "ICSE Board Pattern Paper 1 - Theory (25 MCQ + 15 Short)",
                "ICSE Board Pattern Paper 2 - Descriptive (20 Long Answers)",
                "Mock ICSE Examination (Full 80 marks format)",
                "Sample Paper - Group I Subjects (35 Questions)",
                "Sample Paper - Group II Subjects (30 Questions)", 
                "Sample Paper - Group III Subjects (25 Questions)",
                "Pre-Board Mock Test (40 Mixed Questions)",
                "Chapter-wise Practice Test (30 Questions)"
            ]
        else:  # ISC (11-12)
            return [
                "ISC Board Pattern Paper 1 - Theory (30 Questions)",
                "ISC Board Pattern Paper 2 - Application (25 Questions)",
                "Mock ISC Examination (Full 100 marks format)",
                "Sample Paper Format (35 Mixed Questions)",
                "Pre-Board Assessment (40 Questions)",
                "Term Examination Paper (45 Questions)",
                "Project Work Assessment (20 Research Questions)",
                "Practice Test Series (35 Questions)"
            ]
    
    elif board == "IB":
        if "(PYP)" in str(grade) or grade_num <= 5:  # Primary Years Programme
            return [
                "Formative Assessment Tasks (15 Inquiry Questions)",
                "Unit of Inquiry Assessment (20 Mixed Questions)",
                "Transdisciplinary Skills Test (18 Questions)",
                "Exhibition Preparation Practice (12 Research Tasks)",
                "Concept-Based Assessment (20 Questions)",
                "Student-Led Conference Prep (15 Reflection Questions)",
                "Action-Focused Evaluation (18 Application Tasks)"
            ]
        elif "(MYP)" in str(grade) or (6 <= grade_num <= 10):  # Middle Years Programme
            return [
                "MYP Criterion-Based Assessment (25 Questions)",
                "eAssessment Practice Paper (30 On-Screen Questions)",
                "Personal Project Preparation (15 Research Questions)",
                "Interdisciplinary Unit Test (20 Questions)",
                "Community Project Assessment (18 Service Questions)",
                "ATL Skills Evaluation (25 Questions)",
                "Global Context Exploration (20 Questions)",
                "Subject-Specific Assessment (30 Questions)"
            ]
        elif "(DP)" in str(grade) or grade_num >= 11:  # Diploma Programme
            return [
                "Paper 1 - Multiple Choice (40 MCQs)",
                "Paper 2 - Structured Questions (15 Short + 10 Long)",
                "Paper 3 - Extension/Options (20 Mixed Questions)",
                "Internal Assessment Practice (25 Questions)",
                "Extended Essay Preparation (10 Research Questions)",
                "TOK Assessment Practice (15 Critical Thinking Questions)",
                "Mock IB Examination (Full DP Format)",
                "Higher Level Practice Paper (35 Questions)",
                "Standard Level Practice Paper (30 Questions)"
            ]
        else:
            return []
    
    elif board == "Cambridge IGCSE":
        if grade_num <= 8:  # Lower Secondary
            return [
                "Cambridge Primary Test (20 Questions)",
                "Lower Secondary Assessment (25 Questions)",
                "Checkpoint Practice Paper (30 Questions)",
                "Stage Assessment Test (22 Questions)",
                "Progress Test Format (28 Questions)",
                "Skills Development Assessment (20 Questions)",
                "Term Examination Paper (35 Questions)"
            ]
        elif grade_num <= 10:  # IGCSE Level
            return [
                "Paper 1 - Core Level (30 MCQs + 10 Short)",
                "Paper 2 - Extended Level (25 Mixed Questions)",
                "Paper 3 - Practical/Coursework Assessment (20 Questions)",
                "Paper 4 - Alternative to Practical (25 Questions)",
                "Mock IGCSE Examination (Full Format)",
                "Sample Paper - Foundation Tier (35 Questions)",
                "Sample Paper - Higher Tier (40 Questions)",
                "Pre-Examination Practice (30 Questions)"
            ]
        else:  # AS/A Level (11-12)
            return [
                "AS Level Paper 1 (35 Questions)",
                "AS Level Paper 2 (30 Questions)", 
                "A Level Paper 1 (40 Questions)",
                "A Level Paper 2 (35 Questions)",
                "A Level Paper 3 - Synoptic (25 Questions)",
                "Cambridge Advanced Practice (45 Questions)",
                "Mock AS/A Level Examination (Full Format)",
                "Practical Assessment Paper (20 Questions)"
            ]
    
    elif board == "State Board":
        if grade_num <= 5:  # Primary Classes
            return [
                "State Pattern Primary Test (20 Questions)",
                "Monthly Assessment Paper (15 Questions)",
                "Quarterly Examination (25 Questions)",
                "Half-Yearly Assessment (30 Questions)",
                "Annual Examination Format (35 Questions)",
                "Unit Test Paper (18 Questions)",
                "Progress Evaluation Test (22 Questions)"
            ]
        elif grade_num <= 8:  # Middle Classes
            return [
                "State Board Format Test (30 Questions)",
                "Quarterly Assessment Paper (25 MCQ + 15 Short)",
                "Half-Yearly Examination (35 Questions)",
                "Annual Examination Format (40 Questions)",
                "Chapter-wise Practice Test (25 Questions)",
                "Term Assessment Paper (35 Questions)",
                "Internal Evaluation Test (20 Questions)"
            ]
        elif grade_num == 10:  # SSC/SSLC
            return [
                "SSC Board Pattern Paper 1 (25 MCQ + 15 Short + 5 Long)",
                "SSC Board Pattern Paper 2 (20 Long Answer Questions)",
                "State Board Mock Examination (Full Format)",
                "Pre-Board Practice Test (35 Questions)",
                "Sample Paper - Theory Format (40 Questions)",
                "Chapter-wise Board Practice (30 Questions)",
                "Annual Board Exam Pattern (Full 80 marks)",
                "Model Question Paper (35 Mixed Questions)"
            ]
        else:  # HSC/PUC (11-12)
            return [
                "HSC Board Pattern Paper (35 Mixed Questions)",
                "State Higher Secondary Format (40 Questions)",
                "Pre-University Examination (45 Questions)",
                "Board Exam Mock Test (Full Format)",
                "Sample Paper - Theory + Practical (35 + 15)",
                "Term-End Assessment (40 Questions)",
                "Chapter-wise HSC Practice (30 Questions)",
                "Model HSC Question Paper (Full 100 marks)"
            ]
    
    return []  # Fallback empty list
     
      
    # Grades 11-12
def get_question_counts_from_paper_type(paper_type):
    """Extract EXACT question counts, marks and format from paper type - RESEARCH-BASED DATA"""
    
    mcq_count = 0
    short_count = 0
    long_count = 0
    mcq_marks_each = 1
    short_marks_each = 3
    long_marks_each = 5
    total_marks = 80
    paper_duration = "3 hours"
    
    paper_type_lower = paper_type.lower()
    
    # ========== CBSE PATTERNS (Research-based from official CBSE data) ==========
    
    # CBSE Primary Classes (1-5) - 40-60 marks total
    if "formative assessment test (20 mixed questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 10
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 2
        total_marks = 30
        paper_duration = "2 hours"
        
    elif "summative assessment paper (25 mixed questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 10
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 2.5
        total_marks = 40
        paper_duration = "2.5 hours"
        
    elif "unit test format (15 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 5
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 2
        total_marks = 20
        paper_duration = "1.5 hours"
        
    elif "term examination paper (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 3
        total_marks = 48
        paper_duration = "2.5 hours"
        
    elif "activity-based assessment (20 practical tasks)" in paper_type_lower:
        mcq_count = 0
        short_count = 20
        long_count = 0
        short_marks_each = 2
        total_marks = 40
        paper_duration = "2 hours"
        
    elif "oral assessment test (10 questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 10
        long_count = 0
        short_marks_each = 2
        total_marks = 20
        paper_duration = "30 minutes"
        
    elif "project work assessment (15 creative tasks)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 0
        short_marks_each = 2
        total_marks = 30
        paper_duration = "2 hours"
    
    # CBSE Middle Classes (6-8) - 50-80 marks total
    elif "periodic test paper (35 mixed questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 56
        paper_duration = "2.5 hours"
        
    elif "term examination format (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 70
        paper_duration = "3 hours"
        
    elif "unit assessment test (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 3
        total_marks = 48
        paper_duration = "2.5 hours"
        
    elif "half-yearly examination (45 questions)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "annual examination paper (50 questions)" in paper_type_lower:
        mcq_count = 30
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 90
        paper_duration = "3 hours"
        
    elif "internal assessment format (25 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 39
        paper_duration = "2 hours"
        
    elif "practice test series (35 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 56
        paper_duration = "2.5 hours"
    
    # CBSE Secondary (9-10) - Official 80 marks theory + 20 internal
    elif "board pattern paper - theory (25 mcq + 10 short + 5 long)" in paper_type_lower:
        mcq_count = 25
        short_count = 10
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 5
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "sample paper format - full syllabus (40 mixed questions)" in paper_type_lower:
        mcq_count = 16
        short_count = 16
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "pre-board examination paper (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "mock board test (30 mcq + 15 short answers)" in paper_type_lower:
        mcq_count = 30
        short_count = 15
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 3.33
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "chapter-wise practice test (25 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 7
        total_marks = 67
        paper_duration = "2.5 hours"
        
    elif "competency-based question paper (20 mcq + 15 application)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 4
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "aisse pattern mock test (full 80 marks format)" in paper_type_lower:
        mcq_count = 20
        short_count = 10
        long_count = 6
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 5
        total_marks = 80
        paper_duration = "3 hours"
    
    # CBSE Senior Secondary (11-12) - Official 70-80 marks theory + 20-30 internal
    elif "board examination pattern (30 mixed questions)" in paper_type_lower:
        mcq_count = 12
        short_count = 12
        long_count = 6
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "aissce sample paper format (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "pre-board mock test (40 questions)" in paper_type_lower:
        mcq_count = 16
        short_count = 16
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "term-end examination (45 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 20
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 8
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "practice test series (30 mcq + 10 long)" in paper_type_lower:
        mcq_count = 30
        short_count = 0
        long_count = 10
        mcq_marks_each = 1
        long_marks_each = 5
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "chapter-wise assessment (25 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 10
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 7
        total_marks = 75
        paper_duration = "2.5 hours"
        
    elif "competency-based paper (20 mcq + 15 application + 5 case study)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
    
    # ========== ICSE PATTERNS (Research-based from official ICSE data) ==========
    
    # ICSE Primary Classes (1-5) - 40-60 marks total
    elif "foundation assessment test (20 mixed questions)" in paper_type_lower:
        mcq_count = 12
        short_count = 8
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 3
        total_marks = 36
        paper_duration = "2 hours"
        
    elif "term examination paper (25 questions)" in paper_type_lower and "icse" in paper_type_lower.split()[0:3]:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 39
        paper_duration = "2.5 hours"
        
    elif "progress evaluation test (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 51
        paper_duration = "2.5 hours"
        
    elif "skills assessment format (15 activity-based)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 0
        short_marks_each = 3
        total_marks = 45
        paper_duration = "2 hours"
        
    elif "continuous assessment paper (20 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 34
        paper_duration = "2 hours"
        
    elif "unit test format (18 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 6
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 3
        total_marks = 28
        paper_duration = "1.5 hours"
        
    elif "oral assessment test (12 questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 12
        long_count = 0
        short_marks_each = 2
        total_marks = 24
        paper_duration = "30 minutes"
    
    # ICSE Middle Classes (6-8) - 50-80 marks total
    elif "class test format (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 54
        paper_duration = "2.5 hours"
        
    elif "half-yearly assessment (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "annual examination format (45 questions)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 7
        total_marks = 90
        paper_duration = "3 hours"
        
    elif "internal assessment test (25 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 39
        paper_duration = "2 hours"
        
    elif "chapter-wise practice (20 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 34
        paper_duration = "2 hours"
        
    elif "skills evaluation paper (30 mixed questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 54
        paper_duration = "2.5 hours"
    
    # ICSE Grade 10 - Official 80 marks theory + 20 internal
    elif "icse board pattern paper 1 - theory (25 mcq + 15 short)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 3.67
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "icse board pattern paper 2 - descriptive (20 long answers)" in paper_type_lower:
        mcq_count = 0
        short_count = 0
        long_count = 20
        long_marks_each = 4
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "mock icse examination (full 80 marks format)" in paper_type_lower:
        mcq_count = 15
        short_count = 10
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 5
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "sample paper - group i subjects (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "sample paper - group ii subjects (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 9
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "sample paper - group iii subjects (25 questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 10
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "pre-board mock test (40 mixed questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 8
        total_marks = 80
        paper_duration = "2.5 hours"
        
    elif "chapter-wise practice test (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 75
        paper_duration = "2.5 hours"
    
    # ISC (11-12) - Official 70-100 marks theory + 20-30 internal
    elif "isc board pattern paper 1 - theory (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 10
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 85
        paper_duration = "3 hours"
        
    elif "isc board pattern paper 2 - application (25 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 10
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "mock isc examination (full 100 marks format)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 100
        paper_duration = "3 hours"
        
    elif "sample paper format (35 mixed questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 85
        paper_duration = "3 hours"
        
    elif "pre-board assessment (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 8
        total_marks = 90
        paper_duration = "3 hours"
        
    elif "project work assessment (20 research questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 20
        long_count = 0
        short_marks_each = 4
        total_marks = 80
        paper_duration = "3 hours"
    
    # ========== IB PATTERNS (Research-based from official IB data) ==========
    
    # IB PYP (Primary Years Programme) - 30-50 marks total
    elif "formative assessment tasks (15 inquiry questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 0
        short_marks_each = 2.5
        total_marks = 37.5
        paper_duration = "2 hours"
        
    elif "unit of inquiry assessment (20 mixed questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 36
        paper_duration = "2 hours"
        
    elif "transdisciplinary skills test (18 questions)" in paper_type_lower:
        mcq_count = 8
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 32
        paper_duration = "1.5 hours"
        
    elif "exhibition preparation practice (12 research tasks)" in paper_type_lower:
        mcq_count = 0
        short_count = 12
        long_count = 0
        short_marks_each = 3
        total_marks = 36
        paper_duration = "2 hours"
        
    elif "concept-based assessment (20 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 36
        paper_duration = "2 hours"
        
    elif "student-led conference prep (15 reflection questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 0
        short_marks_each = 3
        total_marks = 45
        paper_duration = "2 hours"
        
    elif "action-focused evaluation (18 application tasks)" in paper_type_lower:
        mcq_count = 0
        short_count = 18
        long_count = 0
        short_marks_each = 2.5
        total_marks = 45
        paper_duration = "2 hours"
    
    # IB MYP (Middle Years Programme) - 50-80 marks total
    elif "myp criterion-based assessment (25 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 52
        paper_duration = "2.5 hours"
        
    elif "eassessment practice paper (30 on-screen questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 60
        paper_duration = "2 hours"
        
    elif "personal project preparation (15 research questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 0
        short_marks_each = 4
        total_marks = 60
        paper_duration = "3 hours"
        
    elif "interdisciplinary unit test (20 questions)" in paper_type_lower:
        mcq_count = 8
        short_count = 10
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 50
        paper_duration = "2 hours"
        
    elif "community project assessment (18 service questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 18
        long_count = 0
        short_marks_each = 3
        total_marks = 54
        paper_duration = "2.5 hours"
        
    elif "atl skills evaluation (25 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 43
        paper_duration = "2 hours"
        
    elif "global context exploration (20 questions)" in paper_type_lower:
        mcq_count = 8
        short_count = 10
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 50
        paper_duration = "2 hours"
        
    elif "subject-specific assessment (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 7
        total_marks = 60
        paper_duration = "2.5 hours"
    
    # IB DP (Diploma Programme) - Official IB marking schemes
    elif "paper 1 - multiple choice (40 mcqs)" in paper_type_lower:
        mcq_count = 40
        short_count = 0
        long_count = 0
        mcq_marks_each = 1
        total_marks = 40
        paper_duration = "1 hour"
        
    elif "paper 2 - structured questions (15 short + 10 long)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 10
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 105
        paper_duration = "2.25 hours"
        
    elif "paper 3 - extension/options (20 mixed questions)" in paper_type_lower:
        mcq_count = 8
        short_count = 8
        long_count = 4
        mcq_marks_each = 1
        short_marks_each = 4
        long_marks_each = 8
        total_marks = 72
        paper_duration = "1.25 hours"
        
    elif "internal assessment practice (25 questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 25
        long_count = 0
        short_marks_each = 1.6
        total_marks = 40
        paper_duration = "2 hours"
        
    elif "extended essay preparation (10 research questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 0
        long_count = 10
        long_marks_each = 3.6
        total_marks = 36
        paper_duration = "3 hours"
        
    elif "tok assessment practice (15 critical thinking questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 15
        long_count = 0
        short_marks_each = 2.67
        total_marks = 40
        paper_duration = "2.5 hours"
        
    elif "mock ib examination (full dp format)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 108
        paper_duration = "3 hours"
        
    elif "higher level practice paper (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 4
        long_marks_each = 8
        total_marks = 115
        paper_duration = "3 hours"
        
    elif "standard level practice paper (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 69
        paper_duration = "2.5 hours"
    
    # ========== CAMBRIDGE IGCSE PATTERNS (Research-based) ==========
    
    # Cambridge Lower Secondary (Grades 6-8) - 40-70 marks
    elif "cambridge primary test (20 questions)" in paper_type_lower:
        mcq_count = 12
        short_count = 6
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 32
        paper_duration = "1.5 hours"
        
    elif "lower secondary assessment (25 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 41
        paper_duration = "2 hours"
        
    elif "checkpoint practice paper (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 54
        paper_duration = "2 hours"
        
    elif "stage assessment test (22 questions)" in paper_type_lower:
        mcq_count = 12
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 36
        paper_duration = "1.5 hours"
        
    elif "progress test format (28 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 10
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 50
        paper_duration = "2 hours"
        
    elif "skills development assessment (20 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 34
        paper_duration = "1.5 hours"
    
    # Cambridge IGCSE Level (Grades 9-10) - 70-90 marks
    elif "paper 1 - core level (30 mcqs + 10 short)" in paper_type_lower:
        mcq_count = 30
        short_count = 10
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 4
        total_marks = 70
        paper_duration = "1.75 hours"
        
    elif "paper 2 - extended level (25 mixed questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 70
        paper_duration = "2.25 hours"
        
    elif "paper 3 - practical/coursework assessment (20 questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 20
        long_count = 0
        short_marks_each = 3
        total_marks = 60
        paper_duration = "2 hours"
        
    elif "paper 4 - alternative to practical (25 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 5
        total_marks = 49
        paper_duration = "2 hours"
        
    elif "mock igcse examination (full format)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 95
        paper_duration = "2.5 hours"
        
    elif "sample paper - foundation tier (35 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 62
        paper_duration = "2 hours"
        
    elif "sample paper - higher tier (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 7
        total_marks = 90
        paper_duration = "2.5 hours"
        
    elif "pre-examination practice (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 69
        paper_duration = "2 hours"
    
    # Cambridge AS/A Level (Grades 11-12) - 60-100 marks
    elif "as level paper 1 (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 60
        paper_duration = "1.5 hours"
        
    elif "as level paper 2 (30 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 70
        paper_duration = "2 hours"
        
    elif "a level paper 1 (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 7
        total_marks = 90
        paper_duration = "3 hours"
        
    elif "a level paper 2 (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 85
        paper_duration = "3 hours"
        
    elif "a level paper 3 - synoptic (25 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 10
        long_count = 5
        mcq_marks_each = 2
        short_marks_each = 4
        long_marks_each = 10
        total_marks = 110
        paper_duration = "3 hours"
        
    elif "cambridge advanced practice (45 questions)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 110
        paper_duration = "3 hours"
        
    elif "mock as/a level examination (full format)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 103
        paper_duration = "3 hours"
        
    elif "practical assessment paper (20 questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 20
        long_count = 0
        short_marks_each = 4
        total_marks = 80
        paper_duration = "2 hours"
    
    # ========== STATE BOARD PATTERNS (Research-based) ==========
    
    # State Board Primary Classes (1-5) - 30-50 marks
    elif "state pattern primary test (20 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 3
        total_marks = 32
        paper_duration = "2 hours"
        
    elif "monthly assessment paper (15 questions)" in paper_type_lower:
        mcq_count = 8
        short_count = 5
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 3
        total_marks = 24
        paper_duration = "1.5 hours"
        
    elif "quarterly examination (25 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 39
        paper_duration = "2 hours"
        
    elif "half-yearly assessment (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 54
        paper_duration = "2.5 hours"
        
    elif "annual examination format (35 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 62
        paper_duration = "3 hours"
        
    elif "unit test paper (18 questions)" in paper_type_lower:
        mcq_count = 10
        short_count = 6
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 3
        total_marks = 28
        paper_duration = "1.5 hours"
        
    elif "progress evaluation test (22 questions)" in paper_type_lower:
        mcq_count = 12
        short_count = 8
        long_count = 2
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 36
        paper_duration = "2 hours"
    
    # State Board Middle Classes (6-8) - 50-80 marks
    elif "state board format test (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 54
        paper_duration = "2.5 hours"
        
    elif "quarterly assessment paper (25 mcq + 15 short)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 0
        mcq_marks_each = 1
        short_marks_each = 3
        total_marks = 70
        paper_duration = "3 hours"
    
    # State Board SSC/SSLC (Grade 10) - Official 80 marks theory + 20 internal
    elif "ssc board pattern paper 1 (25 mcq + 15 short + 5 long)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 5
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "ssc board pattern paper 2 (20 long answer questions)" in paper_type_lower:
        mcq_count = 0
        short_count = 0
        long_count = 20
        long_marks_each = 4
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "state board mock examination (full format)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "pre-board practice test (35 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 75
        paper_duration = "3 hours"
        
    elif "sample paper - theory format (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "chapter-wise board practice (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 69
        paper_duration = "2.5 hours"
        
    elif "annual board exam pattern (full 80 marks)" in paper_type_lower:
        mcq_count = 20
        short_count = 12
        long_count = 6
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 6
        total_marks = 80
        paper_duration = "3 hours"
        
    elif "model question paper (35 mixed questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 75
        paper_duration = "3 hours"
    
    # State Board HSC/PUC (11-12) - Official 70-100 marks theory + 20-30 internal
    elif "hsc board pattern paper (35 mixed questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 85
        paper_duration = "3 hours"
        
    elif "state higher secondary format (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 95
        paper_duration = "3 hours"
        
    elif "pre-university examination (45 questions)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 105
        paper_duration = "3 hours"
        
    elif "board exam mock test (full format)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 103
        paper_duration = "3 hours"
        
    elif "sample paper - theory + practical (35 + 15)" in paper_type_lower:
        mcq_count = 15
        short_count = 20
        long_count = 15
        mcq_marks_each = 1
        short_marks_each = 2
        long_marks_each = 4
        total_marks = 115
        paper_duration = "3 hours"
        
    elif "term-end assessment (40 questions)" in paper_type_lower:
        mcq_count = 20
        short_count = 15
        long_count = 5
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 7
        total_marks = 90
        paper_duration = "3 hours"
        
    elif "chapter-wise hsc practice (30 questions)" in paper_type_lower:
        mcq_count = 15
        short_count = 12
        long_count = 3
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 8
        total_marks = 75
        paper_duration = "2.5 hours"
        
    elif "model hsc question paper (full 100 marks)" in paper_type_lower:
        mcq_count = 25
        short_count = 15
        long_count = 8
        mcq_marks_each = 1
        short_marks_each = 3
        long_marks_each = 6
        total_marks = 100
        paper_duration = "3 hours"
    
    # ========== FALLBACK PATTERNS ==========
    else:
        # Default fallback based on total questions mentioned in paper type
        if "50" in paper_type_lower:
            mcq_count = 30
            short_count = 15
            long_count = 5
            total_marks = 90
        elif "45" in paper_type_lower:
            mcq_count = 25
            short_count = 15
            long_count = 5
            total_marks = 85
        elif "40" in paper_type_lower:
            mcq_count = 20
            short_count = 15
            long_count = 5
            total_marks = 80
        elif "35" in paper_type_lower:
            mcq_count = 15
            short_count = 15
            long_count = 5
            total_marks = 75
        elif "30" in paper_type_lower:
            mcq_count = 15
            short_count = 12
            long_count = 3
            total_marks = 60
        elif "25" in paper_type_lower:
            mcq_count = 15
            short_count = 8
            long_count = 2
            total_marks = 50
        elif "20" in paper_type_lower:
            mcq_count = 10
            short_count = 8
            long_count = 2
            total_marks = 40
        elif "15" in paper_type_lower:
            mcq_count = 8
            short_count = 5
            long_count = 2
            total_marks = 30
        else:
            # Ultimate fallback
            mcq_count = 20
            short_count = 10
            long_count = 5
            total_marks = 80
    
    return mcq_count, short_count, long_count, mcq_marks_each, short_marks_each, long_marks_each, total_marks, paper_duration

def get_enhanced_question_counts_from_paper_type(paper_type):
    """Enhanced version that returns all paper format details"""
    
    mcq_count, short_count, long_count, mcq_marks_each, short_marks_each, long_marks_each, total_marks, paper_duration = get_question_counts_from_paper_type(paper_type)
    
    return {
        'mcq_count': mcq_count,
        'short_count': short_count,
        'long_count': long_count,
        'mcq_marks_each': mcq_marks_each,
        'short_marks_each': short_marks_each,
        'long_marks_each': long_marks_each,
        'total_marks': total_marks,
        'paper_duration': paper_duration,
        'total_questions': mcq_count + short_count + long_count
    }

def get_ib_paper_types(grade):
    """Legacy function - now uses get_paper_types_by_board_and_grade"""
    return get_paper_types_by_board_and_grade("IB", grade)

def get_igcse_paper_types():
    """Legacy function - now uses get_paper_types_by_board_and_grade"""
    return get_paper_types_by_board_and_grade("Cambridge IGCSE", 10)

# COMPREHENSIVE Subject mapping with complete curriculum standards for ALL 5 BOARDS
def get_subjects_by_board():
    return {
        "CBSE": {
            1: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            2: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            3: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            4: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            5: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            6: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education"],
            7: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education"],
            8: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education"],
            9: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education", "Information Technology"],
            10: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education", "Information Technology"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English Core", "Computer Science", "Economics", "Business Studies", "Accountancy", "Political Science", "Geography", "History", "Psychology", "Physical Education", "Applied Mathematics", "Biotechnology", "Engineering Graphics"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English Core", "Computer Science", "Economics", "Business Studies", "Accountancy", "Political Science", "Geography", "History", "Psychology", "Physical Education", "Applied Mathematics", "Biotechnology", "Engineering Graphics"]
        },
        "ICSE": {
            1: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            2: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            3: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Applications", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            4: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Applications", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            5: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Applications", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            6: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education"],
            7: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education"],
            8: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education"],
            9: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education", "Economics", "Commercial Studies"],
            10: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education", "Economics", "Commercial Studies"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accounts", "Business Studies", "Geography", "History", "Political Science", "Psychology", "Sociology", "Art", "Home Science", "Environmental Science"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accounts", "Business Studies", "Geography", "History", "Political Science", "Psychology", "Sociology", "Art", "Home Science", "Environmental Science"]
        },
        "IB": {
            1: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            2: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            3: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            4: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            5: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            6: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design"],
            7: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design"],
            8: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design"],
            9: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design", "Computer Science"],
            10: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design", "Computer Science"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English Literature", "Economics", "Business Management", "Psychology", "Geography", "History", "Philosophy", "Computer Science", "Visual Arts", "Theatre", "Music", "Film"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English Literature", "Economics", "Business Management", "Psychology", "Geography", "History", "Philosophy", "Computer Science", "Visual Arts", "Theatre", "Music", "Film"]
        },
        "Cambridge IGCSE": {
            1: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            2: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            3: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            4: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            5: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            6: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education", "French", "Spanish"],
            7: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education", "French", "Spanish"],
            8: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education", "French", "Spanish"],
            9: ["Mathematics", "English First Language", "English Literature", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business Studies", "Accounting", "Geography", "History", "Art & Design", "Music", "Physical Education", "French", "Spanish", "Additional Mathematics"],
            10: ["Mathematics", "English First Language", "English Literature", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business Studies", "Accounting", "Geography", "History", "Art & Design", "Music", "Physical Education", "French", "Spanish", "Additional Mathematics"],
            11: ["Mathematics", "Further Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business", "Accounting", "Geography", "History", "Psychology", "Sociology", "Art & Design", "Music", "Physical Education", "English Language", "English Literature"],
            12: ["Mathematics", "Further Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business", "Accounting", "Geography", "History", "Psychology", "Sociology", "Art & Design", "Music", "Physical Education", "English Language", "English Literature"]
        },
        "State Board": {
            1: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            2: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            3: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            4: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            5: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            6: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education"],
            7: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education"],
            8: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education"],
            9: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education", "Vocational Subjects"],
            10: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education", "Vocational Subjects"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accountancy", "Business Studies", "Political Science", "Geography", "History", "Psychology", "Sociology", "Agriculture", "Home Science"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accountancy", "Business Studies", "Political Science", "Geography", "History", "Psychology", "Sociology", "Agriculture", "Home Science"]
        }
    }

# NEW COMPREHENSIVE CURRICULUM TOPICS DATABASE
def get_comprehensive_curriculum_topics():
    """Complete topic database for all subjects, grades, and boards"""
    return {
        "CBSE": {
            # ========== MATHEMATICS ==========
            "Mathematics": {
                1: [
                    # Numbers and Counting
                    "Numbers 1-99", "Counting forwards and backwards", "Number recognition", 
                    "Number names", "Before, After, Between", "Skip counting (2s, 5s, 10s)",
                    "Odd and Even numbers", "Greatest and Smallest numbers",
                    
                    # Basic Operations
                    "Addition (single digit)", "Subtraction (single digit)", "Addition using objects",
                    "Subtraction using objects", "Mental math", "Number stories",
                    
                    # Shapes and Patterns
                    "Basic shapes (Circle, Triangle, Square, Rectangle)", "Shape recognition",
                    "Patterns with shapes", "Patterns with numbers", "Patterns with colors",
                    "Pattern completion", "Making patterns",
                    
                    # Measurement and Comparison
                    "Size comparison (Big/Small, Long/Short, Tall/Short, Thick/Thin)",
                    "Length comparison", "Height comparison", "Weight (Heavy/Light)",
                    "Capacity (More/Less, Full/Empty)", "Temperature (Hot/Cold)",
                    
                    # Money and Time
                    "Coins recognition", "Notes recognition", "Value of coins",
                    "Time concepts (Day/Night, Morning/Evening)", "Days of week",
                    "Today/Yesterday/Tomorrow", "Clock introduction",
                    
                    # Data and Logic
                    "Sorting objects", "Classification", "Data collection",
                    "Simple graphs", "Position (Left/Right, Up/Down, Inside/Outside)"
                ],
                
                2: [
                    # Numbers
                    "Numbers 1-100", "Place Value (Tens and Ones)", "Expanded form",
                    "Number line", "Comparing numbers", "Ordering numbers",
                    "Roman numerals I-X", "Skip counting by 2s, 3s, 5s, 10s",
                    
                    # Operations
                    "Addition with carrying", "Subtraction with borrowing", 
                    "Addition of 2-digit numbers", "Subtraction of 2-digit numbers",
                    "Word problems on addition", "Word problems on subtraction",
                    "Introduction to multiplication", "Multiplication tables 2, 3, 4, 5, 10",
                    "Division as sharing", "Division as grouping",
                    
                    # Geometry
                    "2D shapes properties", "3D shapes (Cube, Sphere, Cylinder, Cone)",
                    "Faces, edges, vertices", "Symmetry introduction", "Lines and curves",
                    "Open and closed figures", "Patterns with shapes",
                    
                    # Measurement
                    "Length (cm, m)", "Weight (kg, g)", "Capacity (L, mL)",
                    "Time (hours, minutes)", "Calendar", "Clock reading",
                    "Money (making amounts)", "Shopping problems",
                    
                    # Data Handling
                    "Pictographs", "Bar graphs", "Data interpretation",
                    "Surveys", "Tallying", "Organizing data"
                ],
                
                3: [
                    # Numbers
                    "Numbers up to 1000", "Place value (Hundreds, Tens, Ones)",
                    "Number names", "Expanded notation", "Comparing 3-digit numbers",
                    "Ordering numbers", "Number patterns", "Roman numerals I-XX",
                    "Rounding to nearest 10", "Rounding to nearest 100",
                    
                    # Operations
                    "Addition of 3-digit numbers", "Subtraction of 3-digit numbers",
                    "Multiplication tables up to 10", "Multiplication by 1-digit numbers",
                    "Division by 1-digit numbers", "Division with remainders",
                    "Word problems with multiple operations", "Estimation",
                    
                    # Fractions
                    "Introduction to fractions", "Half, Quarter, Three-quarters",
                    "Proper fractions", "Unit fractions", "Comparing fractions",
                    "Equivalent fractions", "Adding simple fractions",
                    
                    # Geometry
                    "Lines and line segments", "Angles introduction", "Right angles",
                    "Perpendicular lines", "Parallel lines", "Polygons",
                    "Triangles", "Quadrilaterals", "Circles", "Symmetry",
                    
                    # Measurement
                    "Perimeter", "Area introduction", "Units of measurement",
                    "Converting units", "Time intervals", "Elapsed time",
                    "Money problems", "Profit and loss basics",
                    
                    # Data
                    "Bar graphs with scale", "Reading graphs", "Creating graphs",
                    "Data collection methods", "Probability introduction"
                ],
                
                4: [
                    # Numbers
                    "Numbers up to 10,000", "Place value to ten thousands",
                    "Number names in words", "Comparing large numbers",
                    "Ordering large numbers", "Roman numerals I-L",
                    "Factors", "Multiples", "Prime numbers", "Composite numbers",
                    
                    # Operations
                    "Addition of large numbers", "Subtraction of large numbers",
                    "Multiplication by 2-digit numbers", "Division by 2-digit numbers",
                    "Long division", "Word problems", "Mental math strategies",
                    
                    # Fractions and Decimals
                    "Proper and improper fractions", "Mixed numbers",
                    "Adding and subtracting fractions", "Multiplying fractions",
                    "Introduction to decimals", "Decimal place value",
                    "Comparing decimals", "Adding decimals",
                    
                    # Geometry
                    "Types of angles (Acute, Obtuse, Right)", "Measuring angles",
                    "Types of triangles", "Properties of shapes", "Congruence",
                    "Transformations", "Coordinate geometry basics",
                    
                    # Measurement
                    "Area of rectangles", "Area of squares", "Perimeter formulas",
                    "Volume introduction", "Capacity problems", "Weight problems",
                    "Time problems", "Speed introduction",
                    
                    # Data and Probability
                    "Line graphs", "Pictographs with scale", "Mode and median",
                    "Probability experiments", "Likely and unlikely events"
                ],
                
                5: [
                    # Numbers
                    "Numbers up to 100,000 (Lakhs)", "Large number names",
                    "International number system", "Place value charts",
                    "Rounding large numbers", "Estimation strategies",
                    "Prime factorization", "LCM basics", "HCF basics",
                    
                    # Operations
                    "Operations with large numbers", "Order of operations (BODMAS)",
                    "Word problems with multiple steps", "Mental calculation tricks",
                    "Checking answers", "Approximation",
                    
                    # Fractions and Decimals
                    "Converting mixed numbers", "Operations with fractions",
                    "Decimal operations", "Decimal to fraction conversion",
                    "Percentage introduction", "Finding percentages",
                    "Percentage of quantities", "Simple interest basics",
                    
                    # Geometry
                    "Properties of 2D shapes", "Properties of 3D shapes",
                    "Nets of 3D shapes", "Reflection and rotation",
                    "Coordinate grids", "Scale drawing",
                    
                    # Measurement
                    "Metric conversions", "Imperial units", "Area of triangles",
                    "Volume of cubes", "Surface area introduction",
                    "Time zones", "24-hour clock",
                    
                    # Statistics
                    "Mean (average)", "Range", "Data analysis",
                    "Interpreting graphs", "Creating surveys", "Probability scales"
                ],
                
                6: [
                    # NCERT Official Curriculum
                    "Knowing Our Numbers", "Whole Numbers", "Playing with Numbers",
                    "Basic Geometrical Ideas", "Understanding Elementary Shapes",
                    "Integers", "Fractions", "Decimals", "Data Handling",
                    "Mensuration", "Algebra", "Ratio and Proportion",
                    "Symmetry", "Practical Geometry",
                    
                    # Detailed Topics
                    "Number system", "Large numbers", "Place value",
                    "Operations on whole numbers", "Properties of whole numbers",
                    "Factors and multiples", "Divisibility rules", "Prime and composite",
                    "Common factors", "Common multiples", "HCF and LCM",
                    "Introduction to integers", "Representation on number line",
                    "Addition and subtraction of integers", "Properties of fractions",
                    "Equivalent fractions", "Comparison of fractions",
                    "Addition and subtraction of fractions", "Decimal numbers",
                    "Decimal fractions", "Comparison of decimals"
                ],
                
                7: [
                    # NCERT Official Curriculum
                    "Integers", "Fractions and Decimals", "Data Handling",
                    "Simple Equations", "Lines and Angles", "The Triangle and its Properties",
                    "Congruence of Triangles", "Comparing Quantities", "Rational Numbers",
                    "Practical Geometry", "Perimeter and Area", "Algebraic Expressions",
                    "Exponents and Powers", "Symmetry", "Visualising Solid Shapes",
                    
                    # Detailed Topics
                    "Properties of integers", "Operations on integers",
                    "Multiplication and division of integers", "Operations on fractions",
                    "Multiplication and division of decimals", "Arithmetic mean",
                    "Simple equations in one variable", "Applications of simple equations",
                    "Complementary and supplementary angles", "Linear pair",
                    "Vertically opposite angles", "Properties of triangles",
                    "Median and altitude", "Exterior angle property"
                ],
                
                8: [
                    # NCERT Official Curriculum
                    "Rational Numbers", "Linear Equations in One Variable",
                    "Understanding Quadrilaterals", "Practical Geometry",
                    "Data Handling", "Squares and Square Roots",
                    "Cubes and Cube Roots", "Comparing Quantities",
                    "Algebraic Expressions and Identities", "Mensuration",
                    "Exponents and Powers", "Direct and Inverse Proportions",
                    "Factorisation", "Introduction to Graphs", "Playing with Numbers",
                    
                    # Detailed Topics
                    "Properties of rational numbers", "Representation on number line",
                    "Operations on rational numbers", "Solving linear equations",
                    "Word problems on linear equations", "Properties of quadrilaterals",
                    "Construction of quadrilaterals", "Probability", "Compound interest",
                    "Profit and loss", "Sales tax", "Algebraic identities",
                    "Factorisation of algebraic expressions", "Surface area and volume"
                ],
                
                9: [
                    # NCERT Official Curriculum
                    "Number Systems", "Polynomials", "Coordinate Geometry",
                    "Linear Equations in Two Variables", "Introduction to Euclid's Geometry",
                    "Lines and Angles", "Triangles", "Quadrilaterals",
                    "Areas of Parallelograms and Triangles", "Circles",
                    "Constructions", "Heron's Formula", "Surface Areas and Volumes",
                    "Statistics", "Probability",
                    
                    # Detailed Topics
                    "Real numbers", "Irrational numbers", "Rationalization",
                    "Laws of exponents", "Polynomials in one variable",
                    "Remainder theorem", "Factor theorem", "Factorisation of polynomials",
                    "Cartesian plane", "Plotting points", "Linear equations in two variables",
                    "Graphical solution", "Euclid's axioms and postulates",
                    "Angle sum property", "Congruence of triangles", "Inequalities in triangles"
                ],
                
                10: [
                    # NCERT Official Curriculum
                    "Real Numbers", "Polynomials", "Pair of Linear Equations in Two Variables",
                    "Quadratic Equations", "Arithmetic Progressions", "Triangles",
                    "Coordinate Geometry", "Introduction to Trigonometry",
                    "Some Applications of Trigonometry", "Circles",
                    "Constructions", "Areas Related to Circles", "Surface Areas and Volumes",
                    "Statistics", "Probability",
                    
                    # Detailed Topics
                    "Euclid's division lemma", "Fundamental theorem of arithmetic",
                    "Decimal representation of rational numbers", "Geometric meaning of zeros",
                    "Relationship between zeros and coefficients", "Division algorithm for polynomials",
                    "Algebraic methods of solving linear equations", "Graphical method",
                    "Cross-multiplication method", "Standard form of quadratic equation",
                    "Solution by factorisation", "Solution by completing square",
                    "Quadratic formula", "Nature of roots"
                ],
                
                11: [
                    # NCERT Official Curriculum
                    "Sets", "Relations and Functions", "Trigonometric Functions",
                    "Principle of Mathematical Induction", "Complex Numbers and Quadratic Equations",
                    "Linear Inequalities", "Permutations and Combinations",
                    "Binomial Theorem", "Sequences and Series",
                    "Straight Lines", "Conic Sections", "Introduction to Three Dimensional Geometry",
                    "Limits and Derivatives", "Mathematical Reasoning", "Statistics", "Probability",
                    
                    # Detailed Topics
                    "Types of sets", "Venn diagrams", "Operations on sets",
                    "Types of relations", "Types of functions", "Composition of functions",
                    "Inverse functions", "Trigonometric functions and identities",
                    "Trigonometric equations", "Inverse trigonometric functions",
                    "Mathematical induction", "Complex numbers", "Argand plane",
                    "Polar representation", "Linear inequalities", "Graphical solutions"
                ],
                
                12: [
                    # NCERT Official Curriculum
                    "Relations and Functions", "Inverse Trigonometric Functions",
                    "Matrices", "Determinants", "Continuity and Differentiability",
                    "Applications of Derivatives", "Integrals", "Applications of Integrals",
                    "Differential Equations", "Vector Algebra",
                    "Three Dimensional Geometry", "Linear Programming", "Probability",
                    
                    # Detailed Topics
                    "Types of functions", "Composition of functions", "Inverse functions",
                    "Binary operations", "Inverse trigonometric functions",
                    "Operations on matrices", "Transpose of matrix", "Symmetric matrix",
                    "Skew symmetric matrix", "Invertible matrices", "Determinants",
                    "Properties of determinants", "Cofactors", "Adjoint of matrix",
                    "Cramer's rule", "Continuity", "Differentiability", "Derivatives of functions"
                ]
            },
            
            # ========== ENGLISH ==========
            "English": {
                1: [
                    # NCERT Marigold Book
                    "A Happy Child", "Three Little Pigs", "After a Bath",
                    "The Bubble, the Straw and the Shoe", "One Little Kitten",
                    "Lalu and Peelu", "Once I Saw a Little Bird", "Mittu and the Yellow Mango",
                    "Merry-Go-Round", "Circle", "If I Were an Apple", "Our Tree",
                    "A Kite", "Sundari", "A Little Turtle", "The Tiger and the Mosquito",
                    "Clouds", "Anandi's Rainbow", "Flying Man",
                    
                    # NCERT Raindrops Book  
                    "Clap, Clap, Clap", "One, Two", "The Little Bird", "Bubbles",
                    "Chhotu", "Animals and Birds", "Fruits and Vegetables",
                    
                    # Language Skills
                    "Alphabets A-Z", "Letter recognition", "Letter sounds", "Phonics",
                    "Vowels and consonants", "Capital and small letters",
                    "Simple words", "Sight words", "Rhyming words",
                    "Word formation", "Picture reading", "Story telling",
                    "Simple sentences", "Grammar basics", "Nouns", "Action words"
                ],
                
                2: [
                    # NCERT Marigold Book Units
                    "First Day at School", "Haldi's Adventure", "I am Lucky!",
                    "Banana Talk", "The Naughty Boy", "Curlylocks and the Three Bears",
                    "On My Blackboard I can Draw", "My Red Balloon", "What is in the Mailbox?",
                    "The Grasshopper and the Ant", "Rain", "Storm in the Garden",
                    "Golu Grows a Nose", "I am the Music Man", "Helping",
                    
                    # NCERT Raindrops Units
                    "Action Song", "Funny Bunny", "The Magic Garden", "Yeh hai mera ghar",
                    "Zoo Manners", "The Gingerbread Man", "My Family",
                    
                    # Language Development
                    "Reading comprehension", "Vocabulary building", "Sentence formation",
                    "Story sequence", "Character identification", "Grammar rules",
                    "Punctuation marks", "Singular and plural", "Articles (a, an, the)",
                    "Prepositions", "Question formation", "Creative writing"
                ],
                
                3: [
                    # NCERT Units  
                    "The Magic Garden", "A Little Fish Story", "The Enormous Turnip",
                    "Little by Little", "Trains", "The Balloon Man", "The Yellow Butterfly",
                    "A Game of Chance", "Good Morning", "A Story",
                    "The Magic Words", "Don't Tell", "How Creatures Move",
                    "The Story of the Road", "A Little Tiger in the House",
                    
                    # Language Skills
                    "Reading fluency", "Comprehension skills", "Vocabulary expansion",
                    "Grammar concepts", "Tenses introduction", "Adjectives",
                    "Adverbs", "Conjunctions", "Story writing", "Paragraph writing",
                    "Letter writing", "Diary writing", "Poetry appreciation"
                ],
                
                4: [
                    # NCERT Units
                    "Wake Up!", "Nasruddin's Aim", "A Watering Rhyme", "The Donkey",
                    "The Milkman's Cow", "The Scholars Mother Tongue", "Going to Buy a Book",
                    "The Naughty Boy", "Pinocchio", "A Tiger in the Zoo",
                    "The Wish", "How the Camel Got His Hump", "The Giving Tree",
                    "Hiawatha", "The Fisherman and the Fish",
                    
                    # Advanced Skills
                    "Reading with expression", "Critical thinking", "Character analysis",
                    "Plot understanding", "Theme identification", "Advanced grammar",
                    "Complex sentences", "Reported speech", "Active and passive voice",
                    "Essay writing", "Formal letters", "Application writing"
                ],
                
                5: [
                    # NCERT Units
                    "Wonderful Waste!", "Flying Together", "My Shadow", "Robinson Crusoe",
                    "My Elder Brother", "The Shed", "The Tiny Teacher", "Bring out the Best",
                    "A Snake Charmer's Song", "Class Discussion", "The Little Bully",
                    "Whatif", "Malu Bhalu", "Who I Am", "When I Grow Up",
                    
                    # Language Mastery
                    "Advanced comprehension", "Literary analysis", "Creative expression",
                    "Debate skills", "Presentation skills", "Advanced grammar concepts",
                    "Idioms and phrases", "Proverbs", "Advanced writing skills",
                    "Story composition", "Poem writing", "Speech writing"
                ],
                
                6: [
                    # NCERT Poorvi Book (Updated 2024-25)
                    "Fables and Folk Tales", "Friendship and Trust", "Nature and Environment",
                    "Heroes and Role Models", "Family and Community", "Sports and Games",
                    "Art and Culture", "Science and Discovery", "Adventure and Exploration",
                    "Values and Ethics",
                    
                    # Language Components
                    "Reading comprehension", "Vocabulary development", "Grammar and usage",
                    "Writing skills", "Speaking and listening", "Literature appreciation",
                    "Creative writing", "Formal writing", "Informal writing"
                ],
                
                7: [
                    # NCERT Honeycomb and An Alien Hand
                    "Three Questions", "A Gift of Chappals", "Gopal and the Hilsa Fish",
                    "The Ashes That Made Trees Bloom", "Quality", "Expert Detectives",
                    "The Invention of Vita-Wonk", "Fire: Friend and Foe",
                    "A Bicycle in Good Repair", "The Story of Cricket",
                    "Golu Grows a Nose", "I Want Something in a Cage",
                    "Chandni", "The Bear Story", "A Tiger in the House",
                    
                    # Supplementary Reader
                    "The Tiny Teacher", "Bringing up Kari", "The Desert", "The Cop and the Anthem",
                    "Golu Grows a Nose", "The Ashes That Made Trees Bloom"
                ],
                
                8: [
                    # NCERT Honeydew and It So Happened
                    "The Best Christmas Present in the World", "The Tsunami",
                    "Glimpses of the Past", "Bepin Choudhury's Lapse of Memory",
                    "The Summit Within", "This is Jody's Fawn", "A Visit to Cambridge",
                    "A Short Monsoon Diary", "The Great Stone Face I", "The Great Stone Face II",
                    
                    # Poetry
                    "The Ant and the Cricket", "Geography Lesson", "Macavity: The Mystery Cat",
                    "The Last Bargain", "The School Boy", "The Duck and the Kangaroo",
                    "When I Set Out for Lyonnesse", "On the Grasshopper and Cricket"
                ],
                
                9: [
                    # NCERT Beehive and Moments
                    "The Fun They Had", "The Sound of Music", "The Little Girl",
                    "A Truly Beautiful Mind", "The Snake and the Mirror", "My Childhood",
                    "Packing", "Reach for the Top", "The Bond of Love",
                    "Kathmandu", "If I Were You",
                    
                    # Poetry
                    "The Road Not Taken", "Wind", "Rain on the Roof", "The Lake Isle of Innisfree",
                    "A Legend of the Northland", "No Men Are Foreign", "The Duck and the Kangaroo",
                    "On Killing a Tree", "The Snake Trying"
                ],
                
                10: [
                    # NCERT First Flight and Footprints
                    "A Letter to God", "Nelson Mandela: Long Walk to Freedom",
                    "Two Stories about Flying", "From the Diary of Anne Frank",
                    "The Hundred Dresses I", "The Hundred Dresses II", "Glimpses of India",
                    "Mijbil the Otter", "Madam Rides the Bus", "The Sermon at Benares",
                    "The Proposal",
                    
                    # Poetry  
                    "Dust of Snow", "Fire and Ice", "A Tiger in the Zoo",
                    "How to Tell Wild Animals", "The Ball Poem", "Amanda!",
                    "Animals", "The Trees", "Fog", "The Tale of Custard the Dragon",
                    "For Anne Gregory"
                ],
                
                11: [
                    # NCERT Hornbill and Snapshots
                    "The Portrait of a Lady", "We're Not Afraid to Die",
                    "Discovering Tut: The Saga Continues", "Landscape of the Soul",
                    "The Ailing Planet: The Green Movement's Role", "The Browning Version",
                    "Adventure", "Silk Road",
                    
                    # Poetry
                    "A Photograph", "The Laburnum Top", "The Voice of the Rain",
                    "Childhood", "Father to Son",
                    
                    # Supplementary
                    "The Summer of the Beautiful White Horse", "The Address",
                    "Ranga's Marriage", "Albert Einstein at School", "Mother's Day",
                    "The Ghat of the Only World", "Birth"
                ],
                
                12: [
                    # NCERT Flamingo and Vistas
                    "The Last Lesson", "Lost Spring", "Deep Water", "The Rattrap",
                    "Indigo", "Poets and Pancakes", "The Interview", "Going Places",
                    
                    # Poetry
                    "My Mother at Sixty-six", "An Elementary School Classroom in a Slum",
                    "Keeping Quiet", "A Thing of Beauty", "A Roadside Stand", "Aunt Jennifer's Tigers",
                    
                    # Supplementary  
                    "The Third Level", "The Tiger King", "The Enemy", "Should Wizard Hit Mommy?",
                    "On the Face of It", "Evans Tries an O-level", "Memories of Childhood"
                ]
            },
            
            # ========== HINDI ==========
            "Hindi": {
                1: [
                    # NCERT Sarangi (Updated 2024-25)
                    "अम्मा कहती हैं", "बारिश", "आम की टोकरी", "पत्ते ही पत्ते",
                    "पकौड़ी", "छुक-छुक गाड़ी", "रसोईघर", "चूहो! बिल्ली आई",
                    "बंदर और गिलहरी", "पेड़", "पानी रे पानी", "बंदर बाँट",
                    "मिर्च का मजा", "खिचड़ी", "मैं भी", "लालू और पीलू",
                    "चकई के चकदुम", "छोटी का कमाल", "चार चने",
                    "भगदड़", "हलीम चला चाँद पर", "हाथी चल्लम चल्लम",
                    "सर्दी", "गर्मी", "बसंत",
                    
                    # व्याकरण (Grammar)
                    "वर्णमाला", "स्वर और व्यंजन", "मात्राएँ", "शब्द निर्माण",
                    "वाक्य निर्माण", "संज्ञा", "सर्वनाम", "विशेषण", "क्रिया"
                ],
                
                2: [
                    # NCERT Rimjhim
                    "ऊँट चला", "भालू ने खेली फुटबॉल", "म्याऊँ, म्याऊँ!",
                    "अधिक बलवान कौन?", "दोस्त की मदद", "बहुत हुआ",
                    "मेरी किताब", "तितली और कली", "बुलबुल", "मीरा बहन और बाघ",
                    "सूरज जल्दी आना जी", "छत पर", "सात पूँछ का चूहा",
                    "स्वतंत्रता दिवस", "मन करता है", "घर", "संतरे का पेड़",
                    "भगवान के डाकिए", "हाथी", "आगे और पीछे", "हल्दी दाई",
                    
                    # व्याकरण
                    "वर्ण विच्छेद", "शब्द जोड़ना", "वाक्य पूरा करना",
                    "विपरीत शब्द", "तुकांत शब्द", "लिंग", "वचन"
                ],
                
                3: [
                    # NCERT Rimjhim
                    "कठपुतली", "कभी न कभी", "नेहा का प्रसंग", "भालू का सपना",
                    "सास-बहू", "वह सुबह कभी तो आएगी", "मैंने देखा एक बूँद",
                    "रक्त और हमारा शरीर", "घर में घुसा चोर", "चुपके-चुपके",
                    "सीता का सपना", "हमारा मुल्क भारत", "समझी सी समझ",
                    "मंत्र", "रिद्धि हुई चतुर", "मैंने पिताजी की मदद की",
                    "चित्रकार", "सफ़र", "घरवाली पहेली",
                    
                    # व्याकरण
                    "संधि", "उपसर्ग", "प्रत्यय", "समानार्थी शब्द",
                    "विलोम शब्द", "मुहावरे", "कहानी लेखन", "पत्र लेखन"
                ],
                
                4: [
                    # NCERT Rimjhim  
                    "मन के भोले-भाले बादल", "जैसा सवाल वैसा जवाब",
                    "किरमिच की गेंद", "पापा जब बच्चे थे", "दोस्त की पोशाक",
                    "नाव बनाओ नाव बनाओ", "दान का हिसाब", "कौन?",
                    "स्वतंत्रता की ओर", "थप्प रोटी थप्प दाल", "पढ़क्कू की सूझ",
                    "सुनीता की पहिया कुर्सी", "हुदहुद", "मुफ़्त ही मुफ़्त",
                    
                    # व्याकरण
                    "छंद", "अलंकार", "तत्सम-तद्भव", "देशज-विदेशी शब्द",
                    "काल", "वाच्य", "निबंध लेखन", "संवाद लेखन"
                ],
                
                5: [
                    # NCERT Rimjhim
                    "राख की रस्सी", "फसलों के त्योहार", "खुशबू रचते हैं हाथ",
                    "नन्हा फनकार", "जहाँ चाह वहाँ राह", "चिट्ठी का सफर",
                    "डाकिया की कहानी", "वे दिन भी क्या दिन थे", "एक माँ की बेबसी",
                    "एक दिन की बादशाहत", "चावल की रोटियाँ", "गुरु और चेला",
                    "स्वामी की दादी", "बाघ आया उस रात", "बिशन की दिलेरी",
                    "पानी रे पानी", "छोटी सी हमारी नदी", "इरकी की खोज",
                    
                    # व्याकरण
                    "वाक्य विश्लेषण", "पद परिचय", "रचना के आधार पर वाक्य भेद",
                    "अर्थ के आधार पर वाक्य भेद", "औपचारिक पत्र", "अनौपचारिक पत्र"
                ],
                
                6: [
                    # NCERT Malhar (Updated 2024-25)
                    "प्रकृति और पर्यावरण", "मित्रता और विश्वास", "पारिवारिक रिश्ते",
                    "साहस और वीरता", "त्योहार और उत्सव", "कला और संस्कृति",
                    "विज्ञान और खोज", "रोमांच और साहसिक कार्य", "मूल्य और नैतिकता",
                    
                    # व्याकरण
                    "भाषा और व्याकरण", "शब्द भेद", "वाक्य निर्माण",
                    "रचनात्मक लेखन", "औपचारिक लेखन", "अनौपचारिक लेखन"
                ],
                
                7: [
                    # NCERT Durva
                    "हम पंछी उन्मुक्त गगन के", "दादी माँ", "हिमालय की बेटियाँ",
                    "कठपुतली", "मिठाईवाला", "रक्त और हमारा शरीर",
                    "पापा खो गए", "शाम-एक किसान", "चिड़िया की बच्ची",
                    "अपूर्व अनुभव", "रहीम के दोहे", "कंचा",
                    "एक तिनका", "खुशबू रचते हैं हाथ", "मैं सबसे छोटी होऊं",
                    
                    # व्याकरण
                    "संधि विच्छेद", "धातु रूप", "शब्द रूप", "वाक्य शुद्धीकरण",
                    "विराम चिह्न", "पारिभाषिक शब्दावली"
                ],
                
                8: [
                    # NCERT Durva
                    "गुड़िया", "दो गोरैया", "चिट्ठियों में यूरोप", "ओस",
                    "नाटक में नाटक", "सागर यात्रा", "उठ किसान ओ", "सस्ते का चक्कर",
                    "एह! उदंती", "बच्चे काम पर जा रहे हैं", "फसल", "खेती की भाषा",
                    
                    # व्याकरण
                    "वाच्य परिवर्तन", "कारक", "सामासिक पद", "उपवाक्य",
                    "अशुद्ध वाक्य संशोधन", "मुहावरे और लोकोक्तियाँ"
                ],
                
                9: [
                    # NCERT Kshitij and Kritika
                    "दो बैलों की कथा", "ल्हासा की ओर", "उपभोक्तावाद की संस्कृति",
                    "साँवले सपनों की याद", "नाना साहब की पुत्री देवी मैना को भस्म कर दिया गया",
                    "प्रेमचंद के फटे जूते", "मेरे बचपन के दिन", "एक कुत्ता और एक मैना",
                    
                    # काव्य
                    "सखी", "वाख", "सवैये", "कैदी और कोकिला", "ग्राम श्री",
                    "चंद्र गहना से लौटती बेर", "मेघ आए", "यमराज की दिशा",
                    "बच्चे काम पर जा रहे हैं"
                ],
                
                10: [
                    # NCERT Kshitij and Kritika  
                    "सूरदास के पद", "तुलसीदास के पद", "देव के सवैये",
                    "जयशंकर प्रसाद", "सूर्यकांत त्रिपाठी 'निराला'", "नागार्जुन",
                    "गिरिजा कुमार माथुर", "ऋतुराज", "मंगलेश डबराल",
                    "स्वयं प्रकाश", "फणीश्वरनाथ रेणु",
                    
                    # गद्य
                    "नेताजी का चश्मा", "बालगोबिन भगत", "लखनवी अंदाज",
                    "मानवीय करुणा की दिव्य चमक", "एक कहानी यह भी",
                    "स्त्री-शिक्षा के विरोधी कुतर्कों का खंडन", "नौबतखाने में इबादत",
                    "संस्कृति"
                ],
                
                11: [
                    # NCERT Antra and Antral
                    "प्रेमचंद", "बिस्मिल्लाह खान", "फणीश्वरनाथ रेणु", "शेखर जोशी",
                    "निर्मल वर्मा", "रघुवीर सहाय", "ओम थानवी", "हरिशंकर परसाई",
                    "निदा फाजली", "कमलेश्वर",
                    
                    # काव्य
                    "मीराबाई", "तुलसीदास", "सूरदास", "बिहारी", "केशवदास",
                    "घनानंद", "भूषण", "आचार्य रामचंद्र शुक्ल"
                ],
                
                12: [
                    # NCERT Antra and Antral
                    "हरिशंकर परसाई", "श्रीलाल शुक्ल", "यतीन्द्र मिश्र", "भगवतशरण उपाध्याय",
                    "शहीद भगतसिंह", "निर्मल वर्मा", "काशीनाथ सिंह", "चंद्रधर शर्मा गुलेरी",
                    
                    # काव्य
                    "सूरयकांत त्रिपाठी 'निराला'", "मुक्तिबोध", "शमशेर बहादुर सिंह",
                    "सर्वेश्वर दयाल सक्सेना", "धूमिल", "गजानन माधव मुक्तिबोध"
                ]
            },
            
            # ========== SCIENCE ==========
            "Science": {
                1: [
                    # NCERT Looking Around
                    "My Body and I", "Parts of the body", "Five senses", "Sense organs",
                    "Taking care of my body", "Keeping clean", "Good habits", "Bad habits",
                    
                    "Living and Non-living Things", "Characteristics of living things",
                    "Things around us", "Natural and man-made things", "Useful and harmful things",
                    
                    "Plants Around Us", "Parts of plants", "Different types of plants",
                    "Trees, herbs, shrubs", "Uses of plants", "Taking care of plants",
                    
                    "Animals Around Us", "Wild and domestic animals", "Animals and their babies",
                    "Animals and their homes", "Animals and their food", "Uses of animals",
                    "Sounds of animals", "Taking care of animals",
                    
                    "Food We Eat", "Different types of food", "Healthy food", "Junk food",
                    "Food from plants", "Food from animals", "Eating habits",
                    
                    "Water", "Uses of water", "Sources of water", "Clean and dirty water",
                    "Saving water", "Water cycle basics",
                    
                    "My Family", "Family members", "Family relationships", "Helping family",
                    "Family traditions", "Family rules"
                ],
                
                2: [
                    # NCERT Looking Around
                    "Our Body", "Growing and changing", "Exercise and rest", "Staying healthy",
                    "Safety rules", "First aid basics", "Good and bad touch",
                    
                    "Living and Non-living", "Movement in living things", "Growth in living things",
                    "Need for food and water", "Reproduction basics", "Death and birth",
                    
                    "Plants", "Life cycle of plants", "Seeds and plants", "How plants grow",
                    "What plants need", "Medicinal plants", "Plant products",
                    
                    "Animals", "How animals move", "How animals breathe", "Animal homes",
                    "Animal protection", "Migration", "Hibernation",
                    "Classification of animals (birds, mammals, insects, fish, reptiles)",
                    
                    "Food", "Balanced diet", "Food groups", "Cooking food", "Food preservation",
                    "Food chain introduction", "Where does food come from",
                    
                    "Water", "States of water", "Water cycle", "Rain", "Floods and droughts",
                    "Water pollution", "Water conservation",
                    
                    "Air", "Air is everywhere", "Wind", "Uses of air", "Air pollution",
                    "Breathing", "Fresh air",
                    
                    "Weather", "Hot and cold", "Rainy season", "Summer season", "Winter season",
                    "Clothes for different weather", "Weather changes",
                    
                    "Safety and First Aid", "Safety at home", "Road safety", "Safety rules",
                    "Emergency situations", "People who help us"
                ],
                
                3: [
                    # NCERT Looking Around
                    "Our Body", "Digestive system basics", "Breathing and lungs", "Heart and blood",
                    "Bones and muscles", "Brain and nervous system", "Taking care of body",
                    
                    "Living and Non-living", "Characteristics of living things", "Life processes",
                    "Interdependence", "Environment and living things",
                    
                    "Plants", "Types of roots", "Types of stems", "Types of leaves",
                    "Flowers and fruits", "Dispersal of seeds", "Photosynthesis introduction",
                    "Respiration in plants", "Transpiration",
                    
                    "Animals", "Classification of animals", "Vertebrates and invertebrates",
                    "Mammals, birds, reptiles, amphibians, fish", "Insects", "Life cycles",
                    "Food chains", "Herbivores, carnivores, omnivores",
                    
                    "Food", "Sources of food", "Food from plants", "Food from animals",
                    "Nutritious food", "Food preservation methods", "Food adulteration",
                    
                    "Housing and Clothing", "Types of houses", "Materials for building",
                    "Ventilation", "Types of clothes", "Materials for clothes",
                    "Care of clothes",
                    
                    "Transport and Communication", "Means of transport", "Land transport",
                    "Water transport", "Air transport", "Evolution of transport",
                    "Means of communication", "Evolution of communication"
                ],
                
                4: [
                    # NCERT Looking Around
                    "Food", "Food tests", "Nutrients in food", "Vitamins and minerals",
                    "Deficiency diseases", "Food poisoning", "Food hygiene",
                    
                    "Clothing", "Plant fibres", "Animal fibres", "Spinning", "Weaving",
                    "Different fabrics", "Care of clothes",
                    
                    "Housing", "Building materials", "Earthquake-safe buildings", "Ventilation",
                    "Different types of roofs", "Slums", "Good housing",
                    
                    "Water", "Water cycle", "Groundwater", "Wells", "Tube wells",
                    "Water treatment", "Water-borne diseases", "Water harvesting",
                    
                    "Travel and Transport", "History of transport", "Engine and fuel",
                    "Pollution due to vehicles", "Public transport", "Modern vehicles",
                    
                    "The World of Plants", "Root modifications", "Stem modifications",
                    "Leaf modifications", "Flower structure", "Pollination", "Fertilization",
                    "Seed formation", "Seed dispersal",
                    
                    "The World of Animals", "Animal adaptations", "Animal migration",
                    "Animal behavior", "Life cycles of insects", "Metamorphosis",
                    "Animals and their uses",
                    
                    "Birds", "Types of birds", "Bird beaks and feet", "Bird migration",
                    "Bird nests", "Bird calls", "Endangered birds"
                ],
                
                5: [
                    # NCERT Looking Around
                    "Food and Health", "Nutrients and their functions", "Malnutrition",
                    "Food preservation", "Food adulteration", "Organic farming",
                    
                    "Clothing", "History of clothing", "Synthetic fibres", "Plastic",
                    "Environmental impact", "Reduce, reuse, recycle",
                    
                    "Housing", "Traditional building materials", "Modern building materials",
                    "Eco-friendly buildings", "Smart homes", "Architecture",
                    
                    "Water", "Water management", "Dams", "Canals", "Irrigation",
                    "Water scarcity", "Water conflicts", "Watershed management",
                    
                    "Travel and Transport", "GPS", "Traffic rules", "Fuel efficiency",
                    "Electric vehicles", "Future of transport",
                    
                    "Plants", "Classification of plants", "Plant kingdom", "Photosynthesis",
                    "Respiration in plants", "Plant diseases", "Medicinal plants",
                    
                    "Animals", "Animal kingdom", "Classification", "Animal behavior",
                    "Endangered species", "Wildlife conservation", "Zoos and sanctuaries",
                    
                    "Birds", "Bird watching", "Bird photography", "Bird conservation",
                    
                    "Our Environment", "Ecosystem", "Food webs", "Pollution",
                    "Conservation", "Natural resources", "Renewable and non-renewable resources"
                ],
                
                6: [
                    # NCERT Official Chapters
                    "Food: Where Does it Come From?", "Components of Food", "Fibre to Fabric",
                    "Sorting Materials into Groups", "Separation of Substances", "Changes Around Us",
                    "Getting to Know Plants", "Body Movements", "The Living Organisms and Their Surroundings",
                    "Motion and Measurement of Distances", "Light, Shadows and Reflections",
                    "Electricity and Circuits", "Fun with Magnets", "Water", "Air Around Us",
                    "Garbage In, Garbage Out",
                    
                    # Detailed Topics
                    "Food sources", "Plant and animal products", "Ingredients and nutrients",
                    "Balanced diet", "Deficiency diseases", "Natural and synthetic fibres",
                    "Cotton to fabric", "Jute", "Properties of materials", "Metals and non-metals",
                    "Soluble and insoluble", "Transparent and opaque", "Hard and soft",
                    "Handpicking", "Winnowing", "Sieving", "Magnetic separation",
                    "Filtration", "Evaporation", "Condensation", "Reversible and irreversible changes",
                    "Physical and chemical changes"
                ],
                
                7: [
                    # NCERT Official Chapters
                    "Nutrition in Plants", "Nutrition in Animals", "Fibre to Fabric",
                    "Heat", "Acids, Bases and Salts", "Physical and Chemical Changes",
                    "Weather, Climate and Adaptations of Animals to Climate",
                    "Winds, Storms and Cyclones", "Soil", "Respiration in Organisms",
                    "Transportation in Animals and Plants", "Reproduction in Plants",
                    "Motion and Time", "Electric Current and its Effects",
                    "Light", "Water: A Precious Resource", "Forests: Our Lifeline",
                    "Wastewater Story",
                    
                    # Detailed Topics
                    "Photosynthesis", "Symbiosis", "Saprotrophs", "Parasites",
                    "Types of nutrition", "Digestive system", "Digestion process",
                    "Wool", "Silk", "Temperature", "Heat transfer", "Clinical thermometer",
                    "Laboratory thermometer", "Indicators", "Neutralization", "Acids in daily life",
                    "Rusting", "Crystallization", "Climate change", "Animal adaptations"
                ],
                
                8: [
                    # NCERT Official Chapters
                    "Crop Production and Management", "Microorganisms: Friend and Foe",
                    "Synthetic Fibres and Plastics", "Materials: Metals and Non-Metals",
                    "Coal and Petroleum", "Combustion and Flame",
                    "Conservation of Plants and Animals", "Cell — Structure and Functions",
                    "Reproduction in Animals", "Reaching the Age of Adolescence",
                    "Force and Pressure", "Friction", "Sound",
                    "Chemical Effects of Electric Current", "Some Natural Phenomena",
                    "Light", "Stars and the Solar System", "Pollution of Air and Water",
                    
                    # Detailed Topics
                    "Agricultural practices", "Crop improvement", "Food storage",
                    "Useful microorganisms", "Harmful microorganisms", "Food preservation",
                    "Antibiotics", "Vaccines", "Types of synthetic fibres", "Plastics",
                    "Biodegradable and non-biodegradable", "Physical properties of metals",
                    "Chemical properties of metals", "Uses of metals", "Fossil fuels",
                    "Natural gas", "Combustible and non-combustible substances"
                ],
                
                9: [
                    # NCERT Official Chapters
                    "Matter in Our Surroundings", "Is Matter Around Us Pure",
                    "Atoms and Molecules", "Structure of the Atom",
                    "The Fundamental Unit of Life", "Tissues",
                    "Diversity in Living Organisms", "Motion", "Force and Laws of Motion",
                    "Gravitation", "Work and Energy", "Sound",
                    "Why Do We Fall Ill", "Natural Resources", "Improvement in Food Resources",
                    
                    # Detailed Topics
                    "States of matter", "Kinetic theory", "Evaporation", "Sublimation",
                    "Pure substances", "Mixtures", "Solutions", "Suspensions", "Colloids",
                    "Separation techniques", "Dalton's atomic theory", "Molecular formula",
                    "Mole concept", "Discovery of electrons", "Discovery of protons",
                    "Discovery of neutrons", "Atomic models", "Cell theory", "Cell organelles",
                    "Prokaryotes and eukaryotes", "Plant tissues", "Animal tissues"
                ],
                
                10: [
                    # NCERT Official Chapters
                    "Chemical Reactions and Equations", "Acids, Bases and Salts",
                    "Metals and Non-metals", "Carbon and its Compounds",
                    "Periodic Classification of Elements", "Life Processes",
                    "Control and Coordination", "How do Organisms Reproduce?",
                    "Heredity and Evolution", "Light — Reflection and Refraction",
                    "Electricity", "Magnetic Effects of Electric Current",
                    "Our Environment", "Management of Natural Resources",
                    
                    # Detailed Topics
                    "Types of chemical reactions", "Balancing equations", "Oxidation and reduction",
                    "pH scale", "Acids and bases in daily life", "Activity series of metals",
                    "Extraction of metals", "Corrosion", "Alloys", "Covalent compounds",
                    "Functional groups", "Soap and detergents", "Mendeleev's periodic table",
                    "Modern periodic table", "Periodic properties", "Respiration", "Circulation",
                    "Excretion", "Nervous system", "Hormones", "Reproduction in plants and animals"
                ]
            },
            
            # ========== SOCIAL SCIENCE ==========
            "Social Science": {
                6: [
                    # History - Our Pasts
                    "What, Where, How and When?", "From Hunting-Gathering to Growing Food",
                    "In the Earliest Cities", "What Books and Burials Tell Us",
                    "Kingdoms, Kings and an Early Republic", "New Questions and Ideas",
                    "Ashoka, the Emperor Who Gave Up War", "Vital Villages, Thriving Towns",
                    "Traders, Kings and Pilgrims", "New Empires and Kingdoms",
                    "Buildings, Paintings and Books",
                    
                    # Geography - The Earth: Our Habitat
                    "The Earth in the Solar System", "Globe: Latitudes and Longitudes",
                    "Motions of the Earth", "Maps", "Major Domains of the Earth",
                    "Major Landforms of the Earth", "Our Country — India",
                    "India: Climate, Vegetation and Wildlife",
                    
                    # Civics - Social and Political Life
                    "Understanding Diversity", "Diversity and Discrimination",
                    "What is Government?", "Key Elements of a Democratic Government",
                    "Panchayati Raj", "Rural Administration", "Urban Administration",
                    "Rural Livelihoods", "Urban Livelihoods"
                ],
                
                7: [
                    # History - Our Pasts
                    "Tracing Changes Through a Thousand Years", "New Kings and Kingdoms",
                    "The Delhi Sultans", "The Mughal Empire", "Rulers and Buildings",
                    "Towns, Traders and Craftspersons", "Tribes, Nomads and Settled Communities",
                    "Devotional Paths to the Divine", "The Making of Regional Cultures",
                    "Eighteenth-Century Political Formations",
                    
                    # Geography - Our Environment
                    "Environment", "Inside Our Earth", "Our Changing Earth",
                    "Air", "Water", "Natural Vegetation and Wildlife",
                    "Human Environment — Settlement, Transport and Communication",
                    "Human Environment — Interactions",
                    
                    # Civics - Social and Political Life
                    "On Equality", "Role of the Government in Health",
                    "How the State Government Works", "Growing up as Boys and Girls",
                    "Women Change the World", "Understanding Media",
                    "Understanding Advertising", "Markets Around Us",
                    "A Shirt in the Market"
                ],
                
                8: [
                    # History - Our Pasts
                    "How, When and Where", "From Trade to Territory",
                    "Ruling the Countryside", "Tribals, Dikus and the Vision of a Golden Age",
                    "When People Rebel", "Colonialism and the City",
                    "Weavers, Iron Smelters and Factory Owners", "Civilising the 'Native', Educating the Nation",
                    "Women, Caste and Reform", "The Changing World of Visual Arts",
                    "The Making of the National Movement: 1870s–1947",
                    "India After Independence",
                    
                    # Geography - Resources and Development
                    "Resources", "Land, Soil, Water, Natural Vegetation and Wildlife Resources",
                    "Mineral and Power Resources", "Agriculture", "Industries",
                    "Human Resources",
                    
                    # Civics - Social and Political Life
                    "The Indian Constitution", "Understanding Secularism",
                    "Why Do We Need a Parliament?", "Understanding Laws",
                    "Judiciary", "Understanding Our Criminal Justice System",
                    "Understanding Marginalisation", "Confronting Marginalisation",
                    "Public Facilities", "Law and Social Justice"
                ],
                
                9: [
                    # History - India and the Contemporary World
                    "The French Revolution", "Socialism in Europe and the Russian Revolution",
                    "Nazism and the Rise of Hitler", "Forest Society and Colonialism",
                    "Pastoralists in the Modern World",
                    
                    # Geography - Contemporary India
                    "India — Size and Location", "Physical Features of India",
                    "Drainage", "Climate", "Natural Vegetation and Wildlife",
                    "Population",
                    
                    # Political Science - Democratic Politics
                    "What is Democracy? Why Democracy?", "Constitutional Design",
                    "Electoral Politics", "Working of Institutions",
                    "Democratic Rights",
                    
                    # Economics
                    "The Story of Village Palampur", "People as Resource",
                    "Poverty as a Challenge", "Food Security in India"
                ],
                
                10: [
                    # History - India and the Contemporary World
                    "The Rise of Nationalism in Europe", "The Nationalist Movement in Indo-China",
                    "Nationalism in India", "The Making of a Global World",
                    "The Age of Industrialisation", "Print Culture and the Modern World",
                    
                    # Geography - Contemporary India
                    "Resources and Development", "Forest and Wildlife Resources",
                    "Water Resources", "Agriculture", "Minerals and Energy Resources",
                    "Manufacturing Industries", "Lifelines of National Economy",
                    
                    # Political Science - Democratic Politics
                    "Power-sharing", "Federalism", "Democracy and Diversity",
                    "Gender, Religion and Caste", "Popular Struggles and Movements",
                    "Political Parties", "Outcomes of Democracy", "Challenges to Democracy",
                    
                    # Economics - Understanding Economic Development
                    "Development", "Sectors of the Indian Economy",
                    "Money and Credit", "Globalisation and the Indian Economy",
                    "Consumer Rights"
                ]
            },
            
            # ========== PHYSICAL EDUCATION ==========
            "Physical Education": {
                1: [
                    "Body parts and their functions", "Basic movements", "Walking", "Running",
                    "Jumping", "Hopping", "Skipping", "Marching", "Balance activities",
                    "Simple exercises", "Warm-up activities", "Cool-down activities",
                    "Basic sports introduction", "Ball activities", "Games with equipment",
                    "Traditional games", "Hygiene habits", "Health habits", "Safety rules"
                ],
                
                2: [
                    "Fundamental motor skills", "Locomotor movements", "Non-locomotor movements",
                    "Manipulative skills", "Coordination exercises", "Balance beam activities",
                    "Simple gymnastics", "Dance movements", "Rhythmic activities",
                    "Team games", "Individual games", "Water safety", "Personal hygiene",
                    "Nutrition basics", "Rest and sleep", "Exercise benefits"
                ],
                
                3: [
                    "Advanced locomotor skills", "Sports skills introduction", "Throwing",
                    "Catching", "Kicking", "Striking", "Basic athletics", "Track events",
                    "Field events", "Swimming basics", "Cycling", "Team building activities",
                    "Leadership qualities", "Fair play", "Sportsmanship", "First aid basics",
                    "Injury prevention", "Fitness components", "Strength", "Flexibility"
                ],
                
                4: [
                    "Complex movement patterns", "Sport-specific skills", "Basketball basics",
                    "Football basics", "Cricket basics", "Volleyball basics", "Hockey basics",
                    "Badminton basics", "Table tennis basics", "Tennis basics", "Golf basics",
                    "Swimming strokes", "Diving", "Martial arts introduction", "Yoga basics",
                    "Meditation", "Stress management", "Goal setting", "Performance tracking"
                ],
                
                5: [
                    "Advanced sports techniques", "Game strategies", "Tactics", "Rules and regulations",
                    "Officiating", "Scoring systems", "Tournament organization", "Sports psychology",
                    "Mental preparation", "Concentration techniques", "Visualization",
                    "Team dynamics", "Communication skills", "Leadership development",
                    "Fitness testing", "Training methods", "Periodization", "Recovery techniques"
                ],
                
                6: [
                    "Sports science introduction", "Exercise physiology", "Anatomy basics",
                    "Biomechanics", "Nutrition for athletes", "Hydration", "Energy systems",
                    "Training principles", "Adaptation", "Progressive overload", "Specificity",
                    "Recovery", "Injury management", "Rehabilitation", "Sports medicine",
                    "Performance analysis", "Technology in sports", "Ethics in sports",
                    "Doping awareness", "Fair play values"
                ],
                
                7: [
                    "Advanced fitness concepts", "Cardiovascular fitness", "Muscular fitness",
                    "Flexibility training", "Body composition", "Fitness assessment",
                    "Exercise prescription", "Training program design", "Periodization models",
                    "Skill acquisition", "Motor learning", "Practice methods", "Feedback",
                    "Sports specialization", "Talent identification", "Youth sports",
                    "Psychological skills", "Motivation", "Confidence building"
                ],
                
                8: [
                    # Key Concepts (IB MYP Style)
                    "Change", "Communication", "Relationships",
                    
                    # Physical Fitness Components
                    "Cardiovascular Endurance", "Muscular Strength", "Muscular Endurance",
                    "Flexibility", "Body Composition", "Power", "Speed", "Agility",
                    "Balance", "Coordination", "Reaction Time",
                    
                    # Training Principles
                    "FITT Principle", "Progressive Overload", "Specificity", "Reversibility",
                    "Individual Differences", "Recovery", "Adaptation", "Periodization",
                    
                    # Exercise Science
                    "Energy Systems", "Aerobic System", "Anaerobic Alactic System",
                    "Anaerobic Lactic System", "Heart Rate", "VO2 Max", "Lactate Threshold",
                    "Oxygen Debt", "EPOC", "Training Zones",
                    
                    # Nutrition and Health
                    "Macronutrients", "Carbohydrates", "Proteins", "Fats", "Micronutrients",
                    "Vitamins", "Minerals", "Hydration", "Pre-exercise Nutrition",
                    "During-exercise Nutrition", "Post-exercise Nutrition", "Recovery Nutrition",
                    "Sports Supplements", "Weight Management", "Eating Disorders",
                    "Healthy Lifestyle", "Sleep and Recovery", "Stress Management",
                    
                    # Movement and Skills
                    "Fundamental Movement Skills", "Locomotor Skills", "Stability Skills",
                    "Manipulative Skills", "Motor Learning", "Skill Acquisition",
                    "Practice Methods", "Feedback", "Movement Patterns", "Technique Development",
                    "Performance Analysis", "Biomechanical Analysis",
                    
                    # Team Sports
                    "Football", "Basketball", "Volleyball", "Hockey", "Rugby", "Cricket",
                    "Team Tactics", "Team Strategies", "Roles and Responsibilities",
                    "Team Dynamics", "Leadership", "Cooperation", "Communication in Team Sports",
                    "Game Analysis", "Match Preparation",
                    
                    # Individual Sports
                    "Athletics", "Swimming", "Tennis", "Badminton", "Golf", "Track and Field",
                    "Individual Performance", "Goal Setting", "Self-motivation",
                    "Mental Preparation", "Competition Strategies",
                    
                    # Health and Safety
                    "Risk Management", "Injury Prevention", "First Aid", "RICE Protocol",
                    "Safety Guidelines", "Equipment Safety", "Environmental Considerations",
                    "Heat Illness", "Concussion", "Overuse Injuries", "Acute Injuries",
                    "Emergency Procedures", "CPR Basics",
                    
                    # Psychology of Sport
                    "Motivation", "Goal Setting", "Confidence", "Anxiety Management",
                    "Concentration", "Mental Training", "Visualization", "Relaxation Techniques",
                    "Self-talk", "Flow State", "Stress and Performance", "Team Cohesion"
                ],
                
                9: [
                    "Advanced training methodologies", "Scientific training principles",
                    "Biomechanical analysis", "Performance enhancement", "Sports technology",
                    "Data analysis in sports", "Video analysis", "Wearable technology",
                    "Sports analytics", "Performance indicators", "Talent development",
                    "Long-term athlete development", "Specialization vs diversification",
                    "Peak performance", "Competition preparation", "Mental toughness",
                    "Resilience", "Pressure handling", "Sports careers", "Coaching principles"
                ],
                
                10: [
                    "Exercise prescription", "Fitness program design", "Special populations",
                    "Adapted physical education", "Inclusive sports", "Disability sports",
                    "Therapeutic exercise", "Rehabilitation", "Physical therapy basics",
                    "Sports medicine", "Exercise testing", "Health screening",
                    "Fitness assessments", "Body composition analysis", "Metabolic testing",
                    "Sports nutrition advanced", "Ergogenic aids", "Performance supplements",
                    "Anti-doping", "Ethics in sports", "Professional development"
                ],
                
                11: [
                    "Advanced exercise physiology", "Cardiovascular responses to exercise",
                    "Respiratory adaptations", "Muscular adaptations", "Neural adaptations",
                    "Endocrine responses", "Metabolic pathways", "Fatigue mechanisms",
                    "Recovery processes", "Training adaptations", "Overtraining syndrome",
                    "Periodization models", "Block periodization", "Conjugate method",
                    "High-intensity training", "Endurance training", "Strength training",
                    "Power development", "Speed training", "Agility training"
                ],
                
                12: [
                    "Research in sports science", "Statistical analysis", "Research methods",
                    "Data interpretation", "Evidence-based practice", "Sports technology integration",
                    "Performance modeling", "Predictive analytics", "Sports careers",
                    "Coaching certification", "Sports management", "Event organization",
                    "Sports marketing", "Sports journalism", "Sports medicine careers",
                    "Exercise science applications", "Public health", "Community fitness",
                    "Wellness programs", "Corporate fitness", "Fitness entrepreneurship"
                ]
            },
            
            # ========== EVS (ENVIRONMENTAL STUDIES) ==========
            "EVS (Environmental Studies)": {
                1: [
                    # My Family and Friends
                    "My family members", "Family relationships", "Helping at home",
                    "My friends", "Playing with friends", "Sharing and caring",
                    "Good manners", "Saying please and thank you", "Respecting elders",
                    
                    # My School
                    "My classroom", "My teacher", "School rules", "School helpers",
                    "School building", "Playground", "Library", "Cleanliness at school",
                    
                    # Plants and Animals Around Me
                    "Plants in my garden", "Trees around me", "Flowers and fruits",
                    "Animals at home", "Pet animals", "Wild animals", "Birds around me",
                    "Insects", "Taking care of plants and animals",
                    
                    # Food and Water
                    "Food I eat", "Healthy food", "Junk food", "Where food comes from",
                    "Cooking food", "Water for drinking", "Uses of water", "Saving water",
                    
                    # My Body
                    "Parts of my body", "Five senses", "Keeping my body clean",
                    "Exercise and play", "Good habits", "Bad habits", "When I am sick",
                    
                    # My House
                    "Rooms in my house", "Furniture", "Keeping house clean",
                    "Safety at home", "Address", "Different types of houses"
                ],
                
                2: [
                    # My Neighborhood
                    "My neighborhood", "People in my area", "Shops and markets",
                    "Roads and streets", "Traffic rules", "Vehicles", "Public places",
                    "Parks and gardens", "Hospital", "Post office", "Police station",
                    
                    # Festivals and Celebrations
                    "Festivals we celebrate", "Religious festivals", "National festivals",
                    "How we celebrate", "Traditional food", "Decorations",
                    "Gifts and sharing", "Unity in diversity",
                    
                    # Seasons and Weather
                    "Summer season", "Monsoon season", "Winter season",
                    "Changes in weather", "Clothes for different seasons",
                    "Food in different seasons", "Activities in different seasons",
                    
                    # Means of Transport
                    "Land transport", "Water transport", "Air transport",
                    "Public transport", "Private transport", "Rules for safety",
                    "Pollution from vehicles", "Walking and cycling",
                    
                    # Communication
                    "Talking and listening", "Telephone", "Letters", "Email",
                    "Television", "Radio", "Newspapers", "Internet"
                ],
                
                3: [
                    # Our Environment
                    "Living and non-living things", "Natural environment",
                    "Human-made environment", "Interdependence", "Food chains",
                    "Pollution", "Keeping environment clean", "Reduce, reuse, recycle",
                    
                    # Air and Water
                    "Air around us", "Importance of air", "Air pollution",
                    "Sources of air pollution", "Effects of air pollution",
                    "Water sources", "Water cycle", "Water pollution",
                    "Water conservation", "Rainwater harvesting",
                    
                    # Soil and Rocks
                    "Types of soil", "Importance of soil", "Soil pollution",
                    "Soil conservation", "Rocks and minerals", "Uses of rocks",
                    
                    # Maps and Directions
                    "Reading simple maps", "Directions", "Compass", "Landmarks",
                    "My state", "My country", "World map",
                    
                    # Work and Occupations
                    "Different types of work", "Farmers", "Teachers", "Doctors",
                    "Engineers", "Artists", "Workers", "Importance of all work",
                    "Dignity of labor"
                ],
                
                4: [
                    # Natural Resources
                    "Types of natural resources", "Renewable resources",
                    "Non-renewable resources", "Conservation of resources",
                    "Sustainable use", "Forest resources", "Mineral resources",
                    "Energy resources", "Solar energy", "Wind energy",
                    
                    # Ecosystems
                    "What is an ecosystem", "Forest ecosystem", "Grassland ecosystem",
                    "Desert ecosystem", "Aquatic ecosystem", "Food webs",
                    "Energy flow", "Nutrient cycling", "Biodiversity",
                    
                    # Waste Management
                    "Types of waste", "Biodegradable waste", "Non-biodegradable waste",
                    "Plastic pollution", "E-waste", "Composting", "Recycling",
                    "Waste segregation", "Landfills", "Incineration",
                    
                    # Climate Change
                    "Weather vs climate", "Global warming", "Greenhouse effect",
                    "Causes of climate change", "Effects of climate change",
                    "Mitigation", "Adaptation", "Carbon footprint",
                    
                    # Human Impact
                    "Human activities and environment", "Deforestation",
                    "Urbanization", "Industrialization", "Agriculture",
                    "Mining", "Transportation", "Population growth"
                ],
                
                5: [
                    # Environmental Issues
                    "Major environmental problems", "Causes and effects",
                    "Solutions", "Role of individuals", "Role of government",
                    "International cooperation", "Environmental laws",
                    "Environmental movements", "Green technology",
                    
                    # Conservation
                    "Wildlife conservation", "Plant conservation", "Water conservation",
                    "Energy conservation", "Soil conservation", "Forest conservation",
                    "Protected areas", "National parks", "Wildlife sanctuaries",
                    "Biosphere reserves", "Endangered species",
                    
                    # Sustainable Development
                    "What is sustainable development", "Need for sustainability",
                    "Sustainable practices", "Green buildings", "Organic farming",
                    "Eco-friendly transportation", "Sustainable tourism",
                    "Corporate social responsibility",
                    
                    # Environmental Awareness
                    "Creating awareness", "Environmental education",
                    "Community participation", "Environmental clubs",
                    "Tree plantation", "Clean-up drives", "Awareness campaigns",
                    "Environmental days", "Earth Day", "World Environment Day"
                ]
            },
            
            # ========== GK (GENERAL KNOWLEDGE) ==========
            "GK (General Knowledge)": {
                1: [
                    # Basic Information
                    "My name", "My age", "My birthday", "My address", "My phone number",
                    "My parents' names", "My school name", "My teacher's name",
                    "My favorite color", "My favorite food", "My favorite animal",
                    
                    # Animals and Their Sounds
                    "Cow - moo", "Dog - bark", "Cat - meow", "Lion - roar", "Elephant - trumpet",
                    "Horse - neigh", "Sheep - bleat", "Pig - oink", "Duck - quack", "Hen - cluck",
                    
                    # Animals and Their Homes
                    "Dog - kennel", "Bird - nest", "Lion - den", "Bee - hive", "Horse - stable",
                    "Rabbit - burrow", "Spider - web", "Fish - aquarium", "Cow - shed",
                    
                    # Body Parts
                    "Head", "Eyes", "Nose", "Mouth", "Ears", "Hands", "Legs", "Fingers", "Toes",
                    
                    # Colors
                    "Red", "Blue", "Yellow", "Green", "Orange", "Purple", "Pink", "Black", "White", "Brown",
                    
                    # Shapes
                    "Circle", "Square", "Triangle", "Rectangle", "Oval", "Star", "Heart",
                    
                    # Numbers
                    "1 to 20", "Counting", "Before and after", "More and less"
                ],
                
                2: [
                    # Animals and Their Young Ones
                    "Cat - kitten", "Dog - puppy", "Horse - foal", "Cow - calf", "Lion - cub",
                    "Elephant - calf", "Duck - duckling", "Hen - chick", "Frog - tadpole",
                    "Butterfly - caterpillar", "Sheep - lamb", "Goat - kid",
                    
                    # Days of the Week
                    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
                    
                    # Months of the Year
                    "January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December",
                    
                    # Seasons
                    "Summer", "Monsoon", "Winter", "Spring", "Autumn",
                    
                    # Fruits and Vegetables
                    "Apple", "Banana", "Orange", "Mango", "Grapes", "Tomato", "Potato", "Carrot", "Onion",
                    
                    # Means of Transport
                    "Car", "Bus", "Train", "Airplane", "Ship", "Bicycle", "Motorcycle", "Auto-rickshaw",
                    
                    # Community Helpers
                    "Doctor", "Teacher", "Police", "Firefighter", "Postman", "Farmer", "Shopkeeper"
                ],
                
                3: [
                    # Indian States and Capitals
                    "Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Pune", "Ahmedabad",
                    
                    # Important Indian Leaders
                    "Mahatma Gandhi", "Jawaharlal Nehru", "Dr. A.P.J. Abdul Kalam", "Sardar Vallabhbhai Patel",
                    
                    # National Symbols
                    "National Flag - Tricolor", "National Bird - Peacock", "National Animal - Tiger",
                    "National Flower - Lotus", "National Tree - Banyan", "National Fruit - Mango",
                    "National Song - Vande Mataram", "National Anthem - Jana Gana Mana",
                    
                    # Festivals
                    "Diwali", "Holi", "Eid", "Christmas", "Dussehra", "Karva Chauth", "Raksha Bandhan",
                    
                    # Solar System
                    "Sun", "Moon", "Earth", "Mars", "Venus", "Jupiter", "Saturn", "Mercury", "Uranus", "Neptune",
                    
                    # Continents and Oceans
                    "Asia", "Africa", "Europe", "North America", "South America", "Australia", "Antarctica",
                    "Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"
                ],
                
                4: [
                    # World Geography
                    "Largest country - Russia", "Smallest country - Vatican City",
                    "Highest mountain - Mount Everest", "Longest river - Nile",
                    "Largest desert - Sahara", "Largest ocean - Pacific",
                    
                    # Indian Geography
                    "Highest peak in India - K2", "Longest river in India - Ganga",
                    "Largest state - Rajasthan", "Smallest state - Goa",
                    "Most populous state - Uttar Pradesh",
                    
                    # Inventions and Inventors
                    "Telephone - Alexander Graham Bell", "Light bulb - Thomas Edison",
                    "Airplane - Wright Brothers", "Computer - Charles Babbage",
                    
                    # Sports
                    "Cricket", "Football", "Hockey", "Tennis", "Badminton", "Basketball", "Swimming",
                    "Chess", "Kabaddi", "Wrestling",
                    
                    # Famous Personalities
                    "Albert Einstein", "Isaac Newton", "Marie Curie", "Leonardo da Vinci",
                    "William Shakespeare", "Mother Teresa"
                ],
                
                5: [
                    # Advanced General Knowledge
                    "UNESCO World Heritage Sites", "Seven Wonders of the World",
                    "Nobel Prize winners", "Olympic Games", "Commonwealth Games",
                    "International organizations", "UN", "WHO", "UNICEF", "FIFA",
                    
                    # Science and Technology
                    "DNA", "Computer terms", "Internet", "Artificial Intelligence",
                    "Space exploration", "Satellites", "Rovers", "Space stations",
                    
                    # Current Affairs
                    "Current President of India", "Current Prime Minister",
                    "Recent achievements", "Important events", "Award winners",
                    
                    # Environmental Awareness
                    "Climate change", "Global warming", "Renewable energy",
                    "Conservation", "Sustainable development", "Green technology"
                ]
            },
            
            # ========== ART & CRAFT ==========
            "Art & Craft": {
                1: [
                    "Drawing lines", "Circle drawing", "Square drawing", "Triangle drawing",
                    "Coloring within lines", "Primary colors", "Secondary colors",
                    "Finger painting", "Brush painting", "Sponge painting",
                    "Paper tearing", "Paper cutting", "Paper folding", "Simple origami",
                    "Clay modeling", "Play dough activities", "Making balls and snakes with clay",
                    "Collage making", "Sticking pictures", "Scribbling", "Free drawing"
                ],
                
                2: [
                    "Pattern making", "Design creation", "Border designs", "Geometric patterns",
                    "Nature drawing", "Tree drawing", "Flower drawing", "Animal drawing",
                    "Human figure drawing", "Face drawing", "Color mixing", "Shading basics",
                    "Paper craft", "Card making", "Bookmark making", "Paper flowers",
                    "Waste material craft", "Bottle craft", "Box decoration",
                    "Rangoli making", "Sand art", "Leaf painting", "Handprint art"
                ],
                
                3: [
                    "Advanced drawing techniques", "Proportion", "Perspective basics",
                    "Still life drawing", "Landscape drawing", "Portrait drawing",
                    "Different art mediums", "Watercolors", "Oil pastels", "Pencil sketching",
                    "Craft projects", "Puppet making", "Mask making", "Jewelry making",
                    "Fabric painting", "Block printing", "Stencil art", "Pottery basics",
                    "Sculpture", "Wood craft", "Metal craft", "Embroidery basics"
                ],
                
                4: [
                    "Art history", "Famous artists", "Art movements", "Traditional Indian art",
                    "Warli art", "Madhubani art", "Pattachitra", "Tanjore painting",
                    "Modern art techniques", "Abstract art", "Realistic art", "Impressionism",
                    "Advanced crafts", "Macrame", "Quilling", "Decoupage", "Mosaic art",
                    "Digital art basics", "Photography", "Video making", "Animation basics",
                    "Exhibition preparation", "Art appreciation", "Art criticism"
                ],
                
                5: [
                    "Professional art techniques", "Advanced painting", "Advanced sculpture",
                    "Printmaking", "Etching", "Screen printing", "Commercial art",
                    "Graphic design", "Logo design", "Poster design", "Advertising art",
                    "Interior design basics", "Fashion design", "Textile design",
                    "Art careers", "Art business", "Art galleries", "Art museums",
                    "Art conservation", "Art therapy", "Community art projects"
                ]
            },
            
            # ========== COMPUTER SCIENCE ==========
            "Computer Science": {
                3: [
                    "Introduction to computers", "Parts of computer", "Monitor", "Keyboard", "Mouse",
                    "CPU", "Speakers", "What computers can do", "Computer vs human",
                    "On and off", "Login", "Desktop", "Icons", "Clicking", "Double clicking",
                    "Paint program", "Drawing", "Coloring", "Saving", "Opening files",
                    "Typing practice", "Letters", "Numbers", "Simple words"
                ],
                
                4: [
                    "Types of computers", "Desktop", "Laptop", "Tablet", "Smartphone",
                    "Input devices", "Output devices", "Storage devices", "CD", "DVD", "Pen drive",
                    "Internet introduction", "Website", "Email basics", "Search engines",
                    "Word processing", "MS Word basics", "Typing documents", "Formatting text",
                    "Educational games", "Learning software", "Computer safety", "Digital etiquette"
                ],
                
                5: [
                    "Computer memory", "RAM", "Hard disk", "File management", "Folders",
                    "Copy", "Cut", "Paste", "Delete", "Recycle bin",
                    "Internet safety", "Online behavior", "Privacy", "Cyberbullying",
                    "Presentation software", "PowerPoint", "Slides", "Animation",
                    "Multimedia", "Images", "Audio", "Video", "Graphics software",
                    "Programming introduction", "Scratch", "Block programming", "Simple algorithms"
                ],
                
                6: [
                    "Advanced computer concepts", "Operating systems", "Software vs hardware",
                    "System software", "Application software", "Utilities",
                    "Internet applications", "Social media", "Online learning", "Cloud computing",
                    "Digital citizenship", "Information literacy", "Research skills",
                    "Programming concepts", "Loops", "Conditions", "Variables",
                    "Web design basics", "HTML introduction", "Creating web pages",
                    "Database basics", "Spreadsheets", "Excel", "Formulas", "Charts"
                ],
                
                7: [
                    "Programming languages", "Python introduction", "Java basics", "C++ basics",
                    "Algorithm design", "Flowcharts", "Pseudocode", "Problem solving",
                    "Data structures", "Arrays", "Lists", "Strings",
                    "Web development", "CSS", "JavaScript introduction",
                    "Mobile app development", "App design", "User interface",
                    "Computer networks", "LAN", "WAN", "Internet protocols",
                    "Artificial Intelligence basics", "Machine Learning introduction"
                ],
                
                8: [
                    "Advanced programming", "Object-oriented programming", "Classes", "Objects",
                    "Inheritance", "Polymorphism", "Encapsulation",
                    "Data science introduction", "Big data", "Analytics", "Visualization",
                    "Robotics", "Sensors", "Actuators", "Programming robots",
                    "Cybersecurity", "Encryption", "Firewall", "Malware", "Phishing",
                    "Game development", "Game engines", "Game design", "Graphics programming",
                    "Project management", "Software development lifecycle", "Testing", "Debugging"
                ],
                
                9: [
                    "Advanced algorithms", "Sorting", "Searching", "Recursion",
                    "Complex data structures", "Trees", "Graphs", "Hash tables",
                    "Database management", "SQL", "Database design", "Normalization",
                    "Advanced web development", "Frontend frameworks", "Backend development",
                    "Cloud computing", "AWS", "Azure", "Google Cloud",
                    "Artificial Intelligence", "Neural networks", "Deep learning",
                    "Computer vision", "Natural language processing"
                ],
                
                10: [
                    "Software engineering", "System design", "Architecture patterns",
                    "DevOps", "Version control", "Git", "Continuous integration",
                    "Mobile app development", "Android", "iOS", "Cross-platform",
                    "Blockchain technology", "Cryptocurrency", "Smart contracts",
                    "Internet of Things", "Connected devices", "Smart home", "Industrial IoT",
                    "Machine Learning", "Supervised learning", "Unsupervised learning",
                    "Computer graphics", "3D modeling", "Animation", "Virtual reality"
                ],
                
                11: [
                    "Advanced software development", "Design patterns", "Microservices",
                    "Advanced databases", "NoSQL", "Distributed systems", "Scalability",
                    "Advanced AI", "Computer vision", "Robotics", "Expert systems",
                    "Quantum computing", "Quantum algorithms", "Quantum programming",
                    "Advanced cybersecurity", "Ethical hacking", "Penetration testing",
                    "Research projects", "Innovation", "Entrepreneurship", "Startups"
                ],
                
                12: [
                    "Capstone projects", "Industry collaboration", "Internships",
                    "Advanced research", "Publishing papers", "Patent applications",
                    "Emerging technologies", "Augmented reality", "Mixed reality",
                    "5G technology", "Edge computing", "Fog computing",
                    "Career preparation", "Technical interviews", "Portfolio development",
                    "Professional development", "Certifications", "Industry standards",
                    "Ethics in technology", "Social responsibility", "Sustainable computing"
                ]
            },
            
            # ========== ADVANCED SUBJECTS (GRADES 11-12) ==========
            
            # ========== PHYSICS ==========
            "Physics": {
                11: [
                    # Units and Measurements
                    "Physical quantities", "Fundamental and derived units", "SI units",
                    "Measurement of length", "Measurement of mass", "Measurement of time",
                    "Accuracy and precision", "Significant figures", "Dimensions",
                    "Dimensional analysis", "Dimensional equations",
                    
                    # Kinematics
                    "Motion in a straight line", "Position and displacement", "Velocity",
                    "Acceleration", "Kinematic equations", "Graphs of motion",
                    "Motion in a plane", "Projectile motion", "Circular motion",
                    
                    # Laws of Motion
                    "Newton's first law", "Newton's second law", "Newton's third law",
                    "Momentum", "Impulse", "Conservation of momentum", "Friction",
                    "Circular motion dynamics",
                    
                    # Work, Energy and Power
                    "Work", "Energy", "Kinetic energy", "Potential energy",
                    "Work-energy theorem", "Conservation of energy", "Power",
                    "Collisions",
                    
                    # System of Particles and Rotational Motion
                    "Centre of mass", "Motion of centre of mass", "Rotational motion",
                    "Moment of inertia", "Torque", "Angular momentum",
                    "Conservation of angular momentum",
                    
                    # Gravitation
                    "Universal law of gravitation", "Acceleration due to gravity",
                    "Gravitational potential energy", "Escape velocity", "Satellites",
                    "Kepler's laws",
                    
                    # Properties of Bulk Matter
                    "Mechanical properties of solids", "Stress and strain",
                    "Elastic moduli", "Mechanical properties of fluids",
                    "Pressure", "Pascal's law", "Archimedes' principle",
                    "Surface tension", "Viscosity",
                    
                    # Thermodynamics
                    "Thermal equilibrium", "Temperature", "Heat", "Specific heat",
                    "Phase transitions", "Laws of thermodynamics", "Heat engines",
                    "Refrigerators",
                    
                    # Behavior of Perfect Gas and Kinetic Theory
                    "Equation of state", "Kinetic theory", "Law of equipartition of energy",
                    
                    # Oscillations and Waves
                    "Periodic motion", "Simple harmonic motion", "Damped oscillations",
                    "Forced oscillations", "Resonance", "Wave motion", "Sound waves",
                    "Doppler effect"
                ],
                
                12: [
                    # Electrostatics
                    "Electric charges", "Coulomb's law", "Electric field", "Electric flux",
                    "Gauss's law", "Electric potential", "Capacitance", "Dielectrics",
                    
                    # Current Electricity
                    "Electric current", "Resistance", "Ohm's law", "Series and parallel circuits",
                    "Kirchhoff's laws", "Wheatstone bridge", "Potentiometer",
                    
                    # Magnetic Effects of Current and Magnetism
                    "Magnetic field", "Biot-Savart law", "Ampere's law", "Force on current",
                    "Torque on current loop", "Magnetic dipole", "Earth's magnetism",
                    
                    # Electromagnetic Induction and Alternating Currents
                    "Electromagnetic induction", "Faraday's law", "Lenz's law",
                    "Self-inductance", "Mutual inductance", "AC circuits", "Transformers",
                    
                    # Electromagnetic Waves
                    "Electromagnetic spectrum", "Electromagnetic wave equation",
                    
                    # Optics
                    "Reflection of light", "Refraction", "Total internal reflection",
                    "Optical instruments", "Wave optics", "Interference", "Diffraction",
                    "Polarization",
                    
                    # Dual Nature of Radiation and Matter
                    "Photoelectric effect", "Matter waves", "de Broglie wavelength",
                    
                    # Atoms and Nuclei
                    "Atomic structure", "Bohr model", "Hydrogen spectrum",
                    "Nuclear physics", "Radioactivity", "Nuclear reactions",
                    
                    # Electronic Devices
                    "Semiconductors", "p-n junction", "Diode", "Transistor",
                    "Logic gates", "Digital electronics"
                ]
            },
            
            # ========== CHEMISTRY ==========
            "Chemistry": {
                11: [
                    # Some Basic Concepts of Chemistry
                    "Importance of chemistry", "Atomic and molecular masses", "Mole concept",
                    "Percentage composition", "Empirical and molecular formula",
                    "Chemical equations", "Stoichiometry",
                    
                    # Structure of Atom
                    "Discovery of electron", "Discovery of proton", "Discovery of neutron",
                    "Atomic models", "Quantum mechanical model", "Electronic configuration",
                    
                    # Classification of Elements and Periodicity
                    "Development of periodic table", "Modern periodic law",
                    "Periodic trends", "Ionization energy", "Electron affinity",
                    
                    # Chemical Bonding and Molecular Structure
                    "Ionic bonding", "Covalent bonding", "Lewis structures", "VSEPR theory",
                    "Hybridization", "Molecular orbital theory", "Hydrogen bonding",
                    
                    # States of Matter
                    "Gaseous state", "Gas laws", "Kinetic molecular theory",
                    "Liquid state", "Solid state", "Crystal systems",
                    
                    # Thermodynamics
                    "System and surroundings", "First law of thermodynamics",
                    "Enthalpy", "Second law of thermodynamics", "Entropy",
                    
                    # Equilibrium
                    "Chemical equilibrium", "Law of mass action", "Le Chatelier's principle",
                    "Ionic equilibrium", "Acids and bases", "Buffer solutions",
                    
                    # Redox Reactions
                    "Oxidation and reduction", "Redox reactions", "Balancing redox equations",
                    "Electrochemical cells",
                    
                    # Hydrogen
                    "Position of hydrogen", "Preparation of hydrogen", "Properties of hydrogen",
                    "Hydrides",
                    
                    # s-Block Elements
                    "Alkali metals", "Alkaline earth metals", "Properties and uses",
                    
                    # p-Block Elements
                    "Boron family", "Carbon family", "Nitrogen family", "Oxygen family",
                    "Halogen family", "Noble gases",
                    
                    # Organic Chemistry
                    "Purification of organic compounds", "Qualitative analysis",
                    "Quantitative analysis", "IUPAC nomenclature",
                    
                    # Hydrocarbons
                    "Alkanes", "Alkenes", "Alkynes", "Aromatic hydrocarbons",
                    "Petroleum", "Natural gas"
                ],
                
                12: [
                    # Solid State
                    "Classification of solids", "Crystal lattices", "Unit cells",
                    "Packing efficiency", "Imperfections in solids",
                    
                    # Solutions
                    "Types of solutions", "Concentration terms", "Solubility",
                    "Vapour pressure", "Colligative properties", "Abnormal molecular mass",
                    
                    # Electrochemistry
                    "Electrochemical cells", "Galvanic cells", "Nernst equation",
                    "Electrolysis", "Batteries", "Fuel cells", "Corrosion",
                    
                    # Chemical Kinetics
                    "Rate of reaction", "Factors affecting rate", "Rate law",
                    "Order of reaction", "Molecular reactions", "Collision theory",
                    
                    # Surface Chemistry
                    "Adsorption", "Catalysis", "Colloids", "Emulsions",
                    
                    # General Principles of Metallurgy
                    "Occurrence of metals", "Extraction of metals", "Refining of metals",
                    
                    # p-Block Elements
                    "Group 15 elements", "Group 16 elements", "Group 17 elements",
                    "Group 18 elements",
                    
                    # d-Block and f-Block Elements
                    "Transition elements", "Properties of transition elements",
                    "Inner transition elements", "Lanthanoids", "Actinoids",
                    
                    # Coordination Compounds
                    "Coordination entities", "Nomenclature", "Isomerism",
                    "Bonding theories", "Crystal field theory",
                    
                    # Haloalkanes and Haloarenes
                    "Classification", "Nomenclature", "Preparation", "Properties",
                    "Reactions",
                    
                    # Alcohols, Phenols and Ethers
                    "Classification", "Nomenclature", "Preparation", "Properties",
                    
                    # Aldehydes, Ketones and Carboxylic Acids
                    "Structure", "Preparation", "Properties", "Uses",
                    
                    # Amines
                    "Structure", "Classification", "Preparation", "Properties",
                    
                    # Biomolecules
                    "Carbohydrates", "Proteins", "Vitamins", "Nucleic acids",
                    
                    # Polymers
                    "Classification", "Polymerization", "Natural polymers",
                    "Synthetic polymers",
                    
                    # Chemistry in Everyday Life
                    "Drugs and medicines", "Food chemistry", "Cleansing agents"
                ]
            },
            
            # ========== BIOLOGY ==========
            "Biology": {
                11: [
                    # Diversity in Living World
                    "What is living", "Biodiversity", "Taxonomic categories",
                    "Taxonomical aids", "Five kingdom classification",
                    "Kingdom Monera", "Kingdom Protista", "Kingdom Fungi",
                    "Kingdom Plantae", "Kingdom Animalia",
                    
                    # Structural Organisation in Animals and Plants
                    "Tissues", "Morphology of flowering plants", "Anatomy of flowering plants",
                    "Structural organisation in animals",
                    
                    # Cell Structure and Function
                    "Cell theory", "Cell as basic unit of life", "Prokaryotic cells",
                    "Eukaryotic cells", "Cell envelope", "Cell organelles",
                    "Cell cycle", "Cell division",
                    
                    # Plant Physiology
                    "Transport in plants", "Mineral nutrition", "Photosynthesis",
                    "Respiration in plants", "Plant growth and development",
                    
                    # Human Physiology
                    "Digestion and absorption", "Breathing and exchange of gases",
                    "Body fluids and circulation", "Excretory products and elimination",
                    "Locomotion and movement", "Neural control and coordination",
                    "Chemical coordination and integration"
                ],
                
                12: [
                    # Reproduction
                    "Reproduction in organisms", "Sexual reproduction in flowering plants",
                    "Human reproduction", "Reproductive health",
                    
                    # Genetics and Evolution
                    "Heredity and variation", "Molecular basis of inheritance",
                    "Evolution",
                    
                    # Biology and Human Welfare
                    "Human health and disease", "Strategies for enhancement in food production",
                    "Microbes in human welfare",
                    
                    # Biotechnology and its Applications
                    "Biotechnology principles and processes",
                    "Biotechnology and its applications",
                    
                    # Ecology and Environment
                    "Organisms and populations", "Ecosystem",
                    "Biodiversity and conservation", "Environmental issues"
                ]
            },
            
            # ========== ADDITIONAL SUBJECTS ==========
            
            # ========== ECONOMICS ==========
            "Economics": {
                11: [
                    "Introduction to Economics", "Central problems of an economy",
                    "Production possibilities curve", "Consumer's equilibrium",
                    "Demand", "Elasticity of demand", "Producer's equilibrium",
                    "Supply", "Forms of market", "Price determination",
                    "Simple applications of demand and supply"
                ],
                
                12: [
                    "Introduction to macroeconomics", "National income accounting",
                    "Money and banking", "Determination of income and employment",
                    "Government budget", "Balance of payments",
                    "Development experience of India", "Current challenges facing Indian economy"
                ]
            },
            
            # ========== BUSINESS STUDIES ==========
            "Business Studies": {
                11: [
                    "Nature and significance of management", "Principles of management",
                    "Business environment", "Planning", "Organising", "Staffing",
                    "Directing", "Controlling"
                ],
                
                12: [
                    "Nature and significance of management", "Principles of management",
                    "Business environment", "Planning", "Organising", "Staffing",
                    "Directing", "Controlling", "Business finance", "Financial markets",
                    "Marketing", "Consumer protection"
                ]
            },
            
            # ========== ACCOUNTANCY ==========
            "Accountancy": {
                11: [
                    "Introduction to accounting", "Theory base of accounting",
                    "Recording of transactions", "Bank reconciliation statement",
                    "Bills of exchange", "Rectification of errors", "Depreciation",
                    "Provisions and reserves", "Financial statements"
                ],
                
                12: [
                    "Accounting for partnership firms", "Reconstitution of partnership",
                    "Dissolution of partnership", "Accounting for companies",
                    "Issue of shares", "Issue of debentures", "Redemption of debentures",
                    "Financial statement analysis", "Cash flow statement"
                ]
            },
            
            # ========== POLITICAL SCIENCE ==========
            "Political Science": {
                11: [
                    "Political theory", "Freedom", "Equality", "Social justice",
                    "Rights", "Citizenship", "Nationalism", "Secularism",
                    "Peace", "Development"
                ],
                
                12: [
                    "Challenges of nation building", "Era of one-party dominance",
                    "Politics of planned development", "India's external relations",
                    "Challenges to and restoration of Congress system",
                    "Crisis of democratic order", "Rise of popular movements",
                    "Regional aspirations", "Recent developments in Indian politics"
                ]
            },
            
            # ========== PSYCHOLOGY ==========
            "Psychology": {
                11: [
                    "What is psychology", "Methods of psychology", "Biological basis of behavior",
                    "Sensation and perception", "Learning", "Memory", "Thinking",
                    "Motivation and emotion"
                ],
                
                12: [
                    "Variations in psychological attributes", "Self and personality",
                    "Meeting life challenges", "Psychological disorders",
                    "Therapeutic approaches", "Attitude and social cognition",
                    "Social influence and group processes", "Psychology and life"
                ]
            },
            
            # ========== GEOGRAPHY ==========
            "Geography": {
                11: [
                    "Geography as a discipline", "The earth", "Landforms", "Climate",
                    "Water in the atmosphere", "World climate", "Natural vegetation",
                    "Soils", "Natural hazards"
                ],
                
                12: [
                    "Human geography", "People", "Human development",
                    "Primary activities", "Secondary activities", "Tertiary activities",
                    "Transport and communication", "International trade",
                    "Human settlements"
                ]
            },
            
            # ========== HISTORY ==========
            "History": {
                11: [
                    "From the beginning of time", "Writing and city life",
                    "An empire across three continents", "The central Islamic lands",
                    "Nomadic empires", "The three orders", "Changing cultural traditions",
                    "Confrontation of cultures", "The industrial revolution",
                    "Displacing indigenous peoples", "Paths to modernization"
                ],
                
                12: [
                    "Bricks, beads and bones", "Kings, farmers and towns",
                    "Kinship, caste and class", "Thinkers, beliefs and buildings",
                    "Through the eyes of travellers", "Bhakti-Sufi traditions",
                    "An imperial capital", "Peasants, zamindars and the state",
                    "Kings and chronicles", "Colonialism and the countryside",
                    "Rebels and the Raj", "Colonial cities", "Mahatma Gandhi",
                    "Understanding partition", "Framing the constitution"
                ]
            },
            
            # ========== APPLIED MATHEMATICS ==========
            "Applied Mathematics": {
                11: [
                    "Numbers, quantification and numerical applications",
                    "Algebra", "Calculus", "Probability distributions",
                    "Index numbers and time-based data", "Financial mathematics",
                    "Linear programming"
                ],
                
                12: [
                    "Numbers, quantification and numerical applications",
                    "Algebra", "Calculus", "Probability distributions",
                    "Inferential statistics", "Index numbers and time-based data",
                    "Financial mathematics", "Linear programming"
                ]
            },
            
            # ========== BIOTECHNOLOGY ==========
            "Biotechnology": {
                11: [
                    "Introduction to biotechnology", "Genetics", "Molecular biology",
                    "Cell biology and biotechnology", "Microbiology and biotechnology",
                    "Plant biotechnology", "Animal biotechnology"
                ],
                
                12: [
                    "Recombinant DNA technology", "Protein structure and engineering",
                    "Genomics and proteomics", "Plant tissue culture applications",
                    "Animal cell culture applications", "Microbial biotechnology applications",
                    "Environmental biotechnology", "Medical biotechnology",
                    "Industrial biotechnology", "Bioinformatics"
                ]
            },
            
            # ========== ENGINEERING GRAPHICS ==========
            "Engineering Graphics": {
                11: [
                    "Introduction to engineering graphics", "Geometrical constructions",
                    "Orthographic projections", "Sectional views", "Pictorial projections",
                    "Machine drawing basics"
                ],
                
                12: [
                    "Advanced orthographic projections", "Auxiliary views",
                    "Development of surfaces", "Intersection of solids",
                    "Perspective projections", "Computer-aided drafting",
                    "3D modeling", "Assembly drawings"
                ]
            },
            
            # ========== SANSKRIT ==========
            "Sanskrit": {
                6: [
                    "देवनागरी लिपि", "स्वर और व्यंजन", "संधि", "धातु रूप", "शब्द रूप",
                    "सुभाषितानि", "श्लोकाः", "गद्यांशाः", "व्याकरणम्", "छन्दः"
                ],
                
                7: [
                    "व्याकरण", "संधि विच्छेद", "धातु रूप", "शब्द रूप", "प्रत्यय",
                    "उपसर्ग", "समास", "छन्द", "अलंकार", "श्लोक और गद्य"
                ],
                
                8: [
                    "उन्नत व्याकरण", "संधि के भेद", "धातु रूप", "शब्द रूप",
                    "कारक", "काल", "वाच्य", "छन्द शास्त्र", "अलंकार शास्त्र"
                ]
            }
        },

               
        
        "IB": {
            
            # ==================== MATHEMATICS ====================
            "Mathematics": {
                # PYP Mathematics (Grades 1-5) - Based on 5 strands
                1: [
                    # Number
                    "Number Recognition 0-20", "Counting Forward and Backward", "Number Patterns", 
                    "Number Formation", "Greater Than and Less Than", "Before and After", 
                    "Number Bonds to 10", "Skip Counting by 2s, 5s, 10s", "Ordinal Numbers",
                    
                    # Pattern and Function
                    "Repeating Patterns", "Growing Patterns", "Pattern Rules", "Sorting by Attributes",
                    "Color Patterns", "Shape Patterns", "Sound Patterns", "Movement Patterns",
                    
                    # Measurement
                    "Length Comparison", "Weight Comparison", "Capacity Comparison", "Time - Day and Night",
                    "Days of the Week", "Months of the Year", "Seasons", "Money Recognition",
                    "Telling Time - Hour", "Temperature - Hot and Cold",
                    
                    # Shape and Space
                    "2D Shapes Recognition", "3D Shapes Recognition", "Circle", "Square", "Triangle", 
                    "Rectangle", "Sphere", "Cube", "Cylinder", "Position Words", "Direction Words",
                    "Spatial Relationships", "Symmetry in Nature",
                    
                    # Data Handling
                    "Collecting Data", "Sorting Objects", "Simple Graphs", "Tallying", 
                    "Picture Graphs", "Bar Charts", "Interpreting Data", "Probability - Likely/Unlikely"
                ],
                
                2: [
                    # Number
                    "Number Recognition 0-100", "Place Value - Tens and Ones", "Counting by 2s, 5s, 10s",
                    "Number Bonds to 20", "Addition Facts to 20", "Subtraction Facts to 20",
                    "Mental Math Strategies", "Estimation", "Odd and Even Numbers", "Number Lines",
                    
                    # Pattern and Function  
                    "Number Patterns", "Geometric Patterns", "Function Machines", "Input-Output Tables",
                    "Sequence Rules", "Pattern Extensions", "Creating Patterns",
                    
                    # Measurement
                    "Standard Units of Length", "Measuring with Rulers", "Kilograms and Grams",
                    "Liters and Milliliters", "Calendar Reading", "Telling Time - Half Hours",
                    "Digital and Analog Clocks", "Money - Coins and Notes", "Temperature Measurement",
                    
                    # Shape and Space
                    "Properties of 2D Shapes", "Properties of 3D Shapes", "Sides and Vertices",
                    "Faces, Edges, Vertices", "Tessellations", "Lines of Symmetry", "Transformations",
                    "Grid References", "Maps and Plans", "Left and Right",
                    
                    # Data Handling
                    "Data Collection Methods", "Surveys", "Pictographs", "Bar Graphs", 
                    "Interpreting Charts", "Most and Least", "Simple Statistics", "Probability Experiments"
                ],
                
                3: [
                    # Number
                    "Numbers to 1000", "Place Value - Hundreds, Tens, Ones", "Rounding Numbers",
                    "Addition with Regrouping", "Subtraction with Regrouping", "Multiplication Tables 2-10",
                    "Division Facts", "Word Problems", "Mental Math", "Fraction Basics - Halves, Quarters",
                    
                    # Pattern and Function
                    "Number Sequences", "Multiplication Patterns", "Function Rules", "Variables",
                    "Simple Equations", "Pattern Investigation", "Algebraic Thinking",
                    
                    # Measurement
                    "Meters, Centimeters, Millimeters", "Perimeter", "Area - Square Units",
                    "Mass - Kilograms and Grams", "Volume and Capacity", "Time - Minutes and Seconds",
                    "Elapsed Time", "Money - Making Change", "Temperature - Celsius",
                    
                    # Shape and Space
                    "Angles - Right, Acute, Obtuse", "Parallel and Perpendicular Lines", "Quadrilaterals",
                    "Triangles", "Congruent Shapes", "Similar Shapes", "Rotations", "Reflections",
                    "Translations", "Coordinate Grids", "Scale", "Compass Directions",
                    
                    # Data Handling
                    "Data Analysis", "Mean, Median, Mode", "Range", "Frequency Tables",
                    "Line Graphs", "Pie Charts", "Probability - Certain, Possible, Impossible",
                    "Tree Diagrams", "Combinations"
                ],
                
                4: [
                    # Number
                    "Numbers to 10,000", "Place Value to Ten Thousands", "Comparing Large Numbers",
                    "Multi-digit Addition", "Multi-digit Subtraction", "Multiplication by 2-digit Numbers",
                    "Long Division", "Factors and Multiples", "Prime and Composite Numbers",
                    "Equivalent Fractions", "Adding and Subtracting Fractions", "Decimal Places",
                    
                    # Pattern and Function
                    "Linear Patterns", "Geometric Sequences", "Function Tables", "Graphing Functions",
                    "Simple Algebraic Expressions", "Solving Simple Equations", "Variables and Constants",
                    
                    # Measurement
                    "Converting Units", "Area of Rectangles", "Area of Triangles", "Volume of Cubes",
                    "Perimeter of Complex Shapes", "Mass and Weight", "Time Zones", "Speed",
                    "Scale Drawings", "Angles - Measuring and Drawing",
                    
                    # Shape and Space
                    "Properties of Polygons", "Regular and Irregular Shapes", "Circles - Radius and Diameter",
                    "Nets of 3D Shapes", "Cross-sections", "Transformations on Coordinate Plane",
                    "Tessellation Patterns", "Similarity and Scaling", "Geometric Construction",
                    
                    # Data Handling
                    "Statistical Investigations", "Double Bar Graphs", "Scatter Plots", "Trends in Data",
                    "Probability Fractions", "Experimental Probability", "Theoretical Probability",
                    "Sample Space", "Independent Events"
                ],
                
                5: [
                    # Number
                    "Large Numbers to Millions", "Scientific Notation", "Order of Operations", "PEMDAS/BODMAS",
                    "Fraction Operations", "Mixed Numbers", "Decimal Operations", "Percentages",
                    "Ratio and Proportion", "Rate", "Unit Rate", "Integer Introduction",
                    
                    # Pattern and Function
                    "Linear Functions", "Quadratic Patterns", "Exponential Growth", "Recursive Patterns",
                    "Algebraic Expressions", "Solving Linear Equations", "Graphing Linear Functions",
                    
                    # Measurement
                    "Composite Area", "Surface Area", "Volume of Prisms", "Volume of Cylinders",
                    "Pythagorean Theorem Introduction", "Coordinate Geometry", "Distance Formula",
                    "Unit Conversions", "Precision and Accuracy",
                    
                    # Shape and Space
                    "Circle Properties", "Circumference", "Area of Circles", "Polygons - Interior Angles",
                    "Triangles - Properties", "Quadrilaterals - Properties", "3D Geometry",
                    "Perspective Drawing", "Scale Factor", "Geometric Proofs Introduction",
                    
                    # Data Handling
                    "Statistical Analysis", "Quartiles", "Box and Whisker Plots", "Standard Deviation Introduction",
                    "Probability Trees", "Conditional Probability", "Combinations and Permutations",
                    "Bias in Sampling", "Correlation vs Causation"
                ],
                
                # MYP Mathematics (Grades 6-10) - 4 main strands
                6: [
                    # Number and Algebra
                    "Integers", "Rational Numbers", "Operations with Integers", "Fractions and Decimals",
                    "Percentages", "Ratio and Proportion", "Rate and Speed", "Scientific Notation",
                    "Square Roots", "Cube Roots", "Algebraic Expressions", "Linear Equations",
                    "Inequalities", "Graphing Linear Functions", "Systems of Equations",
                    
                    # Geometry and Trigonometry
                    "Angle Properties", "Triangles", "Quadrilaterals", "Polygons", "Circles",
                    "Area and Perimeter", "Surface Area", "Volume", "Coordinate Geometry",
                    "Transformations", "Similarity", "Congruence", "Pythagoras Theorem",
                    
                    # Statistics and Probability
                    "Data Collection", "Frequency Tables", "Histograms", "Box Plots", "Scatter Plots",
                    "Measures of Central Tendency", "Measures of Spread", "Probability",
                    "Tree Diagrams", "Independent Events", "Conditional Probability",
                    
                    # Functions
                    "Function Notation", "Domain and Range", "Linear Functions", "Quadratic Functions",
                    "Exponential Functions", "Graphing Functions", "Function Transformations"
                ],
                
                7: [
                    # Number and Algebra
                    "Number Systems", "Irrational Numbers", "Surds", "Indices and Exponents",
                    "Algebraic Manipulation", "Factoring", "Quadratic Equations", "Simultaneous Equations",
                    "Algebraic Fractions", "Sequences and Series", "Arithmetic Progressions",
                    
                    # Geometry and Trigonometry
                    "Trigonometric Ratios", "Right Triangle Trigonometry", "Sine Rule", "Cosine Rule",
                    "Trigonometric Graphs", "3D Geometry", "Vectors", "Geometric Proofs",
                    "Circle Theorems", "Arc Length", "Sector Area",
                    
                    # Statistics and Probability
                    "Statistical Investigations", "Sampling Methods", "Bias", "Correlation",
                    "Line of Best Fit", "Probability Distributions", "Normal Distribution",
                    "Binomial Probability", "Hypothesis Testing Introduction",
                    
                    # Functions
                    "Composite Functions", "Inverse Functions", "Polynomial Functions", "Rational Functions",
                    "Logarithmic Functions", "Piecewise Functions", "Function Analysis"
                ],
                
                8: [
                    # Number and Algebra
                    "Complex Numbers Introduction", "Matrices", "Determinants", "Matrix Operations",
                    "Systems of Linear Equations", "Parametric Equations", "Polar Coordinates",
                    "Mathematical Induction", "Binomial Theorem", "Sequences and Limits",
                    
                    # Geometry and Trigonometry
                    "Advanced Trigonometry", "Trigonometric Identities", "Trigonometric Equations",
                    "Inverse Trigonometric Functions", "Vectors in 2D and 3D", "Vector Operations",
                    "Dot Product", "Cross Product", "Geometric Applications of Vectors",
                    
                    # Statistics and Probability
                    "Advanced Statistics", "Regression Analysis", "Chi-squared Tests", "ANOVA",
                    "Probability Distributions", "Poisson Distribution", "Continuous Probability",
                    "Confidence Intervals", "Hypothesis Testing",
                    
                    # Functions and Calculus
                    "Limits", "Derivatives", "Differentiation Rules", "Applications of Derivatives",
                    "Integration", "Definite Integrals", "Applications of Integration", "Differential Equations"
                ],
                
                9: [
                    # Number and Algebra
                    "Real Number System", "Complex Numbers", "Algebraic Structures", "Fields and Rings",
                    "Advanced Algebraic Manipulation", "Polynomial Long Division", "Rational Root Theorem",
                    "Factor Theorem", "Remainder Theorem", "Partial Fractions",
                    
                    # Geometry and Trigonometry
                    "Analytic Geometry", "Conic Sections", "Parametric and Polar Equations",
                    "Advanced Trigonometry", "Hyperbolic Functions", "3D Coordinate Geometry",
                    "Vector Calculus", "Geometric Transformations", "Non-Euclidean Geometry",
                    
                    # Statistics and Probability
                    "Advanced Probability Theory", "Markov Chains", "Bayesian Statistics",
                    "Time Series Analysis", "Multivariate Statistics", "Experimental Design",
                    "Statistical Modeling", "Data Mining Concepts",
                    
                    # Advanced Functions and Calculus
                    "Multivariable Calculus", "Partial Derivatives", "Multiple Integrals",
                    "Vector Fields", "Line Integrals", "Surface Integrals", "Green's Theorem",
                    "Stokes' Theorem", "Divergence Theorem"
                ],
                
                10: [
                    # Pre-DP Preparation
                    "Advanced Algebra Review", "Function Analysis", "Trigonometry Mastery",
                    "Statistics and Probability Synthesis", "Calculus Foundations", "Mathematical Proof",
                    "Problem Solving Strategies", "Mathematical Modeling", "Technology in Mathematics",
                    "Mathematical Communication", "Research Methods in Mathematics", "Historical Mathematics",
                    "Mathematics and Other Disciplines", "Real-world Applications", "Extended Investigation",
                    "Mathematical Portfolio", "Peer Teaching", "Mathematical Debates",
                    "Cross-cultural Mathematics", "Ethics in Mathematics"
                ],
                
                # DP Mathematics (Grades 11-12) - Analysis & Approaches and Applications & Interpretation
                11: [
                    # Analysis & Approaches SL/HL
                    "Number and Algebra", "Functions", "Geometry and Trigonometry", "Statistics and Probability", "Calculus",
                    
                    # Detailed AA Topics
                    "Sequences and Series", "Exponentials and Logarithms", "Binomial Theorem",
                    "Complex Numbers", "Vectors", "Functions and Equations", "Circular Functions",
                    "Triangle Trigonometry", "Further Trigonometry", "Descriptive Statistics",
                    "Probability", "Statistical Applications", "Differential Calculus",
                    "Integral Calculus", "Further Calculus", "Differential Equations",
                    
                    # Applications & Interpretation SL/HL
                    "Statistical Applications", "Financial Mathematics", "Calculus Applications",
                    "Discrete Mathematics", "Mathematical Models", "Graph Theory", "Sets and Logic",
                    "Number Theory", "Mathematical Investigations", "Technology in Mathematics"
                ],
                
                12: [
                    # Advanced DP Mathematics
                    "Advanced Calculus", "Mathematical Analysis", "Linear Algebra", "Advanced Statistics",
                    "Mathematical Modeling", "Numerical Methods", "Optimization", "Game Theory",
                    "Abstract Algebra", "Real Analysis", "Complex Analysis", "Topology",
                    "Differential Geometry", "Mathematical Logic", "Set Theory", "Category Theory",
                    "Fractal Geometry", "Chaos Theory", "Mathematical Philosophy", "Research Project",
                    "Extended Essay in Mathematics", "Mathematical Exploration", "Internal Assessment",
                    "External Assessment Preparation", "University Mathematics Preparation"
                ]
            },
            
            # ==================== SCIENCE ====================
            "Science": {
                # PYP Science (Grades 1-5) - Inquiry-based learning
                1: [
                    # Living Things
                    "Living and Non-living", "Plants Around Us", "Parts of Plants", "Animals Around Us",
                    "Animal Homes", "Baby Animals", "Pet Care", "Farm Animals", "Wild Animals",
                    "Birds", "Insects", "Fish", "My Body", "Five Senses", "Healthy Eating",
                    
                    # Materials and Matter
                    "Different Materials", "Hard and Soft", "Rough and Smooth", "Hot and Cold",
                    "Wet and Dry", "Heavy and Light", "Big and Small", "Colors", "Shapes",
                    "Natural and Made", "Recycling", "Waste Management",
                    
                    # Forces and Energy
                    "Push and Pull", "Fast and Slow", "High and Low", "Day and Night",
                    "Light and Dark", "Loud and Quiet", "Moving Objects", "Floating and Sinking",
                    "Magnets", "Simple Machines",
                    
                    # Earth and Space
                    "Weather", "Seasons", "Rain", "Wind", "Sun", "Moon", "Stars", "Sky",
                    "Land and Water", "Rocks and Soil", "Mountains and Rivers"
                ],
                
                2: [
                    # Living Systems
                    "Plant Life Cycle", "Animal Life Cycle", "Growth and Change", "Needs of Living Things",
                    "Habitats", "Food Chains", "Adaptation", "Migration", "Hibernation",
                    "Human Body Systems", "Teeth and Nutrition", "Exercise and Health",
                    
                    # Material Properties
                    "States of Matter", "Solids, Liquids, Gases", "Melting and Freezing",
                    "Evaporation", "Mixing Materials", "Dissolving", "Filtering", "Magnetism",
                    "Transparent and Opaque", "Flexible and Rigid",
                    
                    # Energy and Forces
                    "Sources of Energy", "Heat Energy", "Light Energy", "Sound Energy",
                    "Electrical Energy", "Wind Energy", "Water Energy", "Force and Motion",
                    "Friction", "Gravity", "Levers", "Pulleys",
                    
                    # Earth Systems
                    "Water Cycle", "Clouds and Rain", "Weather Patterns", "Climate",
                    "Rocks and Minerals", "Soil Formation", "Erosion", "Volcanoes", "Earthquakes"
                ],
                
                3: [
                    # Biological Sciences
                    "Classification of Living Things", "Vertebrates and Invertebrates", "Plant Structure",
                    "Photosynthesis", "Respiration", "Food Webs", "Ecosystems", "Biodiversity",
                    "Endangered Species", "Conservation", "Human Impact on Environment",
                    "Digestive System", "Circulatory System", "Respiratory System",
                    
                    # Physical Sciences
                    "Properties of Materials", "Chemical Changes", "Physical Changes",
                    "States of Matter Changes", "Solutions and Mixtures", "Acids and Bases",
                    "Electricity and Circuits", "Conductors and Insulators", "Static Electricity",
                    "Light and Shadow", "Reflection", "Refraction", "Sound Waves",
                    
                    # Earth and Space Sciences
                    "Solar System", "Planets", "Moon Phases", "Gravity", "Tides",
                    "Rock Cycle", "Fossils", "Geological Time", "Natural Disasters",
                    "Climate Change", "Renewable Energy", "Environmental Protection"
                ],
                
                4: [
                    # Advanced Biology
                    "Cells", "Microscopy", "Single-celled Organisms", "Multi-cellular Organisms",
                    "Genetics", "Heredity", "DNA", "Evolution", "Natural Selection",
                    "Symbiosis", "Parasitism", "Mutualism", "Predator-Prey Relationships",
                    "Population Dynamics", "Ecological Succession", "Biomes",
                    
                    # Advanced Chemistry
                    "Atomic Structure", "Elements and Compounds", "Periodic Table",
                    "Chemical Reactions", "Combustion", "Oxidation", "Acids, Bases, Salts",
                    "pH Scale", "Crystals", "Polymers", "Biochemistry", "Enzymes",
                    
                    # Advanced Physics
                    "Forces and Motion", "Newton's Laws", "Energy Transformations",
                    "Mechanical Energy", "Thermal Energy", "Electromagnetic Spectrum",
                    "Waves", "Frequency", "Amplitude", "Resonance", "Simple Machines",
                    
                    # Environmental Science
                    "Human Impact", "Pollution", "Global Warming", "Ozone Depletion",
                    "Deforestation", "Sustainable Development", "Alternative Energy",
                    "Recycling", "Carbon Footprint", "Ecological Footprint"
                ],
                
                5: [
                    # Integrated Science
                    "Scientific Method", "Hypothesis Testing", "Variables", "Data Analysis",
                    "Scientific Communication", "Ethics in Science", "Technology and Society",
                    "Interdisciplinary Science", "Systems Thinking", "Modeling",
                    
                    # Advanced Biological Concepts
                    "Molecular Biology", "Protein Synthesis", "Cell Division", "Mitosis", "Meiosis",
                    "Genetic Engineering", "Biotechnology", "Cloning", "Stem Cells",
                    "Immunology", "Vaccines", "Antibiotics", "Disease", "Epidemiology",
                    
                    # Advanced Chemical Concepts
                    "Chemical Bonding", "Ionic Bonds", "Covalent Bonds", "Molecular Shapes",
                    "Chemical Kinetics", "Catalysts", "Equilibrium", "Thermodynamics",
                    "Organic Chemistry", "Inorganic Chemistry", "Analytical Chemistry",
                    
                    # Advanced Physical Concepts
                    "Quantum Physics", "Relativity", "Nuclear Physics", "Radioactivity",
                    "Particle Physics", "Astronomy", "Cosmology", "Space Exploration",
                    "Nanotechnology", "Materials Science", "Robotics", "Artificial Intelligence"
                ]
            },
            
            # MYP Science (Grades 6-10) - Biology, Chemistry, Physics, Environmental Science
            "Sciences": {
                6: [
                    # Biology
                    "Cell Theory", "Cell Structure", "Cell Organelles", "Cell Membrane", "Diffusion", "Osmosis",
                    "Photosynthesis", "Cellular Respiration", "Classification", "Taxonomy", "Biodiversity",
                    "Ecosystems", "Food Chains", "Food Webs", "Energy Flow", "Nutrient Cycles",
                    "Human Body Systems", "Digestion", "Circulation", "Respiration", "Excretion",
                    
                    # Chemistry
                    "Atomic Structure", "Protons, Neutrons, Electrons", "Periodic Table", "Elements",
                    "Compounds", "Mixtures", "Chemical vs Physical Changes", "Chemical Reactions",
                    "Conservation of Mass", "Acids and Bases", "pH Scale", "Indicators",
                    "Metals and Non-metals", "Chemical Bonding", "Ionic Bonds", "Covalent Bonds",
                    
                    # Physics
                    "Motion", "Speed", "Velocity", "Acceleration", "Forces", "Newton's Laws",
                    "Gravity", "Friction", "Pressure", "Density", "Energy", "Kinetic Energy",
                    "Potential Energy", "Heat", "Temperature", "Light", "Sound", "Waves",
                    "Electricity", "Circuits", "Magnetism", "Electromagnetic Induction"
                ],
                
                7: [
                    # Advanced Biology
                    "Genetics", "DNA Structure", "Chromosomes", "Genes", "Alleles", "Inheritance",
                    "Mendel's Laws", "Genetic Disorders", "Genetic Engineering", "Evolution",
                    "Natural Selection", "Adaptation", "Speciation", "Fossil Evidence",
                    "Comparative Anatomy", "Embryology", "Molecular Evidence", "Biotechnology",
                    
                    # Advanced Chemistry
                    "Chemical Equations", "Balancing Equations", "Stoichiometry", "Mole Concept",
                    "Concentration", "Solutions", "Solubility", "Chemical Kinetics", "Reaction Rates",
                    "Catalysts", "Equilibrium", "Le Chatelier's Principle", "Thermodynamics",
                    "Enthalpy", "Entropy", "Electrochemistry", "Redox Reactions",
                    
                    # Advanced Physics
                    "Wave Properties", "Frequency", "Wavelength", "Amplitude", "Interference",
                    "Diffraction", "Electromagnetic Spectrum", "Optics", "Reflection", "Refraction",
                    "Lenses", "Mirrors", "Nuclear Physics", "Radioactivity", "Half-life",
                    "Nuclear Fission", "Nuclear Fusion", "Particle Physics", "Quantum Mechanics"
                ],
                
                8: [
                    # Molecular Biology
                    "Protein Structure", "Enzymes", "Metabolism", "Cellular Communication",
                    "Signal Transduction", "Gene Expression", "Regulation", "Mutations",
                    "Cancer", "Stem Cells", "Regenerative Medicine", "Immunology",
                    "Vaccines", "Antibodies", "Autoimmune Diseases", "Infectious Diseases",
                    
                    # Organic Chemistry
                    "Carbon Compounds", "Hydrocarbons", "Functional Groups", "Isomers",
                    "Polymers", "Biochemistry", "Carbohydrates", "Lipids", "Proteins", "Nucleic Acids",
                    "Photosynthesis Chemistry", "Cellular Respiration Chemistry", "Fermentation",
                    
                    # Modern Physics
                    "Relativity", "Time Dilation", "Space-time", "Black Holes", "Cosmology",
                    "Big Bang Theory", "Dark Matter", "Dark Energy", "Nanotechnology",
                    "Semiconductors", "Superconductors", "Laser Technology", "Fiber Optics"
                ],
                
                9: [
                    # Advanced Integrated Science
                    "Scientific Research Methods", "Data Analysis", "Statistical Analysis",
                    "Experimental Design", "Peer Review", "Scientific Ethics", "Science Communication",
                    "Interdisciplinary Science", "Systems Biology", "Computational Biology",
                    "Bioinformatics", "Mathematical Modeling", "Simulation", "Artificial Intelligence in Science",
                    
                    # Environmental Science
                    "Ecology", "Population Dynamics", "Community Ecology", "Ecosystem Services",
                    "Conservation Biology", "Climate Science", "Atmospheric Chemistry",
                    "Ocean Chemistry", "Biogeochemical Cycles", "Environmental Toxicology",
                    "Pollution Control", "Renewable Energy", "Sustainability", "Green Chemistry"
                ],
                
                10: [
                    # Pre-DP Science
                    "Advanced Laboratory Techniques", "Instrumental Analysis", "Spectroscopy",
                    "Chromatography", "Microscopy", "Scientific Writing", "Literature Review",
                    "Hypothesis Development", "Independent Research", "Science Fair Projects",
                    "Peer Teaching", "Science Outreach", "Science Policy", "Science and Society",
                    "Emerging Technologies", "Future of Science", "Career Paths in Science"
                ]
            },
            
            # DP Sciences (Grades 11-12) - Biology, Chemistry, Physics
            "Biology": {
                11: [
                    # Core SL/HL Topics
                    "Cell Biology", "Molecular Biology", "Genetics", "Ecology", "Evolution and Biodiversity", "Human Physiology",
                    
                    # Detailed Core Topics
                    "Cell Theory", "Cell Structure", "Membrane Structure", "Membrane Transport", "Origin of Cells",
                    "Cell Division", "Molecules to Metabolism", "Water", "Carbohydrates and Lipids", "Proteins",
                    "Enzymes", "DNA and RNA", "DNA Replication", "Transcription and Translation",
                    "Cell Respiration", "Photosynthesis", "Genes", "Chromosomes", "Meiosis", "Inheritance",
                    "Genetic Modification", "Species and Communities", "Energy Flow", "Nutrient Cycling",
                    "Evidence for Evolution", "Natural Selection", "Classification", "Cladistics",
                    "Digestion and Absorption", "Blood System", "Gas Exchange", "Neurons and Synapses",
                    "Hormones", "Reproduction",
                    
                    # HL Additional Topics
                    "Nucleic Acids", "Metabolism", "Cell Respiration", "Photosynthesis", "Plant Biology",
                    "Genetics and Evolution", "Animal Physiology"
                ],
                
                12: [
                    # Advanced HL Topics and Options
                    "Further Human Physiology", "Plant Biology", "Genetics and Evolution", "Biotechnology and Bioinformatics",
                    "Ecology and Conservation", "Human Evolution", "Physiology of Exercise", "Microbes and Disease",
                    
                    # Option Topics (4 options to choose from)
                    "Neurobiology and Behaviour", "Biotechnology and Bioinformatics", "Ecology and Conservation",
                    "Human Physiology",
                    
                    # Internal Assessment and Extended Essay
                    "Independent Investigation", "Data Collection and Analysis", "Scientific Writing",
                    "Research Methodology", "Statistics in Biology", "Ethical Considerations",
                    "Literature Review", "Scientific Communication", "Peer Review Process"
                ]
            },
            
            "Chemistry": {
                11: [
                    # Core SL/HL Topics
                    "Stoichiometric Relationships", "Atomic Structure", "Periodicity", "Chemical Bonding", "Energetics", 
                    "Chemical Kinetics", "Equilibrium", "Acids and Bases", "Redox Processes", "Organic Chemistry",
                    
                    # Detailed Core Topics
                    "Mole Concept", "Chemical Equations", "Reacting Masses", "Solutions", "Empirical and Molecular Formulas",
                    "Electron Configuration", "Atomic Orbitals", "Ionization Energy", "Electron Affinity",
                    "Periodic Trends", "Chemical Bonding Theory", "VSEPR Theory", "Hybridization",
                    "Intermolecular Forces", "Enthalpy Changes", "Born-Haber Cycles", "Entropy and Gibbs Free Energy",
                    "Rate Laws", "Reaction Mechanisms", "Activation Energy", "Catalysis",
                    "Dynamic Equilibrium", "Le Chatelier's Principle", "Acid-Base Theories", "pH Calculations",
                    "Buffer Solutions", "Indicators", "Oxidation Numbers", "Electrochemical Cells",
                    "Electrolysis", "Functional Groups", "Nomenclature", "Isomerism", "Reaction Mechanisms",
                    
                    # HL Additional Topics
                    "Atomic Structure", "The Periodic Table", "Chemical Bonding and Structure", "Energetics/Thermochemistry",
                    "Chemical Kinetics", "Equilibrium", "Acids and Bases"
                ],
                
                12: [
                    # Advanced HL Topics and Options
                    "Further Organic Chemistry", "The Periodic Table", "Chemical Bonding and Structure",
                    "Energetics/Thermochemistry", "Chemical Kinetics", "Equilibrium", "Acids and Bases",
                    
                    # Option Topics (4 options to choose from)
                    "Materials", "Biochemistry", "Energy", "Medicinal Chemistry",
                    
                    # Practical Chemistry
                    "Laboratory Techniques", "Instrumental Analysis", "Spectroscopy", "Chromatography",
                    "Titrations", "Gravimetric Analysis", "Error Analysis", "Safety Procedures",
                    "Green Chemistry", "Chemical Industry", "Environmental Chemistry"
                ]
            },
            
            "Physics": {
                11: [
                    # Core SL/HL Topics organized by themes
                    "Space, Time and Motion", "The Particulate Nature of Matter", "Wave Behaviour", 
                    "Fields", "Nuclear and Quantum Physics",
                    
                    # Detailed Core Topics
                    "Kinematics", "Forces and Momentum", "Work, Energy and Power", "Rigid Body Mechanics",
                    "Gravitational Fields", "Electric Fields", "Magnetic Fields", "Electromagnetic Induction",
                    "Simple Harmonic Motion", "Wave Characteristics", "Wave Phenomena", "Standing Waves",
                    "Doppler Effect", "Thermal Physics", "Ideal Gases", "Thermodynamics",
                    "Electric Circuits", "Capacitance", "Atomic Structure", "Radioactive Decay",
                    "Nuclear Reactions", "Quantum Mechanics", "Wave-Particle Duality", "Uncertainty Principle",
                    
                    # HL Additional Topics
                    "Wave Phenomena", "Fields", "Electromagnetic Induction", "Quantum and Nuclear Physics"
                ],
                
                12: [
                    # Advanced HL Topics and Options
                    "Relativity", "Engineering Physics", "Imaging", "Astrophysics",
                    
                    # Option Topics (4 options to choose from)
                    "Relativity", "Engineering Physics", "Imaging", "Astrophysics",
                    
                    # Advanced Concepts
                    "Special Relativity", "General Relativity", "Black Holes", "Cosmology",
                    "Particle Physics", "Standard Model", "Quantum Field Theory", "String Theory",
                    "Condensed Matter Physics", "Superconductivity", "Semiconductors", "Nanotechnology"
                ]
            },
            
            # ==================== LANGUAGE & LITERATURE ====================
            "Language & Literature": {
                # PYP Language (Grades 1-5)
                1: [
                    # Oral Language
                    "Listening Skills", "Following Instructions", "Storytelling", "Show and Tell",
                    "Asking Questions", "Expressing Needs", "Conversational Skills", "Phonemic Awareness",
                    "Rhyming", "Sound Recognition", "Voice Modulation", "Pronunciation",
                    
                    # Reading
                    "Letter Recognition", "Phonics", "Sight Words", "Picture Books", "Story Structure",
                    "Beginning, Middle, End", "Characters", "Setting", "Main Ideas", "Predictions",
                    "Comprehension", "Reading Aloud", "Independent Reading", "Fiction vs Non-fiction",
                    
                    # Writing
                    "Letter Formation", "Name Writing", "Copying Words", "Simple Sentences",
                    "Labeling", "List Making", "Story Writing", "Descriptive Words", "Capital Letters",
                    "Periods", "Spacing", "Handwriting", "Creative Expression",
                    
                    # Viewing and Presenting
                    "Visual Literacy", "Picture Interpretation", "Signs and Symbols", "Media Awareness",
                    "Presenting Ideas", "Art and Communication", "Digital Literacy"
                ],
                
                2: [
                    # Advanced Oral Language
                    "Group Discussions", "Formal Presentations", "Poetry Recitation", "Drama",
                    "Role Play", "Interviews", "Debates", "Peer Teaching", "Active Listening",
                    "Critical Listening", "Following Complex Instructions", "Oral Storytelling",
                    
                    # Reading Development
                    "Fluency", "Expression", "Comprehension Strategies", "Making Connections",
                    "Text-to-Self", "Text-to-Text", "Text-to-World", "Inference", "Summarizing",
                    "Genre Recognition", "Poetry", "Drama", "Informational Texts", "Biographies",
                    
                    # Writing Skills
                    "Paragraph Writing", "Topic Sentences", "Supporting Details", "Conclusions",
                    "Narrative Writing", "Descriptive Writing", "Informational Writing", "Opinion Writing",
                    "Research Skills", "Note Taking", "Bibliography", "Editing", "Proofreading",
                    
                    # Media Literacy
                    "Newspaper", "Magazines", "Digital Media", "Video Analysis", "Advertising",
                    "Website Evaluation", "Online Safety", "Digital Citizenship"
                ],
                
                3: [
                    # Literary Analysis
                    "Character Analysis", "Plot Development", "Theme", "Conflict", "Resolution",
                    "Point of View", "Figurative Language", "Metaphor", "Simile", "Personification",
                    "Author's Purpose", "Text Structure", "Compare and Contrast", "Cause and Effect",
                    "Sequence", "Problem and Solution", "Main Idea and Details",
                    
                    # Advanced Writing
                    "Multi-paragraph Essays", "Research Reports", "Creative Writing", "Poetry",
                    "Script Writing", "Persuasive Writing", "Argumentative Writing", "Expository Writing",
                    "Revision Strategies", "Peer Review", "Self-Reflection", "Publishing",
                    
                    # Language Conventions
                    "Grammar", "Parts of Speech", "Verb Tenses", "Subject-Verb Agreement",
                    "Sentence Types", "Complex Sentences", "Punctuation", "Capitalization",
                    "Spelling Patterns", "Vocabulary Development", "Context Clues", "Word Analysis"
                ],
                
                4: [
                    # Literary Studies
                    "Novel Study", "Short Stories", "Poetry Analysis", "Drama", "Mythology",
                    "Folktales", "Historical Fiction", "Science Fiction", "Fantasy", "Mystery",
                    "Literary Devices", "Symbolism", "Irony", "Foreshadowing", "Flashback",
                    "Mood", "Tone", "Author's Craft", "Style", "Voice",
                    
                    # Research and Information
                    "Research Process", "Primary Sources", "Secondary Sources", "Credibility",
                    "Bias", "Fact vs Opinion", "Data Analysis", "Graphic Organizers",
                    "Citation", "Plagiarism", "Academic Integrity", "Presentation Skills",
                    
                    # Advanced Communication
                    "Public Speaking", "Formal Debates", "Panel Discussions", "Interviews",
                    "Multimedia Presentations", "Digital Storytelling", "Podcast Creation",
                    "Video Production", "Social Media Literacy", "Online Collaboration"
                ],
                
                5: [
                    # Advanced Literary Analysis
                    "Literary Criticism", "Cultural Context", "Historical Context", "Social Issues",
                    "Multiple Perspectives", "Bias and Perspective", "Propaganda", "Rhetoric",
                    "Persuasive Techniques", "Logical Fallacies", "Critical Thinking", "Synthesis",
                    
                    # Advanced Writing Forms
                    "Research Papers", "Literary Essays", "Personal Narratives", "Memoirs",
                    "Journalism", "Feature Articles", "Editorials", "Reviews", "Screenwriting",
                    "Grant Writing", "Business Writing", "Technical Writing", "Creative Non-fiction",
                    
                    # Global Literature
                    "World Literature", "Cultural Perspectives", "Translation", "Cross-cultural Communication",
                    "Indigenous Literature", "Post-colonial Literature", "Comparative Literature",
                    "Literature and Social Change", "Literature and Identity", "Contemporary Issues"
                ]
            },
            
            # MYP Language and Literature (Grades 6-10)
            "Language and Literature": {
                6: [
                    # Text Analysis
                    "Literary Analysis", "Textual Analysis", "Close Reading", "Annotation", "Context",
                    "Purpose", "Audience", "Style", "Structure", "Language Choices", "Literary Devices",
                    "Narrative Techniques", "Character Development", "Theme Analysis", "Cultural Context",
                    
                    # Creative Expression
                    "Creative Writing", "Poetry", "Short Fiction", "Drama", "Script Writing",
                    "Personal Writing", "Reflective Writing", "Imaginative Writing", "Experimental Forms",
                    
                    # Communication Skills
                    "Oral Presentations", "Discussions", "Debates", "Interviews", "Dramatic Performance",
                    "Multimedia Presentations", "Digital Storytelling", "Podcast Creation"
                ],
                
                7: [
                    # Advanced Analysis
                    "Comparative Analysis", "Intertextuality", "Genre Studies", "Historical Context",
                    "Social Commentary", "Political Context", "Feminist Criticism", "Post-colonial Criticism",
                    "Psychological Criticism", "Archetypal Criticism", "Reader Response Theory",
                    
                    # Research and Inquiry
                    "Research Methodology", "Source Evaluation", "Academic Writing", "Documentation",
                    "Synthesis", "Original Thesis", "Evidence", "Counter-arguments", "Scholarly Voice",
                    
                    # Global Perspectives
                    "World Literature", "Translation Studies", "Cultural Identity", "Diaspora Literature",
                    "Indigenous Voices", "Marginalized Perspectives", "Literature and Human Rights"
                ],
                
                8: [
                    # Critical Theory
                    "Literary Theory", "Formalism", "Structuralism", "Post-structuralism", "Deconstruction",
                    "Marxist Criticism", "Psychoanalytic Criticism", "New Historicism", "Cultural Studies",
                    
                    # Advanced Writing
                    "Scholarly Writing", "Literary Criticism", "Research Papers", "Conference Presentations",
                    "Peer Review", "Editorial Process", "Publication", "Academic Discourse",
                    
                    # Media and Technology
                    "Digital Humanities", "Hypertext", "Interactive Media", "Virtual Reality Literature",
                    "AI and Literature", "Digital Publishing", "Online Communities", "Transmedia Storytelling"
                ],
                
                9: [
                    # Independent Study
                    "Personal Interest Project", "Extended Reading", "Author Study", "Genre Study",
                    "Thematic Study", "Comparative Study", "Original Research", "Creative Project",
                    
                    # Advanced Communication
                    "Academic Conferences", "Public Presentations", "Community Engagement", "Literary Events",
                    "Workshop Leadership", "Peer Mentoring", "Teaching Skills", "Outreach Programs",
                    
                    # Preparation for DP
                    "DP Preparation", "Extended Essay", "Individual Oral", "Higher Level Essay",
                    "Works in Translation", "Comparative Study", "Time Management", "Study Skills"
                ],
                
                10: [
                    # Culminating Projects
                    "Portfolio Development", "Reflection", "Self-Assessment", "Goal Setting",
                    "University Preparation", "Career Exploration", "Scholarship Applications",
                    "Personal Statement Writing", "Interview Skills", "Life Skills"
                ]
            },
            
            # DP Language A: Literature and Language A: Language and Literature (Grades 11-12)
            "English Literature": {
                11: [
                    # Core Components
                    "Readers, Writers and Texts", "Time and Space", "Intertextuality",
                    
                    # Areas of Exploration
                    "Readers, Writers and Texts", "Time and Space", "Intertextuality: Connecting Texts",
                    
                    # Literary Genres
                    "Poetry", "Prose", "Drama", "Non-fiction", "Graphic Novels", "Digital Literature",
                    
                    # Critical Approaches
                    "Close Reading", "Contextual Analysis", "Comparative Analysis", "Literary Criticism",
                    "Cultural Context", "Historical Context", "Biographical Context", "Genre Theory",
                    
                    # Assessment Components
                    "Individual Oral", "Higher Level Essay", "Paper 1: Guided Literary Analysis",
                    "Paper 2: Comparative Essay", "Works in Translation"
                ],
                
                12: [
                    # Advanced Study
                    "Independent Reading", "Research Project", "Extended Essay", "University Preparation",
                    "Career Planning", "Graduate School Preparation", "Professional Writing",
                    "Literary Scholarship", "Creative Writing Portfolio", "Publication Process"
                ]
            },
            
            # ==================== INDIVIDUALS AND SOCIETIES ====================
            "Individuals & Societies": {
                # PYP Social Studies (Grades 1-5)
                1: [
                    # Who We Are
                    "Self-Identity", "Family", "Friends", "Community", "Similarities and Differences",
                    "Needs and Wants", "Rights and Responsibilities", "Rules", "Fairness",
                    
                    # Where We Are in Place and Time
                    "Home", "School", "Neighborhood", "Past and Present", "Time", "Sequence",
                    "Maps", "Directions", "Local History", "Traditions",
                    
                    # How We Express Ourselves
                    "Communication", "Languages", "Art", "Music", "Dance", "Celebrations",
                    "Symbols", "Stories", "Cultural Expression",
                    
                    # How the World Works
                    "Natural World", "Human-made World", "Systems", "Patterns", "Connections",
                    
                    # How We Organize Ourselves
                    "Groups", "Organizations", "Leaders", "Jobs", "Services", "Government",
                    
                    # Sharing the Planet
                    "Environment", "Animals", "Plants", "Conservation", "Sharing Resources"
                ],
                
                2: [
                    # Expanded Social Concepts
                    "Communities", "Cultures", "Diversity", "Immigration", "Migration", "Citizenship",
                    "Democracy", "Voting", "Laws", "Consequences", "Conflict Resolution",
                    "Peace", "Justice", "Human Rights", "Children's Rights",
                    
                    # Geography Skills
                    "Continents", "Countries", "Oceans", "Landforms", "Weather", "Climate",
                    "Natural Resources", "Population", "Urban", "Rural", "Transportation",
                    
                    # Historical Thinking
                    "Timeline", "Chronology", "Change", "Continuity", "Cause and Effect",
                    "Historical Sources", "Artifacts", "Primary Sources", "Secondary Sources"
                ],
                
                3: [
                    # Global Awareness
                    "World Cultures", "Religion", "Beliefs", "Values", "Traditions", "Customs",
                    "International Organizations", "United Nations", "UNICEF", "Global Issues",
                    "Poverty", "Education", "Health", "Water", "Food Security",
                    
                    # Economic Concepts
                    "Producers", "Consumers", "Goods", "Services", "Trade", "Money", "Banking",
                    "Supply and Demand", "Scarcity", "Choice", "Opportunity Cost",
                    
                    # Civic Engagement
                    "Active Citizenship", "Volunteering", "Community Service", "Social Action",
                    "Advocacy", "Protest", "Civil Rights", "Social Movements"
                ],
                
                4: [
                    # Advanced Social Studies
                    "Civilizations", "Ancient History", "Medieval History", "Renaissance",
                    "Industrial Revolution", "Modern History", "World Wars", "Cold War",
                    "Decolonization", "Globalization", "Contemporary Issues",
                    
                    # Government and Politics
                    "Political Systems", "Monarchy", "Republic", "Democracy", "Dictatorship",
                    "Constitution", "Separation of Powers", "Elections", "Political Parties",
                    "International Relations", "Diplomacy", "Conflict", "Peace-making",
                    
                    # Research Skills
                    "Historical Research", "Geographic Research", "Data Collection", "Surveys",
                    "Interviews", "Archival Research", "Digital Research", "Source Analysis"
                ],
                
                5: [
                    # Preparation for MYP
                    "Critical Thinking", "Analysis", "Evaluation", "Synthesis", "Argumentation",
                    "Evidence", "Perspective", "Bias", "Reliability", "Validity", "Significance",
                    "Independent Research", "Academic Writing", "Presentation Skills", "Debate"
                ]
            },
            
            # MYP Individuals and Societies (Grades 6-10)
            "Individuals and Societies": {
                6: [
                    # History
                    "Ancient Civilizations", "Classical Civilizations", "Medieval Period", "Renaissance",
                    "Age of Exploration", "Colonialism", "Industrial Revolution", "World Wars",
                    "Cold War", "Decolonization", "Modern World", "Historical Methodology",
                    "Primary Sources", "Secondary Sources", "Historical Interpretation", "Causation",
                    "Consequence", "Change and Continuity", "Historical Significance",
                    
                    # Geography
                    "Physical Geography", "Human Geography", "Population", "Migration", "Urbanization",
                    "Development", "Sustainability", "Climate Change", "Natural Disasters",
                    "Resource Management", "Geographic Information Systems", "Cartography",
                    
                    # Economics
                    "Economic Systems", "Market Economy", "Command Economy", "Mixed Economy",
                    "Supply and Demand", "Inflation", "Unemployment", "Economic Growth",
                    "International Trade", "Globalization", "Development Economics"
                ],
                
                7: [
                    # Advanced History
                    "Comparative History", "Thematic History", "Social History", "Cultural History",
                    "Political History", "Economic History", "Gender History", "Environmental History",
                    "Oral History", "Public History", "Digital History", "Microhistory",
                    
                    # Political Science
                    "Government Systems", "Democracy", "Authoritarianism", "Federalism",
                    "Human Rights", "Civil Rights", "Political Participation", "Citizenship",
                    "Political Ideologies", "Nationalism", "Internationalism", "Global Governance",
                    
                    # Sociology
                    "Social Structures", "Social Class", "Social Mobility", "Social Change",
                    "Culture", "Socialization", "Identity", "Community", "Social Problems"
                ],
                
                8: [
                    # Research Methods
                    "Social Science Research", "Quantitative Methods", "Qualitative Methods",
                    "Data Analysis", "Statistics", "Surveys", "Interviews", "Ethnography",
                    "Case Studies", "Comparative Analysis", "Ethics in Research",
                    
                    # Global Issues
                    "Poverty", "Inequality", "Education", "Health", "Environment", "Technology",
                    "Globalization", "Cultural Diversity", "Human Rights", "Conflict Resolution",
                    "Sustainable Development", "Social Justice", "Global Citizenship"
                ],
                
                9: [
                    # Independent Research
                    "Personal Interest Project", "Community Study", "Historical Investigation",
                    "Geographic Fieldwork", "Economic Analysis", "Political Analysis",
                    "Social Research", "Cultural Study", "Comparative Study",
                    
                    # Advanced Skills
                    "Critical Analysis", "Evaluation", "Synthesis", "Argumentation", "Perspective",
                    "Academic Writing", "Presentation Skills", "Digital Literacy", "Media Literacy"
                ],
                
                10: [
                    # Culminating Experience
                    "Community Project", "Action Research", "Social Action", "Advocacy",
                    "Service Learning", "Internship", "Mentorship", "Leadership",
                    "Reflection", "Self-Assessment", "Goal Setting", "Future Planning"
                ]
            },
            
            # DP Group 3: Individuals and Societies (Grades 11-12)
            "History": {
                11: [
                    # Prescribed Subjects
                    "Military Leaders", "Conquest and its Impact", "The Move to Global War",
                    "Rights and Protest", "Conflict and Intervention",
                    
                    # World History Topics
                    "Society and Economy", "Causes and Effects of Wars", "Authoritarian States",
                    "Independence Movements", "Evolution of Democratic States",
                    
                    # Higher Level Topics
                    "History of Africa and the Middle East", "History of the Americas",
                    "History of Asia and Oceania", "History of Europe",
                    
                    # Historical Investigation", "Extended Essay", "Internal Assessment"
                ],
                
                12: [
                    # Advanced Study
                    "Historiography", "Historical Debates", "Multiple Perspectives", "Bias",
                    "Reliability", "University Preparation", "Graduate Studies", "Career Planning"
                ]
            },
            
            "Geography": {
                11: [
                    # Core Theme
                    "Changing Population", "Global Climate", "Global Resource Consumption and Security",
                    
                    # Optional Themes
                    "Freshwater", "Oceans and Coastal Margins", "Extreme Environments",
                    "Hazards and Disasters", "Leisure, Tourism and Sport", "Food and Health",
                    "Urban Environments",
                    
                    # Higher Level Extension
                    "Global Interactions", "Geographic Information Systems", "Remote Sensing",
                    "Fieldwork", "Internal Assessment"
                ],
                
                12: [
                    # Advanced Geographic Analysis
                    "Geographic Perspectives", "Spatial Analysis", "Systems Thinking",
                    "Sustainability", "Global Citizenship", "Research Methods", "Career Planning"
                ]
            },
            
            "Economics": {
                11: [
                    # Microeconomics
                    "Competitive Markets", "Elasticity", "Government Intervention", "Market Failure",
                    "Theory of the Firm", "Market Structures",
                    
                    # Macroeconomics
                    "Economic Activity", "Aggregate Demand and Supply", "Macroeconomic Objectives",
                    "Fiscal Policy", "Monetary Policy", "Supply-side Policies",
                    
                    # International Economics
                    "Trade", "Exchange Rates", "Balance of Payments", "Economic Integration",
                    "Terms of Trade",
                    
                    # Development Economics (HL)
                    "Economic Development", "Measuring Development", "Barriers to Development",
                    "Growth and Development Strategies"
                ],
                
                12: [
                    # Advanced Economic Analysis
                    "Economic Research", "Data Analysis", "Economic Models", "Policy Analysis",
                    "Current Economic Issues", "Economic Commentary", "Extended Essay"
                ]
            },
            
            # ==================== ARTS ====================
            "Arts": {
                # PYP Arts (Grades 1-5)
                1: [
                    # Visual Arts
                    "Drawing", "Painting", "Coloring", "Cutting", "Pasting", "Collage", "Sculpture",
                    "Clay Work", "Paper Crafts", "Texture", "Color", "Shape", "Line", "Pattern",
                    "Art Materials", "Tools", "Techniques", "Creativity", "Expression",
                    
                    # Music
                    "Singing", "Rhythm", "Beat", "Tempo", "Loud and Soft", "High and Low",
                    "Musical Instruments", "Listening", "Movement to Music", "Simple Songs",
                    "Nursery Rhymes", "Folk Songs", "Cultural Music", "Sound Exploration",
                    
                    # Drama
                    "Role Play", "Pretend Play", "Storytelling", "Puppets", "Simple Acting",
                    "Emotions", "Characters", "Movement", "Voice", "Imagination",
                    
                    # Dance
                    "Movement", "Body Parts", "Space", "Direction", "Speed", "Cultural Dances",
                    "Creative Movement", "Rhythm and Movement", "Dance Games"
                ],
                
                2: [
                    # Advanced Visual Arts
                    "Color Theory", "Primary Colors", "Secondary Colors", "Color Mixing",
                    "Warm and Cool Colors", "Landscape", "Portrait", "Still Life", "Abstract Art",
                    "Printmaking", "Mixed Media", "Art History", "Famous Artists", "Art Styles",
                    
                    # Music Development
                    "Note Reading", "Staff", "Treble Clef", "Note Values", "Time Signature",
                    "Musical Symbols", "Dynamics", "Composition", "Simple Instruments",
                    "Recorder", "Percussion", "Ensemble", "Concert Performance",
                    
                    # Theatre Arts
                    "Script Reading", "Character Development", "Costume", "Props", "Stage",
                    "Audience", "Performance", "Theatre Etiquette", "Different Cultures",
                    
                    # Movement and Dance
                    "Dance Styles", "Ballet", "Folk Dance", "Modern Dance", "Choreography",
                    "Dance Notation", "Cultural Context", "Dance History"
                ],
                
                3: [
                    # Artistic Expression
                    "Personal Style", "Artistic Voice", "Cultural Art", "Art from Different Countries",
                    "Art and Society", "Art and History", "Art Criticism", "Art Appreciation",
                    "Museum Studies", "Gallery Visits", "Art Exhibitions", "Digital Art",
                    
                    # Musical Literacy
                    "Music Theory", "Scales", "Key Signatures", "Intervals", "Chords",
                    "Musical Forms", "ABA Form", "Theme and Variations", "Music History",
                    "Classical Music", "Jazz", "World Music", "Music and Culture",
                    
                    # Performance Arts
                    "Public Speaking", "Stage Presence", "Improvisation", "Monologue",
                    "Dialogue", "Stage Directions", "Technical Theatre", "Lighting", "Sound",
                    
                    # Creative Movement
                    "Contemporary Dance", "Jazz Dance", "Hip Hop", "Cultural Dances",
                    "Dance Composition", "Group Choreography", "Dance Video", "Dance Criticism"
                ],
                
                4: [
                    # Advanced Artistic Concepts
                    "Art Movements", "Renaissance", "Impressionism", "Modern Art", "Contemporary Art",
                    "Art and Technology", "Digital Media", "Photography", "Video Art",
                    "Installation Art", "Performance Art", "Conceptual Art", "Art Therapy",
                    
                    # Advanced Music
                    "Advanced Theory", "Composition Techniques", "Song Writing", "Music Production",
                    "Recording", "Music Business", "Copyright", "Music and Technology",
                    "Electronic Music", "Music Genres", "Cross-cultural Music", "Music Research",
                    
                    # Advanced Theatre
                    "Playwriting", "Directing", "Stage Management", "Theatre History",
                    "Shakespeare", "Musical Theatre", "Opera", "Film", "Television",
                    "Media Studies", "Digital Storytelling", "Animation",
                    
                    # Professional Dance
                    "Dance Training", "Dance Technique", "Dance Pedagogy", "Dance Therapy",
                    "Dance and Health", "Professional Dance", "Dance Career", "Dance Criticism"
                ],
                
                5: [
                    # Integrated Arts
                    "Interdisciplinary Arts", "Arts and Other Subjects", "Arts and Science",
                    "Arts and Mathematics", "Arts and Literature", "Arts and Social Studies",
                    "Community Arts", "Arts Advocacy", "Arts Education", "Arts Policy",
                    "Arts and Social Change", "Arts and Identity", "Arts and Healing"
                ]
            },
            
            # MYP Arts (Grades 6-10)
            "Arts": {
                6: [
                    # Visual Arts
                    "Drawing Techniques", "Painting Methods", "Sculpture", "Printmaking", "Digital Art",
                    "Photography", "Mixed Media", "Installation", "Art History", "Art Criticism",
                    "Cultural Context", "Personal Expression", "Technical Skills", "Creative Process",
                    
                    # Music
                    "Music Theory", "Composition", "Performance", "Music History", "Cultural Music",
                    "Technology in Music", "Ensemble Work", "Solo Performance", "Music Analysis",
                    "Improvisation", "Song Writing", "Music Production",
                    
                    # Drama
                    "Acting Techniques", "Script Analysis", "Character Development", "Stage Craft",
                    "Theatre History", "Cultural Theatre", "Improvisation", "Devised Theatre",
                    "Technical Theatre", "Directing", "Playwriting",
                    
                    # Dance
                    "Dance Techniques", "Choreography", "Dance History", "Cultural Dance",
                    "Dance Analysis", "Movement Study", "Dance and Technology", "Performance",
                    "Dance Notation", "Dance Criticism"
                ],
                
                7: [
                    # Advanced Artistic Skills
                    "Portfolio Development", "Artist Statement", "Research Skills", "Critical Analysis",
                    "Comparative Studies", "Cross-cultural Arts", "Contemporary Issues in Arts",
                    "Arts and Society", "Arts and Politics", "Arts and Environment",
                    
                    # Interdisciplinary Arts
                    "Multimedia", "Performance Art", "Video Art", "Sound Art", "Interactive Art",
                    "Virtual Reality", "Augmented Reality", "AI in Arts", "Digital Humanities"
                ],
                
                8: [
                    # Professional Development
                    "Arts Careers", "Arts Business", "Arts Management", "Arts Therapy", "Arts Education",
                    "Community Arts", "Public Art", "Gallery Management", "Museum Studies",
                    "Arts Journalism", "Arts Criticism", "Arts Policy", "Cultural Policy",
                    
                    # Creative Industries
                    "Film Industry", "Music Industry", "Gaming Industry", "Advertising", "Fashion",
                    "Design", "Architecture", "Interior Design", "Graphic Design", "Web Design"
                ],
                
                9: [
                    # Independent Projects
                    "Personal Interest Project", "Community Arts Project", "Collaborative Work",
                    "Exhibition", "Performance", "Concert", "Festival", "Competition",
                    "Arts Outreach", "Teaching", "Mentoring", "Leadership",
                    
                    # Preparation for DP
                    "Portfolio Preparation", "Exhibition Planning", "Research Project", "Extended Study"
                ],
                
                10: [
                    # Culminating Experience
                    "Final Exhibition", "Performance Showcase", "Reflection", "Self-Assessment",
                    "Peer Assessment", "Community Feedback", "Future Planning", "University Preparation"
                ]
            },
            
            # DP Arts (Grades 11-12)
            "Visual Arts": {
                11: [
                    # Core Portfolio
                    "Comparative Study", "Process Portfolio", "Exhibition",
                    
                    # Visual Arts in Context
                    "Art History", "Cultural Context", "Contemporary Art", "Art Criticism",
                    "Art Theory", "Visual Culture", "Museums and Galleries", "Art Movements",
                    
                    # Visual Arts Methods
                    "Drawing", "Painting", "Sculpture", "Printmaking", "Photography", "Digital Media",
                    "Installation", "Performance", "Video", "Mixed Media", "Experimental Media",
                    
                    # Communicating Visual Arts
                    "Artist Statement", "Reflection", "Research", "Documentation", "Critique",
                    "Presentation", "Exhibition Design", "Curatorial Practice"
                ],
                
                12: [
                    # Advanced Portfolio Development
                    "Professional Portfolio", "University Application Portfolio", "Scholarship Applications",
                    "Gallery Submissions", "Competition Entries", "Art Residencies", "Internships",
                    "Career Planning", "Graduate School Preparation", "Professional Networking"
                ]
            },
            
            "Music": {
                11: [
                    # Core Components
                    "Exploring Music in Context", "Experimenting with Music", "Presenting Music",
                    
                    # Music in Context
                    "Music History", "Cultural Music", "World Music", "Popular Music", "Classical Music",
                    "Jazz", "Electronic Music", "Film Music", "Music and Society", "Music Industry",
                    
                    # Music Theory and Analysis
                    "Harmony", "Counterpoint", "Form and Analysis", "Orchestration", "Arranging",
                    "Music Technology", "Recording", "Production", "Sound Design",
                    
                    # Performance and Composition
                    "Solo Performance", "Ensemble Performance", "Conducting", "Composition",
                    "Improvisation", "Song Writing", "Music Theatre", "Opera"
                ],
                
                12: [
                    # Advanced Musical Studies
                    "Music Research", "Ethnomusicology", "Music Psychology", "Music Therapy",
                    "Music Education", "Music Business", "Copyright Law", "Music Journalism",
                    "Concert Production", "Music Festival Management", "Recording Industry"
                ]
            },
            
            "Theatre": {
                11: [
                    # Core Elements
                    "Theatre in Context", "Theatre Processes", "Presenting Theatre",
                    
                    # Theatre History and Styles
                    "Ancient Theatre", "Medieval Theatre", "Renaissance Theatre", "Modern Theatre",
                    "Contemporary Theatre", "World Theatre", "Cultural Theatre", "Political Theatre",
                    "Experimental Theatre", "Devised Theatre", "Physical Theatre", "Musical Theatre",
                    
                    # Theatre Skills
                    "Acting", "Directing", "Playwriting", "Stage Design", "Costume Design",
                    "Lighting Design", "Sound Design", "Stage Management", "Dramaturgy",
                    
                    # Theatre Research and Analysis
                    "Script Analysis", "Character Analysis", "Production Analysis", "Theatre Criticism",
                    "Theatre Reviews", "Research Project", "Independent Study"
                ],
                
                12: [
                    # Professional Theatre
                    "Theatre Careers", "Theatre Business", "Arts Administration", "Theatre Education",
                    "Community Theatre", "Theatre Therapy", "Applied Theatre", "Theatre Outreach",
                    "International Theatre", "Theatre Technology", "Digital Theatre"
                ]
            },
            
            "Film": {
                11: [
                    # Core Components
                    "Film in Context", "Film Production", "Film Analysis",
                    
                    # Film History and Theory
                    "Film History", "Film Movements", "Genre Studies", "Auteur Theory",
                    "Film Criticism", "Documentary Film", "Experimental Film", "World Cinema",
                    "Digital Cinema", "Streaming Media", "Virtual Reality Film",
                    
                    # Film Production Skills
                    "Screenwriting", "Directing", "Cinematography", "Editing", "Sound Design",
                    "Production Design", "Producing", "Distribution", "Marketing",
                    
                    # Film Analysis
                    "Visual Language", "Narrative Structure", "Character Development", "Mise-en-scène",
                    "Montage", "Sound and Image", "Performance Analysis", "Cultural Context"
                ],
                
                12: [
                    # Film Industry and Careers
                    "Film Industry", "Independent Film", "Film Festivals", "Film Distribution",
                    "Film Marketing", "Film Criticism", "Film Journalism", "Film Education",
                    "Film Preservation", "Film Archives", "Digital Media", "New Technologies"
                ]
            },
            
            # ==================== PHYSICAL & HEALTH EDUCATION ====================
            "Physical & Health Education": {
                # PYP Physical Education (Grades 1-5)
                1: [
                    # Movement Skills
                    "Locomotor Skills", "Walking", "Running", "Jumping", "Hopping", "Skipping",
                    "Galloping", "Sliding", "Leaping", "Marching", "Crawling", "Rolling",
                    
                    # Non-Locomotor Skills
                    "Stretching", "Bending", "Twisting", "Turning", "Pushing", "Pulling",
                    "Lifting", "Swinging", "Swaying", "Balancing", "Dodging",
                    
                    # Manipulative Skills
                    "Throwing", "Catching", "Kicking", "Striking", "Bouncing", "Rolling a Ball",
                    "Dribbling", "Volleying", "Punting", "Juggling",
                    
                    # Health and Safety
                    "Personal Hygiene", "Healthy Foods", "Exercise", "Rest", "Safety Rules",
                    "Playground Safety", "Water Safety", "Fire Safety", "Stranger Safety"
                ],
                
                2: [
                    # Advanced Movement
                    "Coordination", "Rhythm", "Timing", "Flow", "Force", "Speed", "Direction",
                    "Level", "Pathway", "Relationships", "Teamwork", "Cooperation",
                    
                    # Games and Sports
                    "Simple Games", "Tag Games", "Ball Games", "Relay Races", "Obstacle Courses",
                    "Parachute Games", "Dance Games", "Singing Games", "Cultural Games",
                    
                    # Health Education
                    "Nutrition", "Food Groups", "Exercise Benefits", "Heart Rate", "Muscles",
                    "Bones", "Flexibility", "Strength", "Endurance", "Body Systems"
                ],
                
                3: [
                    # Sport Skills
                    "Basketball", "Soccer", "Volleyball", "Tennis", "Baseball", "Softball",
                    "Track and Field", "Swimming", "Gymnastics", "Martial Arts", "Yoga",
                    
                    # Fitness Concepts
                    "Physical Fitness", "Cardiovascular Fitness", "Muscular Strength",
                    "Muscular Endurance", "Flexibility", "Body Composition", "Fitness Testing",
                    "Goal Setting", "Exercise Planning", "Warm-up", "Cool-down",
                    
                    # Health Topics
                    "Growth and Development", "Puberty", "Mental Health", "Stress Management",
                    "Conflict Resolution", "Bullying Prevention", "Internet Safety", "Drug Education"
                ],
                
                4: [
                    # Advanced Sports
                    "Sport Rules", "Sport Strategies", "Teamwork", "Leadership", "Sportsmanship",
                    "Fair Play", "Competition", "Officials", "Scoring", "Positions", "Tactics",
                    
                    # Health and Wellness
                    "Wellness", "Lifestyle Choices", "Disease Prevention", "First Aid", "CPR",
                    "Emergency Procedures", "Environmental Health", "Community Health",
                    "Global Health Issues", "Health Advocacy"
                ],
                
                5: [
                    # Preparation for MYP
                    "Advanced Fitness", "Sport Science", "Biomechanics", "Exercise Physiology",
                    "Sports Psychology", "Nutrition Science", "Training Principles", "Injury Prevention",
                    "Sports Medicine", "Athletic Performance", "Technology in Sports"
                ]
            },
            
            # MYP Physical & Health Education (Grades 6-10)
            "Physical and Health Education": {
                6: [
                    # Physical Development
                    "Motor Skills", "Coordination", "Balance", "Agility", "Power", "Speed",
                    "Reaction Time", "Movement Efficiency", "Skill Acquisition", "Motor Learning",
                    
                    # Health Education
                    "Adolescent Development", "Physical Changes", "Emotional Changes", "Social Changes",
                    "Identity Formation", "Self-Esteem", "Body Image", "Peer Pressure", "Decision Making",
                    
                    # Fitness and Training
                    "Training Principles", "FITT Principle", "Progressive Overload", "Specificity",
                    "Reversibility", "Individual Differences", "Periodization", "Recovery"
                ],
                
                7: [
                    # Advanced Health Topics
                    "Nutrition Science", "Macronutrients", "Micronutrients", "Hydration", "Sports Nutrition",
                    "Eating Disorders", "Substance Abuse", "Mental Health", "Depression", "Anxiety",
                    "Suicide Prevention", "Help-Seeking Behaviors", "Support Systems",
                    
                    # Movement Analysis
                    "Biomechanics", "Force", "Motion", "Levers", "Projectile Motion", "Center of Gravity",
                    "Balance", "Stability", "Efficiency", "Technique Analysis", "Performance Enhancement"
                ],
                
                8: [
                    # Global Health Issues
                    "Communicable Diseases", "Non-communicable Diseases", "Pandemics", "Public Health",
                    "Health Promotion", "Health Education", "Health Policy", "Environmental Health",
                    "Social Determinants of Health", "Health Equity", "Global Health Organizations",
                    
                    # Sport Science
                    "Exercise Physiology", "Energy Systems", "Aerobic System", "Anaerobic Systems",
                    "VO2 Max", "Lactate Threshold", "Heart Rate Training", "Training Zones",
                    "Performance Testing", "Data Analysis", "Technology in Sport"
                ],
                
                9: [
                    # Advanced Concepts
                    "Sports Psychology", "Motivation", "Goal Setting", "Confidence", "Anxiety Management",
                    "Mental Training", "Visualization", "Relaxation Techniques", "Team Dynamics",
                    "Leadership", "Communication", "Coaching", "Sport Ethics", "Doping",
                    
                    # Research and Analysis
                    "Research Methods", "Data Collection", "Statistical Analysis", "Scientific Writing",
                    "Literature Review", "Critical Thinking", "Evidence-Based Practice"
                ],
                
                10: [
                    # Culminating Projects
                    "Independent Research", "Community Health Project", "Fitness Program Design",
                    "Coaching Experience", "Teaching Experience", "Health Advocacy", "Policy Analysis",
                    "Career Exploration", "University Preparation", "Portfolio Development"
                ]
            },
            
            # DP Physical Education (Grades 11-12)
            "Sports, Exercise and Health Science": {
                11: [
                    # Core Topics
                    "Anatomy and Physiology", "Exercise Physiology", "Energy Systems", "Movement Analysis",
                    "Skill in Sport", "Measurement and Evaluation of Human Performance",
                    
                    # Option Topics
                    "Optimizing Physiological Performance", "Psychology of Sport", "Physical Activity and Health",
                    "Nutrition for Sport, Exercise and Health",
                    
                    # Practical Component
                    "Practical Activities", "Performance Analysis", "Fitness Testing", "Laboratory Work",
                    "Field Studies", "Research Project", "Internal Assessment"
                ],
                
                12: [
                    # Advanced Study
                    "Research in Sport Science", "Current Issues", "Emerging Technologies",
                    "Career Pathways", "Graduate Studies", "Professional Development",
                    "Sports Industry", "Health Promotion", "Exercise Prescription"
                ]
            },
            
            # ==================== DESIGN ====================
            "Design": {
                # MYP Design (Grades 6-10)
                6: [
                    # Design Cycle
                    "Inquiring and Analyzing", "Developing Ideas", "Creating the Solution", "Evaluating",
                    
                    # Design Contexts
                    "Product Design", "Digital Design", "Engineering Design", "Fashion Design",
                    "Architectural Design", "Graphic Design", "Game Design", "App Design",
                    
                    # Design Skills
                    "Research", "Analysis", "Ideation", "Sketching", "Modeling", "Prototyping",
                    "Testing", "Iteration", "Evaluation", "Reflection", "Communication"
                ],
                
                7: [
                    # Advanced Design
                    "User-Centered Design", "Human Factors", "Ergonomics", "Accessibility",
                    "Sustainability", "Circular Design", "Life Cycle Analysis", "Material Selection",
                    "Manufacturing Processes", "Quality Control", "Safety", "Ethics in Design"
                ],
                
                8: [
                    # Design Technology
                    "CAD Software", "3D Modeling", "3D Printing", "Laser Cutting", "CNC Machining",
                    "Electronics", "Programming", "Sensors", "Actuators", "Microcontrollers",
                    "Internet of Things", "Artificial Intelligence", "Machine Learning"
                ],
                
                9: [
                    # Design Innovation
                    "Innovation Process", "Creative Problem Solving", "Design Thinking",
                    "Entrepreneurship", "Business Model", "Marketing", "Intellectual Property",
                    "Patents", "Trademarks", "Copyright", "Open Source", "Collaboration"
                ],
                
                10: [
                    # Design Portfolio
                    "Portfolio Development", "Design Documentation", "Presentation Skills",
                    "Client Relations", "Project Management", "Time Management", "Teamwork",
                    "Leadership", "Career Planning", "University Preparation"
                ]
            },
            
            # DP Design Technology (Grades 11-12)
            "Design Technology": {
                11: [
                    # Core Topics
                    "Human Factors Design", "Resource Management and Sustainable Production",
                    "Modelling", "Raw Material to Final Product", "Innovation and Design",
                    "Classic Design",
                    
                    # Option Topics
                    "Modern Technology", "Additional Higher Level",
                    
                    # Design Project
                    "Analysis of Need", "Conceptual Design", "Detailed Design", "Testing and Evaluation"
                ],
                
                12: [
                    # Advanced Design
                    "Professional Practice", "Design Management", "Innovation Management",
                    "Technology Transfer", "Design Research", "Future Technologies",
                    "Emerging Materials", "Smart Materials", "Nanotechnology"
                ]
            },
            
            # ==================== ADDITIONAL SUBJECTS ====================
            "Computer Science": {
                # MYP Design/Computer Science preparation
                8: [
                    "Programming Fundamentals", "Algorithms", "Data Structures", "Problem Solving",
                    "Computer Systems", "Networks", "Databases", "Web Development", "App Development",
                    "Artificial Intelligence", "Machine Learning", "Cybersecurity", "Digital Ethics"
                ],
                
                9: [
                    "Advanced Programming", "Object-Oriented Programming", "Software Engineering",
                    "System Design", "Human-Computer Interaction", "Computer Graphics", "Game Development",
                    "Robotics", "Internet of Things", "Cloud Computing", "Big Data"
                ],
                
                10: [
                    "Advanced Algorithms", "Data Science", "Machine Learning", "Neural Networks",
                    "Cybersecurity", "Cryptography", "Blockchain", "Quantum Computing", "Ethics in Technology"
                ],
                
                # DP Computer Science (Grades 11-12)
                11: [
                    # Core Topics
                    "System Fundamentals", "Computer Organization", "Networks", "Computational Thinking",
                    "Abstract Data Structures", "Resource Management", "Control",
                    
                    # Higher Level Topics
                    "Further Programming", "Object-Oriented Programming",
                    
                    # Option Topics
                    "Databases", "Modelling and Simulation", "Web Science", "Computer Science"
                ],
                
                12: [
                    "Advanced Computer Science", "Software Engineering", "Artificial Intelligence",
                    "Machine Learning", "Computer Vision", "Natural Language Processing",
                    "Robotics", "Quantum Computing", "Research Project"
                ]
            },
            
            "Environmental Systems and Societies": {
                11: [
                    # Foundation of ESS
                    "Systems and Models", "The Ecosystem", "Biodiversity and Conservation",
                    "Water and Aquatic Food Production Systems", "Soil Systems and Terrestrial Food Production",
                    "Atmospheric Systems and Societies", "Climate Change and Energy Production",
                    "Human Systems and Resource Use"
                ],
                
                12: [
                    "Advanced Environmental Topics", "Environmental Management", "Sustainability",
                    "Environmental Policy", "Global Environmental Issues", "Future Scenarios",
                    "Research Project", "Environmental Action"
                ]
            },
            
            # ==================== LANGUAGE ACQUISITION ====================
            "Language Acquisition": {
                # Second Language Learning across all grades
                1: [
                    "Basic Vocabulary", "Greetings", "Family", "Colors", "Numbers", "Animals",
                    "Food", "Body Parts", "Classroom Objects", "Simple Phrases", "Pronunciation",
                    "Listening Skills", "Speaking Practice", "Cultural Awareness"
                ],
                
                2: [
                    "Expanded Vocabulary", "Simple Sentences", "Present Tense", "Questions",
                    "Descriptions", "Daily Routines", "Hobbies", "Weather", "Clothing",
                    "Shopping", "Transportation", "Basic Reading", "Simple Writing"
                ],
                
                3: [
                    "Grammar Structures", "Past Tense", "Future Tense", "Adjectives", "Adverbs",
                    "Prepositions", "Storytelling", "Descriptions", "Opinions", "Preferences",
                    "Cultural Studies", "Festivals", "Traditions", "Customs"
                ],
                
                4: [
                    "Complex Sentences", "Subjunctive", "Conditional", "Passive Voice", "Direct/Indirect Speech",
                    "Formal/Informal Language", "Register", "Idioms", "Expressions", "Literature",
                    "Media", "Current Events", "Global Issues", "Cross-cultural Communication"
                ],
                
                5: [
                    "Advanced Grammar", "Literary Texts", "Academic Writing", "Research Skills",
                    "Presentation Skills", "Debate", "Discussion", "Critical Thinking",
                    "Language Analysis", "Cultural Analysis", "Comparative Studies"
                ],
                
                # MYP Language Acquisition continues this progression
                6: ["Phase 1-6 Progression based on student level"],
                7: ["Phase 1-6 Progression based on student level"],
                8: ["Phase 1-6 Progression based on student level"],
                9: ["Phase 1-6 Progression based on student level"],
                10: ["Phase 1-6 Progression based on student level"],
                
                # DP Language B (Grades 11-12)
                11: [
                    # Core Themes
                    "Identities", "Experiences", "Human Ingenuity", "Social Organization",
                    "Sharing the Planet",
                    
                    # Skills
                    "Listening", "Reading", "Speaking", "Writing", "Interactive Skills",
                    "Text Handling", "Cultural Understanding", "Language Analysis"
                ],
                
                12: [
                    "Advanced Language Skills", "Cultural Analysis", "Global Issues",
                    "Contemporary Challenges", "Literature Study", "Extended Study",
                    "Independent Research", "Oral Assessment", "Written Assessment"
                ]
            },
            
            # ==================== ADDITIONAL DP SUBJECTS I MISSED ====================
            "Psychology": {
                11: [
                    # Core Topics
                    "Biological Approach to Understanding Behaviour", "Cognitive Approach to Understanding Behaviour", 
                    "Sociocultural Approach to Understanding Behaviour",
                    
                    # Detailed Core Topics  
                    "Brain and Behaviour", "Hormones and Behaviour", "Genetics and Behaviour", "Neuroplasticity",
                    "Neurotransmitters", "Pheromones", "Cognitive Processing", "Reliability of Memory",
                    "Dual Processing", "Thinking and Decision-making", "Emotion and Cognition", "Social Identity",
                    "Social Cognitive Theory", "Social Learning", "Conformity", "Compliance", "Cultural Dimensions",
                    "Enculturation", "Acculturation", "Cultural Groups", "Discrimination", "Stereotyping",
                    
                    # Research Methodology
                    "Research Methods", "Experimental Design", "Ethics in Psychology", "Sampling", "Variables",
                    "Data Analysis", "Statistical Tests", "Correlation vs Causation", "Validity", "Reliability"
                ],
                
                12: [
                    # HL Extension and Options
                    "Abnormal Psychology", "Developmental Psychology", "Health Psychology", 
                    "Psychology of Human Relationships", "Sport Psychology",
                    
                    # Advanced Topics
                    "Mental Health Disorders", "Treatment and Therapy", "Developmental Stages", "Attachment Theory",
                    "Stress and Health", "Health Promotion", "Relationships and Communication", "Interpersonal Behaviour",
                    "Performance Enhancement", "Team Dynamics", "Advanced Research Methods", "Meta-analysis"
                ]
            },
            
            "Business Management": {
                11: [
                    # Core Topics
                    "Business Organization and Environment", "Human Resource Management", "Finance and Accounts", 
                    "Marketing", "Operations Management",
                    
                    # Detailed Topics
                    "Business Functions", "Stakeholders", "Organizational Objectives", "Business Environment",
                    "SWOT Analysis", "PESTLE Analysis", "Organizational Structure", "Leadership Styles",
                    "Motivation Theories", "Communication", "Organizational Culture", "Change Management",
                    "Industrial Relations", "Sources of Finance", "Investment Appraisal", "Working Capital",
                    "Budgets and Variance Analysis", "Final Accounts", "Marketing Planning", "Market Research",
                    "Product Life Cycle", "Marketing Mix", "E-commerce", "Production Methods", "Quality Management",
                    "Supply Chain Management", "Research and Development", "Location Planning", "Project Management"
                ],
                
                12: [
                    # HL Extension Topics
                    "Strategic Planning", "International Business", "Corporate Social Responsibility",
                    "Business Ethics", "Crisis Management", "Innovation Management", "Digital Transformation",
                    "Sustainability", "Global Markets", "Cultural Considerations", "International Trade"
                ]
            },
            
            "Philosophy": {
                11: [
                    # Core Themes
                    "Being Human", "Knowledge and the Knower", "Ethics", "Political Philosophy",
                    
                    # Detailed Core Topics
                    "Nature of Human Beings", "Free Will and Determinism", "Personal Identity", "Mind-Body Problem",
                    "Consciousness", "Death and Meaning", "Epistemology", "Sources of Knowledge", "Skepticism",
                    "Truth and Belief", "Scientific Knowledge", "Moral Philosophy", "Ethical Theories",
                    "Applied Ethics", "Meta-ethics", "Justice", "Authority", "Rights and Responsibilities",
                    "Democracy", "Political Obligation", "Philosophical Thinking", "Argumentation", "Logic"
                ],
                
                12: [
                    # HL Extension and Prescribed Texts
                    "Advanced Philosophical Analysis", "Prescribed Philosophical Texts", "Comparative Philosophy",
                    "Eastern Philosophy", "Contemporary Issues", "Philosophy of Religion", "Philosophy of Science",
                    "Aesthetics", "Philosophy of Mind", "Advanced Logic", "Independent Research"
                ]
            },
            
            "Global Politics": {
                11: [
                    # Core Units
                    "Power, Sovereignty and International Relations", "Human Rights", "Development", "Peace and Conflict",
                    
                    # Detailed Topics
                    "State and Non-state Actors", "Power in International Relations", "Sovereignty", "Legitimacy",
                    "International Organizations", "Global Governance", "Human Rights Framework", "Civil and Political Rights",
                    "Economic, Social and Cultural Rights", "Human Rights Violations", "Development Theory",
                    "Measuring Development", "Barriers to Development", "Role of International Organizations",
                    "Conflict Analysis", "Causes of Conflict", "Conflict Resolution", "Peacekeeping", "Peacebuilding"
                ],
                
                12: [
                    # HL Extension and Engagement Activity
                    "Advanced Political Analysis", "Contemporary Global Issues", "Case Studies", "Comparative Politics",
                    "Political Engagement Activity", "Research Project", "Policy Analysis", "International Law"
                ]
            },
            
            "Social and Cultural Anthropology": {
                11: [
                    # Core Study
                    "Becoming Human", "Thinking Culturally", "Doing Anthropology",
                    
                    # Detailed Topics
                    "Human Evolution", "Primatology", "Language and Communication", "Culture and Society",
                    "Kinship and Marriage", "Economic Systems", "Political Organization", "Religion and Belief",
                    "Art and Aesthetics", "Fieldwork Methods", "Ethnographic Research", "Participant Observation",
                    "Cultural Relativism", "Ethnocentrism", "Cross-cultural Comparison", "Applied Anthropology"
                ],
                
                12: [
                    # Options and Independent Study
                    "Anthropology of Development", "Medical Anthropology", "Urban Anthropology", 
                    "Environmental Anthropology", "Independent Research", "Ethnographic Project"
                ]
            },
            
            "World Religions": {
                11: [
                    # SL Only Course
                    "Ultimate Questions", "Religious Experience", "Religion and Society",
                    
                    # Major World Religions
                    "Christianity", "Islam", "Judaism", "Hinduism", "Buddhism", "Sikhism", "Taoism", "Shintoism",
                    "Indigenous Religions", "Religious Texts", "Pilgrimage", "Worship and Ritual", "Religious Art",
                    "Religious Music", "Religious Architecture", "Religious Festivals", "Religious Law",
                    "Religious Leadership", "Mysticism", "Religious Conflict", "Religious Dialogue",
                    "Secularization", "Religion and Science", "Religion and Ethics", "Religion and Politics"
                ],
                
                12: [
                    # Advanced Study
                    "Comparative Religion", "Religious Philosophy", "Contemporary Religious Issues",
                    "Religion and Globalization", "New Religious Movements", "Independent Research"
                ]
            },
            
            "Literature and Performance": {
                11: [
                    # Interdisciplinary SL Course (Groups 1 & 6)
                    "Literature in Performance", "Adaptation and Transformation", "Collaborative Creation",
                    
                    # Core Elements
                    "Text Analysis", "Performance Theory", "Theatre History", "Adaptation Studies",
                    "Collaborative Creation", "Performance Criticism", "Interdisciplinary Approaches",
                    "Cultural Context", "Contemporary Performance", "Digital Performance", "Experimental Theatre"
                ],
                
                12: [
                    # Advanced Performance Studies
                    "Independent Performance Project", "Advanced Text Analysis", "Performance Research",
                    "Contemporary Issues in Performance", "Technology and Performance"
                ]
            },
            
            "Information Technology in a Global Society": {
                11: [
                    # Core Topics (Being Phased Out)
                    "Social and Ethical Significance", "Application to Specified Scenarios", "IT Systems",
                    
                    # Detailed Topics
                    "Digital Divide", "Privacy and Anonymity", "Intellectual Property", "Cybercrime", "Surveillance",
                    "Artificial Intelligence", "Robotics", "Automation", "Social Media", "Digital Communication",
                    "E-commerce", "Digital Governance", "Health Informatics", "Environmental Impact", "Globalization"
                ],
                
                12: [
                    # Advanced IT Analysis
                    "Emerging Technologies", "IT Policy", "Digital Ethics", "Future Implications",
                    "Research Project", "Case Study Analysis"
                ]
            },
            
            # Additional Science Options I Missed
            "Marine Science": {
                11: [
                    # School-based Syllabus
                    "Ocean Systems", "Marine Life", "Marine Ecosystems", "Ocean Chemistry", "Ocean Physics",
                    "Marine Pollution", "Climate Change and Oceans", "Marine Conservation", "Coastal Management",
                    "Marine Resources", "Aquaculture", "Marine Technology", "Ocean Exploration"
                ],
                
                12: [
                    "Advanced Marine Biology", "Ocean Modeling", "Marine Research Methods", 
                    "Independent Study", "Field Research"
                ]
            },
            
            "Astronomy": {
                11: [
                    # School-based Syllabus  
                    "Solar System", "Stars and Stellar Evolution", "Galaxies", "Cosmology", "Observational Astronomy",
                    "Astrophysics", "Space Technology", "History of Astronomy", "Exoplanets", "Black Holes",
                    "Dark Matter", "Dark Energy", "Big Bang Theory", "Astrobiology"
                ],
                
                12: [
                    "Advanced Astrophysics", "Radio Astronomy", "Space Missions", "Independent Research",
                    "Astronomical Data Analysis"
                ]
            },
            
            # Additional Arts Subjects I Missed
            "Dance": {
                11: [
                    # Core Components
                    "Dance in Context", "Dance Processes", "Presenting Dance",
                    
                    # Dance Styles and Techniques
                    "Ballet", "Contemporary", "Jazz", "Hip Hop", "Folk Dance", "Cultural Dance", "Modern Dance",
                    "Choreography", "Dance Composition", "Movement Analysis", "Dance History", "Dance Criticism",
                    "Dance and Technology", "Dance Therapy", "Dance Performance", "Dance Notation"
                ],
                
                12: [
                    "Advanced Choreography", "Professional Dance", "Dance Research", "Contemporary Issues in Dance",
                    "Independent Project", "Dance and Society"
                ]
            },
            
            # Language A Options I Missed
            "Classical Languages": {
                11: [
                    # Latin and Ancient Greek
                    "Latin Literature", "Ancient Greek Literature", "Classical Civilization", "Ancient History",
                    "Mythology", "Classical Philosophy", "Classical Art", "Roman History", "Greek History",
                    "Epic Poetry", "Drama", "Lyric Poetry", "Rhetoric", "Classical Reception"
                ],
                
                12: [
                    "Advanced Classical Studies", "Comparative Literature", "Independent Research",
                    "Classical Scholarship", "Modern Reception of Classics"
                ]
            },
            
            # Core DP Components
            "Theory of Knowledge": {
                11: [
                    # Core Course for All DP Students
                    "Knowledge and the Knower", "Knowledge and Technology", "Knowledge and Language", 
                    "Knowledge and Politics", "Knowledge and Religion", "Knowledge and Indigenous Societies",
                    
                    # Areas of Knowledge
                    "Mathematics", "Natural Sciences", "Human Sciences", "History", "The Arts", "Ethics",
                    "Religious Knowledge Systems", "Indigenous Knowledge Systems",
                    
                    # Ways of Knowing
                    "Language", "Sense Perception", "Emotion", "Reason", "Imagination", "Faith", "Intuition", "Memory"
                ],
                
                12: [
                    "TOK Exhibition", "TOK Essay", "Advanced Epistemology", "Knowledge Questions",
                    "Interdisciplinary Connections", "Critical Thinking", "Knowledge Claims"
                ]
            },
            
            "Extended Essay": {
                11: [
                    # Independent Research Project
                    "Research Question", "Research Methodology", "Academic Writing", "Source Analysis",
                    "Data Collection", "Literature Review", "Thesis Development", "Evidence and Analysis",
                    "Reflection", "Academic Integrity", "Citation and Bibliography"
                ],
                
                12: [
                    "Independent Research", "Supervision Process", "Viva Voce", "Final Submission",
                    "Research Ethics", "University Preparation"
                ]
            },
            
            "Creativity, Activity, Service": {
                11: [
                    # Core Requirement
                    "Creativity Projects", "Physical Activity", "Service Learning", "CAS Project",
                    "Personal Growth", "Challenge", "Initiative", "Planning", "Reflection", "Collaboration",
                    "Global Engagement", "Issue Investigation", "Action Planning", "Reflection Skills"
                ],
                
                12: [
                    "Portfolio Completion", "Final Reflections", "Learning Outcomes", "CAS Coordinator Meetings",
                    "Evidence Documentation", "Goal Achievement"
                ]
            }
        },
        "ICSE": {
            "Mathematics": {
                1: [
                    # Pre-Number Concepts
                    "Numbers 1-99", "Number Names", "Counting Forward and Backward", "Before and After",
                    "Number Line", "Skip Counting", "Patterns in Numbers", "Even and Odd Numbers",
                    
                    # Basic Operations
                    "Addition of Single Digits", "Subtraction of Single Digits", "Simple Word Problems",
                    "Addition using Objects", "Subtraction using Objects", "Zero in Addition and Subtraction",
                    
                    # Shapes and Patterns
                    "Basic Shapes", "Circle", "Square", "Rectangle", "Triangle", "Oval",
                    "Shape Recognition", "Patterns with Shapes", "Sorting by Shapes",
                    
                    # Measurement
                    "Comparison of Length", "Tall and Short", "Long and Short", "Heavy and Light",
                    "Big and Small", "Time Concepts", "Day and Night", "Before and After Time",
                    
                    # Money
                    "Recognition of Coins", "Value of Coins", "Simple Money Problems",
                    
                    # Data Handling
                    "Simple Pictographs", "Collecting Information", "Organizing Data"
                ],
                
                2: [
                    # Numbers
                    "Numbers 1-100", "Number Names in Words", "Place Value (Tens and Ones)",
                    "Expanded Form", "Standard Form", "Comparison of Numbers", "Ascending Order",
                    "Descending Order", "Number Patterns", "Skip Counting by 2s, 5s, 10s",
                    
                    # Addition and Subtraction
                    "Addition without Regrouping", "Addition with Regrouping", "Subtraction without Regrouping",
                    "Subtraction with Regrouping", "Addition of Zero", "Subtraction of Zero",
                    "Commutative Property of Addition", "Word Problems on Addition and Subtraction",
                    "Estimation in Addition and Subtraction",
                    
                    # Multiplication
                    "Introduction to Multiplication", "Multiplication as Repeated Addition",
                    "Multiplication Tables 2, 3, 4, 5", "Skip Counting for Tables", "Arrays and Multiplication",
                    
                    # Division
                    "Division as Sharing", "Division as Repeated Subtraction", "Simple Division Facts",
                    
                    # Geometry
                    "2D Shapes", "3D Shapes", "Faces, Edges, Vertices", "Symmetry", "Lines and Curves",
                    
                    # Measurement
                    "Length Measurement", "Weight Measurement", "Capacity Measurement",
                    "Time - Reading Clock", "Calendar", "Days and Months",
                    
                    # Money
                    "Indian Currency", "Addition of Money", "Subtraction of Money", "Making Change",
                    
                    # Data Handling
                    "Pictographs", "Bar Graphs", "Tally Marks", "Data Collection and Organization"
                ],
                
                3: [
                    # Numbers
                    "Numbers up to 1000", "4-digit Numbers", "Place Value (Thousands, Hundreds, Tens, Ones)",
                    "Expanded Form and Standard Form", "Roman Numerals I to XX", "Number Line up to 1000",
                    "Comparison and Ordering", "Rounding to Nearest 10 and 100",
                    
                    # Four Operations
                    "Addition with Regrouping", "Subtraction with Regrouping", "Properties of Addition",
                    "Multiplication Tables up to 10", "2-digit by 1-digit Multiplication",
                    "Division with Remainders", "Long Division Method", "Word Problems",
                    
                    # Fractions
                    "Introduction to Fractions", "Parts of a Whole", "Numerator and Denominator",
                    "Proper and Improper Fractions", "Mixed Numbers", "Equivalent Fractions",
                    "Comparison of Fractions", "Addition of Like Fractions", "Subtraction of Like Fractions",
                    
                    # Geometry
                    "Points, Lines, and Line Segments", "Rays", "Angles", "Types of Angles",
                    "Polygons", "Quadrilaterals", "Perimeter", "Area using Unit Squares",
                    
                    # Measurement
                    "Metric Units of Length", "Metric Units of Weight", "Metric Units of Capacity",
                    "Conversion within Metric System", "Time Intervals", "Elapsed Time",
                    
                    # Money
                    "Decimal Notation for Money", "Addition and Subtraction of Money",
                    "Multiplication of Money", "Word Problems with Money",
                    
                    # Data Handling
                    "Reading and Interpreting Graphs", "Bar Graphs with Scale", "Pictographs with Scale",
                    "Line Graphs", "Data Analysis"
                ],
                
                4: [
                    # Numbers
                    "5-digit and 6-digit Numbers", "Place Value up to Lakhs", "International Number System",
                    "Roman Numerals up to 100", "Factors and Multiples", "Prime and Composite Numbers",
                    "LCM and HCF", "Tests of Divisibility",
                    
                    # Operations
                    "Addition and Subtraction of Large Numbers", "Multiplication by 2-digit Numbers",
                    "Division by 2-digit Numbers", "BODMAS Rule", "Word Problems with Mixed Operations",
                    
                    # Fractions and Decimals
                    "Mixed Numbers and Improper Fractions", "Addition and Subtraction of Unlike Fractions",
                    "Multiplication of Fractions", "Division of Fractions", "Decimal Numbers",
                    "Place Value in Decimals", "Addition and Subtraction of Decimals",
                    "Multiplication of Decimals", "Division of Decimals",
                    
                    # Geometry
                    "Parallel and Perpendicular Lines", "Types of Triangles", "Types of Quadrilaterals",
                    "Circles", "Radius and Diameter", "Perimeter and Area Formulas",
                    "Coordinate Geometry Basics",
                    
                    # Measurement
                    "Conversion between Units", "Problems on Time", "Speed, Distance, Time",
                    "Simple Interest", "Profit and Loss Basics",
                    
                    # Data Handling
                    "Probability Basics", "Certain and Impossible Events", "Likely and Unlikely Events",
                    "Frequency Tables", "Mode and Median"
                ],
                
                5: [
                    # Numbers
                    "Numbers up to Crores", "Place Value System", "Rounding and Estimation",
                    "Negative Numbers", "Number Line with Negative Numbers",
                    
                    # Operations
                    "Operations on Large Numbers", "Square Numbers", "Square Roots",
                    "Cube Numbers", "Applications of Operations",
                    
                    # Fractions and Decimals
                    "Operations on Fractions", "Fractions to Decimals", "Decimals to Fractions",
                    "Percentages", "Percentage to Fraction and Decimal", "Applications of Percentages",
                    
                    # Ratio and Proportion
                    "Introduction to Ratios", "Equivalent Ratios", "Proportion", "Unitary Method",
                    
                    # Geometry
                    "Construction with Compass", "Angle Measurement", "Triangles and Their Properties",
                    "Symmetry and Reflection", "3D Shapes and Nets",
                    
                    # Mensuration
                    "Area and Perimeter of Complex Shapes", "Volume of Cubes and Cuboids",
                    "Surface Area", "Units of Area and Volume",
                    
                    # Algebra Basics
                    "Simple Equations", "Variables and Constants", "Algebraic Expressions",
                    
                    # Data Handling
                    "Mean, Median, Mode", "Range", "Frequency Distribution", "Grouped Data",
                    "Probability with Examples"
                ],
                
                6: [
                    # Number System
                    "Natural Numbers and Whole Numbers", "Integers", "Number Line", "Absolute Value",
                    "Comparison of Integers", "Operations on Integers", "Properties of Operations",
                    
                    # Fractions and Decimals
                    "Fractions on Number Line", "Operations on Fractions", "Decimal Numbers",
                    "Operations on Decimals", "Converting Fractions to Decimals and Vice Versa",
                    
                    # Ratio and Proportion
                    "Ratios and Their Applications", "Proportions", "Unitary Method",
                    "Percentage and Its Applications", "Profit and Loss", "Simple Interest",
                    
                    # Algebra
                    "Introduction to Algebra", "Variables and Constants", "Algebraic Expressions",
                    "Terms and Factors", "Like and Unlike Terms", "Addition and Subtraction of Algebraic Expressions",
                    
                    # Geometry
                    "Basic Geometrical Ideas", "Line Segments", "Rays and Lines", "Angles",
                    "Types of Angles", "Parallel Lines", "Intersecting Lines", "Triangles",
                    "Quadrilaterals", "Circles", "Constructions",
                    
                    # Mensuration
                    "Perimeter and Area", "Area of Rectangle and Square", "Area of Triangle",
                    "Area of Circle", "Volume and Surface Area of Cube and Cuboid",
                    
                    # Data Handling
                    "Data Collection", "Organization of Data", "Pictographs", "Bar Graphs",
                    "Pie Charts", "Mean, Median, Mode", "Probability"
                ],
                
                7: [
                    # Numbers
                    "Integers and Their Operations", "Properties of Addition and Subtraction of Integers",
                    "Multiplication and Division of Integers", "Rational Numbers", "Positive and Negative Rational Numbers",
                    "Operations on Rational Numbers",
                    
                    # Fractions and Decimals
                    "Multiplication and Division of Fractions", "Word Problems on Fractions",
                    "Multiplication and Division of Decimals", "Word Problems on Decimals",
                    
                    # Algebra
                    "Algebraic Expressions", "Terms, Factors and Coefficients", "Like and Unlike Terms",
                    "Addition and Subtraction of Algebraic Expressions", "Finding Value of an Expression",
                    "Simple Linear Equations", "Solving Linear Equations",
                    
                    # Ratio and Proportion
                    "Ratio and Proportion", "Unitary Method", "Percentage", "Applications of Percentage",
                    "Profit and Loss", "Simple Interest", "Compound Interest",
                    
                    # Geometry
                    "Lines and Angles", "Complementary and Supplementary Angles", "Adjacent Angles",
                    "Linear Pair", "Vertically Opposite Angles", "Parallel Lines and Transversal",
                    "Triangles", "Median and Altitude of Triangle", "Angle Sum Property",
                    "Exterior Angle Property", "Congruence of Triangles",
                    
                    # Mensuration
                    "Perimeter and Area of Plane Figures", "Area of Parallelogram", "Area of Triangle",
                    "Circumference and Area of Circle", "Volume and Surface Area of Cube, Cuboid and Cylinder",
                    
                    # Data Handling
                    "Mean, Median and Mode of Ungrouped Data", "Bar Graphs", "Histograms",
                    "Probability", "Experimental Probability"
                ],
                
                8: [
                    # Numbers
                    "Rational Numbers", "Properties of Rational Numbers", "Representation of Rational Numbers on Number Line",
                    "Operations on Rational Numbers", "Powers", "Laws of Exponents", "Expressing Large Numbers in Standard Form",
                    
                    # Algebra
                    "Algebraic Expressions and Identities", "Multiplication of Algebraic Expressions",
                    "Identities", "Factorization", "Division of Algebraic Expressions",
                    "Linear Equations in One Variable", "Solving Linear Equations", "Applications of Linear Equations",
                    
                    # Geometry
                    "Practical Geometry", "Construction of Quadrilaterals", "Understanding Quadrilaterals",
                    "Properties of Parallelogram", "Special Types of Quadrilaterals",
                    "Area of Trapezium", "Area of General Quadrilateral",
                    
                    # Mensuration
                    "Surface Area and Volume", "Surface Area of Cube and Cuboid", "Surface Area of Cylinder",
                    "Volume of Cube and Cuboid", "Volume of Cylinder", "Volume and Surface Area of Sphere and Hemisphere",
                    
                    # Data Handling
                    "Data Handling", "Frequency Distribution Table", "Histograms", "Circle Graphs or Pie Charts",
                    "Probability", "Equally Likely Outcomes", "Probability as a Fraction",
                    
                    # Others
                    "Direct and Inverse Proportions", "Time and Work", "Pipes and Cisterns",
                    "Comparing Quantities", "Finding Increase or Decrease Percent", "Finding Discounts",
                    "Prices Related to Buying and Selling", "Sales Tax/Value Added Tax", "Compound Interest",
                    "Rate Compounded Annually or Half Yearly"
                ],
                
                9: [
                    # Number Systems
                    "Real Numbers", "Rational and Irrational Numbers", "Representation of Real Numbers on Number Line",
                    "Operations on Real Numbers", "Laws of Exponents for Real Numbers", "Rationalization",
                    
                    # Algebra
                    "Polynomials", "Polynomials in One Variable", "Zeroes of a Polynomial", "Remainder Theorem",
                    "Factorization of Polynomials", "Algebraic Identities",
                    "Linear Equations in Two Variables", "Solution of Linear Equation", "Graph of Linear Equation in Two Variables",
                    "Equations of Lines Parallel to Axes",
                    
                    # Coordinate Geometry
                    "Introduction to Coordinate Geometry", "Cartesian System", "Plotting Points in Cartesian Plane",
                    "Distance Between Two Points", "Section Formula",
                    
                    # Geometry
                    "Introduction to Euclid's Geometry", "Euclid's Axioms and Postulates",
                    "Lines and Angles", "Intersecting Lines and Non-intersecting Lines", "Pairs of Angles",
                    "Lines Parallel to Same Line", "Angle Sum Property of Triangle",
                    "Triangles", "Congruence of Triangles", "Criteria for Congruence of Triangles",
                    "Properties of Isosceles Triangle", "Inequalities in Triangle",
                    "Quadrilaterals", "Angle Sum Property of Quadrilateral", "Types of Quadrilaterals",
                    "Properties of Parallelogram", "Mid-point Theorem",
                    
                    # Mensuration
                    "Areas", "Area of Triangle", "Area of Parallelogram", "Area of Trapezium",
                    "Heron's Formula", "Application of Heron's Formula",
                    "Surface Areas and Volumes", "Surface Area of Cuboid and Cube", "Surface Area of Right Circular Cylinder",
                    "Surface Area of Right Circular Cone", "Surface Area of Sphere", "Volume of Cuboid",
                    "Volume of Cylinder", "Volume of Right Circular Cone", "Volume of Sphere",
                    
                    # Statistics and Probability
                    "Statistics", "Collection of Data", "Presentation of Data", "Graphical Representation of Data",
                    "Measures of Central Tendency", "Probability", "Experimental Probability",
                    "Theoretical Probability", "Equally Likely Outcomes"
                ],
                
                10: [
                    # Number Systems
                    "Real Numbers", "Euclid's Division Lemma", "Fundamental Theorem of Arithmetic",
                    "Revisiting Irrational Numbers", "Revisiting Rational Numbers and Their Decimal Expansions",
                    
                    # Algebra
                    "Polynomials", "Geometrical Meaning of Zeroes of Polynomial", "Relationship Between Zeroes and Coefficients of Polynomial",
                    "Division Algorithm for Polynomials",
                    "Pair of Linear Equations in Two Variables", "Graphical Method of Solution", "Algebraic Methods of Solution",
                    "Elimination Method", "Substitution Method", "Cross-multiplication Method", "Equations Reducible to Linear Equations",
                    "Quadratic Equations", "Solution of Quadratic Equations by Factorization", "Solution by Completing the Square",
                    "Quadratic Formula", "Nature of Roots",
                    "Arithmetic Progressions", "nth Term of an AP", "Sum of First n Terms of an AP",
                    
                    # Coordinate Geometry
                    "Lines", "Distance Formula", "Section Formula", "Area of Triangle",
                    
                    # Geometry
                    "Triangles", "Similar Figures", "Similarity of Triangles", "Criteria for Similarity of Triangles",
                    "Areas of Similar Triangles", "Pythagoras Theorem", "Applications of Pythagoras Theorem",
                    "Circles", "Tangent to a Circle", "Number of Tangents from a Point on Circle",
                    
                    # Trigonometry
                    "Introduction to Trigonometry", "Trigonometric Ratios", "Trigonometric Ratios of Some Specific Angles",
                    "Trigonometric Identities", "Some Applications of Trigonometry", "Heights and Distances",
                    
                    # Mensuration
                    "Areas Related to Circles", "Perimeter and Area of Circle", "Areas of Sector and Segment of Circle",
                    "Areas of Combinations of Plane Figures",
                    "Surface Areas and Volumes", "Combination of Solids", "Frustum of Cone", "Conversion of Solid from One Shape to Another",
                    
                    # Statistics and Probability
                    "Statistics", "Mean of Grouped Data", "Mode of Grouped Data", "Median of Grouped Data",
                    "Graphical Representation of Cumulative Frequency Distribution",
                    "Probability", "Classical Definition of Probability", "Simple Problems on Single Events"
                ]
            },
            
            "English": {
                1: [
                    # Reading and Comprehension
                    "Alphabet Recognition", "Capital and Small Letters", "Letter Sounds", "Phonics",
                    "Vowels and Consonants", "Blending Sounds", "Simple Three-Letter Words",
                    "Four-Letter Words", "Sight Words", "Picture Reading", "Simple Sentences",
                    
                    # Writing Skills
                    "Letter Formation", "Writing Capital Letters", "Writing Small Letters",
                    "Copying Words", "Copying Sentences", "Writing Simple Words",
                    "Writing Short Sentences", "Handwriting Practice",
                    
                    # Grammar
                    "Naming Words (Nouns)", "Action Words (Verbs)", "Describing Words (Adjectives)",
                    "A, An, The", "This, That", "Here, There", "Yes, No Questions",
                    
                    # Literature
                    "Simple Poems", "Nursery Rhymes", "Short Stories", "Moral Stories",
                    "Picture Stories", "Character Identification",
                    
                    # Speaking and Listening
                    "Oral Comprehension", "Following Instructions", "Show and Tell",
                    "Recitation", "Role Play", "Conversation Skills"
                ],
                
                2: [
                    # Reading and Comprehension
                    "Reading Short Stories", "Reading Simple Poems", "Understanding Main Ideas",
                    "Answering Simple Questions", "Sequence of Events", "Character Recognition",
                    "Picture Comprehension", "Reading with Expression",
                    
                    # Writing Skills
                    "Sentence Formation", "Writing Simple Paragraphs", "Creative Writing",
                    "Describing Pictures", "Writing About Daily Activities", "Letter Writing Basics",
                    "Diary Writing", "Story Writing",
                    
                    # Grammar
                    "Singular and Plural Nouns", "Masculine and Feminine", "Personal Pronouns",
                    "Present Tense", "Past Tense", "Question Words", "Punctuation Marks",
                    "Capital Letters Usage", "Full Stops and Question Marks",
                    
                    # Literature
                    "Poems with Moral Values", "Stories with Characters", "Fables",
                    "Simple Plays", "Understanding Themes", "Identifying Settings",
                    
                    # Vocabulary
                    "Synonyms", "Antonyms", "New Words", "Word Meanings",
                    "Rhyming Words", "Word Families"
                ],
                
                3: [
                    # Reading and Comprehension
                    "Reading Longer Passages", "Understanding Complex Stories", "Main Idea and Supporting Details",
                    "Making Inferences", "Predicting Outcomes", "Cause and Effect", "Compare and Contrast",
                    "Reading Different Text Types", "Reading for Information",
                    
                    # Writing Skills
                    "Paragraph Writing", "Descriptive Writing", "Narrative Writing", "Letter Writing",
                    "Informal Letters", "Formal Letters", "Story Writing", "Essay Writing",
                    "Report Writing", "Creative Writing Exercises",
                    
                    # Grammar
                    "Types of Nouns", "Common and Proper Nouns", "Collective Nouns", "Abstract Nouns",
                    "Pronouns and Their Types", "Verbs and Tenses", "Simple Present Tense",
                    "Simple Past Tense", "Simple Future Tense", "Adjectives and Their Types",
                    "Adverbs", "Prepositions", "Conjunctions", "Articles", "Sentence Types",
                    "Statements, Questions, Commands, Exclamations", "Subject and Predicate",
                    
                    # Literature
                    "Poetry Appreciation", "Understanding Metaphors and Similes", "Story Analysis",
                    "Character Study", "Plot Development", "Theme Identification", "Moral Lessons",
                    
                    # Vocabulary
                    "Word Building", "Prefixes and Suffixes", "Synonyms and Antonyms",
                    "Homophones", "Word Meanings in Context", "Dictionary Skills"
                ],
                
                4: [
                    # Reading and Comprehension
                    "Critical Reading", "Analyzing Text Structure", "Author's Purpose", "Point of View",
                    "Making Connections", "Summarizing", "Drawing Conclusions", "Reading Between the Lines",
                    
                    # Writing Skills
                    "Expository Writing", "Persuasive Writing", "Research Writing", "Business Letters",
                    "Application Writing", "Resume Writing", "Notice Writing", "Article Writing",
                    "Book Reviews", "Character Sketches",
                    
                    # Grammar
                    "Complex Sentence Structures", "Compound Sentences", "Complex Sentences",
                    "Conditional Sentences", "Active and Passive Voice", "Direct and Indirect Speech",
                    "Modals", "Question Tags", "Phrasal Verbs", "Idiomatic Expressions",
                    
                    # Literature
                    "Poetry Analysis", "Literary Devices", "Prose Appreciation", "Drama Study",
                    "Shakespearean Sonnets", "Modern Poetry", "Short Stories", "Novel Studies",
                    
                    # Communication Skills
                    "Public Speaking", "Debate Preparation", "Group Discussions", "Interview Skills",
                    "Presentation Skills", "Critical Thinking"
                ],
                
                5: [
                    # Advanced Reading
                    "Critical Analysis", "Literary Criticism", "Comparative Literature", "Research Skills",
                    "Academic Reading", "Professional Communication",
                    
                    # Advanced Writing
                    "Academic Writing", "Research Papers", "Thesis Writing", "Creative Writing",
                    "Professional Writing", "Technical Writing",
                    
                    # Advanced Grammar
                    "Advanced Grammar Structures", "Style and Register", "Coherence and Cohesion",
                    "Error Analysis", "Editing and Proofreading",
                    
                    # Literature
                    "World Literature", "Contemporary Literature", "Classical Literature",
                    "Literary Movements", "Cultural Context in Literature",
                    
                    # Communication
                    "Professional Communication", "Business English", "Academic Discourse",
                    "Cross-cultural Communication"
                ],
                
                6: [
                    # Literature
                    "Prose - Stories, Essays, Biographies", "Poetry - Different Forms and Styles",
                    "Drama - One-act Plays", "Character Analysis", "Theme Exploration",
                    "Literary Devices", "Figure of Speech", "Imagery and Symbolism",
                    
                    # Language Skills
                    "Grammar - Parts of Speech", "Sentence Formation", "Tenses", "Voice",
                    "Narration", "Conditionals", "Modals", "Question Formation",
                    
                    # Writing Skills
                    "Creative Writing", "Descriptive Writing", "Narrative Writing",
                    "Letter Writing", "Essay Writing", "Report Writing", "Summary Writing",
                    
                    # Communication Skills
                    "Reading Comprehension", "Oral Communication", "Listening Skills",
                    "Speaking Skills", "Pronunciation", "Intonation"
                ],
                
                7: [
                    # Literature
                    "Short Stories by Indian and Foreign Authors", "Poetry - Classical and Modern",
                    "Drama - Shakespearean Extracts", "Literary Appreciation", "Critical Reading",
                    "Comparative Study", "Author Studies", "Historical Context",
                    
                    # Language Skills
                    "Advanced Grammar", "Syntax", "Semantics", "Vocabulary Development",
                    "Word Formation", "Idioms and Phrases", "Proverbs", "Etymology",
                    
                    # Writing Skills
                    "Argumentative Writing", "Persuasive Writing", "Analytical Writing",
                    "Research Writing", "Technical Writing", "Creative Writing",
                    
                    # Communication
                    "Debate and Discussion", "Public Speaking", "Presentation Skills",
                    "Interview Techniques", "Group Communication"
                ],
                
                8: [
                    # Literature
                    "Novel Studies", "Poetry Analysis", "Drama Appreciation", "Literary Criticism",
                    "World Literature", "Indian English Literature", "Contemporary Writers",
                    "Literary Movements", "Cultural Studies",
                    
                    # Language Skills
                    "Advanced English Grammar", "Style and Register", "Academic English",
                    "Professional English", "Language Varieties", "Sociolinguistics",
                    
                    # Writing Skills
                    "Academic Writing", "Research Methodology", "Citation and References",
                    "Critical Writing", "Professional Writing", "Media Writing",
                    
                    # Communication
                    "Advanced Communication Skills", "Cross-cultural Communication",
                    "Digital Communication", "Mass Communication"
                ],
                
                9: [
                    # Literature Paper I
                    "Shakespeare - Julius Caesar", "Treasure Chest - Poetry and Short Stories",
                    "Character Analysis", "Theme Study", "Literary Techniques", "Critical Appreciation",
                    "Contextual Questions", "Extract-based Questions",
                    
                    # Language Paper II
                    "Reading Comprehension", "Note Making", "Summary Writing", "Letter Writing",
                    "Essay Writing", "Report Writing", "Article Writing", "Speech Writing",
                    "Debate Writing", "Story Writing",
                    
                    # Grammar
                    "Sentence Transformation", "Active and Passive Voice", "Direct and Indirect Speech",
                    "Prepositions", "Conjunctions", "Question Tags", "Conditionals",
                    
                    # Composition
                    "Argumentative Essays", "Descriptive Essays", "Narrative Essays",
                    "Formal and Informal Letters", "Applications", "Notices"
                ],
                
                10: [
                    # Literature Paper I
                    "Shakespeare - Merchant of Venice or Julius Caesar", "Treasure Chest - A Collection of ICSE Poems and Short Stories",
                    "Poetry Appreciation", "Prose Analysis", "Character Portrayal", "Theme Analysis",
                    "Literary Devices", "Irony, Symbolism, Metaphor", "Historical and Social Context",
                    
                    # Language Paper II
                    "Comprehension Passages", "Note Making and Summary", "Letter Writing - Formal and Informal",
                    "Applications", "Essay Writing", "Article Writing", "Report Writing",
                    "Speech Writing", "Story Writing",
                    
                    # Grammar and Usage
                    "Transformation of Sentences", "Synthesis of Sentences", "Active and Passive Voice",
                    "Direct and Indirect Speech", "Prepositions", "Phrasal Verbs", "Idioms",
                    
                    # Composition Skills
                    "Argumentative Writing", "Descriptive Writing", "Narrative Writing",
                    "Expository Writing", "Creative Writing", "Critical Writing"
                ]
            },
            
            "Hindi": {
                1: [
                    # वर्णमाला और उच्चारण
                    "हिंदी वर्णमाला", "स्वर", "व्यंजन", "मात्राएँ", "संयुक्त अक्षर",
                    "उच्चारण", "शुद्ध उच्चारण", "वर्ण पहचान",
                    
                    # शब्द निर्माण
                    "दो अक्षर के शब्द", "तीन अक्षर के शब्द", "चार अक्षर के शब्द",
                    "सरल शब्द", "चित्र देखकर शब्द", "वाक्य निर्माण",
                    
                    # पठन कौशल
                    "सरल वाक्य पढ़ना", "चित्र देखकर कहानी", "छोटी कविताएँ",
                    "नैतिक कहानियाँ", "बालगीत",
                    
                    # लेखन कौशल
                    "वर्ण लेखन", "शब्द लेखन", "वाक्य लेखन", "सुंदर लेखन",
                    "नकल करके लिखना"
                ],
                
                2: [
                    # व्याकरण
                    "संज्ञा", "सर्वनाम", "विशेषण", "क्रिया", "वचन", "लिंग",
                    "एकवचन-बहुवचन", "पुल्लिंग-स्त्रीलिंग",
                    
                    # शब्द भंडार
                    "नए शब्द", "शब्द अर्थ", "विपरीत शब्द", "समान अर्थ वाले शब्द",
                    "तुकांत शब्द", "शब्द खेल",
                    
                    # पठन पाठन
                    "कहानी पठन", "कविता पठन", "नैतिक शिक्षा", "चरित्र पहचान",
                    "मुख्य विचार", "घटना क्रम",
                    
                    # लेखन
                    "वाक्य रचना", "अनुच्छेद लेखन", "चित्र वर्णन", "पत्र लेखन",
                    "दैनिक गतिविधियाँ"
                ],
                
                3: [
                    # साहित्य पठन
                    "कहानी संग्रह", "काव्य संग्रह", "नाटक", "जीवनी", "यात्रा वृत्तांत",
                    "बाल साहित्य", "लोक कथाएँ", "परी कथाएँ",
                    
                    # व्याकरण
                    "संज्ञा के भेद", "सर्वनाम के भेद", "विशेषण के भेद", "क्रिया के भेद",
                    "काल", "भूतकाल", "वर्तमान काल", "भविष्य काल", "वाक्य के भेद",
                    
                    # रचनात्मक लेखन
                    "कहानी लेखन", "निबंध लेखन", "पत्र लेखन", "संवाद लेखन",
                    "चरित्र चित्रण", "भाव व्यक्ति",
                    
                    # भाषा कौशल
                    "शुद्ध उच्चारण", "वाचन कला", "भाषण कला", "कविता पाठ",
                    "अभिनय", "संवाद अदायगी"
                ],
                
                4: [
                    # उन्नत साहित्य
                    "आधुनिक कविता", "प्राचीन काव्य", "कहानी विश्लेषण", "नाटक अध्ययन",
                    "महाकाव्य परिचय", "संत साहित्य", "भक्ति काव्य",
                    
                    # व्याकरण और भाषा
                    "छंद शास्त्र", "अलंकार", "रस", "समास", "संधि", "तत्सम-तद्भव",
                    "देशज-विदेशज शब्द", "मुहावरे", "लोकोक्तियाँ",
                    
                    # लेखन कला
                    "आलोचनात्मक लेखन", "शोध लेखन", "साक्षात्कार", "रिपोर्ट लेखन",
                    "समीक्षा लेखन", "व्यावसायिक पत्राचार",
                    
                    # संप्रेषण कौशल
                    "सार्वजनिक भाषण", "वाद-विवाद", "समूह चर्चा", "प्रस्तुतीकरण",
                    "साक्षात्कार तकनीक"
                ],
                
                5: [
                    # शास्त्रीय साहित्य
                    "संस्कृत काव्य", "हिंदी काव्य", "आधुनिक साहित्य", "समसामयिक लेखन",
                    "तुलनात्मक साहित्य", "विश्व साहित्य",
                    
                    # भाषा विज्ञान
                    "भाषा विज्ञान के सिद्धांत", "हिंदी भाषा का विकास", "बोली और भाषा",
                    "मानक हिंदी", "तकनीकी हिंदी",
                    
                    # शोध और आलोचना
                    "साहित्यिक आलोचना", "शोध प्रविधि", "ग्रंथ सूची", "संदर्भ सूची",
                    "थीसिस लेखन", "शोध पत्र लेखन"
                ],
                
                6: [
                    # गद्य साहित्य
                    "कहानी संग्रह", "निबंध संग्रह", "जीवनी", "आत्मकथा", "यात्रा वृत्तांत",
                    "संस्मरण", "रेखाचित्र", "हास्य व्यंग्य",
                    
                    # काव्य साहित्य
                    "आदिकालीन काव्य", "भक्तिकालीन काव्य", "रीतिकालीन काव्य", "आधुनिक काव्य",
                    "छायावादी काव्य", "प्रगतिवादी काव्य", "प्रयोगवादी काव्य",
                    
                    # व्याकरण
                    "संधि विचार", "समास विचार", "प्रत्यय", "उपसर्ग", "तत्सम-तद्भव",
                    "देशज-विदेशज", "पर्यायवाची", "विलोम", "अनेकार्थी शब्द",
                    
                    # रचना कौशल
                    "अनुच्छेद लेखन", "पत्र लेखन", "निबंध लेखन", "कहानी लेखन",
                    "संवाद लेखन", "विज्ञापन लेखन"
                ],
                
                7: [
                    # साहित्य अध्ययन
                    "हिंदी साहित्य का इतिहास", "काव्य शास्त्र", "नाट्य शास्त्र",
                    "कथा साहित्य", "निबंध साहित्य", "आलोचना साहित्य",
                    
                    # भाषा विज्ञान
                    "हिंदी व्याकरण", "छंद शास्त्र", "अलंकार शास्त्र", "रस सिद्धांत",
                    "ध्वनि विज्ञान", "रूप विज्ञान", "वाक्य विज्ञान",
                    
                    # प्रयोजनमूलक हिंदी
                    "कार्यालयी हिंदी", "तकनीकी हिंदी", "व्यावसायिक हिंदी",
                    "संचार माध्यम की हिंदी", "कंप्यूटर और हिंदी",
                    
                    # रचनात्मक लेखन
                    "काव्य रचना", "कहानी लेखन", "नाटक लेखन", "निबंध लेखन",
                    "समीक्षा लेखन", "साक्षात्कार लेखन"
                ],
                
                8: [
                    # उच्च साहित्य
                    "महाकाव्य अध्ययन", "खंडकाव्य अध्ययन", "गीतिकाव्य", "मुक्तक काव्य",
                    "प्रबंध काव्य", "गद्यकाव्य", "नवगीत", "गज़ल",
                    
                    # आलोचना और समीक्षा
                    "साहित्यिक आलोचना", "व्यावहारिक आलोचना", "तुलनात्मक अध्ययन",
                    "मूल्यांकन", "व्याख्या", "विश्लेषण",
                    
                    # भाषा और शैली
                    "भाषा की शुद्धता", "शैली विज्ञान", "अनुवाद कला", "संपादन कला",
                    "प्रूफ रीडिंग", "भाषा नियोजन",
                    
                    # संचार कौशल
                    "उच्च संचार कौशल", "मीडिया लेखन", "पत्रकारिता", "रेडियो-टीवी लेखन",
                    "फिल्म लेखन", "रंगमंच लेखन"
                ],
                
                9: [
                    # गद्य खंड
                    "गद्य की विविध विधाएँ", "कहानी", "निबंध", "एकांकी", "जीवनी",
                    "संस्मरण", "यात्रा वृत्तांत", "डायरी", "पत्र साहित्य",
                    
                    # काव्य खंड
                    "काव्य की परंपरा", "छंदबद्ध काव्य", "मुक्त छंद", "गीत", "गज़ल",
                    "दोहे", "सॉनेट", "हाइकू", "तांका",
                    
                    # व्याकरण
                    "व्याकरण के नियम", "वाक्य संशोधन", "वाक्य परिवर्तन", "संधि-विग्रह",
                    "समास-विग्रह", "उपसर्ग-प्रत्यय", "काल परिवर्तन",
                    
                    # लेखन कौशल
                    "रचनात्मक लेखन", "भावानुवाद", "सारांश लेखन", "पत्र लेखन",
                    "आवेदन पत्र", "शिकायती पत्र", "बधाई पत्र"
                ],
                
                10: [
                    # गद्य साहित्य
                    "आधुनिक हिंदी गद्य", "कहानी साहित्य", "उपन्यास साहित्य", "नाटक साहित्य",
                    "निबंध साहित्य", "आलोचना साहित्य", "जीवनी साहित्य", "यात्रा साहित्य",
                    
                    # काव्य साहित्य
                    "आधुनिक हिंदी काव्य", "छायावाद", "प्रगतिवाद", "प्रयोगवाद", "नई कविता",
                    "समकालीन कविता", "गीत काव्य", "प्रगीत काव्य",
                    
                    # व्याकरण और भाषा
                    "उच्च व्याकरण", "भाषा की शुद्धता", "वाक्य संरचना", "शब्द संपदा",
                    "मुहावरे-लोकोक्तियाँ", "पारिभाषिक शब्दावली",
                    
                    # रचना विधान
                    "निबंध लेखन", "कहानी लेखन", "नाटक लेखन", "संवाद लेखन",
                    "चरित्र चित्रण", "दृश्य चित्रण", "भाव चित्रण"
                ]
            },
            
            "Physics": {
                6: [
                    # Matter and Materials
                    "Matter and Its Properties", "States of Matter", "Solids, Liquids and Gases",
                    "Changes of State", "Melting and Freezing", "Evaporation and Condensation",
                    "Expansion and Contraction",
                    
                    # Force and Motion
                    "Force", "Effects of Force", "Types of Forces", "Contact and Non-contact Forces",
                    "Gravitational Force", "Magnetic Force", "Friction", "Motion", "Types of Motion",
                    
                    # Energy
                    "Forms of Energy", "Mechanical Energy", "Heat Energy", "Light Energy",
                    "Sound Energy", "Electrical Energy", "Energy Transformations",
                    "Sources of Energy", "Renewable and Non-renewable Energy",
                    
                    # Light
                    "Light and Its Properties", "Sources of Light", "Reflection of Light",
                    "Mirrors", "Plane Mirror", "Images", "Shadows", "Transparent, Translucent and Opaque Objects",
                    
                    # Sound
                    "Sound and Its Properties", "Sources of Sound", "How Sound Travels",
                    "Vibrations", "Musical Instruments", "Noise and Music",
                    
                    # Heat
                    "Heat and Temperature", "Thermometer", "Effects of Heat", "Conduction",
                    "Convection", "Radiation", "Good and Bad Conductors",
                    
                    # Magnetism
                    "Magnets", "Properties of Magnets", "Types of Magnets", "Magnetic Materials",
                    "Earth as a Magnet", "Compass"
                ],
                
                7: [
                    # Force and Pressure
                    "Force", "Balanced and Unbalanced Forces", "Pressure", "Pressure in Liquids",
                    "Atmospheric Pressure", "Applications of Pressure",
                    
                    # Motion and Time
                    "Motion", "Types of Motion", "Speed", "Measurement of Speed", "Distance-Time Graph",
                    "Uniform and Non-uniform Motion",
                    
                    # Heat
                    "Heat and Temperature", "Clinical Thermometer", "Laboratory Thermometer",
                    "Transfer of Heat", "Conduction, Convection and Radiation", "Sea Breeze and Land Breeze",
                    "Dark and Light Colored Objects",
                    
                    # Light
                    "Light", "Reflection of Light", "Laws of Reflection", "Regular and Irregular Reflection",
                    "Images formed by Plane Mirror", "Spherical Mirrors", "Images formed by Spherical Mirrors",
                    "Uses of Concave and Convex Mirrors",
                    
                    # Sound
                    "Sound", "How Sound is Produced", "How Sound Travels", "Audible and Inaudible Sounds",
                    "Noise and Music", "Noise Pollution",
                    
                    # Electric Current and Its Effects
                    "Electric Current", "Electric Circuit", "Effects of Electric Current",
                    "Magnetic Effect of Electric Current", "Electromagnet", "Electric Bell",
                    
                    # Energy
                    "Work and Energy", "Forms of Energy", "Law of Conservation of Energy",
                    "Commercial Unit of Energy"
                ],
                
                8: [
                    # Force and Pressure
                    "Force", "Contact and Non-contact Forces", "Pressure", "Pressure Exerted by Liquids and Gases",
                    "Atmospheric Pressure", "Buoyancy", "Archimedes' Principle",
                    
                    # Friction
                    "Friction", "Factors Affecting Friction", "Advantages and Disadvantages of Friction",
                    "Methods to Increase and Reduce Friction", "Fluid Friction",
                    
                    # Sound
                    "Production of Sound", "Propagation of Sound", "Reflection of Sound", "Echo",
                    "Range of Hearing", "Applications of Ultrasound",
                    
                    # Chemical Effects of Electric Current
                    "Conduction of Electricity", "Chemical Effects of Electric Current", "Electroplating",
                    "Electrolysis",
                    
                    # Some Natural Phenomena
                    "Lightning", "Charges and Sparks", "Transfer of Charge", "Story of Lightning",
                    "Lightning Safety", "Earthquakes", "Protection Against Earthquakes",
                    
                    # Light
                    "Reflection of Light", "Laws of Reflection", "Regular and Diffused Reflection",
                    "Images formed by Plane Mirror", "Kaleidoscope", "Periscope",
                    "Dispersion of Light", "Rainbow Formation"
                ],
                
                9: [
                    # Motion
                    "Motion in One Dimension", "Distance and Displacement", "Speed and Velocity",
                    "Acceleration", "Equations of Motion", "Uniform and Non-uniform Motion",
                    "Graphical Representation of Motion",
                    
                    # Force and Laws of Motion
                    "Force", "Newton's Laws of Motion", "Inertia", "Momentum", "Conservation of Momentum",
                    "Action and Reaction Forces",
                    
                    # Gravitation
                    "Universal Law of Gravitation", "Gravitational Constant", "Free Fall",
                    "Acceleration due to Gravity", "Weight", "Thrust and Pressure",
                    "Buoyancy", "Archimedes' Principle",
                    
                    # Work and Energy
                    "Work", "Energy", "Kinetic Energy", "Potential Energy", "Law of Conservation of Energy",
                    "Power", "Commercial Unit of Energy",
                    
                    # Sound
                    "Production of Sound", "Propagation of Sound", "Reflection of Sound",
                    "Reverberation and Echo", "Audible Range", "Ultrasound and Its Applications"
                ],
                
                10: [
                    # Light - Reflection and Refraction
                    "Reflection of Light", "Spherical Mirrors", "Image Formation by Spherical Mirrors",
                    "Mirror Formula", "Magnification", "Refraction of Light", "Laws of Refraction",
                    "Refractive Index", "Refraction by Spherical Lenses", "Image Formation by Lenses",
                    "Lens Formula", "Power of Lens",
                    
                    # The Human Eye and Colourful World
                    "Human Eye", "Defects of Vision", "Correction of Eye Defects", "Refraction of Light through Prism",
                    "Dispersion of White Light", "Atmospheric Refraction", "Scattering of Light",
                    
                    # Electricity
                    "Electric Current and Potential Difference", "Ohm's Law", "Resistance", "Factors Affecting Resistance",
                    "Series and Parallel Combinations", "Heating Effect of Electric Current", "Electric Power",
                    
                    # Magnetic Effects of Electric Current
                    "Magnetic Field", "Magnetic Field due to Current-carrying Conductor", "Force on Current-carrying Conductor",
                    "Fleming's Left-hand Rule", "Electric Motor", "Electromagnetic Induction", "Electric Generator",
                    
                    # Sources of Energy
                    "Conventional Sources of Energy", "Non-conventional Sources of Energy", "Fossil Fuels",
                    "Solar Energy", "Biogas", "Wind Energy", "Hydro Energy", "Nuclear Energy",
                    "Environmental Consequences"
                ]
            },
            
            "Chemistry": {
                6: [
                    # Introduction to Chemistry
                    "Matter", "Physical and Chemical Properties", "Elements, Compounds and Mixtures",
                    "Pure and Impure Substances", "Separation of Mixtures",
                    
                    # Air and Water
                    "Composition of Air", "Properties of Air", "Uses of Air", "Air Pollution",
                    "Water", "Sources of Water", "Properties of Water", "Hard and Soft Water",
                    "Water Pollution", "Water Treatment",
                    
                    # Acids, Bases and Salts
                    "Acids", "Bases", "Indicators", "Neutralization", "Salts",
                    
                    # Metals and Non-metals
                    "Properties of Metals", "Properties of Non-metals", "Uses of Metals and Non-metals",
                    
                    # Atomic Structure
                    "Atoms and Molecules", "Structure of Atom", "Elements and Symbols"
                ],
                
                7: [
                    # Elements, Compounds and Mixtures
                    "Elements", "Compounds", "Mixtures", "Separation Techniques",
                    "Crystallization", "Distillation", "Chromatography",
                    
                    # Atomic Structure
                    "Atomic Theory", "Structure of Atom", "Protons, Neutrons and Electrons",
                    "Electronic Configuration", "Valency",
                    
                    # Chemical Reactions
                    "Chemical Changes", "Chemical Equations", "Balancing Chemical Equations",
                    "Types of Chemical Reactions",
                    
                    # Acids, Bases and Salts
                    "Properties of Acids", "Properties of Bases", "Indicators", "pH Scale",
                    "Neutralization", "Preparation of Salts",
                    
                    # Air and Atmosphere
                    "Composition of Atmosphere", "Oxygen", "Carbon Dioxide", "Water Cycle",
                    "Air Pollution", "Greenhouse Effect"
                ],
                
                8: [
                    # Atomic Structure and Chemical Bonding
                    "Atomic Structure", "Electronic Configuration", "Valency", "Chemical Bonding",
                    "Ionic Bonding", "Covalent Bonding",
                    
                    # Chemical Reactions
                    "Types of Chemical Reactions", "Oxidation and Reduction", "Displacement Reactions",
                    "Double Displacement Reactions", "Precipitation Reactions",
                    
                    # Acids, Bases and Salts
                    "Strong and Weak Acids and Bases", "pH Scale", "Salt Hydrolysis",
                    "Preparation of Salts", "Uses of Acids, Bases and Salts",
                    
                    # Hydrogen
                    "Preparation of Hydrogen", "Properties of Hydrogen", "Uses of Hydrogen",
                    
                    # Water
                    "Water as a Universal Solvent", "Solutions", "Solubility", "Concentration",
                    "Crystallization", "Water of Crystallization",
                    
                    # Carbon and Its Compounds
                    "Allotropes of Carbon", "Diamond", "Graphite", "Coal", "Petroleum"
                ],
                
                9: [
                    # Atomic Structure and Chemical Bonding
                    "Atomic Models", "Bohr's Model", "Electronic Configuration", "Valency",
                    "Chemical Bonding", "Ionic Bond", "Covalent Bond", "Properties of Ionic and Covalent Compounds",
                    
                    # Study of Gas Laws
                    "Boyle's Law", "Charles' Law", "Gay-Lussac's Law", "Avogadro's Law",
                    "Ideal Gas Equation", "Kinetic Molecular Theory",
                    
                    # Atmospheric Pollution
                    "Air Pollution", "Water Pollution", "Soil Pollution", "Greenhouse Effect",
                    "Ozone Depletion", "Acid Rain",
                    
                    # The Language of Chemistry
                    "Chemical Symbols", "Chemical Formulae", "Chemical Equations", "Balancing Equations",
                    "Information from Chemical Equations",
                    
                    # Chemical Changes and Reactions
                    "Physical and Chemical Changes", "Types of Chemical Reactions", "Energy Changes in Reactions",
                    "Catalysts", "Reversible and Irreversible Reactions"
                ],
                
                10: [
                    # Periodic Properties and Variations
                    "Modern Periodic Table", "Periodic Properties", "Atomic Size", "Ionization Energy",
                    "Electron Affinity", "Electronegativity", "Metallic and Non-metallic Character",
                    
                    # Chemical Bonding
                    "Ionic Bonding", "Covalent Bonding", "Coordinate Bonding", "Metallic Bonding",
                    "Intermolecular Forces", "Hydrogen Bonding",
                    
                    # Study of Acids, Bases and Salts
                    "Arrhenius Theory", "Bronsted-Lowry Theory", "Lewis Theory", "pH Scale",
                    "Buffer Solutions", "Hydrolysis of Salts", "Preparation of Salts",
                    
                    # Analytical Chemistry
                    "Qualitative Analysis", "Tests for Cations", "Tests for Anions", "Flame Tests",
                    "Precipitation Reactions", "Confirmatory Tests",
                    
                    # Mole Concept and Stoichiometry
                    "Atomic Mass", "Molecular Mass", "Mole Concept", "Avogadro's Number",
                    "Empirical and Molecular Formula", "Stoichiometric Calculations",
                    
                    # Electrolysis
                    "Electrolytes and Non-electrolytes", "Electrolysis", "Applications of Electrolysis",
                    "Electroplating", "Extraction of Metals",
                    
                    # Metallurgy
                    "Occurrence of Metals", "Extraction of Metals", "Refining of Metals",
                    "Alloys", "Corrosion and Its Prevention",
                    
                    # Study of Compounds
                    "Hydrogen Chloride", "Ammonia", "Nitric Acid", "Sulphuric Acid",
                    "Preparation, Properties and Uses",
                    
                    # Organic Chemistry
                    "Introduction to Organic Chemistry", "Hydrocarbons", "Alkanes, Alkenes, Alkynes",
                    "Functional Groups", "Alcohols", "Carboxylic Acids"
                ]
            },
            
            "Biology": {
                6: [
                    # Cell - The Basic Unit of Life
                    "Cell Theory", "Cell Structure", "Plant Cell", "Animal Cell", "Cell Organelles",
                    "Differences between Plant and Animal Cells",
                    
                    # Plant Life
                    "Parts of a Plant", "Root System", "Shoot System", "Leaves", "Photosynthesis",
                    "Respiration in Plants", "Transportation in Plants",
                    
                    # Flowering Plants
                    "Parts of a Flower", "Types of Flowers", "Pollination", "Fertilization",
                    "Seed Formation", "Fruit Formation", "Seed Dispersal",
                    
                    # Animal Life
                    "Classification of Animals", "Vertebrates and Invertebrates", "Animal Habitats",
                    "Adaptation in Animals", "Life Cycles of Animals",
                    
                    # Human Body
                    "Human Body Systems", "Skeletal System", "Muscular System", "Digestive System",
                    "Respiratory System", "Circulatory System", "Nervous System",
                    
                    # Health and Hygiene
                    "Personal Hygiene", "Dental Care", "Balanced Diet", "Exercise and Health",
                    "Common Diseases", "Prevention of Diseases",
                    
                    # Habitat and Adaptation
                    "Types of Habitats", "Terrestrial Habitats", "Aquatic Habitats", "Arboreal Habitats",
                    "Adaptation for Protection", "Adaptation for Getting Food"
                ],
                
                7: [
                    # Classification of Plants
                    "Plant Kingdom", "Classification Criteria", "Thallophyta", "Bryophyta",
                    "Pteridophyta", "Gymnosperms", "Angiosperms", "Monocots and Dicots",
                    
                    # Classification of Animals
                    "Animal Kingdom", "Classification Criteria", "Invertebrates", "Vertebrates",
                    "Phylum Coelenterata", "Phylum Platyhelminthes", "Phylum Nematoda",
                    "Phylum Annelida", "Phylum Arthropoda", "Phylum Mollusca", "Phylum Echinodermata",
                    "Phylum Chordata",
                    
                    # Photosynthesis
                    "Process of Photosynthesis", "Conditions for Photosynthesis", "Raw Materials",
                    "Products of Photosynthesis", "Factors Affecting Photosynthesis",
                    
                    # Respiration
                    "Respiration in Plants", "Respiration in Animals", "Breathing in Humans",
                    "Respiratory System", "Exchange of Gases",
                    
                    # Transportation
                    "Transportation in Plants", "Xylem and Phloem", "Transpiration",
                    "Transportation in Animals", "Circulatory System", "Heart", "Blood Vessels", "Blood",
                    
                    # Reproduction
                    "Reproduction in Plants", "Vegetative Reproduction", "Sexual Reproduction",
                    "Reproduction in Animals", "Sexual and Asexual Reproduction",
                    
                    # Health and Disease
                    "Health and Disease", "Communicable Diseases", "Non-communicable Diseases",
                    "Disease Prevention", "Immunization"
                ],
                
                8: [
                    # Crop Production and Management
                    "Agricultural Practices", "Crop Variety Improvement", "Crop Production",
                    "Crop Protection", "Animal Husbandry",
                    
                    # Cell Division and Reproduction
                    "Cell Division", "Mitosis", "Meiosis", "Reproduction in Animals",
                    "Sexual and Asexual Reproduction", "Reproductive Health",
                    
                    # Heredity and Evolution
                    "Heredity", "Inheritance of Traits", "Mendel's Laws", "Chromosomes and Genes",
                    "Sex Determination", "Evolution", "Origin of Life",
                    
                    # Microorganisms
                    "Microorganisms", "Classification of Microorganisms", "Bacteria", "Viruses",
                    "Fungi", "Protozoa", "Algae", "Useful and Harmful Microorganisms",
                    
                    # Ecosystem
                    "Ecosystem", "Components of Ecosystem", "Food Chain", "Food Web",
                    "Energy Flow", "Biogeochemical Cycles", "Human Impact on Environment",
                    
                    # Human Body Systems
                    "Digestive System", "Respiratory System", "Circulatory System", "Excretory System",
                    "Nervous System", "Endocrine System", "Reproductive System"
                ],
                
                9: [
                    # The Fundamental Unit of Life
                    "Cell Theory", "Prokaryotic and Eukaryotic Cells", "Plant and Animal Cells",
                    "Cell Organelles and Their Functions", "Cell Division",
                    
                    # Tissues
                    "Plant Tissues", "Meristematic Tissues", "Permanent Tissues", "Simple Tissues",
                    "Complex Tissues", "Animal Tissues", "Epithelial Tissue", "Connective Tissue",
                    "Muscular Tissue", "Nervous Tissue",
                    
                    # Diversity in Living Organisms
                    "Classification of Living Organisms", "Five Kingdom Classification",
                    "Monera", "Protista", "Fungi", "Plantae", "Animalia",
                    "Hierarchy of Classification", "Nomenclature",
                    
                    # Plant Physiology
                    "Life Processes in Plants", "Nutrition", "Photosynthesis", "Respiration",
                    "Transportation", "Excretion", "Control and Coordination",
                    
                    # Animal Physiology
                    "Life Processes in Animals", "Nutrition in Animals", "Respiration in Animals",
                    "Transportation in Animals", "Excretion in Animals", "Control and Coordination in Animals",
                    
                    # Reproduction
                    "Reproduction in Plants", "Vegetative Propagation", "Sexual Reproduction in Plants",
                    "Reproduction in Animals", "Sexual and Asexual Reproduction",
                    
                    # Health and Disease
                    "Health and Its Significance", "Disease and Its Causes", "Infectious Diseases",
                    "Prevention and Control of Diseases", "Immunization"
                ],
                
                10: [
                    # Life Processes
                    "Nutrition", "Autotrophic Nutrition", "Heterotrophic Nutrition", "Nutrition in Human Beings",
                    "Respiration", "Respiration in Plants", "Respiration in Animals", "Human Respiratory System",
                    "Transportation", "Transportation in Plants", "Transportation in Animals", "Human Circulatory System",
                    "Excretion", "Excretion in Plants", "Excretion in Animals", "Human Excretory System",
                    
                    # Control and Coordination
                    "Control and Coordination in Animals", "Nervous System", "Endocrine System",
                    "Control and Coordination in Plants", "Plant Hormones", "Movements in Plants",
                    
                    # How do Organisms Reproduce
                    "Reproduction", "Asexual Reproduction", "Sexual Reproduction", "Reproductive Health",
                    "Reproduction in Plants", "Reproduction in Animals", "Reproduction in Human Beings",
                    
                    # Heredity and Evolution
                    "Heredity", "Inheritance of Traits", "Mendel's Laws of Inheritance", "Sex Determination",
                    "Evolution", "Origin of Life", "Natural Selection", "Speciation",
                    
                    # Our Environment
                    "Ecosystem", "Components of Ecosystem", "Food Chains and Food Webs",
                    "Energy Flow in Ecosystem", "Biogeochemical Cycles", "Environmental Problems",
                    "Biodiversity and Its Conservation"
                ]
            },
            
            "History & Civics": {
                6: [
                    # History
                    "What is History", "Sources of History", "Prehistoric Times", "Stone Age",
                    "Indus Valley Civilization", "Vedic Civilization", "Life in Vedic Times",
                    "Rise of Kingdoms", "Mahajanapadas", "Rise of Magadha", "Alexander's Invasion",
                    "Mauryan Empire", "Chandragupta Maurya", "Ashoka the Great", "Gupta Empire",
                    "Golden Age of Guptas", "Harsha's Empire",
                    
                    # Ancient Civilizations
                    "Mesopotamian Civilization", "Egyptian Civilization", "Chinese Civilization",
                    "Greek Civilization", "Roman Civilization",
                    
                    # Civics
                    "What is Government", "Levels of Government", "Local Government",
                    "Panchayati Raj", "Village Panchayat", "Block Panchayat", "District Panchayat",
                    "Municipal Corporation", "Municipality", "Cantonment Board",
                    "Citizen and Citizenship", "Rights and Duties of Citizens",
                    "Unity in Diversity", "National Symbols"
                ],
                
                7: [
                    # Medieval History
                    "Medieval Period", "Arab Invasion", "Turkish Invasion", "Delhi Sultanate",
                    "Slave Dynasty", "Khilji Dynasty", "Tughlaq Dynasty", "Sayyid Dynasty", "Lodi Dynasty",
                    "Vijayanagara Empire", "Bahmani Kingdom", "Regional Kingdoms",
                    "Mughal Empire", "Babur", "Humayun", "Akbar", "Jahangir", "Shah Jahan", "Aurangzeb",
                    "Decline of Mughal Empire", "Rise of Regional Powers",
                    
                    # Medieval Society and Culture
                    "Medieval Society", "Religion in Medieval India", "Art and Architecture",
                    "Literature", "Science and Technology", "Trade and Commerce",
                    
                    # Civics
                    "State Government", "Chief Minister", "Governor", "State Legislature",
                    "State Assembly", "Legislative Council", "Functions of State Government",
                    "Union Government", "President", "Prime Minister", "Parliament",
                    "Lok Sabha", "Rajya Sabha", "Functions of Union Government",
                    "Constitution of India", "Fundamental Rights", "Fundamental Duties"
                ],
                
                8: [
                    # Modern History
                    "Coming of Europeans", "Portuguese", "Dutch", "French", "English",
                    "East India Company", "Battle of Plassey", "Battle of Buxar", "British Rule in India",
                    "Administrative Policies", "Economic Policies", "Social Reforms",
                    "Indian Renaissance", "Reform Movements", "Great Revolt of 1857",
                    "Growth of Nationalism", "Indian National Congress", "Partition of Bengal",
                    "Swadeshi Movement", "Revolutionary Movement",
                    
                    # Freedom Struggle
                    "Mahatma Gandhi", "Non-Cooperation Movement", "Civil Disobedience Movement",
                    "Quit India Movement", "World War II and India", "Indian National Army",
                    "Partition of India", "Independence Day",
                    
                    # Civics
                    "Judiciary", "Supreme Court", "High Court", "District Court", "Independence of Judiciary",
                    "Election Commission", "Electoral Process", "Political Parties",
                    "Pressure Groups", "Media and Democracy", "Challenges to Democracy"
                ],
                
                9: [
                    # French Revolution
                    "Causes of French Revolution", "Course of Revolution", "Reign of Terror",
                    "Rise of Napoleon", "Effects of French Revolution",
                    
                    # Industrial Revolution
                    "Industrial Revolution in England", "Causes and Effects", "Transportation Revolution",
                    "Social Changes", "Working Class Movement",
                    
                    # Rise of Nationalism
                    "Nationalism in Europe", "Unification of Germany", "Unification of Italy",
                    "Russian Revolution", "Rise of Fascism and Nazism",
                    
                    # World Wars
                    "First World War", "Causes and Effects", "Second World War",
                    "Rise of Hitler", "Cold War", "Formation of UNO",
                    
                    # Civics
                    "Democratic Government", "What is Democracy", "Features of Democracy",
                    "Electoral Politics", "Working of Institutions", "Democratic Rights",
                    "Constitutional Design", "Making of Indian Constitution"
                ],
                
                10: [
                    # Nationalism in India
                    "First War of Independence 1857", "Growth of Nationalism", "Partition of Bengal",
                    "Swadeshi Movement", "Formation of Muslim League", "Morley-Minto Reforms",
                    "Home Rule Movement", "Rowlatt Act", "Jallianwala Bagh Massacre",
                    "Khilafat Movement", "Non-Cooperation Movement", "Civil Disobedience Movement",
                    "Government of India Act 1935", "Quit India Movement", "Partition and Independence",
                    
                    # The Making of Global World
                    "Trade and Globalization", "Colonialism", "Rinderpest in Africa",
                    "Impact of Technology", "World Wars and Recovery", "Bretton Woods System",
                    
                    # The Age of Industrialization
                    "Before Industrial Revolution", "Industrial Revolution", "Industrialization in Colonies",
                    "Factory System", "Impact on Workers", "Industrial Cities",
                    
                    # Print Culture and Modern World
                    "History of Print", "Print Revolution", "Print Culture in India",
                    "Religious Reform and Public Debates", "New Forms of Publication",
                    
                    # Civics - Power Sharing
                    "Power Sharing", "Belgium and Sri Lanka", "Forms of Power Sharing",
                    "Federal System", "Indian Federalism", "Language Policy",
                    
                    # Democracy and Diversity
                    "Social Differences", "Overlapping and Cross-cutting Differences", "Politics of Social Divisions",
                    "Democracy and Social Diversity", "Gender, Religion and Caste",
                    
                    # Political Parties
                    "Political Parties", "Functions of Political Parties", "Necessity of Political Parties",
                    "How Many Parties", "National and Regional Parties", "Challenges to Political Parties",
                    
                    # Outcomes of Democracy
                    "How do we Assess Democracy", "Accountable, Responsive and Legitimate Government",
                    "Economic Growth and Development", "Reduction of Inequality and Poverty",
                    "Accommodation of Social Diversity", "Dignity and Freedom of Citizens"
                ]
            },
            
            "Geography": {
                6: [
                    # The Earth
                    "Earth as a Planet", "Shape and Size of Earth", "Globe and Maps",
                    "Latitudes and Longitudes", "Geographic Grid", "Time Zones",
                    
                    # Motions of Earth
                    "Rotation of Earth", "Revolution of Earth", "Seasons", "Day and Night",
                    
                    # Structure of Earth
                    "Internal Structure of Earth", "Crust", "Mantle", "Core", "Rocks and Minerals",
                    "Types of Rocks", "Rock Cycle",
                    
                    # Landforms
                    "Major Landforms", "Mountains", "Plateaus", "Plains", "Deserts",
                    "Coastal Landforms", "Islands",
                    
                    # Water Bodies
                    "Hydrosphere", "Oceans", "Seas", "Rivers", "Lakes", "Water Cycle",
                    
                    # Weather and Climate
                    "Atmosphere", "Weather and Climate", "Elements of Weather", "Climate Zones",
                    
                    # Natural Vegetation
                    "Natural Vegetation", "Forests", "Grasslands", "Desert Vegetation",
                    "Wildlife", "National Parks and Sanctuaries"
                ],
                
                7: [
                    # Environment
                    "Natural Environment", "Human Environment", "Human-Environment Interaction",
                    "Environmental Problems", "Conservation of Environment",
                    
                    # Inside Our Earth
                    "Interior of Earth", "Rocks and Minerals", "Rock Cycle", "Earth's Crust",
                    
                    # Our Changing Earth
                    "Lithospheric Plates", "Plate Tectonics", "Volcanoes", "Earthquakes",
                    "Weathering", "Erosion", "Deposition",
                    
                    # Air
                    "Atmosphere", "Composition of Atmosphere", "Structure of Atmosphere",
                    "Weather", "Climate", "Adaptation by Animals and Plants",
                    
                    # Water
                    "Water Cycle", "Distribution of Water", "Ocean Currents", "Tides", "Waves",
                    
                    # Natural Vegetation and Wildlife
                    "Forests", "Grasslands", "Desert Vegetation", "Wildlife", "Conservation",
                    
                    # Human Environment
                    "Settlement", "Rural Settlement", "Urban Settlement", "Transport",
                    "Communication"
                ],
                
                8: [
                    # Resources
                    "Resources", "Types of Resources", "Natural Resources", "Human Resources",
                    "Conservation of Resources", "Sustainable Development",
                    
                    # Land, Soil, Water, Natural Vegetation and Wildlife
                    "Land Use", "Land Degradation", "Soil Formation", "Soil Types", "Soil Erosion",
                    "Water Scarcity", "Water Conservation", "Forests", "Deforestation",
                    "Wildlife Conservation",
                    
                    # Mineral and Power Resources
                    "Minerals", "Types of Minerals", "Distribution of Minerals", "Coal", "Petroleum",
                    "Natural Gas", "Renewable Energy", "Solar Energy", "Wind Energy", "Hydroelectric Power",
                    
                    # Agriculture
                    "Agriculture", "Types of Farming", "Crop Seasons", "Major Crops", "Agricultural Development",
                    
                    # Industries
                    "Industries", "Types of Industries", "Cotton Textile Industry", "Iron and Steel Industry",
                    "Information Technology Industry", "Industrial Pollution",
                    
                    # Human Resources
                    "People as Resource", "Population", "Population Distribution", "Population Density",
                    "Population Growth", "Age Structure", "Human Development"
                ],
                
                9: [
                    # India - Size and Location
                    "India's Location", "India's Neighbors", "India's Size", "Administrative Divisions",
                    
                    # Physical Features of India
                    "Major Physical Divisions", "The Himalayan Mountains", "The Northern Plains",
                    "The Peninsular Plateau", "The Indian Desert", "The Coastal Plains", "The Islands",
                    
                    # Drainage
                    "Drainage Systems", "The Himalayan Rivers", "The Peninsular Rivers",
                    "Lakes", "Role of Rivers in Economy", "River Pollution",
                    
                    # Climate
                    "Climate Controls", "Factors Affecting Climate", "Indian Monsoon", "Seasons",
                    "Distribution of Rainfall", "Climate and Human Life",
                    
                    # Natural Vegetation and Wildlife
                    "Factors of Natural Vegetation", "Types of Vegetation", "Tropical Rainforests",
                    "Tropical Deciduous Forests", "Thorn Forests", "Mountain Vegetation",
                    "Mangrove Vegetation", "Wildlife", "National Parks", "Biosphere Reserves",
                    
                    # Population
                    "Population Size and Distribution", "Population Growth", "Age Composition",
                    "Sex Ratio", "Literacy Rate", "Population Policy"
                ],
                
                10: [
                    # Resources and Development
                    "Resource Planning", "Land Resources", "Land Use Pattern", "Land Degradation",
                    "Soil as a Resource", "Soil Formation", "Soil Types", "Soil Erosion and Conservation",
                    
                    # Forest and Wildlife Resources
                    "Forest and Wildlife", "Biodiversity", "Forest Types", "Deforestation",
                    "Conservation of Forest and Wildlife", "Community and Conservation",
                    
                    # Water Resources
                    "Water Scarcity", "Water Resources", "Multipurpose River Projects", "Rainwater Harvesting",
                    "Water Pollution", "Water Conservation",
                    
                    # Agriculture
                    "Types of Farming", "Cropping Pattern", "Major Crops", "Food Crops", "Cash Crops",
                    "Technological and Institutional Reforms", "Food Security",
                    
                    # Minerals and Energy Resources
                    "Mineral Resources", "Ferrous Minerals", "Non-ferrous Minerals", "Non-metallic Minerals",
                    "Energy Resources", "Conventional Sources", "Non-conventional Sources",
                    
                    # Manufacturing Industries
                    "Manufacturing", "Types of Industries", "Spatial Distribution", "Industrial Pollution",
                    "Iron and Steel Industry", "Textile Industry", "Information Technology",
                    
                    # Lifelines of National Economy
                    "Transport", "Roadways", "Railways", "Waterways", "Airways", "Pipelines",
                    "Communication", "International Trade"
                ]
            },
            
            "Computer Applications": {
                6: [
                    # Introduction to Computers
                    "What is a Computer", "Characteristics of Computer", "Types of Computers",
                    "Applications of Computer", "Computer System", "Hardware and Software",
                    
                    # Hardware Components
                    "Input Devices", "Output Devices", "Processing Unit", "Memory", "Storage Devices",
                    
                    # Software
                    "System Software", "Application Software", "Operating System", "Programming Languages",
                    
                    # Windows Operating System
                    "Introduction to Windows", "Desktop", "Taskbar", "Start Menu", "Windows Explorer",
                    "File Management", "Control Panel",
                    
                    # MS Paint
                    "Introduction to Paint", "Drawing Tools", "Color Palette", "Text Tool",
                    "Saving and Opening Files",
                    
                    # Word Processing
                    "Introduction to Word Processor", "Creating Documents", "Formatting Text",
                    "Inserting Pictures", "Tables", "Saving and Printing"
                ],
                
                7: [
                    # Computer Fundamentals
                    "Computer Generation", "Computer Architecture", "Von Neumann Architecture",
                    "Data and Information", "Number Systems", "Binary System",
                    
                    # Operating Systems
                    "Functions of Operating System", "Types of Operating System", "File Management",
                    "Memory Management", "Process Management",
                    
                    # MS Word Advanced
                    "Advanced Formatting", "Styles", "Headers and Footers", "Page Setup",
                    "Mail Merge", "Track Changes", "Comments",
                    
                    # MS Excel
                    "Introduction to Spreadsheet", "Workbook and Worksheet", "Data Entry",
                    "Formulas and Functions", "Charts and Graphs", "Data Analysis",
                    
                    # MS PowerPoint
                    "Introduction to Presentation Software", "Slides", "Text and Graphics",
                    "Animation", "Slide Transitions", "Presentation Delivery",
                    
                    # Internet
                    "Introduction to Internet", "World Wide Web", "Web Browser", "Search Engines",
                    "Email", "Internet Safety"
                ],
                
                8: [
                    # Advanced Computer Concepts
                    "Computer Networks", "Types of Networks", "Internet", "Protocols",
                    "Client-Server Model", "Database Concepts",
                    
                    # Programming Concepts
                    "Introduction to Programming", "Algorithms", "Flowcharts", "Programming Languages",
                    "Syntax and Semantics", "Debugging",
                    
                    # HTML
                    "Introduction to HTML", "HTML Tags", "Structure of HTML Document",
                    "Text Formatting", "Links", "Images", "Tables", "Forms",
                    
                    # Advanced Applications
                    "Database Management", "Creating Databases", "Tables", "Queries", "Reports",
                    "Web Design", "Multimedia Applications",
                    
                    # Digital Citizenship
                    "Computer Ethics", "Cyber Safety", "Digital Footprint", "Copyright",
                    "Privacy and Security", "Social Media Responsibility"
                ],
                
                9: [
                    # Computer Systems
                    "Computer Organization", "CPU Architecture", "Memory Hierarchy", "Storage Systems",
                    "Input/Output Systems", "Performance Metrics",
                    
                    # Programming in Java
                    "Introduction to Java", "Object-Oriented Programming", "Classes and Objects",
                    "Data Types", "Variables", "Operators", "Control Structures",
                    "Methods", "Arrays", "Inheritance", "Polymorphism",
                    
                    # Database Management
                    "Database Concepts", "Relational Database", "SQL", "Creating Tables",
                    "Data Manipulation", "Queries", "Joins", "Database Design",
                    
                    # Web Technologies
                    "Advanced HTML", "CSS", "JavaScript", "Dynamic Web Pages",
                    "Client-Side Scripting", "Server-Side Scripting",
                    
                    # Computer Networks
                    "Network Topologies", "Network Protocols", "Internet", "Email",
                    "Network Security", "Firewalls", "Encryption"
                ],
                
                10: [
                    # Object-Oriented Programming
                    "OOP Concepts", "Encapsulation", "Inheritance", "Polymorphism", "Abstraction",
                    "Classes and Objects", "Constructors", "Method Overloading", "Method Overriding",
                    
                    # Java Programming
                    "Java Syntax", "Data Types", "Variables", "Operators", "Control Flow",
                    "Arrays", "Strings", "Exception Handling", "File Handling",
                    "Collections Framework", "Multithreading",
                    
                    # Database Connectivity
                    "JDBC", "Database Connection", "SQL Queries", "ResultSet",
                    "Prepared Statements", "Database Applications",
                    
                    # Web Development
                    "HTML5", "CSS3", "JavaScript", "DOM Manipulation", "Event Handling",
                    "AJAX", "jQuery", "Responsive Design",
                    
                    # Project Work
                    "System Analysis", "Design", "Implementation", "Testing", "Documentation",
                    "Project Management", "Software Development Life Cycle"
                ]
            },
            
            "Sanskrit": {
                6: [
                    # देवनागरी और उच्चारण
                    "देवनागरी लिपि", "संस्कृत वर्णमाला", "स्वर और व्यंजन", "संयुक्त अक्षर",
                    "उच्चारण नियम", "मात्राएँ", "अनुस्वार और विसर्ग",
                    
                    # व्याकरण आधार
                    "संज्ञा", "सर्वनाम", "विशेषण", "क्रिया", "धातु", "प्रत्यय",
                    "उपसर्ग", "संधि परिचय", "समास परिचय",
                    
                    # श्लोक और मंत्र
                    "सरस्वती वंदना", "गायत्री मंत्र", "शांति मंत्र", "सरल श्लोक",
                    "संस्कृत गीत", "संस्कृत संख्या",
                    
                    # सरल गद्य
                    "सरल संस्कृत वाक्य", "दैनिक प्रयोग के शब्द", "परिवार के संबंध",
                    "रंग", "फल", "फूल", "पशु-पक्षी के नाम"
                ],
                
                7: [
                    # व्याकरण विस्तार
                    "संधि विधि", "स्वर संधि", "व्यंजन संधि", "विसर्ग संधि",
                    "समास के भेद", "तत्पुरुष", "द्वंद", "बहुव्रीहि", "अव्ययीभाव",
                    "धातु रूप", "भू", "कृ", "गम्", "पठ्", "हस्",
                    
                    # छंद शास्त्र
                    "अनुष्टुप छंद", "श्लोक की संरचना", "गुरु-लघु", "यति-गति",
                    
                    # गद्य पाठ
                    "कथा संग्रह", "हितोपदेश से कहानियाँ", "पंचतंत्र की कथाएँ",
                    "नीति श्लोक", "सुभाषित",
                    
                    # श्लोक संग्रह
                    "भगवद्गीता के श्लोक", "रामायण के श्लोक", "महाभारत के श्लोक",
                    "कालिदास के श्लोक"
                ],
                
                8: [
                    # उन्नत व्याकरण
                    "कारक प्रकरण", "आठ कारक", "विभक्ति प्रयोग", "संज्ञा रूप",
                    "राम शब्द", "हरि शब्द", "मति शब्द", "नदी शब्द",
                    "सर्वनाम रूप", "तत्", "यत्", "एतत्", "किम्",
                    
                    # छंद और काव्य
                ],
                6: [
                    # Health and Fitness
                    "Physical Fitness", "Components of Fitness", "Health-related Fitness",
                    "Skill-related Fitness", "Exercise and Health", "Benefits of Physical Activity",
                    
                    # Basic Movement Skills
                    "Fundamental Movement Skills", "Locomotor Skills", "Non-locomotor Skills",
                    "Manipulative Skills", "Body Awareness", "Spatial Awareness",
                    
                    # Games and Sports
                    "Introduction to Games", "Team Games", "Individual Games", "Traditional Games",
                    "Rules and Regulations", "Sportsmanship", "Fair Play",
                    
                    # Athletics
                    "Track Events", "Field Events", "Running", "Jumping", "Throwing",
                    "Athletic Meet", "Records and Measurements",
                    
                    # Gymnastics
                    "Basic Gymnastics", "Floor Exercises", "Balance", "Flexibility",
                    "Coordination", "Rhythmic Activities",
                    
                    # Health Education
                    "Personal Hygiene", "Nutrition", "First Aid", "Safety Measures",
                    "Common Injuries", "Prevention of Diseases"
                ],
                
                7: [
                    # Fitness Training
                    "Physical Fitness Training", "Strength Training", "Endurance Training",
                    "Flexibility Training", "Speed Training", "Training Principles",
                    
                    # Sports Skills
                    "Skill Development", "Motor Learning", "Practice Methods", "Technique Training",
                    "Performance Enhancement", "Skill Assessment",
                    
                    # Team Sports
                    "Football", "Basketball", "Volleyball", "Hockey", "Cricket",
                    "Handball", "Kabaddi", "Kho-Kho",
                    
                    # Individual Sports
                    "Badminton", "Table Tennis", "Tennis", "Swimming", "Athletics",
                    "Boxing", "Wrestling", "Martial Arts",
                    
                    # Yoga and Meditation
                    "Introduction to Yoga", "Asanas", "Pranayama", "Meditation",
                    "Benefits of Yoga", "Stress Management",
                    
                    # Sports Psychology
                    "Motivation", "Goal Setting", "Concentration", "Confidence Building",
                    "Stress and Anxiety", "Mental Preparation"
                ],
                
                8: [
                    # Advanced Fitness
                    "Advanced Training Methods", "Periodization", "Overload Principle",
                    "Recovery and Rest", "Fitness Testing", "Performance Evaluation",
                    
                    # Sports Biomechanics
                    "Movement Analysis", "Technique Improvement", "Efficiency of Movement",
                    "Force and Motion", "Leverage", "Projectile Motion",
                    
                    # Sports Medicine
                    "Sports Injuries", "Injury Prevention", "Treatment of Injuries",
                    "Rehabilitation", "Sports Massage", "Therapeutic Exercises",
                    
                    # Leadership and Coaching
                    "Leadership Skills", "Coaching Principles", "Teaching Methods",
                    "Communication Skills", "Team Management", "Official Rules",
                    
                    # Adventure Sports
                    "Outdoor Activities", "Trekking", "Camping", "Rock Climbing",
                    "Water Sports", "Safety in Adventure Sports",
                    
                    # Sports Management
                    "Organization of Sports Events", "Tournament Systems", "Sports Administration",
                    "Facilities and Equipment", "Budgeting", "Sponsorship"
                ],
                
                9: [
                    # Exercise Physiology
                    "Human Body Systems", "Muscular System", "Cardiovascular System",
                    "Respiratory System", "Energy Systems", "Fatigue and Recovery",
                    
                    # Training Methodology
                    "Training Plans", "Macrocycles", "Mesocycles", "Microcycles",
                    "Periodization Models", "Peak Performance", "Tapering",
                    
                    # Sports Nutrition
                    "Nutritional Requirements", "Pre-competition Nutrition", "During Competition",
                    "Post-competition Recovery", "Hydration Strategies", "Supplements",
                    
                    # Psychology of Sports
                    "Mental Training", "Visualization", "Relaxation Techniques", "Arousal Control",
                    "Attention and Concentration", "Team Dynamics", "Leadership",
                    
                    # Olympic Movement
                    "History of Olympics", "Olympic Values", "International Sports Organizations",
                    "Olympic Games", "Paralympic Games", "Commonwealth Games",
                    
                    # Career in Sports
                    "Professional Sports", "Sports Careers", "Sports Sciences", "Sports Journalism",
                    "Sports Marketing", "Sports Law", "Sports Technology"
                ],
                
                10: [
                    # Sports Science
                    "Exercise Physiology", "Biomechanics", "Sports Psychology", "Sports Nutrition",
                    "Sports Medicine", "Training Science", "Performance Analysis",
                    
                    # Research in Sports
                    "Research Methods", "Data Collection", "Statistical Analysis", "Research Design",
                    "Sports Technology", "Performance Measurement", "Innovation in Sports",
                    
                    # International Sports
                    "Global Sports Organizations", "International Competitions", "Sports Diplomacy",
                    "Cultural Exchange through Sports", "Sports and Peace", "Women in Sports",
                    
                    # Professional Development
                    "Coaching Certification", "Referee Training", "Sports Management Courses",
                    "Fitness Training Certification", "Sports Therapy", "Career Planning",
                    
                    # Ethics in Sports
                    "Fair Play", "Doping", "Sports Integrity", "Gender Equality", "Inclusion",
                    "Environmental Responsibility", "Social Responsibility of Sports",
                    
                    # Future of Sports
                    "Technology in Sports", "Virtual Reality", "Artificial Intelligence",
                    "E-sports", "Future Trends", "Innovation in Training", "Sustainable Sports"
                ]
            },
            
            # ISC Subjects (Grades 11-12)
            "Mathematics (ISC)": {
                11: [
                    # Sets and Functions
                    "Sets", "Subsets", "Union and Intersection", "Complement of Sets", "Venn Diagrams",
                    "Relations", "Types of Relations", "Functions", "Types of Functions",
                    "Composition of Functions", "Inverse of Functions",
                    
                    # Algebra
                    "Principle of Mathematical Induction", "Complex Numbers", "Quadratic Equations",
                    "Linear Inequalities", "Permutations and Combinations", "Binomial Theorem",
                    "Sequences and Series", "Arithmetic Progression", "Geometric Progression",
                    
                    # Coordinate Geometry
                    "Straight Lines", "Circle", "Parabola", "Ellipse", "Hyperbola",
                    "Introduction to Three-dimensional Geometry",
                    
                    # Calculus
                    "Limits and Derivatives", "Limits of Functions", "Derivatives",
                    "Applications of Derivatives",
                    
                    # Mathematical Reasoning
                    "Mathematical Reasoning", "Statements", "Logical Connectives",
                    "Implications", "Validating Statements",
                    
                    # Statistics and Probability
                    "Statistics", "Measures of Dispersion", "Probability", "Random Experiments",
                    "Events", "Probability of Events"
                ],
                
                12: [
                    # Relations and Functions
                    "Relations and Functions", "Types of Functions", "Composition of Functions",
                    "Invertible Functions", "Binary Operations",
                    
                    # Algebra
                    "Inverse Trigonometric Functions", "Matrices", "Determinants",
                    "Properties of Determinants", "Applications of Determinants and Matrices",
                    
                    # Calculus
                    "Continuity and Differentiability", "Applications of Derivatives",
                    "Integrals", "Applications of Integrals", "Differential Equations",
                    
                    # Vectors and 3D Geometry
                    "Vectors", "Scalar and Vector Products", "Three Dimensional Geometry",
                    
                    # Linear Programming
                    "Linear Programming", "Related Problems", "Mathematical Formulation",
                    "Graphical Method of Solution",
                    
                    # Probability
                    "Probability", "Conditional Probability", "Multiplication Theorem",
                    "Independence", "Bayes' Theorem", "Random Variables", "Bernoulli Trials",
                    "Binomial Distribution"
                ]
            },
            
            "Physics (ISC)": {
                11: [
                    # Physical World and Measurement
                    "Physical World", "Units and Measurements", "Dimensional Analysis",
                    "Significant Figures", "Error Analysis",
                    
                    # Kinematics
                    "Motion in a Straight Line", "Motion in a Plane", "Projectile Motion",
                    "Uniform Circular Motion",
                    
                    # Laws of Motion
                    "Newton's Laws of Motion", "Law of Conservation of Momentum",
                    "Equilibrium of Concurrent Forces", "Static and Kinetic Friction",
                    "Dynamics of Uniform Circular Motion", "Centripetal Force",
                    
                    # Work, Energy and Power
                    "Work", "Energy", "Power", "Collision", "Centre of Mass",
                    
                    # Motion of System of Particles and Rigid Body
                    "Centre of Mass", "Motion of Centre of Mass", "Linear Momentum",
                    "Angular Momentum", "Equilibrium of Rigid Bodies", "Moment of Inertia",
                    "Theorems of Perpendicular and Parallel Axes", "Kinematics of Rotational Motion",
                    
                    # Gravitation
                    "Kepler's Laws", "Universal Law of Gravitation", "Acceleration due to Gravity",
                    "Gravitational Potential Energy", "Escape Velocity", "Satellite Motion",
                    
                    # Properties of Bulk Matter
                    "Mechanical Properties of Solids", "Mechanical Properties of Fluids",
                    "Thermal Properties of Matter",
                    
                    # Thermodynamics
                    "Thermal Equilibrium", "Zeroth Law of Thermodynamics", "Heat, Work and Internal Energy",
                    "First Law of Thermodynamics", "Second Law of Thermodynamics",
                    "Reversible and Irreversible Processes", "Carnot Engine",
                    
                    # Behaviour of Perfect Gas and Kinetic Theory
                    "Equation of State of Perfect Gas", "Work Done by Compressed Gas",
                    "Kinetic Theory of Gases", "Law of Equipartition of Energy",
                    "Mean Free Path",
                    
                    # Oscillations and Waves
                    "Periodic Motion", "Simple Harmonic Motion", "Oscillations of Spring",
                    "Simple Pendulum", "Forced Oscillations and Resonance", "Wave Motion",
                    "Longitudinal and Transverse Waves", "Superposition of Waves",
                    "Progressive and Stationary Waves", "Beats", "Doppler Effect"
                ],
                
                12: [
                    # Electric Charges and Fields
                    "Electric Charges", "Conservation of Charge", "Coulomb's Law",
                    "Electric Field", "Electric Field Lines", "Electric Flux", "Gauss's Law",
                    
                    # Electrostatic Potential and Capacitance
                    "Electric Potential", "Potential Difference", "Electric Potential due to Point Charge",
                    "Equipotential Surfaces", "Potential Energy", "Conductors and Insulators",
                    "Dielectrics", "Capacitors", "Combination of Capacitors",
                    
                    # Current Electricity
                    "Electric Current", "Flow of Electric Charges", "Ohm's Law",
                    "Resistance and Resistivity", "Combination of Resistors", "Temperature Dependence",
                    "Internal Resistance", "Potentiometer", "Wheatstone Bridge",
                    
                    # Moving Charges and Magnetism
                    "Concept of Magnetic Field", "Oersted's Experiment", "Biot-Savart Law",
                    "Ampere's Law", "Magnetic Dipole", "Force on Moving Charge", "Cyclotron",
                    
                    # Magnetism and Matter
                    "Current Loop as Magnetic Dipole", "Bar Magnet", "Magnetism and Gauss's Law",
                    "Earth's Magnetism", "Magnetic Materials",
                    
                    # Electromagnetic Induction
                    "Electromagnetic Induction", "Faraday's Laws", "Induced EMF and Current",
                    "Lenz's Law", "Eddy Currents", "Self and Mutual Induction",
                    
                    # Alternating Current
                    "AC Voltage Applied to Resistor", "Inductor", "Capacitor",
                    "LCR Series Circuit", "Power in AC Circuit", "LC Oscillations", "Transformers",
                    
                    # Electromagnetic Waves
                    "Basic Idea of Displacement Current", "Electromagnetic Waves",
                    "Electromagnetic Spectrum",
                    
                    # Ray Optics and Optical Instruments
                    "Ray Optics", "Reflection of Light", "Spherical Mirrors", "Refraction",
                    "Total Internal Reflection", "Refraction at Spherical Surfaces", "Lenses",
                    "Refraction through Prism", "Scattering of Light", "Optical Instruments",
                    
                    # Wave Optics
                    "Huygens Principle", "Interference", "Young's Double Slit Experiment",
                    "Diffraction", "Polarisation",
                    
                    # Dual Nature of Radiation and Matter
                    "Dual Nature of Radiation", "Photoelectric Effect", "Einstein's Equation",
                    "Particle Nature of Light", "Wave Nature of Matter", "Davisson and Germer Experiment",
                    
                    # Atoms and Nuclei
                    "Alpha-particle Scattering Experiment", "Rutherford's Model of Atom",
                    "Bohr Model", "Hydrogen Spectrum", "Composition and Size of Nucleus",
                    "Atomic Masses", "Radioactivity", "Nuclear Fission and Fusion",
                    
                    # Electronic Devices
                    "Energy Bands in Conductors", "Semiconductors and Insulators",
                    "Semiconductor Diode", "I-V Characteristics", "Diode as Rectifier",
                    "Special Purpose p-n Junction Diodes", "Junction Transistor",
                    "Digital Electronics and Logic Gates"
                ]
            },
            
            "Chemistry (ISC)": {
                11: [
                    # Some Basic Concepts of Chemistry
                    "General Introduction", "Laws of Chemical Combination", "Dalton's Atomic Theory",
                    "Atomic and Molecular Masses", "Mole Concept", "Stoichiometry",
                    
                    # Structure of Atom
                    "Sub-atomic Particles", "Atomic Models", "Quantum Mechanical Model",
                    "Quantum Numbers", "Aufbau Principle", "Electronic Configuration",
                    
                    # Classification of Elements and Periodicity
                    "Modern Periodic Law", "Present Form of Periodic Table", "Periodic Trends",
                    "Ionization Enthalpy", "Electron Gain Enthalpy", "Electronegativity", "Valency",
                    
                    # Chemical Bonding and Molecular Structure
                    "Kossel-Lewis Approach", "Ionic Bonding", "Bond Parameters", "Lewis Structure",
                    "Polar Character of Covalent Bond", "Covalent Character of Ionic Bond",
                    "Valence Bond Theory", "Hybridisation", "Molecular Orbital Theory",
                    "Bonding in Some Homonuclear Diatomic Molecules", "Hydrogen Bonding",
                    
                    # States of Matter
                    "Intermolecular Forces", "Thermal Energy", "Intermolecular Forces vs Thermal Interactions",
                    "The Gaseous State", "The Gas Laws", "Ideal Gas Equation", "Graham's Law of Diffusion",
                    "Dalton's Law of Partial Pressures", "Kinetic Molecular Theory of Gases",
                    "Behaviour of Real Gases", "Liquefaction of Gases", "Liquid State",
                    
                    # Chemical Thermodynamics
                    "Thermodynamic Terms", "The Zeroth Law of Thermodynamics", "The First Law of Thermodynamics",
                    "Internal Energy", "Enthalpy", "Heat Capacity", "Measurement of ΔU and ΔH",
                    "Hess's Law of Constant Heat Summation", "Enthalpies for Different Types of Reactions",
                    "Spontaneity", "Gibbs Energy Change and Equilibrium", "Second Law of Thermodynamics",
                    "Third Law of Thermodynamics",
                    
                    # Equilibrium
                    "Equilibrium in Physical Processes", "Equilibrium in Chemical Processes",
                    "Law of Chemical Equilibrium", "Equilibrium Constant", "Homogeneous Equilibria",
                    "Heterogeneous Equilibria", "Applications of Equilibrium Constants",
                    "Relationship between Equilibrium Constant K, Reaction Quotient Q and Gibbs Energy G",
                    "Factors Affecting Equilibria", "Ionic Equilibrium in Solution", "Acids, Bases and Salts",
                    "Ionization of Acids and Bases", "Buffer Solutions", "Solubility Equilibria",
                    
                    # Redox Reactions
                    "Classical Idea of Redox Reactions", "Redox Reactions in Terms of Electron Transfer",
                    "Oxidation Number", "Types of Redox Reactions", "Balancing of Redox Reactions",
                    "Redox Reactions as the Basis for Titrations",
                    
                    # Hydrogen
                    "Position of Hydrogen in Periodic Table", "Occurrence", "Isotopes",
                    "Preparation", "Properties", "Hydrides", "Water", "Hydrogen Peroxide",
                    "Heavy Water", "Hydrogen as a Fuel",
                    
                    # The s-Block Elements
                    "Group 1 Elements: Alkali Metals", "General Characteristics", "Occurrence",
                    "Anomalous Properties of Lithium", "Some Important Compounds of Sodium",
                    "Biological Importance of Sodium and Potassium", "Group 2 Elements: Alkaline Earth Metals",
                    "General Characteristics", "Anomalous Behaviour of Beryllium",
                    "Some Important Compounds of Calcium", "Biological Importance of Magnesium and Calcium",
                    
                    # Some p-Block Elements
                    "Group 13 Elements: The Boron Family", "Group 14 Elements: The Carbon Family",
                    
                    # Organic Chemistry - Some Basic Principles and Techniques
                    "General Introduction", "Tetravalence of Carbon", "Structural Representations",
                    "Classification of Organic Compounds", "Nomenclature", "Isomerism",
                    "Fundamental Concepts in Organic Reaction Mechanism", "Methods of Purification",
                    "Qualitative Analysis", "Quantitative Analysis",
                    
                    # Hydrocarbons
                    "Classification", "Aliphatic Hydrocarbons", "Alkanes", "Alkenes", "Alkynes",
                    "Aromatic Hydrocarbons", "Carcinogenicity and Toxicity"
                ],
                
                12: [
                    # Solid State
                    "General Characteristics of Solid State", "Amorphous and Crystalline Solids",
                    "Classification of Crystalline Solids", "Crystal Lattices and Unit Cells",
                    "Number of Atoms in a Unit Cell", "Close Packed Structures", "Packing Efficiency",
                    "Calculations Involving Unit Cell Dimensions", "Imperfections in Solids", "Electrical Properties",
                    "Magnetic Properties",
                    
                    # Solutions
                    "Types of Solutions", "Expressing Concentration of Solutions", "Solubility",
                    "Vapour Pressure of Liquid Solutions", "Raoult's Law", "Colligative Properties",
                    "Relative Molecular Masses of Non-volatile Substances", "Abnormal Molecular Masses",
                    
                    # Electrochemistry
                    "Electrochemical Cells", "Galvanic Cells", "Nernst Equation", "Conductance in Electrolytic Solutions",
                    "Electrolytic Cells and Electrolysis", "Batteries", "Fuel Cells", "Corrosion",
                    
                    # Chemical Kinetics
                    "Rate of a Chemical Reaction", "Factors Influencing Rate of a Reaction",
                    "Integrated Rate Equations", "Pseudo First Order Reaction", "Temperature Dependence",
                    "Collision Theory of Chemical Reactions",
                    
                    # Surface Chemistry
                    "Adsorption", "Catalysis", "Colloids",
                    
                    # General Principles and Processes of Isolation of Elements
                    "Occurrence of Metals", "Concentration of Ores", "Extraction of Crude Metal",
                    "Thermodynamic Principles of Metallurgy", "Electrochemical Principles", "Oxidation & Reduction",
                    "Refining", "Uses of Aluminium, Copper, Zinc and Iron",
                    
                    # The p-Block Elements
                    "Group 15 Elements", "Group 16 Elements", "Group 17 Elements", "Group 18 Elements",
                    
                    # The d and f Block Elements
                    "General Introduction", "Electronic Configuration", "Occurrence and Characteristics",
                    "General Trends", "Oxidation States", "Magnetic Properties", "Catalytic Properties",
                    "Applications", "Preparation and Properties of K2Cr2O7 and KMnO4",
                    "Lanthanoids", "Actinoids",
                    
                    # Coordination Compounds
                    "Introduction", "Ligands", "Coordination Number", "Colour", "Magnetic Properties and Shapes",
                    "IUPAC Nomenclature", "Isomerism", "Bonding", "Werner's Theory", "VBT", "CFT",
                    "Importance of Coordination Compounds",
                    
                    # Haloalkanes and Haloarenes
                    "Classification", "Nomenclature", "Nature of C-X Bond", "Physical Properties",
                    "Chemical Reactions", "Polyhalogen Compounds",
                    
                    # Alcohols, Phenols and Ethers
                    "Classification", "Nomenclature", "Structures of Functional Groups", "Physical Properties",
                    "Chemical Reactions", "Uses",
                    
                    # Aldehydes, Ketones and Carboxylic Acids
                    "Classification", "Nomenclature", "Nature of Carbonyl Group", "Physical Properties",
                    "Chemical Reactions", "Uses",
                    
                    # Organic Compounds Containing Nitrogen
                    "Classification", "Structure", "Nomenclature", "Preparation", "Physical Properties",
                    "Chemical Reactions", "Uses", "Identification",
                    
                    # Biomolecules
                    "Carbohydrates", "Proteins", "Vitamins", "Nucleic Acids",
                    
                    # Polymers
                    "Classification", "Terms Related to Polymers", "Types of Polymerisation Reactions",
                    "Molecular Mass", "Biodegradable and Non-biodegradable Polymers",
                    
                    # Chemistry in Everyday Life
                    "Drugs and their Classification", "Drug-Target Interaction", "Therapeutic Action",
                    "Chemicals in Food", "Cleansing Agents"
                ]
            },
            
            "Biology (ISC)": {
                11: [
                    # Diversity in the Living World
                    "What is Living", "Biodiversity", "Need for Classification", "Three Domains of Life",
                    "Taxonomy and Systematics", "Concept of Species and Taxonomical Hierarchy",
                    "Binomial Nomenclature", "Tools for Study of Taxonomy", "Museums", "Zoological Parks",
                    "Herbaria", "Botanical Gardens",
                    
                    # Structural Organisation in Animals and Plants
                    "Animal Tissues", "Morphology and Modifications", "Anatomy of Flowering Plants",
                    "Structural Organisation of Animals",
                    
                    # Cell Structure and Function
                    "Cell Theory and Cell as the Basic Unit of Life", "Structure of Prokaryotic and Eukaryotic Cells",
                    "Plant Cell and Animal Cell", "Cell Envelope", "Cell Membrane", "Cell Wall",
                    "Cell Organelles", "Nucleus", "Chromosome", "Microbodies", "Cytoskeleton",
                    "Cilia", "Flagella", "Centrosome", "Ribosome", "Endoplasmic Reticulum",
                    
                    # Plant Physiology
                    "Transport in Plants", "Mineral Nutrition", "Photosynthesis in Higher Plants",
                    "Respiration in Plants", "Plant Growth and Development",
                    
                    # Human Physiology
                    "Digestion and Absorption", "Breathing and Exchange of Gases", "Body Fluids and Circulation",
                    "Excretory Products and their Elimination", "Locomotion and Movement",
                    "Neural Control and Coordination", "Chemical Coordination and Integration"
                ],
                
                12: [
                    # Reproduction
                    "Reproduction in Organisms", "Sexual Reproduction in Flowering Plants",
                    "Human Reproduction", "Reproductive Health",
                    
                    # Genetics and Evolution
                    "Heredity and Variation", "Molecular Basis of Inheritance", "Evolution",
                    
                    # Biology and Human Welfare
                    "Human Health and Disease", "Strategies for Enhancement in Food Production",
                    "Microbes in Human Welfare",
                    
                    # Biotechnology and its Applications
                    "Biotechnology: Principles and Processes", "Biotechnology and its Applications",
                    
                    # Ecology and Environment
                    "Organisms and Populations", "Ecosystem", "Biodiversity and Conservation",
                    "Environmental Issues"
                ]
            },
            
            "English (ISC)": {
                11: [
                    # Literature in English Paper 1
                    "Poetry", "Prose", "Drama", "Fiction", "Literary Appreciation",
                    "Critical Analysis", "Contextual Questions", "Character Analysis",
                    "Theme Study", "Literary Devices", "Historical Context",
                    
                    # Language Paper 2
                    "Reading Comprehension", "Writing Skills", "Grammar and Usage",
                    "Vocabulary", "Composition", "Creative Writing", "Functional Writing",
                    "Formal and Informal Writing", "Report Writing", "Article Writing",
                    "Speech Writing", "Debate Writing"
                ],
                
                12: [
                    # Literature in English Paper 1
                    "Prescribed Texts", "Poetry Analysis", "Prose Appreciation", "Drama Study",
                    "Novel Study", "Short Stories", "Essays", "Comparative Literature",
                    "Critical Essays", "Literary Criticism", "Evaluation and Assessment",
                    
                    # Language Paper 2
                    "Advanced Composition", "Directed Writing", "Argumentative Writing",
                    "Discursive Writing", "Narrative Writing", "Descriptive Writing",
                    "Critical Writing", "Commercial Correspondence", "Official Correspondence",
                    "Media Writing", "Digital Communication"
                ]
            },
            
            "Economics (ISC)": {
                11: [
                    # Introduction to Economics
                    "What is Economics", "Microeconomics and Macroeconomics", "Central Problems of an Economy",
                    "Economic Systems", "Production Possibility Frontier",
                    
                    # Theory of Consumer Behaviour
                    "Consumer's Equilibrium", "Utility Analysis", "Indifference Curve Analysis",
                    "Price Effect", "Income Effect", "Substitution Effect", "Demand",
                    "Law of Demand", "Elasticity of Demand",
                    
                    # Producer Behaviour and Supply
                    "Production Function", "Short Run and Long Run", "Law of Variable Proportions",
                    "Returns to Scale", "Cost", "Revenue", "Producer's Equilibrium", "Supply",
                    
                    # Forms of Market and Price Determination
                    "Perfect Competition", "Monopoly", "Monopolistic Competition", "Oligopoly",
                    "Price Determination in Different Markets"
                ],
                
                12: [
                    # Introductory Macroeconomics
                    "National Income", "Money and Banking", "Income Determination",
                    "Government Budget and the Economy", "Balance of Payments",
                    
                    # Indian Economic Development
                    "Development Experience", "Independence", "Economic Reforms Since 1991",
                    "Current Challenges Facing Indian Economy", "Development Experience of India"
                ]
            },
            
            "Business Studies (ISC)": {
                11: [
                    # Nature and Significance of Management
                    "Concept of Management", "Objectives of Management", "Importance of Management",
                    "Nature of Management", "Management as Science, Art and Profession",
                    "Levels of Management", "Functions of Management",
                    
                    # Principles of Management
                    "Principles of Management", "Fayol's Principles", "Taylor's Principles",
                    "Scientific Management",
                    
                    # Business Environment
                    "Concept of Business Environment", "Importance of Business Environment",
                    "Dimensions of Business Environment", "Economic Environment", "Political Environment",
                    "Social Environment", "Technological Environment", "Legal Environment",
                    
                    # Planning
                    "Concept of Planning", "Importance of Planning", "Limitations of Planning",
                    "Planning Process", "Types of Plans",
                    
                    # Organising
                    "Concept of Organisation", "Importance of Organising", "Organising Process",
                    "Structure of Organisation", "Formal and Informal Organisation", "Delegation",
                    "Decentralisation",
                    
                    # Staffing
                    "Concept of Staffing", "Importance of Staffing", "Staffing Process",
                    "Recruitment", "Selection", "Training and Development",
                    
                    # Directing
                    "Concept of Directing", "Importance of Directing", "Elements of Directing",
                    "Supervision", "Motivation", "Leadership", "Communication",
                    
                    # Controlling
                    "Concept of Controlling", "Importance of Controlling", "Limitations of Controlling",
                    "Controlling Process", "Techniques of Controlling"
                ],
                
                12: [
                    # Financial Management
                    "What is Financial Management", "Role of Financial Management", "Objectives of Financial Management",
                    "Financial Decisions", "Financial Planning", "Capital Structure", "Fixed and Working Capital",
                    
                    # Marketing Management
                    "What is Marketing", "Marketing Management Philosophies", "Functions of Marketing",
                    "Marketing Mix", "Product", "Price", "Place", "Promotion",
                    
                    # Consumer Protection
                    "Why Consumer Protection", "Ways and Means of Consumer Protection",
                    "Consumer Protection Act", "Role of Consumer Organisations and NGOs"
                ]
            }
        },

        "ICSE": {
            "Mathematics": {
                1: [
                    # Pre-Number Concepts
                    "Numbers 1-99", "Number Names", "Counting Forward and Backward", "Before and After",
                    "Number Line", "Skip Counting", "Patterns in Numbers", "Even and Odd Numbers",
                    
                    # Basic Operations
                    "Addition of Single Digits", "Subtraction of Single Digits", "Simple Word Problems",
                    "Addition using Objects", "Subtraction using Objects", "Zero in Addition and Subtraction",
                    
                    # Shapes and Patterns
                    "Basic Shapes", "Circle", "Square", "Rectangle", "Triangle", "Oval",
                    "Shape Recognition", "Patterns with Shapes", "Sorting by Shapes",
                    
                    # Measurement
                    "Comparison of Length", "Tall and Short", "Long and Short", "Heavy and Light",
                    "Big and Small", "Time Concepts", "Day and Night", "Before and After Time",
                    
                    # Money
                    "Recognition of Coins", "Value of Coins", "Simple Money Problems",
                    
                    # Data Handling
                    "Simple Pictographs", "Collecting Information", "Organizing Data"
                ],
                
                2: [
                    # Numbers
                    "Numbers 1-100", "Number Names in Words", "Place Value (Tens and Ones)",
                    "Expanded Form", "Standard Form", "Comparison of Numbers", "Ascending Order",
                    "Descending Order", "Number Patterns", "Skip Counting by 2s, 5s, 10s",
                    
                    # Addition and Subtraction
                    "Addition without Regrouping", "Addition with Regrouping", "Subtraction without Regrouping",
                    "Subtraction with Regrouping", "Addition of Zero", "Subtraction of Zero",
                    "Commutative Property of Addition", "Word Problems on Addition and Subtraction",
                    "Estimation in Addition and Subtraction",
                    
                    # Multiplication
                    "Introduction to Multiplication", "Multiplication as Repeated Addition",
                    "Multiplication Tables 2, 3, 4, 5", "Skip Counting for Tables", "Arrays and Multiplication",
                    
                    # Division
                    "Division as Sharing", "Division as Repeated Subtraction", "Simple Division Facts",
                    
                    # Geometry
                    "2D Shapes", "3D Shapes", "Faces, Edges, Vertices", "Symmetry", "Lines and Curves",
                    
                    # Measurement
                    "Length Measurement", "Weight Measurement", "Capacity Measurement",
                    "Time - Reading Clock", "Calendar", "Days and Months",
                    
                    # Money
                    "Indian Currency", "Addition of Money", "Subtraction of Money", "Making Change",
                    
                    # Data Handling
                    "Pictographs", "Bar Graphs", "Tally Marks", "Data Collection and Organization"
                ],
                
                3: [
                    # Numbers
                    "Numbers up to 1000", "4-digit Numbers", "Place Value (Thousands, Hundreds, Tens, Ones)",
                    "Expanded Form and Standard Form", "Roman Numerals I to XX", "Number Line up to 1000",
                    "Comparison and Ordering", "Rounding to Nearest 10 and 100",
                    
                    # Four Operations
                    "Addition with Regrouping", "Subtraction with Regrouping", "Properties of Addition",
                    "Multiplication Tables up to 10", "2-digit by 1-digit Multiplication",
                    "Division with Remainders", "Long Division Method", "Word Problems",
                    
                    # Fractions
                    "Introduction to Fractions", "Parts of a Whole", "Numerator and Denominator",
                    "Proper and Improper Fractions", "Mixed Numbers", "Equivalent Fractions",
                    "Comparison of Fractions", "Addition of Like Fractions", "Subtraction of Like Fractions",
                    
                    # Geometry
                    "Points, Lines, and Line Segments", "Rays", "Angles", "Types of Angles",
                    "Polygons", "Quadrilaterals", "Perimeter", "Area using Unit Squares",
                    
                    # Measurement
                    "Metric Units of Length", "Metric Units of Weight", "Metric Units of Capacity",
                    "Conversion within Metric System", "Time Intervals", "Elapsed Time",
                    
                    # Money
                    "Decimal Notation for Money", "Addition and Subtraction of Money",
                    "Multiplication of Money", "Word Problems with Money",
                    
                    # Data Handling
                    "Reading and Interpreting Graphs", "Bar Graphs with Scale", "Pictographs with Scale",
                    "Line Graphs", "Data Analysis"
                ],
                
                4: [
                    # Numbers
                    "5-digit and 6-digit Numbers", "Place Value up to Lakhs", "International Number System",
                    "Roman Numerals up to 100", "Factors and Multiples", "Prime and Composite Numbers",
                    "LCM and HCF", "Tests of Divisibility",
                    
                    # Operations
                    "Addition and Subtraction of Large Numbers", "Multiplication by 2-digit Numbers",
                    "Division by 2-digit Numbers", "BODMAS Rule", "Word Problems with Mixed Operations",
                    
                    # Fractions and Decimals
                    "Mixed Numbers and Improper Fractions", "Addition and Subtraction of Unlike Fractions",
                    "Multiplication of Fractions", "Division of Fractions", "Decimal Numbers",
                    "Place Value in Decimals", "Addition and Subtraction of Decimals",
                    "Multiplication of Decimals", "Division of Decimals",
                    
                    # Geometry
                    "Parallel and Perpendicular Lines", "Types of Triangles", "Types of Quadrilaterals",
                    "Circles", "Radius and Diameter", "Perimeter and Area Formulas",
                    "Coordinate Geometry Basics",
                    
                    # Measurement
                    "Conversion between Units", "Problems on Time", "Speed, Distance, Time",
                    "Simple Interest", "Profit and Loss Basics",
                    
                    # Data Handling
                    "Probability Basics", "Certain and Impossible Events", "Likely and Unlikely Events",
                    "Frequency Tables", "Mode and Median"
                ],
                
                5: [
                    # Numbers
                    "Numbers up to Crores", "Place Value System", "Rounding and Estimation",
                    "Negative Numbers", "Number Line with Negative Numbers",
                    
                    # Operations
                    "Operations on Large Numbers", "Square Numbers", "Square Roots",
                    "Cube Numbers", "Applications of Operations",
                    
                    # Fractions and Decimals
                    "Operations on Fractions", "Fractions to Decimals", "Decimals to Fractions",
                    "Percentages", "Percentage to Fraction and Decimal", "Applications of Percentages",
                    
                    # Ratio and Proportion
                    "Introduction to Ratios", "Equivalent Ratios", "Proportion", "Unitary Method",
                    
                    # Geometry
                    "Construction with Compass", "Angle Measurement", "Triangles and Their Properties",
                    "Symmetry and Reflection", "3D Shapes and Nets",
                    
                    # Mensuration
                    "Area and Perimeter of Complex Shapes", "Volume of Cubes and Cuboids",
                    "Surface Area", "Units of Area and Volume",
                    
                    # Algebra Basics
                    "Simple Equations", "Variables and Constants", "Algebraic Expressions",
                    
                    # Data Handling
                    "Mean, Median, Mode", "Range", "Frequency Distribution", "Grouped Data",
                    "Probability with Examples"
                ],
                
                6: [
                    # Number System
                    "Natural Numbers and Whole Numbers", "Integers", "Number Line", "Absolute Value",
                    "Comparison of Integers", "Operations on Integers", "Properties of Operations",
                    
                    # Fractions and Decimals
                    "Fractions on Number Line", "Operations on Fractions", "Decimal Numbers",
                    "Operations on Decimals", "Converting Fractions to Decimals and Vice Versa",
                    
                    # Ratio and Proportion
                    "Ratios and Their Applications", "Proportions", "Unitary Method",
                    "Percentage and Its Applications", "Profit and Loss", "Simple Interest",
                    
                    # Algebra
                    "Introduction to Algebra", "Variables and Constants", "Algebraic Expressions",
                    "Terms and Factors", "Like and Unlike Terms", "Addition and Subtraction of Algebraic Expressions",
                    
                    # Geometry
                    "Basic Geometrical Ideas", "Line Segments", "Rays and Lines", "Angles",
                    "Types of Angles", "Parallel Lines", "Intersecting Lines", "Triangles",
                    "Quadrilaterals", "Circles", "Constructions",
                    
                    # Mensuration
                    "Perimeter and Area", "Area of Rectangle and Square", "Area of Triangle",
                    "Area of Circle", "Volume and Surface Area of Cube and Cuboid",
                    
                    # Data Handling
                    "Data Collection", "Organization of Data", "Pictographs", "Bar Graphs",
                    "Pie Charts", "Mean, Median, Mode", "Probability"
                ],
                
                7: [
                    # Numbers
                    "Integers and Their Operations", "Properties of Addition and Subtraction of Integers",
                    "Multiplication and Division of Integers", "Rational Numbers", "Positive and Negative Rational Numbers",
                    "Operations on Rational Numbers",
                    
                    # Fractions and Decimals
                    "Multiplication and Division of Fractions", "Word Problems on Fractions",
                    "Multiplication and Division of Decimals", "Word Problems on Decimals",
                    
                    # Algebra
                    "Algebraic Expressions", "Terms, Factors and Coefficients", "Like and Unlike Terms",
                    "Addition and Subtraction of Algebraic Expressions", "Finding Value of an Expression",
                    "Simple Linear Equations", "Solving Linear Equations",
                    
                    # Ratio and Proportion
                    "Ratio and Proportion", "Unitary Method", "Percentage", "Applications of Percentage",
                    "Profit and Loss", "Simple Interest", "Compound Interest",
                    
                    # Geometry
                    "Lines and Angles", "Complementary and Supplementary Angles", "Adjacent Angles",
                    "Linear Pair", "Vertically Opposite Angles", "Parallel Lines and Transversal",
                    "Triangles", "Median and Altitude of Triangle", "Angle Sum Property",
                    "Exterior Angle Property", "Congruence of Triangles",
                    
                    # Mensuration
                    "Perimeter and Area of Plane Figures", "Area of Parallelogram", "Area of Triangle",
                    "Circumference and Area of Circle", "Volume and Surface Area of Cube, Cuboid and Cylinder",
                    
                    # Data Handling
                    "Mean, Median and Mode of Ungrouped Data", "Bar Graphs", "Histograms",
                    "Probability", "Experimental Probability"
                ],
                
                8: [
                    # Numbers
                    "Rational Numbers", "Properties of Rational Numbers", "Representation of Rational Numbers on Number Line",
                    "Operations on Rational Numbers", "Powers", "Laws of Exponents", "Expressing Large Numbers in Standard Form",
                    
                    # Algebra
                    "Algebraic Expressions and Identities", "Multiplication of Algebraic Expressions",
                    "Identities", "Factorization", "Division of Algebraic Expressions",
                    "Linear Equations in One Variable", "Solving Linear Equations", "Applications of Linear Equations",
                    
                    # Geometry
                    "Practical Geometry", "Construction of Quadrilaterals", "Understanding Quadrilaterals",
                    "Properties of Parallelogram", "Special Types of Quadrilaterals",
                    "Area of Trapezium", "Area of General Quadrilateral",
                    
                    # Mensuration
                    "Surface Area and Volume", "Surface Area of Cube and Cuboid", "Surface Area of Cylinder",
                    "Volume of Cube and Cuboid", "Volume of Cylinder", "Volume and Surface Area of Sphere and Hemisphere",
                    
                    # Data Handling
                    "Data Handling", "Frequency Distribution Table", "Histograms", "Circle Graphs or Pie Charts",
                    "Probability", "Equally Likely Outcomes", "Probability as a Fraction",
                    
                    # Others
                    "Direct and Inverse Proportions", "Time and Work", "Pipes and Cisterns",
                    "Comparing Quantities", "Finding Increase or Decrease Percent", "Finding Discounts",
                    "Prices Related to Buying and Selling", "Sales Tax/Value Added Tax", "Compound Interest",
                    "Rate Compounded Annually or Half Yearly"
                ],
                
                9: [
                    # Number Systems
                    "Real Numbers", "Rational and Irrational Numbers", "Representation of Real Numbers on Number Line",
                    "Operations on Real Numbers", "Laws of Exponents for Real Numbers", "Rationalization",
                    
                    # Algebra
                    "Polynomials", "Polynomials in One Variable", "Zeroes of a Polynomial", "Remainder Theorem",
                    "Factorization of Polynomials", "Algebraic Identities",
                    "Linear Equations in Two Variables", "Solution of Linear Equation", "Graph of Linear Equation in Two Variables",
                    "Equations of Lines Parallel to Axes",
                    
                    # Coordinate Geometry
                    "Introduction to Coordinate Geometry", "Cartesian System", "Plotting Points in Cartesian Plane",
                    "Distance Between Two Points", "Section Formula",
                    
                    # Geometry
                    "Introduction to Euclid's Geometry", "Euclid's Axioms and Postulates",
                    "Lines and Angles", "Intersecting Lines and Non-intersecting Lines", "Pairs of Angles",
                    "Lines Parallel to Same Line", "Angle Sum Property of Triangle",
                    "Triangles", "Congruence of Triangles", "Criteria for Congruence of Triangles",
                    "Properties of Isosceles Triangle", "Inequalities in Triangle",
                    "Quadrilaterals", "Angle Sum Property of Quadrilateral", "Types of Quadrilaterals",
                    "Properties of Parallelogram", "Mid-point Theorem",
                    
                    # Mensuration
                    "Areas", "Area of Triangle", "Area of Parallelogram", "Area of Trapezium",
                    "Heron's Formula", "Application of Heron's Formula",
                    "Surface Areas and Volumes", "Surface Area of Cuboid and Cube", "Surface Area of Right Circular Cylinder",
                    "Surface Area of Right Circular Cone", "Surface Area of Sphere", "Volume of Cuboid",
                    "Volume of Cylinder", "Volume of Right Circular Cone", "Volume of Sphere",
                    
                    # Statistics and Probability
                    "Statistics", "Collection of Data", "Presentation of Data", "Graphical Representation of Data",
                    "Measures of Central Tendency", "Probability", "Experimental Probability",
                    "Theoretical Probability", "Equally Likely Outcomes"
                ],
                
                10: [
                    # Number Systems
                    "Real Numbers", "Euclid's Division Lemma", "Fundamental Theorem of Arithmetic",
                    "Revisiting Irrational Numbers", "Revisiting Rational Numbers and Their Decimal Expansions",
                    
                    # Algebra
                    "Polynomials", "Geometrical Meaning of Zeroes of Polynomial", "Relationship Between Zeroes and Coefficients of Polynomial",
                    "Division Algorithm for Polynomials",
                    "Pair of Linear Equations in Two Variables", "Graphical Method of Solution", "Algebraic Methods of Solution",
                    "Elimination Method", "Substitution Method", "Cross-multiplication Method", "Equations Reducible to Linear Equations",
                    "Quadratic Equations", "Solution of Quadratic Equations by Factorization", "Solution by Completing the Square",
                    "Quadratic Formula", "Nature of Roots",
                    "Arithmetic Progressions", "nth Term of an AP", "Sum of First n Terms of an AP",
                    
                    # Coordinate Geometry
                    "Lines", "Distance Formula", "Section Formula", "Area of Triangle",
                    
                    # Geometry
                    "Triangles", "Similar Figures", "Similarity of Triangles", "Criteria for Similarity of Triangles",
                    "Areas of Similar Triangles", "Pythagoras Theorem", "Applications of Pythagoras Theorem",
                    "Circles", "Tangent to a Circle", "Number of Tangents from a Point on Circle",
                    
                    # Trigonometry
                    "Introduction to Trigonometry", "Trigonometric Ratios", "Trigonometric Ratios of Some Specific Angles",
                    "Trigonometric Identities", "Some Applications of Trigonometry", "Heights and Distances",
                    
                    # Mensuration
                    "Areas Related to Circles", "Perimeter and Area of Circle", "Areas of Sector and Segment of Circle",
                    "Areas of Combinations of Plane Figures",
                    "Surface Areas and Volumes", "Combination of Solids", "Frustum of Cone", "Conversion of Solid from One Shape to Another",
                    
                    # Statistics and Probability
                    "Statistics", "Mean of Grouped Data", "Mode of Grouped Data", "Median of Grouped Data",
                    "Graphical Representation of Cumulative Frequency Distribution",
                    "Probability", "Classical Definition of Probability", "Simple Problems on Single Events"
                ]
            },
            
            "English": {
                1: [
                    # Reading and Comprehension
                    "Alphabet Recognition", "Capital and Small Letters", "Letter Sounds", "Phonics",
                    "Vowels and Consonants", "Blending Sounds", "Simple Three-Letter Words",
                    "Four-Letter Words", "Sight Words", "Picture Reading", "Simple Sentences",
                    
                    # Writing Skills
                    "Letter Formation", "Writing Capital Letters", "Writing Small Letters",
                    "Copying Words", "Copying Sentences", "Writing Simple Words",
                    "Writing Short Sentences", "Handwriting Practice",
                    
                    # Grammar
                    "Naming Words (Nouns)", "Action Words (Verbs)", "Describing Words (Adjectives)",
                    "A, An, The", "This, That", "Here, There", "Yes, No Questions",
                    
                    # Literature
                    "Simple Poems", "Nursery Rhymes", "Short Stories", "Moral Stories",
                    "Picture Stories", "Character Identification",
                    
                    # Speaking and Listening
                    "Oral Comprehension", "Following Instructions", "Show and Tell",
                    "Recitation", "Role Play", "Conversation Skills"
                ],
                
                2: [
                    # Reading and Comprehension
                    "Reading Short Stories", "Reading Simple Poems", "Understanding Main Ideas",
                    "Answering Simple Questions", "Sequence of Events", "Character Recognition",
                    "Picture Comprehension", "Reading with Expression",
                    
                    # Writing Skills
                    "Sentence Formation", "Writing Simple Paragraphs", "Creative Writing",
                    "Describing Pictures", "Writing About Daily Activities", "Letter Writing Basics",
                    "Diary Writing", "Story Writing",
                    
                    # Grammar
                    "Singular and Plural Nouns", "Masculine and Feminine", "Personal Pronouns",
                    "Present Tense", "Past Tense", "Question Words", "Punctuation Marks",
                    "Capital Letters Usage", "Full Stops and Question Marks",
                    
                    # Literature
                    "Poems with Moral Values", "Stories with Characters", "Fables",
                    "Simple Plays", "Understanding Themes", "Identifying Settings",
                    
                    # Vocabulary
                    "Synonyms", "Antonyms", "New Words", "Word Meanings",
                    "Rhyming Words", "Word Families"
                ],
                
                3: [
                    # Reading and Comprehension
                    "Reading Longer Passages", "Understanding Complex Stories", "Main Idea and Supporting Details",
                    "Making Inferences", "Predicting Outcomes", "Cause and Effect", "Compare and Contrast",
                    "Reading Different Text Types", "Reading for Information",
                    
                    # Writing Skills
                    "Paragraph Writing", "Descriptive Writing", "Narrative Writing", "Letter Writing",
                    "Informal Letters", "Formal Letters", "Story Writing", "Essay Writing",
                    "Report Writing", "Creative Writing Exercises",
                    
                    # Grammar
                    "Types of Nouns", "Common and Proper Nouns", "Collective Nouns", "Abstract Nouns",
                    "Pronouns and Their Types", "Verbs and Tenses", "Simple Present Tense",
                    "Simple Past Tense", "Simple Future Tense", "Adjectives and Their Types",
                    "Adverbs", "Prepositions", "Conjunctions", "Articles", "Sentence Types",
                    "Statements, Questions, Commands, Exclamations", "Subject and Predicate",
                    
                    # Literature
                    "Poetry Appreciation", "Understanding Metaphors and Similes", "Story Analysis",
                    "Character Study", "Plot Development", "Theme Identification", "Moral Lessons",
                    
                    # Vocabulary
                    "Word Building", "Prefixes and Suffixes", "Synonyms and Antonyms",
                    "Homophones", "Word Meanings in Context", "Dictionary Skills"
                ],
                
                4: [
                    # Reading and Comprehension
                    "Critical Reading", "Analyzing Text Structure", "Author's Purpose", "Point of View",
                    "Making Connections", "Summarizing", "Drawing Conclusions", "Reading Between the Lines",
                    
                    # Writing Skills
                    "Expository Writing", "Persuasive Writing", "Research Writing", "Business Letters",
                    "Application Writing", "Resume Writing", "Notice Writing", "Article Writing",
                    "Book Reviews", "Character Sketches",
                    
                    # Grammar
                    "Complex Sentence Structures", "Compound Sentences", "Complex Sentences",
                    "Conditional Sentences", "Active and Passive Voice", "Direct and Indirect Speech",
                    "Modals", "Question Tags", "Phrasal Verbs", "Idiomatic Expressions",
                    
                    # Literature
                    "Poetry Analysis", "Literary Devices", "Prose Appreciation", "Drama Study",
                    "Shakespearean Sonnets", "Modern Poetry", "Short Stories", "Novel Studies",
                    
                    # Communication Skills
                    "Public Speaking", "Debate Preparation", "Group Discussions", "Interview Skills",
                    "Presentation Skills", "Critical Thinking"
                ],
                
                5: [
                    # Advanced Reading
                    "Critical Analysis", "Literary Criticism", "Comparative Literature", "Research Skills",
                    "Academic Reading", "Professional Communication",
                    
                    # Advanced Writing
                    "Academic Writing", "Research Papers", "Thesis Writing", "Creative Writing",
                    "Professional Writing", "Technical Writing",
                    
                    # Advanced Grammar
                    "Advanced Grammar Structures", "Style and Register", "Coherence and Cohesion",
                    "Error Analysis", "Editing and Proofreading",
                    
                    # Literature
                    "World Literature", "Contemporary Literature", "Classical Literature",
                    "Literary Movements", "Cultural Context in Literature",
                    
                    # Communication
                    "Professional Communication", "Business English", "Academic Discourse",
                    "Cross-cultural Communication"
                ],
                
                6: [
                    # Literature
                    "Prose - Stories, Essays, Biographies", "Poetry - Different Forms and Styles",
                    "Drama - One-act Plays", "Character Analysis", "Theme Exploration",
                    "Literary Devices", "Figure of Speech", "Imagery and Symbolism",
                    
                    # Language Skills
                    "Grammar - Parts of Speech", "Sentence Formation", "Tenses", "Voice",
                    "Narration", "Conditionals", "Modals", "Question Formation",
                    
                    # Writing Skills
                    "Creative Writing", "Descriptive Writing", "Narrative Writing",
                    "Letter Writing", "Essay Writing", "Report Writing", "Summary Writing",
                    
                    # Communication Skills
                    "Reading Comprehension", "Oral Communication", "Listening Skills",
                    "Speaking Skills", "Pronunciation", "Intonation"
                ],
                
                7: [
                    # Literature
                    "Short Stories by Indian and Foreign Authors", "Poetry - Classical and Modern",
                    "Drama - Shakespearean Extracts", "Literary Appreciation", "Critical Reading",
                    "Comparative Study", "Author Studies", "Historical Context",
                    
                    # Language Skills
                    "Advanced Grammar", "Syntax", "Semantics", "Vocabulary Development",
                    "Word Formation", "Idioms and Phrases", "Proverbs", "Etymology",
                    
                    # Writing Skills
                    "Argumentative Writing", "Persuasive Writing", "Analytical Writing",
                    "Research Writing", "Technical Writing", "Creative Writing",
                    
                    # Communication
                    "Debate and Discussion", "Public Speaking", "Presentation Skills",
                    "Interview Techniques", "Group Communication"
                ],
                
                8: [
                    # Literature
                    "Novel Studies", "Poetry Analysis", "Drama Appreciation", "Literary Criticism",
                    "World Literature", "Indian English Literature", "Contemporary Writers",
                    "Literary Movements", "Cultural Studies",
                    
                    # Language Skills
                    "Advanced English Grammar", "Style and Register", "Academic English",
                    "Professional English", "Language Varieties", "Sociolinguistics",
                    
                    # Writing Skills
                    "Academic Writing", "Research Methodology", "Citation and References",
                    "Critical Writing", "Professional Writing", "Media Writing",
                    
                    # Communication
                    "Advanced Communication Skills", "Cross-cultural Communication",
                    "Digital Communication", "Mass Communication"
                ],
                
                9: [
                    # Literature Paper I
                    "Shakespeare - Julius Caesar", "Treasure Chest - Poetry and Short Stories",
                    "Character Analysis", "Theme Study", "Literary Techniques", "Critical Appreciation",
                    "Contextual Questions", "Extract-based Questions",
                    
                    # Language Paper II
                    "Reading Comprehension", "Note Making", "Summary Writing", "Letter Writing",
                    "Essay Writing", "Report Writing", "Article Writing", "Speech Writing",
                    "Debate Writing", "Story Writing",
                    
                    # Grammar
                    "Sentence Transformation", "Active and Passive Voice", "Direct and Indirect Speech",
                    "Prepositions", "Conjunctions", "Question Tags", "Conditionals",
                    
                    # Composition
                    "Argumentative Essays", "Descriptive Essays", "Narrative Essays",
                    "Formal and Informal Letters", "Applications", "Notices"
                ],
                
                10: [
                    # Literature Paper I
                    "Shakespeare - Merchant of Venice or Julius Caesar", "Treasure Chest - A Collection of ICSE Poems and Short Stories",
                    "Poetry Appreciation", "Prose Analysis", "Character Portrayal", "Theme Analysis",
                    "Literary Devices", "Irony, Symbolism, Metaphor", "Historical and Social Context",
                    
                    # Language Paper II
                    "Comprehension Passages", "Note Making and Summary", "Letter Writing - Formal and Informal",
                    "Applications", "Essay Writing", "Article Writing", "Report Writing",
                    "Speech Writing", "Story Writing",
                    
                    # Grammar and Usage
                    "Transformation of Sentences", "Synthesis of Sentences", "Active and Passive Voice",
                    "Direct and Indirect Speech", "Prepositions", "Phrasal Verbs", "Idioms",
                    
                    # Composition Skills
                    "Argumentative Writing", "Descriptive Writing", "Narrative Writing",
                    "Expository Writing", "Creative Writing", "Critical Writing"
                ]
            },
            
            "Hindi": {
                1: [
                    # वर्णमाला और उच्चारण
                    "हिंदी वर्णमाला", "स्वर", "व्यंजन", "मात्राएँ", "संयुक्त अक्षर",
                    "उच्चारण", "शुद्ध उच्चारण", "वर्ण पहचान",
                    
                    # शब्द निर्माण
                    "दो अक्षर के शब्द", "तीन अक्षर के शब्द", "चार अक्षर के शब्द",
                    "सरल शब्द", "चित्र देखकर शब्द", "वाक्य निर्माण",
                    
                    # पठन कौशल
                    "सरल वाक्य पढ़ना", "चित्र देखकर कहानी", "छोटी कविताएँ",
                    "नैतिक कहानियाँ", "बालगीत",
                    
                    # लेखन कौशल
                    "वर्ण लेखन", "शब्द लेखन", "वाक्य लेखन", "सुंदर लेखन",
                    "नकल करके लिखना"
                ],
                
                2: [
                    # व्याकरण
                    "संज्ञा", "सर्वनाम", "विशेषण", "क्रिया", "वचन", "लिंग",
                    "एकवचन-बहुवचन", "पुल्लिंग-स्त्रीलिंग",
                    
                    # शब्द भंडार
                    "नए शब्द", "शब्द अर्थ", "विपरीत शब्द", "समान अर्थ वाले शब्द",
                    "तुकांत शब्द", "शब्द खेल",
                    
                    # पठन पाठन
                    "कहानी पठन", "कविता पठन", "नैतिक शिक्षा", "चरित्र पहचान",
                    "मुख्य विचार", "घटना क्रम",
                    
                    # लेखन
                    "वाक्य रचना", "अनुच्छेद लेखन", "चित्र वर्णन", "पत्र लेखन",
                    "दैनिक गतिविधियाँ"
                ],
                
                3: [
                    # साहित्य पठन
                    "कहानी संग्रह", "काव्य संग्रह", "नाटक", "जीवनी", "यात्रा वृत्तांत",
                    "बाल साहित्य", "लोक कथाएँ", "परी कथाएँ",
                    
                    # व्याकरण
                    "संज्ञा के भेद", "सर्वनाम के भेद", "विशेषण के भेद", "क्रिया के भेद",
                    "काल", "भूतकाल", "वर्तमान काल", "भविष्य काल", "वाक्य के भेद",
                    
                    # रचनात्मक लेखन
                    "कहानी लेखन", "निबंध लेखन", "पत्र लेखन", "संवाद लेखन",
                    "चरित्र चित्रण", "भाव व्यक्ति",
                    
                    # भाषा कौशल
                    "शुद्ध उच्चारण", "वाचन कला", "भाषण कला", "कविता पाठ",
                    "अभिनय", "संवाद अदायगी"
                ],
                
                4: [
                    # उन्नत साहित्य
                    "आधुनिक कविता", "प्राचीन काव्य", "कहानी विश्लेषण", "नाटक अध्ययन",
                    "महाकाव्य परिचय", "संत साहित्य", "भक्ति काव्य",
                    
                    # व्याकरण और भाषा
                    "छंद शास्त्र", "अलंकार", "रस", "समास", "संधि", "तत्सम-तद्भव",
                    "देशज-विदेशज शब्द", "मुहावरे", "लोकोक्तियाँ",
                    
                    # लेखन कला
                    "आलोचनात्मक लेखन", "शोध लेखन", "साक्षात्कार", "रिपोर्ट लेखन",
                    "समीक्षा लेखन", "व्यावसायिक पत्राचार",
                    
                    # संप्रेषण कौशल
                    "सार्वजनिक भाषण", "वाद-विवाद", "समूह चर्चा", "प्रस्तुतीकरण",
                    "साक्षात्कार तकनीक"
                ],
                
                5: [
                    # शास्त्रीय साहित्य
                    "संस्कृत काव्य", "हिंदी काव्य", "आधुनिक साहित्य", "समसामयिक लेखन",
                    "तुलनात्मक साहित्य", "विश्व साहित्य",
                    
                    # भाषा विज्ञान
                    "भाषा विज्ञान के सिद्धांत", "हिंदी भाषा का विकास", "बोली और भाषा",
                    "मानक हिंदी", "तकनीकी हिंदी",
                    
                    # शोध और आलोचना
                    "साहित्यिक आलोचना", "शोध प्रविधि", "ग्रंथ सूची", "संदर्भ सूची",
                    "थीसिस लेखन", "शोध पत्र लेखन"
                ],
                
                6: [
                    # गद्य साहित्य
                    "कहानी संग्रह", "निबंध संग्रह", "जीवनी", "आत्मकथा", "यात्रा वृत्तांत",
                    "संस्मरण", "रेखाचित्र", "हास्य व्यंग्य",
                    
                    # काव्य साहित्य
                    "आदिकालीन काव्य", "भक्तिकालीन काव्य", "रीतिकालीन काव्य", "आधुनिक काव्य",
                    "छायावादी काव्य", "प्रगतिवादी काव्य", "प्रयोगवादी काव्य",
                    
                    # व्याकरण
                    "संधि विचार", "समास विचार", "प्रत्यय", "उपसर्ग", "तत्सम-तद्भव",
                    "देशज-विदेशज", "पर्यायवाची", "विलोम", "अनेकार्थी शब्द",
                    
                    # रचना कौशल
                    "अनुच्छेद लेखन", "पत्र लेखन", "निबंध लेखन", "कहानी लेखन",
                    "संवाद लेखन", "विज्ञापन लेखन"
                ],
                
                7: [
                    # साहित्य अध्ययन
                    "हिंदी साहित्य का इतिहास", "काव्य शास्त्र", "नाट्य शास्त्र",
                    "कथा साहित्य", "निबंध साहित्य", "आलोचना साहित्य",
                    
                    # भाषा विज्ञान
                    "हिंदी व्याकरण", "छंद शास्त्र", "अलंकार शास्त्र", "रस सिद्धांत",
                    "ध्वनि विज्ञान", "रूप विज्ञान", "वाक्य विज्ञान",
                    
                    # प्रयोजनमूलक हिंदी
                    "कार्यालयी हिंदी", "तकनीकी हिंदी", "व्यावसायिक हिंदी",
                    "संचार माध्यम की हिंदी", "कंप्यूटर और हिंदी",
                    
                    # रचनात्मक लेखन
                    "काव्य रचना", "कहानी लेखन", "नाटक लेखन", "निबंध लेखन",
                    "समीक्षा लेखन", "साक्षात्कार लेखन"
                ],
                
                8: [
                    # उच्च साहित्य
                    "महाकाव्य अध्ययन", "खंडकाव्य अध्ययन", "गीतिकाव्य", "मुक्तक काव्य",
                    "प्रबंध काव्य", "गद्यकाव्य", "नवगीत", "गज़ल",
                    
                    # आलोचना और समीक्षा
                    "साहित्यिक आलोचना", "व्यावहारिक आलोचना", "तुलनात्मक अध्ययन",
                    "मूल्यांकन", "व्याख्या", "विश्लेषण",
                    
                    # भाषा और शैली
                    "भाषा की शुद्धता", "शैली विज्ञान", "अनुवाद कला", "संपादन कला",
                    "प्रूफ रीडिंग", "भाषा नियोजन",
                    
                    # संचार कौशल
                    "उच्च संचार कौशल", "मीडिया लेखन", "पत्रकारिता", "रेडियो-टीवी लेखन",
                    "फिल्म लेखन", "रंगमंच लेखन"
                ],
                
                9: [
                    # गद्य खंड
                    "गद्य की विविध विधाएँ", "कहानी", "निबंध", "एकांकी", "जीवनी",
                    "संस्मरण", "यात्रा वृत्तांत", "डायरी", "पत्र साहित्य",
                    
                    # काव्य खंड
                    "काव्य की परंपरा", "छंदबद्ध काव्य", "मुक्त छंद", "गीत", "गज़ल",
                    "दोहे", "सॉनेट", "हाइकू", "तांका",
                    
                    # व्याकरण
                    "व्याकरण के नियम", "वाक्य संशोधन", "वाक्य परिवर्तन", "संधि-विग्रह",
                    "समास-विग्रह", "उपसर्ग-प्रत्यय", "काल परिवर्तन",
                    
                    # लेखन कौशल
                    "रचनात्मक लेखन", "भावानुवाद", "सारांश लेखन", "पत्र लेखन",
                    "आवेदन पत्र", "शिकायती पत्र", "बधाई पत्र"
                ],
                
                10: [
                    # गद्य साहित्य
                    "आधुनिक हिंदी गद्य", "कहानी साहित्य", "उपन्यास साहित्य", "नाटक साहित्य",
                    "निबंध साहित्य", "आलोचना साहित्य", "जीवनी साहित्य", "यात्रा साहित्य",
                    
                    # काव्य साहित्य
                    "आधुनिक हिंदी काव्य", "छायावाद", "प्रगतिवाद", "प्रयोगवाद", "नई कविता",
                    "समकालीन कविता", "गीत काव्य", "प्रगीत काव्य",
                    
                    # व्याकरण और भाषा
                    "उच्च व्याकरण", "भाषा की शुद्धता", "वाक्य संरचना", "शब्द संपदा",
                    "मुहावरे-लोकोक्तियाँ", "पारिभाषिक शब्दावली",
                    
                    # रचना विधान
                    "निबंध लेखन", "कहानी लेखन", "नाटक लेखन", "संवाद लेखन",
                    "चरित्र चित्रण", "दृश्य चित्रण", "भाव चित्रण"
                ]
            },
            
            "Physics": {
                6: [
                    # Matter and Materials
                    "Matter and Its Properties", "States of Matter", "Solids, Liquids and Gases",
                    "Changes of State", "Melting and Freezing", "Evaporation and Condensation",
                    "Expansion and Contraction",
                    
                    # Force and Motion
                    "Force", "Effects of Force", "Types of Forces", "Contact and Non-contact Forces",
                    "Gravitational Force", "Magnetic Force", "Friction", "Motion", "Types of Motion",
                    
                    # Energy
                    "Forms of Energy", "Mechanical Energy", "Heat Energy", "Light Energy",
                    "Sound Energy", "Electrical Energy", "Energy Transformations",
                    "Sources of Energy", "Renewable and Non-renewable Energy",
                    
                    # Light
                    "Light and Its Properties", "Sources of Light", "Reflection of Light",
                    "Mirrors", "Plane Mirror", "Images", "Shadows", "Transparent, Translucent and Opaque Objects",
                    
                    # Sound
                    "Sound and Its Properties", "Sources of Sound", "How Sound Travels",
                    "Vibrations", "Musical Instruments", "Noise and Music",
                    
                    # Heat
                    "Heat and Temperature", "Thermometer", "Effects of Heat", "Conduction",
                    "Convection", "Radiation", "Good and Bad Conductors",
                    
                    # Magnetism
                    "Magnets", "Properties of Magnets", "Types of Magnets", "Magnetic Materials",
                    "Earth as a Magnet", "Compass"
                ],
                
                7: [
                    # Force and Pressure
                    "Force", "Balanced and Unbalanced Forces", "Pressure", "Pressure in Liquids",
                    "Atmospheric Pressure", "Applications of Pressure",
                    
                    # Motion and Time
                    "Motion", "Types of Motion", "Speed", "Measurement of Speed", "Distance-Time Graph",
                    "Uniform and Non-uniform Motion",
                    
                    # Heat
                    "Heat and Temperature", "Clinical Thermometer", "Laboratory Thermometer",
                    "Transfer of Heat", "Conduction, Convection and Radiation", "Sea Breeze and Land Breeze",
                    "Dark and Light Colored Objects",
                    
                    # Light
                    "Light", "Reflection of Light", "Laws of Reflection", "Regular and Irregular Reflection",
                    "Images formed by Plane Mirror", "Spherical Mirrors", "Images formed by Spherical Mirrors",
                    "Uses of Concave and Convex Mirrors",
                    
                    # Sound
                    "Sound", "How Sound is Produced", "How Sound Travels", "Audible and Inaudible Sounds",
                    "Noise and Music", "Noise Pollution",
                    
                    # Electric Current and Its Effects
                    "Electric Current", "Electric Circuit", "Effects of Electric Current",
                    "Magnetic Effect of Electric Current", "Electromagnet", "Electric Bell",
                    
                    # Energy
                    "Work and Energy", "Forms of Energy", "Law of Conservation of Energy",
                    "Commercial Unit of Energy"
                ],
                
                8: [
                    # Force and Pressure
                    "Force", "Contact and Non-contact Forces", "Pressure", "Pressure Exerted by Liquids and Gases",
                    "Atmospheric Pressure", "Buoyancy", "Archimedes' Principle",
                    
                    # Friction
                    "Friction", "Factors Affecting Friction", "Advantages and Disadvantages of Friction",
                    "Methods to Increase and Reduce Friction", "Fluid Friction",
                    
                    # Sound
                    "Production of Sound", "Propagation of Sound", "Reflection of Sound", "Echo",
                    "Range of Hearing", "Applications of Ultrasound",
                    
                    # Chemical Effects of Electric Current
                    "Conduction of Electricity", "Chemical Effects of Electric Current", "Electroplating",
                    "Electrolysis",
                    
                    # Some Natural Phenomena
                    "Lightning", "Charges and Sparks", "Transfer of Charge", "Story of Lightning",
                    "Lightning Safety", "Earthquakes", "Protection Against Earthquakes",
                    
                    # Light
                    "Reflection of Light", "Laws of Reflection", "Regular and Diffused Reflection",
                    "Images formed by Plane Mirror", "Kaleidoscope", "Periscope",
                    "Dispersion of Light", "Rainbow Formation"
                ],
                
                9: [
                    # Motion
                    "Motion in One Dimension", "Distance and Displacement", "Speed and Velocity",
                    "Acceleration", "Equations of Motion", "Uniform and Non-uniform Motion",
                    "Graphical Representation of Motion",
                    
                    # Force and Laws of Motion
                    "Force", "Newton's Laws of Motion", "Inertia", "Momentum", "Conservation of Momentum",
                    "Action and Reaction Forces",
                    
                    # Gravitation
                    "Universal Law of Gravitation", "Gravitational Constant", "Free Fall",
                    "Acceleration due to Gravity", "Weight", "Thrust and Pressure",
                    "Buoyancy", "Archimedes' Principle",
                    
                    # Work and Energy
                    "Work", "Energy", "Kinetic Energy", "Potential Energy", "Law of Conservation of Energy",
                    "Power", "Commercial Unit of Energy",
                    
                    # Sound
                    "Production of Sound", "Propagation of Sound", "Reflection of Sound",
                    "Reverberation and Echo", "Audible Range", "Ultrasound and Its Applications"
                ],
                
                10: [
                    # Light - Reflection and Refraction
                    "Reflection of Light", "Spherical Mirrors", "Image Formation by Spherical Mirrors",
                    "Mirror Formula", "Magnification", "Refraction of Light", "Laws of Refraction",
                    "Refractive Index", "Refraction by Spherical Lenses", "Image Formation by Lenses",
                    "Lens Formula", "Power of Lens",
                    
                    # The Human Eye and Colourful World
                    "Human Eye", "Defects of Vision", "Correction of Eye Defects", "Refraction of Light through Prism",
                    "Dispersion of White Light", "Atmospheric Refraction", "Scattering of Light",
                    
                    # Electricity
                    "Electric Current and Potential Difference", "Ohm's Law", "Resistance", "Factors Affecting Resistance",
                    "Series and Parallel Combinations", "Heating Effect of Electric Current", "Electric Power",
                    
                    # Magnetic Effects of Electric Current
                    "Magnetic Field", "Magnetic Field due to Current-carrying Conductor", "Force on Current-carrying Conductor",
                    "Fleming's Left-hand Rule", "Electric Motor", "Electromagnetic Induction", "Electric Generator",
                    
                    # Sources of Energy
                    "Conventional Sources of Energy", "Non-conventional Sources of Energy", "Fossil Fuels",
                    "Solar Energy", "Biogas", "Wind Energy", "Hydro Energy", "Nuclear Energy",
                    "Environmental Consequences"
                ]
            },
            
            "Chemistry": {
                6: [
                    # Introduction to Chemistry
                    "Matter", "Physical and Chemical Properties", "Elements, Compounds and Mixtures",
                    "Pure and Impure Substances", "Separation of Mixtures",
                    
                    # Air and Water
                    "Composition of Air", "Properties of Air", "Uses of Air", "Air Pollution",
                    "Water", "Sources of Water", "Properties of Water", "Hard and Soft Water",
                    "Water Pollution", "Water Treatment",
                    
                    # Acids, Bases and Salts
                    "Acids", "Bases", "Indicators", "Neutralization", "Salts",
                    
                    # Metals and Non-metals
                    "Properties of Metals", "Properties of Non-metals", "Uses of Metals and Non-metals",
                    
                    # Atomic Structure
                    "Atoms and Molecules", "Structure of Atom", "Elements and Symbols"
                ],
                
                7: [
                    # Elements, Compounds and Mixtures
                    "Elements", "Compounds", "Mixtures", "Separation Techniques",
                    "Crystallization", "Distillation", "Chromatography",
                    
                    # Atomic Structure
                    "Atomic Theory", "Structure of Atom", "Protons, Neutrons and Electrons",
                    "Electronic Configuration", "Valency",
                    
                    # Chemical Reactions
                    "Chemical Changes", "Chemical Equations", "Balancing Chemical Equations",
                    "Types of Chemical Reactions",
                    
                    # Acids, Bases and Salts
                    "Properties of Acids", "Properties of Bases", "Indicators", "pH Scale",
                    "Neutralization", "Preparation of Salts",
                    
                    # Air and Atmosphere
                    "Composition of Atmosphere", "Oxygen", "Carbon Dioxide", "Water Cycle",
                    "Air Pollution", "Greenhouse Effect"
                ],
                
                8: [
                    # Atomic Structure and Chemical Bonding
                    "Atomic Structure", "Electronic Configuration", "Valency", "Chemical Bonding",
                    "Ionic Bonding", "Covalent Bonding",
                    
                    # Chemical Reactions
                    "Types of Chemical Reactions", "Oxidation and Reduction", "Displacement Reactions",
                    "Double Displacement Reactions", "Precipitation Reactions",
                    
                    # Acids, Bases and Salts
                    "Strong and Weak Acids and Bases", "pH Scale", "Salt Hydrolysis",
                    "Preparation of Salts", "Uses of Acids, Bases and Salts",
                    
                    # Hydrogen
                    "Preparation of Hydrogen", "Properties of Hydrogen", "Uses of Hydrogen",
                    
                    # Water
                    "Water as a Universal Solvent", "Solutions", "Solubility", "Concentration",
                    "Crystallization", "Water of Crystallization",
                    
                    # Carbon and Its Compounds
                    "Allotropes of Carbon", "Diamond", "Graphite", "Coal", "Petroleum"
                ],
                
                9: [
                    # Atomic Structure and Chemical Bonding
                    "Atomic Models", "Bohr's Model", "Electronic Configuration", "Valency",
                    "Chemical Bonding", "Ionic Bond", "Covalent Bond", "Properties of Ionic and Covalent Compounds",
                    
                    # Study of Gas Laws
                    "Boyle's Law", "Charles' Law", "Gay-Lussac's Law", "Avogadro's Law",
                    "Ideal Gas Equation", "Kinetic Molecular Theory",
                    
                    # Atmospheric Pollution
                    "Air Pollution", "Water Pollution", "Soil Pollution", "Greenhouse Effect",
                    "Ozone Depletion", "Acid Rain",
                    
                    # The Language of Chemistry
                    "Chemical Symbols", "Chemical Formulae", "Chemical Equations", "Balancing Equations",
                    "Information from Chemical Equations",
                    
                    # Chemical Changes and Reactions
                    "Physical and Chemical Changes", "Types of Chemical Reactions", "Energy Changes in Reactions",
                    "Catalysts", "Reversible and Irreversible Reactions"
                ],
                
                10: [
                    # Periodic Properties and Variations
                    "Modern Periodic Table", "Periodic Properties", "Atomic Size", "Ionization Energy",
                    "Electron Affinity", "Electronegativity", "Metallic and Non-metallic Character",
                    
                    # Chemical Bonding
                    "Ionic Bonding", "Covalent Bonding", "Coordinate Bonding", "Metallic Bonding",
                    "Intermolecular Forces", "Hydrogen Bonding",
                    
                    # Study of Acids, Bases and Salts
                    "Arrhenius Theory", "Bronsted-Lowry Theory", "Lewis Theory", "pH Scale",
                    "Buffer Solutions", "Hydrolysis of Salts", "Preparation of Salts",
                    
                    # Analytical Chemistry
                    "Qualitative Analysis", "Tests for Cations", "Tests for Anions", "Flame Tests",
                    "Precipitation Reactions", "Confirmatory Tests",
                    
                    # Mole Concept and Stoichiometry
                    "Atomic Mass", "Molecular Mass", "Mole Concept", "Avogadro's Number",
                    "Empirical and Molecular Formula", "Stoichiometric Calculations",
                    
                    # Electrolysis
                    "Electrolytes and Non-electrolytes", "Electrolysis", "Applications of Electrolysis",
                    "Electroplating", "Extraction of Metals",
                    
                    # Metallurgy
                    "Occurrence of Metals", "Extraction of Metals", "Refining of Metals",
                    "Alloys", "Corrosion and Its Prevention",
                    
                    # Study of Compounds
                    "Hydrogen Chloride", "Ammonia", "Nitric Acid", "Sulphuric Acid",
                    "Preparation, Properties and Uses",
                    
                    # Organic Chemistry
                    "Introduction to Organic Chemistry", "Hydrocarbons", "Alkanes, Alkenes, Alkynes",
                    "Functional Groups", "Alcohols", "Carboxylic Acids"
                ]
            },
            
            "Biology": {
                6: [
                    # Cell - The Basic Unit of Life
                    "Cell Theory", "Cell Structure", "Plant Cell", "Animal Cell", "Cell Organelles",
                    "Differences between Plant and Animal Cells",
                    
                    # Plant Life
                    "Parts of a Plant", "Root System", "Shoot System", "Leaves", "Photosynthesis",
                    "Respiration in Plants", "Transportation in Plants",
                    
                    # Flowering Plants
                    "Parts of a Flower", "Types of Flowers", "Pollination", "Fertilization",
                    "Seed Formation", "Fruit Formation", "Seed Dispersal",
                    
                    # Animal Life
                    "Classification of Animals", "Vertebrates and Invertebrates", "Animal Habitats",
                    "Adaptation in Animals", "Life Cycles of Animals",
                    
                    # Human Body
                    "Human Body Systems", "Skeletal System", "Muscular System", "Digestive System",
                    "Respiratory System", "Circulatory System", "Nervous System",
                    
                    # Health and Hygiene
                    "Personal Hygiene", "Dental Care", "Balanced Diet", "Exercise and Health",
                    "Common Diseases", "Prevention of Diseases",
                    
                    # Habitat and Adaptation
                    "Types of Habitats", "Terrestrial Habitats", "Aquatic Habitats", "Arboreal Habitats",
                    "Adaptation for Protection", "Adaptation for Getting Food"
                ],
                
                7: [
                    # Classification of Plants
                    "Plant Kingdom", "Classification Criteria", "Thallophyta", "Bryophyta",
                    "Pteridophyta", "Gymnosperms", "Angiosperms", "Monocots and Dicots",
                    
                    # Classification of Animals
                    "Animal Kingdom", "Classification Criteria", "Invertebrates", "Vertebrates",
                    "Phylum Coelenterata", "Phylum Platyhelminthes", "Phylum Nematoda",
                    "Phylum Annelida", "Phylum Arthropoda", "Phylum Mollusca", "Phylum Echinodermata",
                    "Phylum Chordata",
                    
                    # Photosynthesis
                    "Process of Photosynthesis", "Conditions for Photosynthesis", "Raw Materials",
                    "Products of Photosynthesis", "Factors Affecting Photosynthesis",
                    
                    # Respiration
                    "Respiration in Plants", "Respiration in Animals", "Breathing in Humans",
                    "Respiratory System", "Exchange of Gases",
                    
                    # Transportation
                    "Transportation in Plants", "Xylem and Phloem", "Transpiration",
                    "Transportation in Animals", "Circulatory System", "Heart", "Blood Vessels", "Blood",
                    
                    # Reproduction
                    "Reproduction in Plants", "Vegetative Reproduction", "Sexual Reproduction",
                    "Reproduction in Animals", "Sexual and Asexual Reproduction",
                    
                    # Health and Disease
                    "Health and Disease", "Communicable Diseases", "Non-communicable Diseases",
                    "Disease Prevention", "Immunization"
                ],
                
                8: [
                    # Crop Production and Management
                    "Agricultural Practices", "Crop Variety Improvement", "Crop Production",
                    "Crop Protection", "Animal Husbandry",
                    
                    # Cell Division and Reproduction
                    "Cell Division", "Mitosis", "Meiosis", "Reproduction in Animals",
                    "Sexual and Asexual Reproduction", "Reproductive Health",
                    
                    # Heredity and Evolution
                    "Heredity", "Inheritance of Traits", "Mendel's Laws", "Chromosomes and Genes",
                    "Sex Determination", "Evolution", "Origin of Life",
                    
                    # Microorganisms
                    "Microorganisms", "Classification of Microorganisms", "Bacteria", "Viruses",
                    "Fungi", "Protozoa", "Algae", "Useful and Harmful Microorganisms",
                    
                    # Ecosystem
                    "Ecosystem", "Components of Ecosystem", "Food Chain", "Food Web",
                    "Energy Flow", "Biogeochemical Cycles", "Human Impact on Environment",
                    
                    # Human Body Systems
                    "Digestive System", "Respiratory System", "Circulatory System", "Excretory System",
                    "Nervous System", "Endocrine System", "Reproductive System"
                ],
                
                9: [
                    # The Fundamental Unit of Life
                    "Cell Theory", "Prokaryotic and Eukaryotic Cells", "Plant and Animal Cells",
                    "Cell Organelles and Their Functions", "Cell Division",
                    
                    # Tissues
                    "Plant Tissues", "Meristematic Tissues", "Permanent Tissues", "Simple Tissues",
                    "Complex Tissues", "Animal Tissues", "Epithelial Tissue", "Connective Tissue",
                    "Muscular Tissue", "Nervous Tissue",
                    
                    # Diversity in Living Organisms
                    "Classification of Living Organisms", "Five Kingdom Classification",
                    "Monera", "Protista", "Fungi", "Plantae", "Animalia",
                    "Hierarchy of Classification", "Nomenclature",
                    
                    # Plant Physiology
                    "Life Processes in Plants", "Nutrition", "Photosynthesis", "Respiration",
                    "Transportation", "Excretion", "Control and Coordination",
                    
                    # Animal Physiology
                    "Life Processes in Animals", "Nutrition in Animals", "Respiration in Animals",
                    "Transportation in Animals", "Excretion in Animals", "Control and Coordination in Animals",
                    
                    # Reproduction
                    "Reproduction in Plants", "Vegetative Propagation", "Sexual Reproduction in Plants",
                    "Reproduction in Animals", "Sexual and Asexual Reproduction",
                    
                    # Health and Disease
                    "Health and Its Significance", "Disease and Its Causes", "Infectious Diseases",
                    "Prevention and Control of Diseases", "Immunization"
                ],
                
                10: [
                    # Life Processes
                    "Nutrition", "Autotrophic Nutrition", "Heterotrophic Nutrition", "Nutrition in Human Beings",
                    "Respiration", "Respiration in Plants", "Respiration in Animals", "Human Respiratory System",
                    "Transportation", "Transportation in Plants", "Transportation in Animals", "Human Circulatory System",
                    "Excretion", "Excretion in Plants", "Excretion in Animals", "Human Excretory System",
                    
                    # Control and Coordination
                    "Control and Coordination in Animals", "Nervous System", "Endocrine System",
                    "Control and Coordination in Plants", "Plant Hormones", "Movements in Plants",
                    
                    # How do Organisms Reproduce
                    "Reproduction", "Asexual Reproduction", "Sexual Reproduction", "Reproductive Health",
                    "Reproduction in Plants", "Reproduction in Animals", "Reproduction in Human Beings",
                    
                    # Heredity and Evolution
                    "Heredity", "Inheritance of Traits", "Mendel's Laws of Inheritance", "Sex Determination",
                    "Evolution", "Origin of Life", "Natural Selection", "Speciation",
                    
                    # Our Environment
                    "Ecosystem", "Components of Ecosystem", "Food Chains and Food Webs",
                    "Energy Flow in Ecosystem", "Biogeochemical Cycles", "Environmental Problems",
                    "Biodiversity and Its Conservation"
                ]
            },
            
            "History & Civics": {
                6: [
                    # History
                    "What is History", "Sources of History", "Prehistoric Times", "Stone Age",
                    "Indus Valley Civilization", "Vedic Civilization", "Life in Vedic Times",
                    "Rise of Kingdoms", "Mahajanapadas", "Rise of Magadha", "Alexander's Invasion",
                    "Mauryan Empire", "Chandragupta Maurya", "Ashoka the Great", "Gupta Empire",
                    "Golden Age of Guptas", "Harsha's Empire",
                    
                    # Ancient Civilizations
                    "Mesopotamian Civilization", "Egyptian Civilization", "Chinese Civilization",
                    "Greek Civilization", "Roman Civilization",
                    
                    # Civics
                    "What is Government", "Levels of Government", "Local Government",
                    "Panchayati Raj", "Village Panchayat", "Block Panchayat", "District Panchayat",
                    "Municipal Corporation", "Municipality", "Cantonment Board",
                    "Citizen and Citizenship", "Rights and Duties of Citizens",
                    "Unity in Diversity", "National Symbols"
                ],
                
                7: [
                    # Medieval History
                    "Medieval Period", "Arab Invasion", "Turkish Invasion", "Delhi Sultanate",
                    "Slave Dynasty", "Khilji Dynasty", "Tughlaq Dynasty", "Sayyid Dynasty", "Lodi Dynasty",
                    "Vijayanagara Empire", "Bahmani Kingdom", "Regional Kingdoms",
                    "Mughal Empire", "Babur", "Humayun", "Akbar", "Jahangir", "Shah Jahan", "Aurangzeb",
                    "Decline of Mughal Empire", "Rise of Regional Powers",
                    
                    # Medieval Society and Culture
                    "Medieval Society", "Religion in Medieval India", "Art and Architecture",
                    "Literature", "Science and Technology", "Trade and Commerce",
                    
                    # Civics
                    "State Government", "Chief Minister", "Governor", "State Legislature",
                    "State Assembly", "Legislative Council", "Functions of State Government",
                    "Union Government", "President", "Prime Minister", "Parliament",
                    "Lok Sabha", "Rajya Sabha", "Functions of Union Government",
                    "Constitution of India", "Fundamental Rights", "Fundamental Duties"
                ],
                
                8: [
                    # Modern History
                    "Coming of Europeans", "Portuguese", "Dutch", "French", "English",
                    "East India Company", "Battle of Plassey", "Battle of Buxar", "British Rule in India",
                    "Administrative Policies", "Economic Policies", "Social Reforms",
                    "Indian Renaissance", "Reform Movements", "Great Revolt of 1857",
                    "Growth of Nationalism", "Indian National Congress", "Partition of Bengal",
                    "Swadeshi Movement", "Revolutionary Movement",
                    
                    # Freedom Struggle
                    "Mahatma Gandhi", "Non-Cooperation Movement", "Civil Disobedience Movement",
                    "Quit India Movement", "World War II and India", "Indian National Army",
                    "Partition of India", "Independence Day",
                    
                    # Civics
                    "Judiciary", "Supreme Court", "High Court", "District Court", "Independence of Judiciary",
                    "Election Commission", "Electoral Process", "Political Parties",
                    "Pressure Groups", "Media and Democracy", "Challenges to Democracy"
                ],
                
                9: [
                    # French Revolution
                    "Causes of French Revolution", "Course of Revolution", "Reign of Terror",
                    "Rise of Napoleon", "Effects of French Revolution",
                    
                    # Industrial Revolution
                    "Industrial Revolution in England", "Causes and Effects", "Transportation Revolution",
                    "Social Changes", "Working Class Movement",
                    
                    # Rise of Nationalism
                    "Nationalism in Europe", "Unification of Germany", "Unification of Italy",
                    "Russian Revolution", "Rise of Fascism and Nazism",
                    
                    # World Wars
                    "First World War", "Causes and Effects", "Second World War",
                    "Rise of Hitler", "Cold War", "Formation of UNO",
                    
                    # Civics
                    "Democratic Government", "What is Democracy", "Features of Democracy",
                    "Electoral Politics", "Working of Institutions", "Democratic Rights",
                    "Constitutional Design", "Making of Indian Constitution"
                ],
                
                10: [
                    # Nationalism in India
                    "First War of Independence 1857", "Growth of Nationalism", "Partition of Bengal",
                    "Swadeshi Movement", "Formation of Muslim League", "Morley-Minto Reforms",
                    "Home Rule Movement", "Rowlatt Act", "Jallianwala Bagh Massacre",
                    "Khilafat Movement", "Non-Cooperation Movement", "Civil Disobedience Movement",
                    "Government of India Act 1935", "Quit India Movement", "Partition and Independence",
                    
                    # The Making of Global World
                    "Trade and Globalization", "Colonialism", "Rinderpest in Africa",
                    "Impact of Technology", "World Wars and Recovery", "Bretton Woods System",
                    
                    # The Age of Industrialization
                    "Before Industrial Revolution", "Industrial Revolution", "Industrialization in Colonies",
                    "Factory System", "Impact on Workers", "Industrial Cities",
                    
                    # Print Culture and Modern World
                    "History of Print", "Print Revolution", "Print Culture in India",
                    "Religious Reform and Public Debates", "New Forms of Publication",
                    
                    # Civics - Power Sharing
                    "Power Sharing", "Belgium and Sri Lanka", "Forms of Power Sharing",
                    "Federal System", "Indian Federalism", "Language Policy",
                    
                    # Democracy and Diversity
                    "Social Differences", "Overlapping and Cross-cutting Differences", "Politics of Social Divisions",
                    "Democracy and Social Diversity", "Gender, Religion and Caste",
                    
                    # Political Parties
                    "Political Parties", "Functions of Political Parties", "Necessity of Political Parties",
                    "How Many Parties", "National and Regional Parties", "Challenges to Political Parties",
                    
                    # Outcomes of Democracy
                    "How do we Assess Democracy", "Accountable, Responsive and Legitimate Government",
                    "Economic Growth and Development", "Reduction of Inequality and Poverty",
                    "Accommodation of Social Diversity", "Dignity and Freedom of Citizens"
                ]
            },
            
            "Geography": {
                6: [
                    # The Earth
                    "Earth as a Planet", "Shape and Size of Earth", "Globe and Maps",
                    "Latitudes and Longitudes", "Geographic Grid", "Time Zones",
                    
                    # Motions of Earth
                    "Rotation of Earth", "Revolution of Earth", "Seasons", "Day and Night",
                    
                    # Structure of Earth
                    "Internal Structure of Earth", "Crust", "Mantle", "Core", "Rocks and Minerals",
                    "Types of Rocks", "Rock Cycle",
                    
                    # Landforms
                    "Major Landforms", "Mountains", "Plateaus", "Plains", "Deserts",
                    "Coastal Landforms", "Islands",
                    
                    # Water Bodies
                    "Hydrosphere", "Oceans", "Seas", "Rivers", "Lakes", "Water Cycle",
                    
                    # Weather and Climate
                    "Atmosphere", "Weather and Climate", "Elements of Weather", "Climate Zones",
                    
                    # Natural Vegetation
                    "Natural Vegetation", "Forests", "Grasslands", "Desert Vegetation",
                    "Wildlife", "National Parks and Sanctuaries"
                ],
                
                7: [
                    # Environment
                    "Natural Environment", "Human Environment", "Human-Environment Interaction",
                    "Environmental Problems", "Conservation of Environment",
                    
                    # Inside Our Earth
                    "Interior of Earth", "Rocks and Minerals", "Rock Cycle", "Earth's Crust",
                    
                    # Our Changing Earth
                    "Lithospheric Plates", "Plate Tectonics", "Volcanoes", "Earthquakes",
                    "Weathering", "Erosion", "Deposition",
                    
                    # Air
                    "Atmosphere", "Composition of Atmosphere", "Structure of Atmosphere",
                    "Weather", "Climate", "Adaptation by Animals and Plants",
                    
                    # Water
                    "Water Cycle", "Distribution of Water", "Ocean Currents", "Tides", "Waves",
                    
                    # Natural Vegetation and Wildlife
                    "Forests", "Grasslands", "Desert Vegetation", "Wildlife", "Conservation",
                    
                    # Human Environment
                    "Settlement", "Rural Settlement", "Urban Settlement", "Transport",
                    "Communication"
                ],
                
                8: [
                    # Resources
                    "Resources", "Types of Resources", "Natural Resources", "Human Resources",
                    "Conservation of Resources", "Sustainable Development",
                    
                    # Land, Soil, Water, Natural Vegetation and Wildlife
                    "Land Use", "Land Degradation", "Soil Formation", "Soil Types", "Soil Erosion",
                    "Water Scarcity", "Water Conservation", "Forests", "Deforestation",
                    "Wildlife Conservation",
                    
                    # Mineral and Power Resources
                    "Minerals", "Types of Minerals", "Distribution of Minerals", "Coal", "Petroleum",
                    "Natural Gas", "Renewable Energy", "Solar Energy", "Wind Energy", "Hydroelectric Power",
                    
                    # Agriculture
                    "Agriculture", "Types of Farming", "Crop Seasons", "Major Crops", "Agricultural Development",
                    
                    # Industries
                    "Industries", "Types of Industries", "Cotton Textile Industry", "Iron and Steel Industry",
                    "Information Technology Industry", "Industrial Pollution",
                    
                    # Human Resources
                    "People as Resource", "Population", "Population Distribution", "Population Density",
                    "Population Growth", "Age Structure", "Human Development"
                ],
                
                9: [
                    # India - Size and Location
                    "India's Location", "India's Neighbors", "India's Size", "Administrative Divisions",
                    
                    # Physical Features of India
                    "Major Physical Divisions", "The Himalayan Mountains", "The Northern Plains",
                    "The Peninsular Plateau", "The Indian Desert", "The Coastal Plains", "The Islands",
                    
                    # Drainage
                    "Drainage Systems", "The Himalayan Rivers", "The Peninsular Rivers",
                    "Lakes", "Role of Rivers in Economy", "River Pollution",
                    
                    # Climate
                    "Climate Controls", "Factors Affecting Climate", "Indian Monsoon", "Seasons",
                    "Distribution of Rainfall", "Climate and Human Life",
                    
                    # Natural Vegetation and Wildlife
                    "Factors of Natural Vegetation", "Types of Vegetation", "Tropical Rainforests",
                    "Tropical Deciduous Forests", "Thorn Forests", "Mountain Vegetation",
                    "Mangrove Vegetation", "Wildlife", "National Parks", "Biosphere Reserves",
                    
                    # Population
                    "Population Size and Distribution", "Population Growth", "Age Composition",
                    "Sex Ratio", "Literacy Rate", "Population Policy"
                ],
                
                10: [
                    # Resources and Development
                    "Resource Planning", "Land Resources", "Land Use Pattern", "Land Degradation",
                    "Soil as a Resource", "Soil Formation", "Soil Types", "Soil Erosion and Conservation",
                    
                    # Forest and Wildlife Resources
                    "Forest and Wildlife", "Biodiversity", "Forest Types", "Deforestation",
                    "Conservation of Forest and Wildlife", "Community and Conservation",
                    
                    # Water Resources
                    "Water Scarcity", "Water Resources", "Multipurpose River Projects", "Rainwater Harvesting",
                    "Water Pollution", "Water Conservation",
                    
                    # Agriculture
                    "Types of Farming", "Cropping Pattern", "Major Crops", "Food Crops", "Cash Crops",
                    "Technological and Institutional Reforms", "Food Security",
                    
                    # Minerals and Energy Resources
                    "Mineral Resources", "Ferrous Minerals", "Non-ferrous Minerals", "Non-metallic Minerals",
                    "Energy Resources", "Conventional Sources", "Non-conventional Sources",
                    
                    # Manufacturing Industries
                    "Manufacturing", "Types of Industries", "Spatial Distribution", "Industrial Pollution",
                    "Iron and Steel Industry", "Textile Industry", "Information Technology",
                    
                    # Lifelines of National Economy
                    "Transport", "Roadways", "Railways", "Waterways", "Airways", "Pipelines",
                    "Communication", "International Trade"
                ]
            },
            
            "Computer Applications": {
                6: [
                    # Introduction to Computers
                    "What is a Computer", "Characteristics of Computer", "Types of Computers",
                    "Applications of Computer", "Computer System", "Hardware and Software",
                    
                    # Hardware Components
                    "Input Devices", "Output Devices", "Processing Unit", "Memory", "Storage Devices",
                    
                    # Software
                    "System Software", "Application Software", "Operating System", "Programming Languages",
                    
                    # Windows Operating System
                    "Introduction to Windows", "Desktop", "Taskbar", "Start Menu", "Windows Explorer",
                    "File Management", "Control Panel",
                    
                    # MS Paint
                    "Introduction to Paint", "Drawing Tools", "Color Palette", "Text Tool",
                    "Saving and Opening Files",
                    
                    # Word Processing
                    "Introduction to Word Processor", "Creating Documents", "Formatting Text",
                    "Inserting Pictures", "Tables", "Saving and Printing"
                ],
                
                7: [
                    # Computer Fundamentals
                    "Computer Generation", "Computer Architecture", "Von Neumann Architecture",
                    "Data and Information", "Number Systems", "Binary System",
                    
                    # Operating Systems
                    "Functions of Operating System", "Types of Operating System", "File Management",
                    "Memory Management", "Process Management",
                    
                    # MS Word Advanced
                    "Advanced Formatting", "Styles", "Headers and Footers", "Page Setup",
                    "Mail Merge", "Track Changes", "Comments",
                    
                    # MS Excel
                    "Introduction to Spreadsheet", "Workbook and Worksheet", "Data Entry",
                    "Formulas and Functions", "Charts and Graphs", "Data Analysis",
                    
                    # MS PowerPoint
                    "Introduction to Presentation Software", "Slides", "Text and Graphics",
                    "Animation", "Slide Transitions", "Presentation Delivery",
                    
                    # Internet
                    "Introduction to Internet", "World Wide Web", "Web Browser", "Search Engines",
                    "Email", "Internet Safety"
                ],
                
                8: [
                    # Advanced Computer Concepts
                    "Computer Networks", "Types of Networks", "Internet", "Protocols",
                    "Client-Server Model", "Database Concepts",
                    
                    # Programming Concepts
                    "Introduction to Programming", "Algorithms", "Flowcharts", "Programming Languages",
                    "Syntax and Semantics", "Debugging",
                    
                    # HTML
                    "Introduction to HTML", "HTML Tags", "Structure of HTML Document",
                    "Text Formatting", "Links", "Images", "Tables", "Forms",
                    
                    # Advanced Applications
                    "Database Management", "Creating Databases", "Tables", "Queries", "Reports",
                    "Web Design", "Multimedia Applications",
                    
                    # Digital Citizenship
                    "Computer Ethics", "Cyber Safety", "Digital Footprint", "Copyright",
                    "Privacy and Security", "Social Media Responsibility"
                ],
                
                9: [
                    # Computer Systems
                    "Computer Organization", "CPU Architecture", "Memory Hierarchy", "Storage Systems",
                    "Input/Output Systems", "Performance Metrics",
                    
                    # Programming in Java
                    "Introduction to Java", "Object-Oriented Programming", "Classes and Objects",
                    "Data Types", "Variables", "Operators", "Control Structures",
                    "Methods", "Arrays", "Inheritance", "Polymorphism",
                    
                    # Database Management
                    "Database Concepts", "Relational Database", "SQL", "Creating Tables",
                    "Data Manipulation", "Queries", "Joins", "Database Design",
                    
                    # Web Technologies
                    "Advanced HTML", "CSS", "JavaScript", "Dynamic Web Pages",
                    "Client-Side Scripting", "Server-Side Scripting",
                    
                    # Computer Networks
                    "Network Topologies", "Network Protocols", "Internet", "Email",
                    "Network Security", "Firewalls", "Encryption"
                ],
                
                10: [
                    # Object-Oriented Programming
                    "OOP Concepts", "Encapsulation", "Inheritance", "Polymorphism", "Abstraction",
                    "Classes and Objects", "Constructors", "Method Overloading", "Method Overriding",
                    
                    # Java Programming
                    "Java Syntax", "Data Types", "Variables", "Operators", "Control Flow",
                    "Arrays", "Strings", "Exception Handling", "File Handling",
                    "Collections Framework", "Multithreading",
                    
                    # Database Connectivity
                    "JDBC", "Database Connection", "SQL Queries", "ResultSet",
                    "Prepared Statements", "Database Applications",
                    
                    # Web Development
                    "HTML5", "CSS3", "JavaScript", "DOM Manipulation", "Event Handling",
                    "AJAX", "jQuery", "Responsive Design",
                    
                    # Project Work
                    "System Analysis", "Design", "Implementation", "Testing", "Documentation",
                    "Project Management", "Software Development Life Cycle"
                ]
            },
            
            "Sanskrit": {
                6: [
                    # देवनागरी और उच्चारण
                    "देवनागरी लिपि", "संस्कृत वर्णमाला", "स्वर और व्यंजन", "संयुक्त अक्षर",
                    "उच्चारण नियम", "मात्राएँ", "अनुस्वार और विसर्ग",
                    
                    # व्याकरण आधार
                    "संज्ञा", "सर्वनाम", "विशेषण", "क्रिया", "धातु", "प्रत्यय",
                    "उपसर्ग", "संधि परिचय", "समास परिचय",
                    
                    # श्लोक और मंत्र
                    "सरस्वती वंदना", "गायत्री मंत्र", "शांति मंत्र", "सरल श्लोक",
                    "संस्कृत गीत", "संस्कृत संख्या",
                    
                    # सरल गद्य
                    "सरल संस्कृत वाक्य", "दैनिक प्रयोग के शब्द", "परिवार के संबंध",
                    "रंग", "फल", "फूल", "पशु-पक्षी के नाम"
                ],
                
                7: [
                    # व्याकरण विस्तार
                    "संधि विधि", "स्वर संधि", "व्यंजन संधि", "विसर्ग संधि",
                    "समास के भेद", "तत्पुरुष", "द्वंद", "बहुव्रीहि", "अव्ययीभाव",
                    "धातु रूप", "भू", "कृ", "गम्", "पठ्", "हस्",
                    
                    # छंद शास्त्र
                    "अनुष्टुप छंद", "श्लोक की संरचना", "गुरु-लघु", "यति-गति",
                    
                    # गद्य पाठ
                    "कथा संग्रह", "हितोपदेश से कहानियाँ", "पंचतंत्र की कथाएँ",
                    "नीति श्लोक", "सुभाषित",
                    
                    # श्लोक संग्रह
                    "भगवद्गीता के श्लोक", "रामायण के श्लोक", "महाभारत के श्लोक",
                    "कालिदास के श्लोक"
                ],
                
                8: [
                    # उन्नत व्याकरण
                    "कारक प्रकरण", "आठ कारक", "विभक्ति प्रयोग", "संज्ञा रूप",
                    "राम शब्द", "हरि शब्द", "मति शब्द", "नदी शब्द",
                    "सर्वनाम रूप", "तत्", "यत्", "एतत्", "किम्",
                    
                ],
                6: [
                    # Health and Fitness
                    "Physical Fitness", "Components of Fitness", "Health-related Fitness",
                    "Skill-related Fitness", "Exercise and Health", "Benefits of Physical Activity",
                    
                    # Basic Movement Skills
                    "Fundamental Movement Skills", "Locomotor Skills", "Non-locomotor Skills",
                    "Manipulative Skills", "Body Awareness", "Spatial Awareness",
                    
                    # Games and Sports
                    "Introduction to Games", "Team Games", "Individual Games", "Traditional Games",
                    "Rules and Regulations", "Sportsmanship", "Fair Play",
                    
                    # Athletics
                    "Track Events", "Field Events", "Running", "Jumping", "Throwing",
                    "Athletic Meet", "Records and Measurements",
                    
                    # Gymnastics
                    "Basic Gymnastics", "Floor Exercises", "Balance", "Flexibility",
                    "Coordination", "Rhythmic Activities",
                    
                    # Health Education
                    "Personal Hygiene", "Nutrition", "First Aid", "Safety Measures",
                    "Common Injuries", "Prevention of Diseases"
                ],
                
                7: [
                    # Fitness Training
                    "Physical Fitness Training", "Strength Training", "Endurance Training",
                    "Flexibility Training", "Speed Training", "Training Principles",
                    
                    # Sports Skills
                    "Skill Development", "Motor Learning", "Practice Methods", "Technique Training",
                    "Performance Enhancement", "Skill Assessment",
                    
                    # Team Sports
                    "Football", "Basketball", "Volleyball", "Hockey", "Cricket",
                    "Handball", "Kabaddi", "Kho-Kho",
                    
                    # Individual Sports
                    "Badminton", "Table Tennis", "Tennis", "Swimming", "Athletics",
                    "Boxing", "Wrestling", "Martial Arts",
                    
                    # Yoga and Meditation
                    "Introduction to Yoga", "Asanas", "Pranayama", "Meditation",
                    "Benefits of Yoga", "Stress Management",
                    
                    # Sports Psychology
                    "Motivation", "Goal Setting", "Concentration", "Confidence Building",
                    "Stress and Anxiety", "Mental Preparation"
                ],
                
                8: [
                    # Advanced Fitness
                    "Advanced Training Methods", "Periodization", "Overload Principle",
                    "Recovery and Rest", "Fitness Testing", "Performance Evaluation",
                    
                    # Sports Biomechanics
                    "Movement Analysis", "Technique Improvement", "Efficiency of Movement",
                    "Force and Motion", "Leverage", "Projectile Motion",
                    
                    # Sports Medicine
                    "Sports Injuries", "Injury Prevention", "Treatment of Injuries",
                    "Rehabilitation", "Sports Massage", "Therapeutic Exercises",
                    
                    # Leadership and Coaching
                    "Leadership Skills", "Coaching Principles", "Teaching Methods",
                    "Communication Skills", "Team Management", "Official Rules",
                    
                    # Adventure Sports
                    "Outdoor Activities", "Trekking", "Camping", "Rock Climbing",
                    "Water Sports", "Safety in Adventure Sports",
                    
                    # Sports Management
                    "Organization of Sports Events", "Tournament Systems", "Sports Administration",
                    "Facilities and Equipment", "Budgeting", "Sponsorship"
                ],
                
                9: [
                    # Exercise Physiology
                    "Human Body Systems", "Muscular System", "Cardiovascular System",
                    "Respiratory System", "Energy Systems", "Fatigue and Recovery",
                    
                    # Training Methodology
                    "Training Plans", "Macrocycles", "Mesocycles", "Microcycles",
                    "Periodization Models", "Peak Performance", "Tapering",
                    
                    # Sports Nutrition
                    "Nutritional Requirements", "Pre-competition Nutrition", "During Competition",
                    "Post-competition Recovery", "Hydration Strategies", "Supplements",
                    
                    # Psychology of Sports
                    "Mental Training", "Visualization", "Relaxation Techniques", "Arousal Control",
                    "Attention and Concentration", "Team Dynamics", "Leadership",
                    
                    # Olympic Movement
                    "History of Olympics", "Olympic Values", "International Sports Organizations",
                    "Olympic Games", "Paralympic Games", "Commonwealth Games",
                    
                    # Career in Sports
                    "Professional Sports", "Sports Careers", "Sports Sciences", "Sports Journalism",
                    "Sports Marketing", "Sports Law", "Sports Technology"
                ],
                
                10: [
                    # Sports Science
                    "Exercise Physiology", "Biomechanics", "Sports Psychology", "Sports Nutrition",
                    "Sports Medicine", "Training Science", "Performance Analysis",
                    
                    # Research in Sports
                    "Research Methods", "Data Collection", "Statistical Analysis", "Research Design",
                    "Sports Technology", "Performance Measurement", "Innovation in Sports",
                    
                    # International Sports
                    "Global Sports Organizations", "International Competitions", "Sports Diplomacy",
                    "Cultural Exchange through Sports", "Sports and Peace", "Women in Sports",
                    
                    # Professional Development
                    "Coaching Certification", "Referee Training", "Sports Management Courses",
                    "Fitness Training Certification", "Sports Therapy", "Career Planning",
                    
                    # Ethics in Sports
                    "Fair Play", "Doping", "Sports Integrity", "Gender Equality", "Inclusion",
                    "Environmental Responsibility", "Social Responsibility of Sports",
                    
                    # Future of Sports
                    "Technology in Sports", "Virtual Reality", "Artificial Intelligence",
                    "E-sports", "Future Trends", "Innovation in Training", "Sustainable Sports"
                ]
            },
            
            # ISC Subjects (Grades 11-12)
            "Mathematics (ISC)": {
                11: [
                    # Sets and Functions
                    "Sets", "Subsets", "Union and Intersection", "Complement of Sets", "Venn Diagrams",
                    "Relations", "Types of Relations", "Functions", "Types of Functions",
                    "Composition of Functions", "Inverse of Functions",
                    
                    # Algebra
                    "Principle of Mathematical Induction", "Complex Numbers", "Quadratic Equations",
                    "Linear Inequalities", "Permutations and Combinations", "Binomial Theorem",
                    "Sequences and Series", "Arithmetic Progression", "Geometric Progression",
                    
                    # Coordinate Geometry
                    "Straight Lines", "Circle", "Parabola", "Ellipse", "Hyperbola",
                    "Introduction to Three-dimensional Geometry",
                    
                    # Calculus
                    "Limits and Derivatives", "Limits of Functions", "Derivatives",
                    "Applications of Derivatives",
                    
                    # Mathematical Reasoning
                    "Mathematical Reasoning", "Statements", "Logical Connectives",
                    "Implications", "Validating Statements",
                    
                    # Statistics and Probability
                    "Statistics", "Measures of Dispersion", "Probability", "Random Experiments",
                    "Events", "Probability of Events"
                ],
                
                12: [
                    # Relations and Functions
                    "Relations and Functions", "Types of Functions", "Composition of Functions",
                    "Invertible Functions", "Binary Operations",
                    
                    # Algebra
                    "Inverse Trigonometric Functions", "Matrices", "Determinants",
                    "Properties of Determinants", "Applications of Determinants and Matrices",
                    
                    # Calculus
                    "Continuity and Differentiability", "Applications of Derivatives",
                    "Integrals", "Applications of Integrals", "Differential Equations",
                    
                    # Vectors and 3D Geometry
                    "Vectors", "Scalar and Vector Products", "Three Dimensional Geometry",
                    
                    # Linear Programming
                    "Linear Programming", "Related Problems", "Mathematical Formulation",
                    "Graphical Method of Solution",
                    
                    # Probability
                    "Probability", "Conditional Probability", "Multiplication Theorem",
                    "Independence", "Bayes' Theorem", "Random Variables", "Bernoulli Trials",
                    "Binomial Distribution"
                ]
            },
            
            "Physics (ISC)": {
                11: [
                    # Physical World and Measurement
                    "Physical World", "Units and Measurements", "Dimensional Analysis",
                    "Significant Figures", "Error Analysis",
                    
                    # Kinematics
                    "Motion in a Straight Line", "Motion in a Plane", "Projectile Motion",
                    "Uniform Circular Motion",
                    
                    # Laws of Motion
                    "Newton's Laws of Motion", "Law of Conservation of Momentum",
                    "Equilibrium of Concurrent Forces", "Static and Kinetic Friction",
                    "Dynamics of Uniform Circular Motion", "Centripetal Force",
                    
                    # Work, Energy and Power
                    "Work", "Energy", "Power", "Collision", "Centre of Mass",
                    
                    # Motion of System of Particles and Rigid Body
                    "Centre of Mass", "Motion of Centre of Mass", "Linear Momentum",
                    "Angular Momentum", "Equilibrium of Rigid Bodies", "Moment of Inertia",
                    "Theorems of Perpendicular and Parallel Axes", "Kinematics of Rotational Motion",
                    
                    # Gravitation
                    "Kepler's Laws", "Universal Law of Gravitation", "Acceleration due to Gravity",
                    "Gravitational Potential Energy", "Escape Velocity", "Satellite Motion",
                    
                    # Properties of Bulk Matter
                    "Mechanical Properties of Solids", "Mechanical Properties of Fluids",
                    "Thermal Properties of Matter",
                    
                    # Thermodynamics
                    "Thermal Equilibrium", "Zeroth Law of Thermodynamics", "Heat, Work and Internal Energy",
                    "First Law of Thermodynamics", "Second Law of Thermodynamics",
                    "Reversible and Irreversible Processes", "Carnot Engine",
                    
                    # Behaviour of Perfect Gas and Kinetic Theory
                    "Equation of State of Perfect Gas", "Work Done by Compressed Gas",
                    "Kinetic Theory of Gases", "Law of Equipartition of Energy",
                    "Mean Free Path",
                    
                    # Oscillations and Waves
                    "Periodic Motion", "Simple Harmonic Motion", "Oscillations of Spring",
                    "Simple Pendulum", "Forced Oscillations and Resonance", "Wave Motion",
                    "Longitudinal and Transverse Waves", "Superposition of Waves",
                    "Progressive and Stationary Waves", "Beats", "Doppler Effect"
                ],
                
                12: [
                    # Electric Charges and Fields
                    "Electric Charges", "Conservation of Charge", "Coulomb's Law",
                    "Electric Field", "Electric Field Lines", "Electric Flux", "Gauss's Law",
                    
                    # Electrostatic Potential and Capacitance
                    "Electric Potential", "Potential Difference", "Electric Potential due to Point Charge",
                    "Equipotential Surfaces", "Potential Energy", "Conductors and Insulators",
                    "Dielectrics", "Capacitors", "Combination of Capacitors",
                    
                    # Current Electricity
                    "Electric Current", "Flow of Electric Charges", "Ohm's Law",
                    "Resistance and Resistivity", "Combination of Resistors", "Temperature Dependence",
                    "Internal Resistance", "Potentiometer", "Wheatstone Bridge",
                    
                    # Moving Charges and Magnetism
                    "Concept of Magnetic Field", "Oersted's Experiment", "Biot-Savart Law",
                    "Ampere's Law", "Magnetic Dipole", "Force on Moving Charge", "Cyclotron",
                    
                    # Magnetism and Matter
                    "Current Loop as Magnetic Dipole", "Bar Magnet", "Magnetism and Gauss's Law",
                    "Earth's Magnetism", "Magnetic Materials",
                    
                    # Electromagnetic Induction
                    "Electromagnetic Induction", "Faraday's Laws", "Induced EMF and Current",
                    "Lenz's Law", "Eddy Currents", "Self and Mutual Induction",
                    
                    # Alternating Current
                    "AC Voltage Applied to Resistor", "Inductor", "Capacitor",
                    "LCR Series Circuit", "Power in AC Circuit", "LC Oscillations", "Transformers",
                    
                    # Electromagnetic Waves
                    "Basic Idea of Displacement Current", "Electromagnetic Waves",
                    "Electromagnetic Spectrum",
                    
                    # Ray Optics and Optical Instruments
                    "Ray Optics", "Reflection of Light", "Spherical Mirrors", "Refraction",
                    "Total Internal Reflection", "Refraction at Spherical Surfaces", "Lenses",
                    "Refraction through Prism", "Scattering of Light", "Optical Instruments",
                    
                    # Wave Optics
                    "Huygens Principle", "Interference", "Young's Double Slit Experiment",
                    "Diffraction", "Polarisation",
                    
                    # Dual Nature of Radiation and Matter
                    "Dual Nature of Radiation", "Photoelectric Effect", "Einstein's Equation",
                    "Particle Nature of Light", "Wave Nature of Matter", "Davisson and Germer Experiment",
                    
                    # Atoms and Nuclei
                    "Alpha-particle Scattering Experiment", "Rutherford's Model of Atom",
                    "Bohr Model", "Hydrogen Spectrum", "Composition and Size of Nucleus",
                    "Atomic Masses", "Radioactivity", "Nuclear Fission and Fusion",
                    
                    # Electronic Devices
                    "Energy Bands in Conductors", "Semiconductors and Insulators",
                    "Semiconductor Diode", "I-V Characteristics", "Diode as Rectifier",
                    "Special Purpose p-n Junction Diodes", "Junction Transistor",
                    "Digital Electronics and Logic Gates"
                ]
            },
            
            "Chemistry (ISC)": {
                11: [
                    # Some Basic Concepts of Chemistry
                    "General Introduction", "Laws of Chemical Combination", "Dalton's Atomic Theory",
                    "Atomic and Molecular Masses", "Mole Concept", "Stoichiometry",
                    
                    # Structure of Atom
                    "Sub-atomic Particles", "Atomic Models", "Quantum Mechanical Model",
                    "Quantum Numbers", "Aufbau Principle", "Electronic Configuration",
                    
                    # Classification of Elements and Periodicity
                    "Modern Periodic Law", "Present Form of Periodic Table", "Periodic Trends",
                    "Ionization Enthalpy", "Electron Gain Enthalpy", "Electronegativity", "Valency",
                    
                    # Chemical Bonding and Molecular Structure
                    "Kossel-Lewis Approach", "Ionic Bonding", "Bond Parameters", "Lewis Structure",
                    "Polar Character of Covalent Bond", "Covalent Character of Ionic Bond",
                    "Valence Bond Theory", "Hybridisation", "Molecular Orbital Theory",
                    "Bonding in Some Homonuclear Diatomic Molecules", "Hydrogen Bonding",
                    
                    # States of Matter
                    "Intermolecular Forces", "Thermal Energy", "Intermolecular Forces vs Thermal Interactions",
                    "The Gaseous State", "The Gas Laws", "Ideal Gas Equation", "Graham's Law of Diffusion",
                    "Dalton's Law of Partial Pressures", "Kinetic Molecular Theory of Gases",
                    "Behaviour of Real Gases", "Liquefaction of Gases", "Liquid State",
                    
                    # Chemical Thermodynamics
                    "Thermodynamic Terms", "The Zeroth Law of Thermodynamics", "The First Law of Thermodynamics",
                    "Internal Energy", "Enthalpy", "Heat Capacity", "Measurement of ΔU and ΔH",
                    "Hess's Law of Constant Heat Summation", "Enthalpies for Different Types of Reactions",
                    "Spontaneity", "Gibbs Energy Change and Equilibrium", "Second Law of Thermodynamics",
                    "Third Law of Thermodynamics",
                    
                    # Equilibrium
                    "Equilibrium in Physical Processes", "Equilibrium in Chemical Processes",
                    "Law of Chemical Equilibrium", "Equilibrium Constant", "Homogeneous Equilibria",
                    "Heterogeneous Equilibria", "Applications of Equilibrium Constants",
                    "Relationship between Equilibrium Constant K, Reaction Quotient Q and Gibbs Energy G",
                    "Factors Affecting Equilibria", "Ionic Equilibrium in Solution", "Acids, Bases and Salts",
                    "Ionization of Acids and Bases", "Buffer Solutions", "Solubility Equilibria",
                    
                    # Redox Reactions
                    "Classical Idea of Redox Reactions", "Redox Reactions in Terms of Electron Transfer",
                    "Oxidation Number", "Types of Redox Reactions", "Balancing of Redox Reactions",
                    "Redox Reactions as the Basis for Titrations",
                    
                    # Hydrogen
                    "Position of Hydrogen in Periodic Table", "Occurrence", "Isotopes",
                    "Preparation", "Properties", "Hydrides", "Water", "Hydrogen Peroxide",
                    "Heavy Water", "Hydrogen as a Fuel",
                    
                    # The s-Block Elements
                    "Group 1 Elements: Alkali Metals", "General Characteristics", "Occurrence",
                    "Anomalous Properties of Lithium", "Some Important Compounds of Sodium",
                    "Biological Importance of Sodium and Potassium", "Group 2 Elements: Alkaline Earth Metals",
                    "General Characteristics", "Anomalous Behaviour of Beryllium",
                    "Some Important Compounds of Calcium", "Biological Importance of Magnesium and Calcium",
                    
                    # Some p-Block Elements
                    "Group 13 Elements: The Boron Family", "Group 14 Elements: The Carbon Family",
                    
                    # Organic Chemistry - Some Basic Principles and Techniques
                    "General Introduction", "Tetravalence of Carbon", "Structural Representations",
                    "Classification of Organic Compounds", "Nomenclature", "Isomerism",
                    "Fundamental Concepts in Organic Reaction Mechanism", "Methods of Purification",
                    "Qualitative Analysis", "Quantitative Analysis",
                    
                    # Hydrocarbons
                    "Classification", "Aliphatic Hydrocarbons", "Alkanes", "Alkenes", "Alkynes",
                    "Aromatic Hydrocarbons", "Carcinogenicity and Toxicity"
                ],
                
                12: [
                    # Solid State
                    "General Characteristics of Solid State", "Amorphous and Crystalline Solids",
                    "Classification of Crystalline Solids", "Crystal Lattices and Unit Cells",
                    "Number of Atoms in a Unit Cell", "Close Packed Structures", "Packing Efficiency",
                    "Calculations Involving Unit Cell Dimensions", "Imperfections in Solids", "Electrical Properties",
                    "Magnetic Properties",
                    
                    # Solutions
                    "Types of Solutions", "Expressing Concentration of Solutions", "Solubility",
                    "Vapour Pressure of Liquid Solutions", "Raoult's Law", "Colligative Properties",
                    "Relative Molecular Masses of Non-volatile Substances", "Abnormal Molecular Masses",
                    
                    # Electrochemistry
                    "Electrochemical Cells", "Galvanic Cells", "Nernst Equation", "Conductance in Electrolytic Solutions",
                    "Electrolytic Cells and Electrolysis", "Batteries", "Fuel Cells", "Corrosion",
                    
                    # Chemical Kinetics
                    "Rate of a Chemical Reaction", "Factors Influencing Rate of a Reaction",
                    "Integrated Rate Equations", "Pseudo First Order Reaction", "Temperature Dependence",
                    "Collision Theory of Chemical Reactions",
                    
                    # Surface Chemistry
                    "Adsorption", "Catalysis", "Colloids",
                    
                    # General Principles and Processes of Isolation of Elements
                    "Occurrence of Metals", "Concentration of Ores", "Extraction of Crude Metal",
                    "Thermodynamic Principles of Metallurgy", "Electrochemical Principles", "Oxidation & Reduction",
                    "Refining", "Uses of Aluminium, Copper, Zinc and Iron",
                    
                    # The p-Block Elements
                    "Group 15 Elements", "Group 16 Elements", "Group 17 Elements", "Group 18 Elements",
                    
                    # The d and f Block Elements
                    "General Introduction", "Electronic Configuration", "Occurrence and Characteristics",
                    "General Trends", "Oxidation States", "Magnetic Properties", "Catalytic Properties",
                    "Applications", "Preparation and Properties of K2Cr2O7 and KMnO4",
                    "Lanthanoids", "Actinoids",
                    
                    # Coordination Compounds
                    "Introduction", "Ligands", "Coordination Number", "Colour", "Magnetic Properties and Shapes",
                    "IUPAC Nomenclature", "Isomerism", "Bonding", "Werner's Theory", "VBT", "CFT",
                    "Importance of Coordination Compounds",
                    
                    # Haloalkanes and Haloarenes
                    "Classification", "Nomenclature", "Nature of C-X Bond", "Physical Properties",
                    "Chemical Reactions", "Polyhalogen Compounds",
                    
                    # Alcohols, Phenols and Ethers
                    "Classification", "Nomenclature", "Structures of Functional Groups", "Physical Properties",
                    "Chemical Reactions", "Uses",
                    
                    # Aldehydes, Ketones and Carboxylic Acids
                    "Classification", "Nomenclature", "Nature of Carbonyl Group", "Physical Properties",
                    "Chemical Reactions", "Uses",
                    
                    # Organic Compounds Containing Nitrogen
                    "Classification", "Structure", "Nomenclature", "Preparation", "Physical Properties",
                    "Chemical Reactions", "Uses", "Identification",
                    
                    # Biomolecules
                    "Carbohydrates", "Proteins", "Vitamins", "Nucleic Acids",
                    
                    # Polymers
                    "Classification", "Terms Related to Polymers", "Types of Polymerisation Reactions",
                    "Molecular Mass", "Biodegradable and Non-biodegradable Polymers",
                    
                    # Chemistry in Everyday Life
                    "Drugs and their Classification", "Drug-Target Interaction", "Therapeutic Action",
                    "Chemicals in Food", "Cleansing Agents"
                ]
            },
            
            "Biology (ISC)": {
                11: [
                    # Diversity in the Living World
                    "What is Living", "Biodiversity", "Need for Classification", "Three Domains of Life",
                    "Taxonomy and Systematics", "Concept of Species and Taxonomical Hierarchy",
                    "Binomial Nomenclature", "Tools for Study of Taxonomy", "Museums", "Zoological Parks",
                    "Herbaria", "Botanical Gardens",
                    
                    # Structural Organisation in Animals and Plants
                    "Animal Tissues", "Morphology and Modifications", "Anatomy of Flowering Plants",
                    "Structural Organisation of Animals",
                    
                    # Cell Structure and Function
                    "Cell Theory and Cell as the Basic Unit of Life", "Structure of Prokaryotic and Eukaryotic Cells",
                    "Plant Cell and Animal Cell", "Cell Envelope", "Cell Membrane", "Cell Wall",
                    "Cell Organelles", "Nucleus", "Chromosome", "Microbodies", "Cytoskeleton",
                    "Cilia", "Flagella", "Centrosome", "Ribosome", "Endoplasmic Reticulum",
                    
                    # Plant Physiology
                    "Transport in Plants", "Mineral Nutrition", "Photosynthesis in Higher Plants",
                    "Respiration in Plants", "Plant Growth and Development",
                    
                    # Human Physiology
                    "Digestion and Absorption", "Breathing and Exchange of Gases", "Body Fluids and Circulation",
                    "Excretory Products and their Elimination", "Locomotion and Movement",
                    "Neural Control and Coordination", "Chemical Coordination and Integration"
                ],
                
                12: [
                    # Reproduction
                    "Reproduction in Organisms", "Sexual Reproduction in Flowering Plants",
                    "Human Reproduction", "Reproductive Health",
                    
                    # Genetics and Evolution
                    "Heredity and Variation", "Molecular Basis of Inheritance", "Evolution",
                    
                    # Biology and Human Welfare
                    "Human Health and Disease", "Strategies for Enhancement in Food Production",
                    "Microbes in Human Welfare",
                    
                    # Biotechnology and its Applications
                    "Biotechnology: Principles and Processes", "Biotechnology and its Applications",
                    
                    # Ecology and Environment
                    "Organisms and Populations", "Ecosystem", "Biodiversity and Conservation",
                    "Environmental Issues"
                ]
            },
            
            "English (ISC)": {
                11: [
                    # Literature in English Paper 1
                    "Poetry", "Prose", "Drama", "Fiction", "Literary Appreciation",
                    "Critical Analysis", "Contextual Questions", "Character Analysis",
                    "Theme Study", "Literary Devices", "Historical Context",
                    
                    # Language Paper 2
                    "Reading Comprehension", "Writing Skills", "Grammar and Usage",
                    "Vocabulary", "Composition", "Creative Writing", "Functional Writing",
                    "Formal and Informal Writing", "Report Writing", "Article Writing",
                    "Speech Writing", "Debate Writing"
                ],
                
                12: [
                    # Literature in English Paper 1
                    "Prescribed Texts", "Poetry Analysis", "Prose Appreciation", "Drama Study",
                    "Novel Study", "Short Stories", "Essays", "Comparative Literature",
                    "Critical Essays", "Literary Criticism", "Evaluation and Assessment",
                    
                    # Language Paper 2
                    "Advanced Composition", "Directed Writing", "Argumentative Writing",
                    "Discursive Writing", "Narrative Writing", "Descriptive Writing",
                    "Critical Writing", "Commercial Correspondence", "Official Correspondence",
                    "Media Writing", "Digital Communication"
                ]
            },
            
            "Economics (ISC)": {
                11: [
                    # Introduction to Economics
                    "What is Economics", "Microeconomics and Macroeconomics", "Central Problems of an Economy",
                    "Economic Systems", "Production Possibility Frontier",
                    
                    # Theory of Consumer Behaviour
                    "Consumer's Equilibrium", "Utility Analysis", "Indifference Curve Analysis",
                    "Price Effect", "Income Effect", "Substitution Effect", "Demand",
                    "Law of Demand", "Elasticity of Demand",
                    
                    # Producer Behaviour and Supply
                    "Production Function", "Short Run and Long Run", "Law of Variable Proportions",
                    "Returns to Scale", "Cost", "Revenue", "Producer's Equilibrium", "Supply",
                    
                    # Forms of Market and Price Determination
                    "Perfect Competition", "Monopoly", "Monopolistic Competition", "Oligopoly",
                    "Price Determination in Different Markets"
                ],
                
                12: [
                    # Introductory Macroeconomics
                    "National Income", "Money and Banking", "Income Determination",
                    "Government Budget and the Economy", "Balance of Payments",
                    
                    # Indian Economic Development
                    "Development Experience", "Independence", "Economic Reforms Since 1991",
                    "Current Challenges Facing Indian Economy", "Development Experience of India"
                ]
            },
            
            "Business Studies (ISC)": {
                11: [
                    # Nature and Significance of Management
                    "Concept of Management", "Objectives of Management", "Importance of Management",
                    "Nature of Management", "Management as Science, Art and Profession",
                    "Levels of Management", "Functions of Management",
                    
                    # Principles of Management
                    "Principles of Management", "Fayol's Principles", "Taylor's Principles",
                    "Scientific Management",
                    
                    # Business Environment
                    "Concept of Business Environment", "Importance of Business Environment",
                    "Dimensions of Business Environment", "Economic Environment", "Political Environment",
                    "Social Environment", "Technological Environment", "Legal Environment",
                    
                    # Planning
                    "Concept of Planning", "Importance of Planning", "Limitations of Planning",
                    "Planning Process", "Types of Plans",
                    
                    # Organising
                    "Concept of Organisation", "Importance of Organising", "Organising Process",
                    "Structure of Organisation", "Formal and Informal Organisation", "Delegation",
                    "Decentralisation",
                    
                    # Staffing
                    "Concept of Staffing", "Importance of Staffing", "Staffing Process",
                    "Recruitment", "Selection", "Training and Development",
                    
                    # Directing
                    "Concept of Directing", "Importance of Directing", "Elements of Directing",
                    "Supervision", "Motivation", "Leadership", "Communication",
                    
                    # Controlling
                    "Concept of Controlling", "Importance of Controlling", "Limitations of Controlling",
                    "Controlling Process", "Techniques of Controlling"
                ],
                
                12: [
                    # Financial Management
                    "What is Financial Management", "Role of Financial Management", "Objectives of Financial Management",
                    "Financial Decisions", "Financial Planning", "Capital Structure", "Fixed and Working Capital",
                    
                    # Marketing Management
                    "What is Marketing", "Marketing Management Philosophies", "Functions of Marketing",
                    "Marketing Mix", "Product", "Price", "Place", "Promotion",
                    
                    # Consumer Protection
                    "Why Consumer Protection", "Ways and Means of Consumer Protection",
                    "Consumer Protection Act", "Role of Consumer Organisations and NGOs"
                ]
            }
        },
          
        
        "Cambridge IGCSE": {
            # MATHEMATICS - Based on official Cambridge IGCSE 0580 syllabus (2025-2027)
            "Mathematics": {
                1: [
                    # Cambridge Primary Stage 1 Mathematics - Complete Topics
                    "Numbers 0-20", "Counting forwards and backwards", "Number recognition", "Number formation", 
                    "Ordinal numbers (1st, 2nd, 3rd)", "Number bonds to 10", "Addition within 10", "Subtraction within 10",
                    "2D shapes (circle, triangle, square, rectangle)", "3D shapes (cube, sphere, cylinder)", 
                    "Shape properties", "Patterns and sequences", "Continue simple patterns", "Create patterns",
                    "Length (longer, shorter, same)", "Mass (heavier, lighter)", "Capacity (more, less, same)",
                    "Position and direction (left, right, up, down)", "Time (day, night, before, after)",
                    "Days of the week", "Money (coins recognition)", "Sorting and classifying"
                ],
                2: [
                    # Cambridge Primary Stage 2 Mathematics - Complete Topics
                    "Numbers 0-100", "Place value (tens and ones)", "Comparing numbers", "Ordering numbers",
                    "Number line", "Rounding to nearest 10", "Addition within 20", "Subtraction within 20",
                    "Addition with regrouping", "Subtraction with regrouping", "Multiplication tables (2, 5, 10)",
                    "Division by 2, 5, 10", "Repeated addition", "Arrays", "Fractions (halves, quarters, thirds)",
                    "Equivalent fractions", "2D shapes and properties", "3D shapes and properties", "Symmetry",
                    "Right angles", "Measurement units", "Length in cm and m", "Mass in g and kg", 
                    "Capacity in ml and l", "Time (hours, minutes, seconds)", "Digital and analog clocks",
                    "Money calculations", "Data handling", "Pictographs", "Bar charts", "Tally charts"
                ],
                3: [
                    # Cambridge Primary Stage 3 Mathematics - Complete Topics
                    "Numbers 0-1000", "Place value (hundreds, tens, ones)", "Negative numbers", "Roman numerals",
                    "Addition and subtraction (3-digit numbers)", "Mental calculation strategies", "Written methods",
                    "Multiplication tables (2, 3, 4, 5, 6, 8, 10)", "Division facts", "Multiplication by 10 and 100",
                    "Fractions (unit and non-unit)", "Equivalent fractions", "Adding fractions", "Decimal tenths",
                    "Properties of shapes", "Angles (right, acute, obtuse)", "Perpendicular and parallel lines",
                    "Perimeter", "Area by counting", "Measurement conversions", "Time calculations", "24-hour clock",
                    "Data interpretation", "Frequency tables", "Line graphs"
                ],
                4: [
                    # Cambridge Primary Stage 4 Mathematics - Complete Topics
                    "Numbers to 10,000", "Roman numerals to 100", "Rounding to nearest 10, 100, 1000",
                    "Addition and subtraction (4-digit numbers)", "Multiplication (2-digit by 1-digit)",
                    "Division with remainders", "Factors and multiples", "Prime numbers", "Square numbers",
                    "Fractions (proper, improper, mixed)", "Decimal equivalents", "Hundredths", "Percentages",
                    "Classification of triangles", "Quadrilaterals", "Lines of symmetry", "Coordinate grids",
                    "Translation", "Area and perimeter", "Volume", "Time problems", "Money problems",
                    "Statistics and graphs", "Mean average", "Mode"
                ],
                5: [
                    # Cambridge Primary Stage 5 Mathematics - Complete Topics
                    "Numbers to 1,000,000", "Place value", "Negative numbers", "Rounding", "Order of operations",
                    "Addition and subtraction", "Multiplication (4-digit by 2-digit)", "Long division",
                    "Prime factors", "Common factors and multiples", "Fractions (all operations)",
                    "Decimals to 3 places", "Percentages", "Ratio and proportion", "Properties of shapes",
                    "Angles in triangles and quadrilaterals", "Reflection and rotation", "Scale drawings",
                    "Converting units", "Area of rectangles", "Volume of cuboids", "Statistics", "Line graphs",
                    "Pie charts", "Probability"
                ],
                6: [
                    # Cambridge Lower Secondary Stage 6 Mathematics - Complete Topics
                    "Integers", "Powers and roots", "Factors and multiples", "Fractions, decimals, percentages",
                    "Approximation and estimation", "Algebraic notation", "Algebraic manipulation", "Simple equations",
                    "Coordinates", "Linear graphs", "Angles", "Triangles and quadrilaterals", "Circle facts",
                    "Area and perimeter", "Volume and surface area", "Data collection and presentation",
                    "Averages", "Probability"
                ],
                7: [
                    # Cambridge Lower Secondary Stage 7 Mathematics - Complete Topics
                    "Directed numbers", "Indices", "Standard form", "Fractions and decimals", "Percentages",
                    "Ratio and proportion", "Algebraic expressions", "Equations and inequalities", "Sequences",
                    "Coordinate geometry", "Functions and graphs", "Geometric reasoning", "Pythagoras' theorem",
                    "Mensuration", "Transformations", "Statistical representation", "Probability"
                ],
                8: [
                    # Cambridge Lower Secondary Stage 8 Mathematics - Complete Topics
                    "Number concepts", "Calculations", "Solving numerical problems", "Expressions and formulae",
                    "Equations, inequalities and sequences", "Graphs", "Geometric reasoning", "Mensuration",
                    "Sets", "Probability", "Statistics"
                ],
                9: [
                    # Cambridge IGCSE Mathematics 0580 Core Topics (Detailed)
                    "Types of number", "Sets", "Powers and roots", "Fractions, decimals and percentages",
                    "Ordering", "The four operations", "Indices I", "Standard form", "Estimation",
                    "Limits of accuracy", "Ratio and proportion", "Rates", "Percentages", "Using a calculator",
                    "Time", "Money", "Introduction to algebra", "Algebraic manipulation", "Indices II",
                    "Equations", "Inequalities", "Sequences", "Graphs in practical situations", "Graphs of functions",
                    "Sketching curves", "Coordinates", "Drawing linear graphs", "Gradient of linear graphs",
                    "Equations of linear graphs", "Parallel lines", "Geometrical terms", "Geometrical constructions",
                    "Scale drawings", "Similarity", "Symmetry", "Angles", "Circle theorems", "Units of measure",
                    "Area and perimeter", "Circles, arcs and sectors", "Surface area and volume",
                    "Compound shapes and parts of shapes", "Pythagoras' theorem", "Right-angled triangles",
                    "Transformations", "Introduction to probability", "Relative and expected frequencies",
                    "Probability of combined events", "Classifying statistical data", "Interpreting statistical data",
                    "Averages and range", "Statistical charts and diagrams", "Scatter diagrams"
                ],
                10: [
                    # Cambridge IGCSE Mathematics 0580 Extended Topics (Detailed)
                    "Types of number", "Sets", "Powers and roots", "Fractions, decimals and percentages",
                    "Ordering", "The four operations", "Indices I", "Standard form", "Estimation",
                    "Limits of accuracy", "Ratio and proportion", "Rates", "Percentages", "Using a calculator",
                    "Time", "Money", "Exponential growth and decay", "Surds", "Introduction to algebra",
                    "Algebraic manipulation", "Algebraic fractions", "Indices II", "Equations", "Inequalities",
                    "Sequences", "Proportion", "Graphs in practical situations", "Graphs of functions",
                    "Sketching curves", "Differentiation", "Functions", "Coordinates", "Drawing linear graphs",
                    "Gradient of linear graphs", "Length and midpoint", "Equations of linear graphs",
                    "Parallel lines", "Perpendicular lines", "Geometrical terms", "Geometrical constructions",
                    "Scale drawings", "Similarity", "Symmetry", "Angles", "Circle theorems I", "Circle theorems II",
                    "Units of measure", "Area and perimeter", "Circles, arcs and sectors", "Surface area and volume",
                    "Compound shapes and parts of shapes", "Pythagoras' theorem", "Right-angled triangles",
                    "Exact trigonometric values", "Trigonometric functions", "Non-right-angled triangles",
                    "Pythagoras' theorem and trigonometry in 3D", "Transformations", "Vectors in two dimensions",
                    "Magnitude of a vector", "Vector geometry", "Introduction to probability",
                    "Relative and expected frequencies", "Probability of combined events", "Conditional probability",
                    "Classifying statistical data", "Interpreting statistical data", "Averages and measures of spread",
                    "Statistical charts and diagrams", "Scatter diagrams", "Cumulative frequency diagrams", "Histograms"
                ],
                11: [
                    # Cambridge Advanced Mathematics (AS Level)
                    "Pure Mathematics 1", "Quadratics", "Functions", "Coordinate geometry", 
                    "Circular measure", "Trigonometry", "Permutations and combinations", 
                    "Binomial expansion", "Sequences and series", "Differentiation", "Integration",
                    "Statistics 1", "Mechanics 1"
                ],
                12: [
                    # Cambridge Advanced Mathematics (A Level)
                    "Pure Mathematics 1", "Pure Mathematics 2", "Pure Mathematics 3", 
                    "Further Pure Mathematics", "Statistics", "Mechanics", "Decision Mathematics"
                ]
            },

            # PHYSICS - Based on Cambridge IGCSE 0625 syllabus
            "Physics": {
                1: [
                    "Light and dark", "Sound and hearing", "Forces and movement", "Materials", 
                    "Hot and cold", "Living things and non-living things"
                ],
                2: [
                    "Light sources", "Sounds around us", "Push and pull", "Different materials", 
                    "Hot and cold things", "Magnets"
                ],
                3: [
                    "Light and shadows", "How sounds are made", "Forces and motion", 
                    "Properties of materials", "Heat and temperature", "Simple machines"
                ],
                4: [
                    "Light travels", "Sound travels", "Forces", "States of matter", 
                    "Changes of state", "Simple circuits"
                ],
                5: [
                    "How we see", "How we hear", "Gravity and weight", "Solids, liquids and gases", 
                    "Heating and cooling", "Electrical circuits"
                ],
                6: [
                    "General physics", "Thermal physics", "Properties of waves, including light and sound", 
                    "Electricity and magnetism"
                ],
                7: [
                    "General physics", "Thermal physics", "Properties of waves, including light and sound", 
                    "Electricity and magnetism", "Atomic physics"
                ],
                8: [
                    "General physics", "Thermal physics", "Properties of waves, including light and sound", 
                    "Electricity and magnetism", "Atomic physics"
                ],
                9: [
                    # Cambridge IGCSE Physics 0625 Core Topics
                    "Motion, forces and energy", "Thermal physics", "Waves", "Electricity and magnetism", 
                    "Atomic physics", "Length and time", "Motion", "Mass and weight", "Density", 
                    "Forces", "Momentum", "Energy, work and power", "Pressure"
                ],
                10: [
                    # Cambridge IGCSE Physics 0625 Extended Topics
                    "Motion, forces and energy", "Thermal physics", "Waves", "Electricity and magnetism", 
                    "Atomic physics", "Space physics", "Kinetic particle theory", "Transfer of thermal energy", 
                    "Temperature", "Thermal properties of materials", "General wave properties", 
                    "Light", "Sound", "Electromagnetic spectrum", "Static electricity", "Current electricity", 
                    "Electric circuits", "Magnetism", "Electromagnetic induction", "The nuclear atom", 
                    "Radioactivity", "Earth and the Solar System", "Stars and the Universe"
                ],
                11: [
                    # Cambridge International AS Level Physics
                    "Physical quantities and units", "Kinematics", "Dynamics", "Forces, density and pressure", 
                    "Work, energy and power", "Deformation of solids", "Waves", "Superposition", 
                    "Electricity", "D.C. circuits", "Particle physics"
                ],
                12: [
                    # Cambridge International A Level Physics
                    "Further mechanics", "Gravitational fields", "Deformation of solids", "Oscillations", 
                    "Thermal physics", "Ideal gases", "Molecular kinetic theory", "Capacitors", 
                    "Electric fields", "Magnetism", "Electromagnetic induction", "Alternating currents", 
                    "Quantum physics", "Nuclear physics", "Medical physics", "Astronomy and cosmology"
                ]
            },

            # CHEMISTRY - Based on Cambridge IGCSE 0620 syllabus
            "Chemistry": {
                1: [
                    "Different materials", "Properties of materials", "Changing materials", 
                    "Mixing and separating", "Hot and cold"
                ],
                2: [
                    "Grouping materials", "Changing materials", "Reversible and irreversible changes", 
                    "Heating and cooling", "Dissolving"
                ],
                3: [
                    "Solids, liquids and gases", "Material properties", "Chemical changes", 
                    "Physical changes", "Solutions and mixtures"
                ],
                4: [
                    "States of matter", "Properties and changes of materials", "Rocks and soils", 
                    "Separating mixtures", "Irreversible changes"
                ],
                5: [
                    "Properties and changes of materials", "States of matter", "Mixtures and solutions", 
                    "Chemical reactions", "Acids and alkalis"
                ],
                6: [
                    "Properties and structure of matter", "Chemistry of our environment", 
                    "Patterns and properties of metals", "Chemical reactions"
                ],
                7: [
                    "Properties and structure of matter", "Chemistry of our environment", 
                    "Patterns and properties of metals", "Chemical reactions"
                ],
                8: [
                    "Properties and structure of matter", "Chemistry of our environment", 
                    "Patterns and properties of metals", "Chemical reactions"
                ],
                9: [
                    # Cambridge IGCSE Chemistry 0620 Core Topics
                    "States of matter", "Atoms, elements and compounds", "Stoichiometry", 
                    "Electrochemistry", "Chemical energetics", "Chemical reactions", 
                    "Acids, bases and salts", "The Periodic Table", "Metals", "Chemistry of the environment", 
                    "Organic chemistry", "Experimental techniques"
                ],
                10: [
                    # Cambridge IGCSE Chemistry 0620 Extended Topics
                    "The particulate nature of matter", "Experimental techniques", "Atoms, elements and compounds", 
                    "Stoichiometry", "Electricity and chemistry", "Chemical energetics", "Chemical reactions", 
                    "Acids, bases and salts", "The Periodic Table", "Metals", "Air and water", 
                    "Sulfur", "Carbonates", "Organic chemistry", "Polymers"
                ],
                11: [
                    # Cambridge International AS Level Chemistry
                    "Atomic structure", "Chemical bonding", "States of matter", "Chemical energetics", 
                    "Electrochemistry", "Equilibria", "Reaction kinetics", "The Periodic Table", 
                    "Group chemistry", "Introduction to organic chemistry", "Polymerisation"
                ],
                12: [
                    # Cambridge International A Level Chemistry
                    "Atomic structure", "Chemical bonding", "States of matter", "Chemical energetics", 
                    "Electrochemistry", "Equilibria", "Reaction kinetics", "The Periodic Table", 
                    "Nitrogen and sulfur", "Introduction to organic chemistry", "Hydrocarbons", 
                    "Halogen derivatives", "Hydroxy compounds", "Carbonyl compounds", 
                    "Carboxylic acids and derivatives", "Nitrogen compounds", "Polymerisation", 
                    "Analytical techniques", "Organic synthesis"
                ]
            },

            # BIOLOGY - Based on Cambridge IGCSE 0610 syllabus (Complete Detailed Topics)
            "Biology": {
                1: [
                    # Cambridge Primary Stage 1 Biology/Science
                    "Living and non-living things", "Characteristics of living things", "Basic needs of living things",
                    "Parts of the human body", "Five senses", "Animals and their babies", "Animal homes",
                    "Plant parts (roots, stem, leaves, flowers)", "What plants need to grow", "Seasonal changes",
                    "Day and night", "Weather patterns", "Healthy eating", "Exercise and rest"
                ],
                2: [
                    # Cambridge Primary Stage 2 Biology/Science
                    "Life processes", "Growth and development", "Human body systems (basic)", "Senses and safety",
                    "Animal groups", "Animal needs", "Life cycles (butterflies, frogs)", "Plant growth",
                    "Seeds and germination", "Habitats", "Food chains (simple)", "Adaptation", "Materials from living things",
                    "Keeping healthy", "Medicine and doctors"
                ],
                3: [
                    # Cambridge Primary Stage 3 Biology/Science
                    "Classification of living things", "Vertebrates and invertebrates", "Plant and animal cells (basic)",
                    "Human skeleton and muscles", "Digestive system (basic)", "Teeth and dental health",
                    "Breathing and lungs", "Heart and circulation (basic)", "Reproduction in plants",
                    "Pollination and seed dispersal", "Life cycles", "Ecosystems", "Food webs", "Environmental changes",
                    "Nutrition and balanced diet"
                ],
                4: [
                    # Cambridge Primary Stage 4 Biology/Science
                    "Cell structure and function", "Organ systems", "Circulatory system", "Respiratory system",
                    "Skeletal and muscular systems", "Nervous system (basic)", "Digestive system", "Plant structure",
                    "Photosynthesis (introduction)", "Plant reproduction", "Animal reproduction", "Genetics (basic)",
                    "Evolution and adaptation", "Biodiversity", "Conservation", "Human impact on environment"
                ],
                5: [
                    # Cambridge Primary Stage 5 Biology/Science
                    "Cells, tissues, organs, and systems", "Human body systems integration", "Genetics and inheritance",
                    "Evolution and natural selection", "Ecology and ecosystems", "Environmental issues",
                    "Biotechnology (introduction)", "Health and disease", "Immune system", "Adolescence and puberty",
                    "Scientific method", "Experimental design", "Data collection and analysis"
                ],
                6: [
                    # Cambridge Lower Secondary Stage 6 Biology
                    "Cells and organization", "Human body systems", "Plant systems", "Reproduction",
                    "Genetics and inheritance", "Ecology and environment", "Classification", "Evolution"
                ],
                7: [
                    # Cambridge Lower Secondary Stage 7 Biology
                    "Cells and organization", "Human body systems", "Plant systems", "Reproduction",
                    "Genetics and inheritance", "Ecology and environment", "Classification", "Evolution"
                ],
                8: [
                    # Cambridge Lower Secondary Stage 8 Biology
                    "Cells and organization", "Human body systems", "Plant systems", "Reproduction",
                    "Genetics and inheritance", "Ecology and environment", "Classification", "Evolution"
                ],
                9: [
                    # Cambridge IGCSE Biology 0610 Core Topics (Complete Detailed)
                    "Characteristics and classification of living organisms", "Concept and use of a classificatory system",
                    "Features of organisms", "Organisation and maintenance of the organism", "Cell structure and organisation",
                    "Levels of organisation", "Size of specimens", "Movement into and out of cells", "Diffusion",
                    "Osmosis", "Active transport", "Biological molecules", "Carbohydrates", "Proteins", "Lipids",
                    "DNA", "Water", "Enzymes", "Enzyme action", "Factors affecting enzyme action",
                    "Plant nutrition", "Photosynthesis", "Leaf structure", "Mineral requirements",
                    "Human nutrition", "Diet", "Alimentary canal", "Mechanical and chemical digestion",
                    "Absorption", "Assimilation", "Transport in plants", "Xylem and phloem", "Transpiration",
                    "Translocation", "Transport in animals", "Circulatory systems", "Heart", "Blood vessels",
                    "Blood", "Lymphatic system", "Diseases and immunity", "Disease transmission", "Body defences",
                    "Immune system", "Antibiotics", "Gas exchange", "Gas exchange in humans", "Breathing",
                    "Gas exchange in plants", "Respiration", "Aerobic respiration", "Anaerobic respiration",
                    "Gas exchange during respiration", "Excretion in humans", "Excretion", "Kidney structure",
                    "Kidney function", "Coordination and response", "Nervous system in humans", "Sense organs",
                    "Hormones in humans", "Tropic responses in plants", "Drugs", "Medical drugs", "Misused drugs"
                ],
                10: [
                    # Cambridge IGCSE Biology 0610 Extended Topics (Complete Detailed)
                    "Characteristics and classification of living organisms", "Concept and use of a classificatory system",
                    "Features of organisms", "Organisation and maintenance of the organism", "Cell structure and organisation",
                    "Levels of organisation", "Size of specimens", "Movement into and out of cells", "Diffusion",
                    "Osmosis", "Active transport", "Biological molecules", "Carbohydrates", "Proteins", "Lipids",
                    "DNA", "Water", "Enzymes", "Enzyme action", "Factors affecting enzyme action",
                    "Plant nutrition", "Photosynthesis", "Leaf structure", "Mineral requirements",
                    "Human nutrition", "Diet", "Alimentary canal", "Mechanical and chemical digestion",
                    "Absorption", "Assimilation", "Transport in plants", "Xylem and phloem", "Transpiration",
                    "Translocation", "Transport in animals", "Circulatory systems", "Heart", "Blood vessels",
                    "Blood", "Lymphatic system", "Diseases and immunity", "Disease transmission", "Body defences",
                    "Immune system", "Antibiotics", "Gas exchange", "Gas exchange in humans", "Breathing",
                    "Gas exchange in plants", "Respiration", "Aerobic respiration", "Anaerobic respiration",
                    "Gas exchange during respiration", "Excretion in humans", "Excretion", "Kidney structure",
                    "Kidney function", "Coordination and response", "Nervous system in humans", "Sense organs",
                    "Hormones in humans", "Tropic responses in plants", "Drugs", "Medical drugs", "Misused drugs",
                    "Reproduction", "Asexual reproduction", "Sexual reproduction in plants", "Sexual reproduction in humans",
                    "Sex hormones", "Fertilisation and development", "Inheritance", "Chromosomes, genes and proteins",
                    "Mitosis", "Meiosis", "Monohybrid inheritance", "Codominance", "Sex-linked characteristics",
                    "Variation and selection", "Variation", "Adaptive features", "Selection", "Selective breeding",
                    "Organisms and their environment", "Energy flow", "Food webs", "Nutrient cycles", "Population size",
                    "Human influences on ecosystems", "Food supply", "Habitat destruction", "Pollution", "Conservation",
                    "Biotechnology and genetic engineering", "Biotechnology", "Genetic engineering"
                ],
                11: [
                    # Cambridge International AS Level Biology
                    "Cell structure", "Biological molecules", "Enzymes", "Cell membranes and transport", 
                    "The mitotic cell cycle", "Nucleic acids and protein synthesis", "Transport in plants", 
                    "Transport in mammals", "Gas exchange", "Infectious diseases", "Immunity"
                ],
                12: [
                    # Cambridge International A Level Biology
                    "Energy and respiration", "Photosynthesis", "Homeostasis", "Coordination", "Inherited change", 
                    "Selection and evolution", "Biodiversity, classification and conservation", "Genetic technology"
                ]
            },

            # ENGLISH - Based on Cambridge IGCSE 0500 syllabus
            "English": {
                1: [
                    "Phonics and decoding", "Reading comprehension", "Vocabulary development", 
                    "Speaking and listening", "Writing simple sentences", "Handwriting", 
                    "Story elements", "Poetry appreciation"
                ],
                2: [
                    "Reading fluency", "Comprehension skills", "Grammar basics", "Vocabulary expansion", 
                    "Creative writing", "Non-fiction texts", "Speaking skills", "Listening skills"
                ],
                3: [
                    "Reading strategies", "Text types", "Grammar and punctuation", "Spelling patterns", 
                    "Narrative writing", "Descriptive writing", "Poetry", "Drama"
                ],
                4: [
                    "Reading comprehension", "Literary devices", "Grammar rules", "Vocabulary building", 
                    "Essay writing", "Report writing", "Public speaking", "Critical thinking"
                ],
                5: [
                    "Advanced reading", "Literature appreciation", "Advanced grammar", "Research skills", 
                    "Persuasive writing", "Comparative analysis", "Presentation skills", "Media literacy"
                ],
                6: [
                    "Reading and understanding", "Writing skills", "Speaking and listening", 
                    "Language and grammar", "Literature study"
                ],
                7: [
                    "Reading and understanding", "Writing skills", "Speaking and listening", 
                    "Language and grammar", "Literature study"
                ],
                8: [
                    "Reading and understanding", "Writing skills", "Speaking and listening", 
                    "Language and grammar", "Literature study"
                ],
                9: [
                    # Cambridge IGCSE English Language 0500 Core Topics
                    "Reading", "Writing", "Speaking and listening", "Language study", 
                    "Text analysis", "Creative writing", "Transactional writing", "Summary writing"
                ],
                10: [
                    # Cambridge IGCSE English Language 0500 Extended Topics
                    "Reading comprehension", "Directed writing", "Composition writing", "Summary", 
                    "Note-making", "Language study", "Speaking skills", "Listening skills", 
                    "Literary appreciation", "Critical analysis"
                ],
                11: [
                    # Cambridge International AS Level English Language
                    "Text analysis", "Directed writing", "Essay writing", "Summary writing", 
                    "Language commentary", "Speaking and listening", "Media studies"
                ],
                12: [
                    # Cambridge International A Level English Language
                    "Language analysis", "Text production", "Language topics", "Language investigation", 
                    "Speaking and listening", "Language change", "Language variation"
                ]
            },

            # HISTORY - Based on Cambridge IGCSE 0470 syllabus
            "History": {
                1: [
                    "My family history", "Changes in daily life", "Famous people from the past", 
                    "Old and new", "Festivals and celebrations", "Transport through time"
                ],
                2: [
                    "Life in the past", "Great explorers", "Famous leaders", "Inventions that changed the world", 
                    "Ancient civilizations", "Local history"
                ],
                3: [
                    "Stone Age to Iron Age", "Ancient Egypt", "Ancient Greece", "Roman Empire", 
                    "Anglo-Saxons and Vikings", "Medieval times"
                ],
                4: [
                    "Roman Britain", "Anglo-Saxon and Viking struggle", "Medieval history", 
                    "Tudor period", "Stuart period", "Georgian period"
                ],
                5: [
                    "Victorian era", "World War I", "World War II", "Post-war Britain", 
                    "Ancient civilizations", "Non-European societies"
                ],
                6: [
                    "The medieval world", "The early modern world", "The modern world", 
                    "International relations since 1919"
                ],
                7: [
                    "The medieval world", "The early modern world", "The modern world", 
                    "International relations since 1919"
                ],
                8: [
                    "The medieval world", "The early modern world", "The modern world", 
                    "International relations since 1919"
                ],
                9: [
                    # Cambridge IGCSE History 0470 Core Topics
                    "International relations since 1919", "The First World War", "The peace settlements", 
                    "The League of Nations and international co-operation", "The origins and course of the Second World War", 
                    "The Cold War", "Contemporary conflicts"
                ],
                10: [
                    # Cambridge IGCSE History 0470 Extended Topics
                    "International relations since 1919", "Germany, 1918-1945", "Russia, 1905-1941", 
                    "The USA, 1919-1941", "China, c.1930-1990", "South Africa, c.1940-1994", 
                    "Israelis and Palestinians since 1945"
                ],
                11: [
                    # Cambridge International AS Level History
                    "Modern European history", "Modern world history", "Southeast Asian history", 
                    "African history", "American history"
                ],
                12: [
                    # Cambridge International A Level History
                    "European history", "American history", "African history", "Southeast Asian history", 
                    "International history"
                ]
            },

            # GEOGRAPHY - Based on Cambridge IGCSE 0460 syllabus
            "Geography": {
                1: [
                    "My local area", "Where I live", "Weather and seasons", "Land and water", 
                    "Animals and plants", "People and places"
                ],
                2: [
                    "Our world", "Continents and oceans", "Different places", "Weather patterns", 
                    "Physical features", "Human activities"
                ],
                3: [
                    "Location knowledge", "Place knowledge", "Human and physical geography", 
                    "Geographical skills", "Fieldwork", "Map work"
                ],
                4: [
                    "Locational knowledge", "Place knowledge", "Human and physical geography", 
                    "Geographical skills and fieldwork", "Environmental geography"
                ],
                5: [
                    "Locational knowledge", "Place knowledge", "Human and physical geography", 
                    "Geographical skills and fieldwork", "Development geography"
                ],
                6: [
                    "Population and settlement", "The natural environment", "Economic development", 
                    "Environmental management"
                ],
                7: [
                    "Population and settlement", "The natural environment", "Economic development", 
                    "Environmental management"
                ],
                8: [
                    "Population and settlement", "The natural environment", "Economic development", 
                    "Environmental management"
                ],
                9: [
                    # Cambridge IGCSE Geography 0460 Core Topics
                    "Population and settlement", "The natural environment", "Economic development", 
                    "Environmental management", "Population dynamics", "Migration", "Settlement patterns", 
                    "Urbanisation"
                ],
                10: [
                    # Cambridge IGCSE Geography 0460 Extended Topics
                    "Population and settlement", "The natural environment", "Economic development", 
                    "Environmental management", "Earthquakes and volcanoes", "Rivers", "Coasts", 
                    "Weather, climate and natural vegetation", "Agriculture", "Industry", "Tourism", 
                    "Energy", "Water", "Environmental risks", "Fragile environments"
                ],
                11: [
                    # Cambridge International AS Level Geography
                    "Hydrology and fluvial geomorphology", "Atmosphere and weather", 
                    "Rocks and weathering", "Population", "Migration", "Settlement dynamics"
                ],
                12: [
                    # Cambridge International A Level Geography
                    "Tropical environments", "Coastal environments", "Hazard-prone environments", 
                    "Arid and semi-arid environments", "Production, location and change", 
                    "Environmental management", "Global interdependence"
                ]
            },

            # COMPUTER SCIENCE - Based on Cambridge IGCSE 0478 syllabus
            "Computer Science": {
                1: [
                    "What is a computer?", "Using a computer", "Computer games", "Digital art", 
                    "Simple programming", "Online safety"
                ],
                2: [
                    "Computer parts", "Using software", "Creating digital content", "Simple algorithms", 
                    "Programming basics", "Internet safety"
                ],
                3: [
                    "Computer systems", "Networks", "Creating programs", "Data and information", 
                    "Digital literacy", "E-safety"
                ],
                4: [
                    "Computer science concepts", "Programming fundamentals", "Data representation", 
                    "Computer networks", "Cyber security", "Impact of technology"
                ],
                5: [
                    "Computing systems", "Programming", "Data and data representation", 
                    "Computer networks", "Computer security", "Algorithms"
                ],
                6: [
                    "Computer systems", "Algorithms and programming", "Data representation", 
                    "Computer networks", "Cyber security"
                ],
                7: [
                    "Computer systems", "Algorithms and programming", "Data representation", 
                    "Computer networks", "Cyber security"
                ],
                8: [
                    "Computer systems", "Algorithms and programming", "Data representation", 
                    "Computer networks", "Cyber security"
                ],
                9: [
                    # Cambridge IGCSE Computer Science 0478 Core Topics
                    "Data representation", "Data transmission", "Hardware", "Software", 
                    "The internet and its uses", "Automated and emerging technologies", 
                    "Algorithm design and problem solving", "Programming", "Databases", "Boolean logic"
                ],
                10: [
                    # Cambridge IGCSE Computer Science 0478 Extended Topics
                    "Data representation", "Data transmission", "Hardware", "Software", 
                    "The internet and its uses", "Automated and emerging technologies", 
                    "Algorithm design and problem solving", "Programming", "Databases", "Boolean logic",
                    "Ethics and ownership", "Database concepts", "Sound and video editing"
                ],
                11: [
                    # Cambridge International AS Level Computer Science
                    "Information representation", "Communication and Internet technologies", 
                    "Hardware", "Processor fundamentals", "System software", "Security", 
                    "Monitoring", "Programming", "Advanced theory"
                ],
                12: [
                    # Cambridge International A Level Computer Science
                    "Data representation", "Communication", "Hardware", "System software", 
                    "Security", "Artificial intelligence", "Computational thinking", 
                    "Further programming", "Advanced theory"
                ]
            },

            # ECONOMICS - Based on Cambridge IGCSE 0455 syllabus
            "Economics": {
                9: [
                    # Cambridge IGCSE Economics 0455 Core Topics
                    "The basic economic problem", "Resource allocation", "Microeconomics", 
                    "Government and the macroeconomy", "Economic development", "International trade and specialisation"
                ],
                10: [
                    # Cambridge IGCSE Economics 0455 Extended Topics
                    "The basic economic problem", "The allocation of resources", "Microeconomic decision makers", 
                    "Government and the macroeconomy", "Economic development", "International trade and globalisation",
                    "Markets", "Market failure", "The role of government in an economy"
                ],
                11: [
                    # Cambridge International AS Level Economics
                    "Basic economic ideas and resource allocation", "The price system and the microeconomy", 
                    "Government microeconomic intervention", "The macroeconomy"
                ],
                12: [
                    # Cambridge International A Level Economics
                    "The price system and the macroeconomy", "Government macroeconomic intervention", 
                    "International economic issues", "Development economics"
                ]
            },

            # BUSINESS STUDIES - Based on Cambridge IGCSE 0450 syllabus
            "Business Studies": {
                9: [
                    # Cambridge IGCSE Business Studies 0450 Core Topics
                    "Understanding business activity", "People in business", "Marketing", 
                    "Operations management", "Financial information and decisions", "External influences on business activity"
                ],
                10: [
                    # Cambridge IGCSE Business Studies 0450 Extended Topics
                    "Understanding business activity", "People in business", "Marketing", 
                    "Operations management", "Financial information and decisions", "External influences on business activity",
                    "Business objectives", "Stakeholders", "Business structure", "Size of business"
                ],
                11: [
                    # Cambridge International AS Level Business
                    "Business and its environment", "People in organisations", "Marketing", 
                    "Operations and project management", "Finance and accounting"
                ],
                12: [
                    # Cambridge International A Level Business
                    "Strategic management", "External influences", "Marketing", "Human resource management", 
                    "Operations management", "Strategic planning"
                ]
            },

            # ACCOUNTING - Based on Cambridge IGCSE 0452 syllabus
            "Accounting": {
                9: [
                    # Cambridge IGCSE Accounting 0452 Core Topics
                    "The accounting system", "Accounting procedures", "Preparation of financial statements", 
                    "Analysis and interpretation", "Accounting principles", "Books of original entry"
                ],
                10: [
                    # Cambridge IGCSE Accounting 0452 Extended Topics
                    "The accounting system", "Accounting procedures", "Preparation of financial statements", 
                    "Analysis and interpretation", "Accounting principles", "Books of original entry",
                    "Ledger accounts", "Trial balance", "Financial statements of sole traders"
                ],
                11: [
                    # Cambridge International AS Level Accounting
                    "The accounting system", "Accounting procedures", "Preparation of financial statements", 
                    "Analysis and interpretation"
                ],
                12: [
                    # Cambridge International A Level Accounting
                    "Advanced financial accounting", "Cost and management accounting", 
                    "Accounting theory", "Analysis and interpretation"
                ]
            },

            # ART & DESIGN - Based on Cambridge IGCSE 0400 syllabus
            "Art & Design": {
                1: [
                    "Drawing and mark making", "Painting and color", "Sculpture and 3D", 
                    "Digital art", "Observational drawing", "Creative expression"
                ],
                2: [
                    "Line and shape", "Color theory", "Texture and pattern", "Collage", 
                    "Printmaking", "Art appreciation"
                ],
                3: [
                    "Drawing techniques", "Painting methods", "Sculpture", "Design principles", 
                    "Art history", "Cultural art"
                ],
                4: [
                    "Advanced drawing", "Mixed media", "Photography", "Graphic design", 
                    "Art movements", "Personal expression"
                ],
                5: [
                    "Portfolio development", "Art criticism", "Contemporary art", "Digital design", 
                    "Installation art", "Art careers"
                ],
                6: [
                    "Observational studies", "Design development", "Material exploration", 
                    "Cultural influences", "Personal investigations"
                ],
                7: [
                    "Observational studies", "Design development", "Material exploration", 
                    "Cultural influences", "Personal investigations"
                ],
                8: [
                    "Observational studies", "Design development", "Material exploration", 
                    "Cultural influences", "Personal investigations"
                ],
                9: [
                    # Cambridge IGCSE Art & Design 0400 Core Topics
                    "Drawing", "Painting and related media", "Printmaking", "Three-dimensional studies", 
                    "Photography", "Digital and new media"
                ],
                10: [
                    # Cambridge IGCSE Art & Design 0400 Extended Topics
                    "Drawing", "Painting and related media", "Printmaking", "Three-dimensional studies", 
                    "Photography", "Digital and new media", "Textile design", "Graphic communication"
                ],
                11: [
                    # Cambridge International AS Level Art & Design
                    "Fine art", "Graphic design", "Textile design", "Three-dimensional design", 
                    "Photography"
                ],
                12: [
                    # Cambridge International A Level Art & Design
                    "Fine art", "Graphic design", "Textile design", "Three-dimensional design", 
                    "Photography", "Digital media"
                ]
            },

            # MUSIC - Based on Cambridge IGCSE 0410 syllabus
            "Music": {
                1: [
                    "Singing simple songs", "Listening to music", "Playing instruments", 
                    "Music and movement", "Sound exploration", "Musical games"
                ],
                2: [
                    "Pulse and rhythm", "High and low sounds", "Loud and quiet", 
                    "Musical instruments", "Songs and singing", "Music from different places"
                ],
                3: [
                    "Musical elements", "Notation basics", "Composition", "Performance", 
                    "Listening skills", "World music"
                ],
                4: [
                    "Musical structure", "Rhythm patterns", "Melody", "Harmony", 
                    "Musical instruments", "Composers and styles"
                ],
                5: [
                    "Musical periods", "Composition techniques", "Performance skills", 
                    "Music technology", "Analysis", "Cultural context"
                ],
                6: [
                    "Performing", "Composing", "Listening", "Musical elements", 
                    "Musical contexts and traditions"
                ],
                7: [
                    "Performing", "Composing", "Listening", "Musical elements", 
                    "Musical contexts and traditions"
                ],
                8: [
                    "Performing", "Composing", "Listening", "Musical elements", 
                    "Musical contexts and traditions"
                ],
                9: [
                    # Cambridge IGCSE Music 0410 Core Topics
                    "Performing", "Composing", "Listening", "Musical perception and analysis"
                ],
                10: [
                    # Cambridge IGCSE Music 0410 Extended Topics
                    "Performing", "Composing", "Listening", "Musical perception and analysis",
                    "World music", "Popular music", "Musical technology"
                ],
                11: [
                    # Cambridge International AS Level Music
                    "Performing", "Composing", "Listening", "Analysis"
                ],
                12: [
                    # Cambridge International A Level Music
                    "Performing", "Composing", "Listening", "Analysis", "Music technology"
                ]
            },

            # PHYSICAL EDUCATION - Based on Cambridge IGCSE 0413 syllabus
            "Physical Education": {
                1: [
                    "Basic movement skills", "Games and play", "Health and fitness", 
                    "Dance and gymnastics", "Swimming", "Team cooperation"
                ],
                2: [
                    "Fundamental movement", "Sports skills", "Health awareness", 
                    "Creative movement", "Water safety", "Fair play"
                ],
                3: [
                    "Athletic skills", "Game strategies", "Fitness concepts", 
                    "Rhythmic activities", "Outdoor activities", "Sportsmanship"
                ],
                4: [
                    "Sport techniques", "Tactical awareness", "Physical fitness", 
                    "Performance skills", "Adventure activities", "Leadership"
                ],
                5: [
                    "Advanced skills", "Game analysis", "Training principles", 
                    "Specialized sports", "Risk assessment", "Coaching"
                ],
                6: [
                    "Practical activities", "Health, fitness and training", "Sport psychology", 
                    "Biomechanics", "Skill acquisition"
                ],
                7: [
                    "Practical activities", "Health, fitness and training", "Sport psychology", 
                    "Biomechanics", "Skill acquisition"
                ],
                8: [
                    "Practical activities", "Health, fitness and training", "Sport psychology", 
                    "Biomechanics", "Skill acquisition"
                ],
                9: [
                    # Cambridge IGCSE Physical Education 0413 Core Topics
                    "Anatomy and physiology", "Health, fitness and training", "Skill acquisition", 
                    "Sport psychology", "Social, cultural and ethical influences"
                ],
                10: [
                    # Cambridge IGCSE Physical Education 0413 Extended Topics
                    "Anatomy and physiology", "Health, fitness and training", "Skill acquisition", 
                    "Sport psychology", "Social, cultural and ethical influences",
                    "Biomechanics", "Training methods", "Performance analysis"
                ],
                11: [
                    # Cambridge International AS Level Physical Education
                    "Applied anatomy and physiology", "Exercise physiology", "Biomechanics", 
                    "Skill acquisition", "Sport and society", "Contemporary studies in sport"
                ],
                12: [
                    # Cambridge International A Level Physical Education
                    "Applied anatomy and physiology", "Exercise physiology", "Biomechanics", 
                    "Skill acquisition", "Sport and society", "Contemporary studies in sport",
                    "Sports psychology", "Technology in sport"
                ]
            },

            # INFORMATION & COMMUNICATION TECHNOLOGY (ICT) - Based on Cambridge IGCSE 0417 syllabus
            "ICT": {
                1: [
                    "Using computers", "Input devices", "Output devices", "Software basics", 
                    "Digital citizenship", "Creating simple documents"
                ],
                2: [
                    "Computer systems", "Using applications", "Internet basics", "Digital safety", 
                    "Word processing", "Graphics"
                ],
                3: [
                    "Hardware and software", "Networks", "Data handling", "Multimedia", 
                    "Presentations", "Spreadsheets"
                ],
                4: [
                    "Computer operations", "Communication technology", "Data management", 
                    "Digital creation", "Programming concepts", "Ethics"
                ],
                5: [
                    "Information systems", "Database fundamentals", "Web design", "Programming", 
                    "Digital media", "Impact of ICT"
                ],
                6: [
                    "Communication and collaboration", "Digital citizenship", "Technology operations", 
                    "Data analysis", "Creative communication"
                ],
                7: [
                    "Communication and collaboration", "Digital citizenship", "Technology operations", 
                    "Data analysis", "Creative communication"
                ],
                8: [
                    "Communication and collaboration", "Digital citizenship", "Technology operations", 
                    "Data analysis", "Creative communication"
                ],
                9: [
                    # Cambridge IGCSE ICT 0417 Core Topics
                    "Types and components of computer systems", "Input and output devices", 
                    "Storage devices and media", "Networks", "Effects of using ICT", 
                    "ICT applications", "The systems life cycle", "Safety and security", 
                    "Audience", "Communication", "File management", "Images", "Layout", 
                    "Styles", "Proofing", "Graphs and charts", "Document production", 
                    "Data manipulation", "Presentations", "Data analysis", "Website authoring", 
                    "Testing", "Data types"
                ],
                10: [
                    # Cambridge IGCSE ICT 0417 Extended Topics
                    "Types and components of computer systems", "Input and output devices", 
                    "Storage devices and media", "Networks", "Effects of using ICT", 
                    "ICT applications", "The systems life cycle", "Safety and security", 
                    "Audience", "Communication", "File management", "Images", "Layout", 
                    "Styles", "Proofing", "Graphs and charts", "Document production", 
                    "Data manipulation", "Presentations", "Data analysis", "Website authoring", 
                    "Testing", "Data types", "Databases", "Modeling", "Control systems"
                ],
                11: [
                    # Cambridge International AS Level ICT
                    "Communication", "Hardware", "Software", "Practical production"
                ],
                12: [
                    # Cambridge International A Level ICT
                    "Communication", "Hardware", "Software", "Practical production", 
                    "Advanced databases", "Multimedia products", "Networking"
                ]
            },

            # PSYCHOLOGY - Based on Cambridge IGCSE Psychology
            "Psychology": {
                9: [
                    # Cambridge IGCSE Psychology Core Topics
                    "Research methods", "Biological approach", "Cognitive approach", 
                    "Learning approach", "Social approach", "Developmental approach"
                ],
                10: [
                    # Cambridge IGCSE Psychology Extended Topics
                    "Research methods", "Biological approach", "Cognitive approach", 
                    "Learning approach", "Social approach", "Developmental approach",
                    "Individual differences", "Abnormal psychology", "Health psychology"
                ],
                11: [
                    # Cambridge International AS Level Psychology
                    "Approaches", "Research methods", "Core studies", "Contemporary debate"
                ],
                12: [
                    # Cambridge International A Level Psychology
                    "Psychology and abnormality", "Psychology and consumer behaviour", 
                    "Psychology and health", "Psychology and organisations"
                ]
            },

            # SOCIOLOGY - Based on Cambridge IGCSE Sociology
            "Sociology": {
                9: [
                    # Cambridge IGCSE Sociology Core Topics
                    "Family", "Education", "Crime, deviance and social control", 
                    "Mass media", "Research methods"
                ],
                10: [
                    # Cambridge IGCSE Sociology Extended Topics
                    "Family", "Education", "Crime, deviance and social control", 
                    "Mass media", "Research methods", "Social inequality", "Work and leisure"
                ],
                11: [
                    # Cambridge International AS Level Sociology
                    "Theory and methods", "Education", "Health", "Families and households"
                ],
                12: [
                    # Cambridge International A Level Sociology
                    "Theory and methods", "Global development", "Media", "Crime and deviance"
                ]
            },

            # FRENCH - Based on Cambridge IGCSE 0520 syllabus
            "French": {
                1: [
                    "Greetings and introductions", "Numbers 1-10", "Colors", "Family members", 
                    "Basic vocabulary", "Simple phrases"
                ],
                2: [
                    "Classroom language", "Days of the week", "Months", "Weather", 
                    "Food and drink", "Animals"
                ],
                3: [
                    "School subjects", "Time", "Daily routines", "House and home", 
                    "Hobbies", "Sports"
                ],
                4: [
                    "Shopping", "Clothes", "Body parts", "Health", "Transport", "Directions"
                ],
                5: [
                    "Holidays", "Countries", "Past tense", "Future plans", "Opinions", "Descriptions"
                ],
                6: [
                    "Personal information", "Family and friends", "Free time activities", 
                    "Home and local area", "Daily life"
                ],
                7: [
                    "Personal information", "Family and friends", "Free time activities", 
                    "Home and local area", "Daily life"
                ],
                8: [
                    "Personal information", "Family and friends", "Free time activities", 
                    "Home and local area", "Daily life"
                ],
                9: [
                    # Cambridge IGCSE French 0520 Core Topics
                    "Personal identification", "Home and family", "Food and drink", 
                    "School and career", "Leisure", "Travel and transport", "Shopping", 
                    "Health and fitness", "Local area", "Holidays"
                ],
                10: [
                    # Cambridge IGCSE French 0520 Extended Topics
                    "Personal identification", "Home and family", "Food and drink", 
                    "School and career", "Leisure", "Travel and transport", "Shopping", 
                    "Health and fitness", "Local area", "Holidays", "Environment", 
                    "Media and technology", "Social issues"
                ],
                11: [
                    # Cambridge International AS Level French
                    "Young people today", "Family relationships", "Education and employment", 
                    "Leisure and entertainment", "Travel and tourism"
                ],
                12: [
                    # Cambridge International A Level French
                    "Media", "Popular culture", "Healthy living/lifestyle", "Family/relationships", 
                    "Environment", "The multicultural society"
                ]
            },

            # SPANISH - Based on Cambridge IGCSE 0530 syllabus
            "Spanish": {
                1: [
                    "Basic greetings", "Numbers 1-10", "Colors", "Family", "Simple vocabulary", "Pronunciation"
                ],
                2: [
                    "Classroom objects", "Days and months", "Weather", "Food", "Animals", "Basic conversation"
                ],
                3: [
                    "School", "Time", "Daily routine", "House", "Hobbies", "Sports"
                ],
                4: [
                    "Shopping", "Clothing", "Body", "Health", "Transport", "Directions"
                ],
                5: [
                    "Holidays", "Countries", "Past events", "Future plans", "Opinions", "Descriptions"
                ],
                6: [
                    "Personal details", "Family and friends", "Leisure activities", "Local area", "Daily life"
                ],
                7: [
                    "Personal details", "Family and friends", "Leisure activities", "Local area", "Daily life"
                ],
                8: [
                    "Personal details", "Family and friends", "Leisure activities", "Local area", "Daily life"
                ],
                9: [
                    # Cambridge IGCSE Spanish 0530 Core Topics
                    "Personal identification", "Family and home", "Food and restaurants", 
                    "School and work", "Free time", "Travel", "Shopping", "Health", 
                    "Local environment", "Holidays"
                ],
                10: [
                    # Cambridge IGCSE Spanish 0530 Extended Topics
                    "Personal identification", "Family and home", "Food and restaurants", 
                    "School and work", "Free time", "Travel", "Shopping", "Health", 
                    "Local environment", "Holidays", "Environment", "Technology", "Social issues"
                ],
                11: [
                    # Cambridge International AS Level Spanish
                    "Youth matters", "Family and relationships", "Education and future career", 
                    "Leisure and entertainment", "Travel and holidays"
                ],
                12: [
                    # Cambridge International A Level Spanish
                    "Media and culture", "Health and lifestyle", "Family and society", 
                    "Environment", "Technology", "Cultural heritage"
                ]
            }
        },
        
        "State Board": {
            "Mathematics": {
                1: [
                    # Grade 1 Mathematics - Foundation Level
                    "Numbers 1 to 99", "Counting Objects", "Number Recognition", "Number Writing",
                    "Before and After Numbers", "Between Numbers", "Smallest and Largest",
                    "Ascending and Descending Order", "Place Value - Tens and Ones",
                    "Addition within 20", "Subtraction within 20", "Addition without Carrying",
                    "Subtraction without Borrowing", "Word Problems on Addition",
                    "Word Problems on Subtraction", "Basic Shapes - Circle, Square, Triangle, Rectangle",
                    "Shapes in Environment", "Patterns with Objects", "Patterns with Numbers",
                    "Patterns with Shapes", "Size Comparison - Big and Small", "Length Comparison",
                    "Weight Comparison - Heavy and Light", "Capacity - More and Less",
                    "Time Concepts - Day and Night", "Days of the Week", "Months of the Year",
                    "Yesterday, Today, Tomorrow", "Clock Reading - Hour Hand",
                    "Money Recognition - Coins and Notes", "Value of Coins", "Simple Money Problems",
                    "Data Collection", "Simple Graphs", "Tally Marks",
                    "Spatial Concepts - Inside, Outside, Above, Below"
                ],
                2: [
                    # Grade 2 Mathematics
                    "Numbers 1 to 1000", "Three Digit Numbers", "Number Names in Words",
                    "Expanded Form of Numbers", "Place Value - Hundreds, Tens, Ones",
                    "Comparison of Numbers", "Odd and Even Numbers", "Skip Counting by 2, 5, 10",
                    "Number Patterns", "Addition with Carrying", "Addition of Two Digit Numbers",
                    "Addition of Three Digit Numbers", "Subtraction with Borrowing",
                    "Subtraction of Two Digit Numbers", "Subtraction of Three Digit Numbers",
                    "Introduction to Multiplication", "Multiplication Tables 2, 3, 4, 5, 10",
                    "Multiplication as Repeated Addition", "Introduction to Division",
                    "Division as Repeated Subtraction", "Division by 2, 3, 4, 5, 10",
                    "Word Problems on Four Operations", "Geometric Shapes - Properties",
                    "2D and 3D Shapes", "Faces, Edges, Vertices", "Symmetry in Shapes",
                    "Measurement of Length - Centimeter, Meter", "Measurement of Weight - Gram, Kilogram",
                    "Measurement of Capacity - Liter", "Time - Hours and Minutes",
                    "Calendar Reading", "Money - Addition and Subtraction", "Making Change",
                    "Data Handling - Bar Graphs", "Pictographs", "Simple Probability",
                    "Fractions - Half and Quarter", "Equal Parts"
                ],
                3: [
                    # Grade 3 Mathematics
                    "Numbers up to 10,000", "Four Digit Numbers", "Roman Numerals I to XII",
                    "Place Value up to Thousands", "Rounding Numbers", "Estimation",
                    "Addition of Four Digit Numbers", "Subtraction of Four Digit Numbers",
                    "Properties of Addition", "Mental Mathematics", "Multiplication Tables up to 12",
                    "Multiplication of Two Digit Numbers", "Multiplication of Three Digit Numbers",
                    "Division by One Digit Numbers", "Division by Two Digit Numbers",
                    "Remainder in Division", "Factors and Multiples - Introduction",
                    "Prime and Composite Numbers - Basic", "Fractions - Unit Fractions",
                    "Proper and Improper Fractions", "Mixed Numbers", "Equivalent Fractions",
                    "Addition and Subtraction of Like Fractions", "Decimals - Introduction",
                    "Decimal Notation", "Place Value in Decimals", "Angles - Introduction",
                    "Types of Angles", "Lines and Line Segments", "Parallel and Perpendicular Lines",
                    "Triangles and their Types", "Quadrilaterals", "Circles and Circumference",
                    "Perimeter of Squares and Rectangles", "Area - Introduction",
                    "Measurement - Standard Units", "Conversion of Units",
                    "Time - 12 Hour and 24 Hour Format", "Elapsed Time", "Temperature",
                    "Money Problems - All Operations", "Profit and Loss - Basic",
                    "Data Interpretation", "Mean and Mode - Introduction", "Simple Equations"
                ],
                4: [
                    # Grade 4 Mathematics
                    "Large Numbers up to 1,00,000", "Indian and International Number System",
                    "Roman Numerals up to 100", "Estimation and Approximation",
                    "Operations on Large Numbers", "Word Problems on Mixed Operations",
                    "Properties of Operations", "BODMAS Rule", "Factors and Common Factors",
                    "Multiples and Common Multiples", "Prime Factorization", "LCM and HCF - Basic",
                    "Tests of Divisibility", "Fractions on Number Line", "Comparison of Fractions",
                    "Addition and Subtraction of Unlike Fractions", "Multiplication of Fractions",
                    "Division of Fractions", "Decimal Place Value", "Operations on Decimals",
                    "Conversion between Fractions and Decimals", "Percentage - Introduction",
                    "Percentage as Fraction", "Simple Percentage Problems",
                    "Ratio and Proportion - Introduction", "Unitary Method - Basic",
                    "Simple Interest - Introduction", "Profit and Loss Percentage",
                    "Coordinate Geometry - Introduction", "Plotting Points", "Geometry - Constructions",
                    "Area and Perimeter of Complex Shapes", "Volume and Capacity",
                    "Surface Area - Introduction", "Data Analysis - Frequency Tables",
                    "Probability - Basic Concepts", "Algebraic Expressions - Introduction",
                    "Simple Linear Equations", "Patterns and Sequences"
                ],
                5: [
                    # Grade 5 Mathematics
                    "Number System up to 10,00,000", "Place Value in Large Numbers",
                    "Operations on Large Numbers", "Estimation in Operations",
                    "Number Patterns and Sequences", "Prime and Composite Numbers",
                    "Prime Factorization Methods", "LCM and HCF by Different Methods",
                    "Applications of LCM and HCF", "Fraction Operations - All Types",
                    "Mixed Number Operations", "Decimal Operations - All Types",
                    "Decimal to Fraction Conversion", "Percentage Calculations",
                    "Percentage Increase and Decrease", "Profit and Loss Problems",
                    "Simple Interest Calculations", "Compound Interest - Introduction",
                    "Ratio and Proportion Problems", "Direct and Inverse Proportion",
                    "Unitary Method Applications", "Time and Work - Basic",
                    "Speed, Distance and Time", "Basic Algebra", "Linear Equations in One Variable",
                    "Coordinate Geometry", "Plotting Graphs", "Geometric Constructions",
                    "Properties of Triangles", "Congruence - Introduction", "Area Calculations",
                    "Volume of Cubes and Cuboids", "Surface Area Calculations",
                    "Data Handling - Mean, Median, Mode", "Bar Graphs and Pie Charts",
                    "Probability Experiments", "Statistics - Introduction"
                ],
                6: [
                    # Grade 6 Mathematics
                    "Natural Numbers and Whole Numbers", "Integers - Positive and Negative",
                    "Number Line Representation", "Operations on Integers", "Properties of Integers",
                    "Rational Numbers - Introduction", "Fractions as Rational Numbers",
                    "Operations on Rational Numbers", "Decimal Representation",
                    "Percentage and its Applications", "Profit and Loss Advanced",
                    "Simple Interest and Compound Interest", "Ratio and Proportion Advanced",
                    "Unitary Method", "Direct and Inverse Variation", "Basic Proportionality",
                    "Introduction to Algebra", "Variables and Constants", "Algebraic Expressions",
                    "Terms and Coefficients", "Like and Unlike Terms", "Addition and Subtraction of Expressions",
                    "Linear Equations in One Variable", "Solving Simple Equations",
                    "Basic Geometrical Ideas", "Points, Lines and Planes", "Line Segments and Rays",
                    "Angles and their Types", "Measurement of Angles", "Pairs of Angles",
                    "Properties of Triangles", "Types of Triangles", "Quadrilaterals and their Properties",
                    "Circles - Basic Concepts", "Perimeter and Area", "Area of Rectangles and Squares",
                    "Data Handling", "Collection and Organization of Data", "Pictographs and Bar Graphs",
                    "Mean, Median and Mode", "Introduction to Probability"
                ],
                7: [
                    # Grade 7 Mathematics
                    "Integers and their Operations", "Properties of Addition and Multiplication",
                    "Rational Numbers", "Operations on Rational Numbers", "Representation on Number Line",
                    "Exponents and Powers", "Laws of Exponents", "Expressing Large Numbers",
                    "Algebraic Expressions", "Addition and Subtraction of Algebraic Expressions",
                    "Multiplication of Algebraic Expressions", "Simple Linear Equations",
                    "Solving Linear Equations", "Applications of Linear Equations",
                    "Lines and Angles", "Pairs of Lines", "Transversals and Parallel Lines",
                    "Properties of Parallel Lines", "Triangles and their Properties",
                    "Median and Altitude of Triangles", "Angle Sum Property", "Exterior Angle Property",
                    "Congruence of Triangles", "Criteria for Congruence", "Applications of Congruence",
                    "Quadrilaterals", "Angle Sum Property of Quadrilaterals", "Types of Quadrilaterals",
                    "Circle and its Parts", "Arc, Chord and Segment", "Central and Inscribed Angles",
                    "Practical Geometry", "Construction of Triangles", "Construction of Parallel Lines",
                    "Perimeter and Area", "Area of Parallelograms", "Area of Triangles",
                    "Ratio and Proportion", "Unitary Method", "Percentage", "Applications of Percentage",
                    "Simple Interest", "Data Handling", "Arithmetic Mean", "Mode and Median",
                    "Bar Graphs", "Probability", "Symmetry", "Lines of Symmetry"
                ],
                8: [
                    # Grade 8 Mathematics
                    "Rational Numbers", "Properties of Rational Numbers", "Representation of Rational Numbers",
                    "Operations between Rational Numbers", "Linear Equations in One Variable",
                    "Solving Linear Equations", "Reducing Equations to Linear Form",
                    "Understanding Quadrilaterals", "Properties of Parallelograms", "Types of Quadrilaterals",
                    "Practical Geometry", "Constructing Quadrilaterals", "Construction using Given Conditions",
                    "Data Handling", "Frequency Distribution", "Histograms", "Circle Graphs or Pie Charts",
                    "Probability", "Squares and Square Roots", "Finding Square Roots", "Properties of Square Roots",
                    "Cubes and Cube Roots", "Finding Cube Roots", "Comparing Quantities",
                    "Calculating Discount", "Sales Tax/VAT", "Compound Interest", "Compound Interest Formula",
                    "Algebraic Expressions and Identities", "Multiplication of Algebraic Expressions",
                    "Standard Identities", "Factorisation", "Factorisation of Algebraic Expressions",
                    "Division of Algebraic Expressions", "Introduction to Graphs", "Linear Graphs",
                    "Some Applications", "Playing with Numbers", "Games with Numbers",
                    "Letters for Digits", "Tests of Divisibility", "Mensuration", "Area of Trapezium",
                    "Area of General Quadrilateral", "Area of Polygon", "Surface Area", "Volume",
                    "Volume and Capacity", "Exponents and Powers", "Powers with Negative Exponents",
                    "Laws of Exponents", "Use of Exponents to Express Small Numbers in Standard Form"
                ],
                9: [
                    # Grade 9 Mathematics
                    "Number Systems", "Real Numbers", "Irrational Numbers", "Representation on Number Line",
                    "Operations on Real Numbers", "Laws of Exponents for Real Numbers", "Rationalization",
                    "Polynomials", "Polynomials in One Variable", "Zeroes of a Polynomial",
                    "Remainder Theorem", "Factorization of Polynomials", "Algebraic Identities",
                    "Coordinate Geometry", "Cartesian Coordinate System", "Plotting Points in the Plane",
                    "Distance Formula", "Section Formula", "Linear Equations in Two Variables",
                    "Solution of Linear Equation", "Graph of Linear Equation", "Equations of Lines",
                    "Introduction to Euclid's Geometry", "Euclid's Definitions and Axioms",
                    "Equivalent Versions of Euclid's Fifth Postulate", "Lines and Angles",
                    "Intersecting Lines and Non-intersecting Lines", "Pairs of Angles",
                    "Lines Parallel to Same Line", "Angle Sum Property", "Triangles",
                    "Congruence of Triangles", "Criteria for Congruence of Triangles",
                    "Some Properties of a Triangle", "Some More Criteria for Congruence",
                    "Inequalities in a Triangle", "Quadrilaterals", "Angle Sum Property of a Quadrilateral",
                    "Types of Quadrilaterals", "Properties of a Parallelogram", "Another Condition for a Quadrilateral to be a Parallelogram",
                    "The Mid-point Theorem", "Areas of Parallelograms and Triangles", "Figures on the Same Base and Between the Same Parallels",
                    "Parallelograms on the Same Base and Between the Same Parallels", "Triangles on the Same Base and Between the Same Parallels",
                    "Circles", "Introduction", "Angle Subtended by a Chord at a Point", "Perpendicular from the Centre to a Chord",
                    "Circle through Three Points", "Equal Chords and their Distances from the Centre", "Angle Subtended by an Arc of a Circle",
                    "Cyclic Quadrilaterals", "Constructions", "Construction of Bisectors of Line Segments and Angles",
                    "Construction of Triangles", "Heron's Formula", "Area of a Triangle by Heron's Formula",
                    "Application of Heron's Formula in Finding Areas of Quadrilaterals", "Surface Areas and Volumes",
                    "Surface Area of a Cuboid and a Cube", "Surface Area of a Right Circular Cylinder",
                    "Surface Area of a Right Circular Cone", "Surface Area of a Sphere", "Volume of a Cuboid",
                    "Volume of a Cylinder", "Volume of a Right Circular Cone", "Volume of a Sphere",
                    "Statistics", "Collection of Data", "Presentation of Data", "Graphical Representation of Data",
                    "Measures of Central Tendency", "Probability", "Probability - an Experimental Approach"
                ],
                10: [
                    # Grade 10 Mathematics  
                    "Real Numbers", "Euclid's Division Lemma", "Fundamental Theorem of Arithmetic",
                    "Revisiting Irrational Numbers", "Revisiting Rational Numbers and Their Decimal Expansions",
                    "Polynomials", "Geometrical Meaning of the Zeroes of a Polynomial", "Relationship between Zeroes and Coefficients of a Polynomial",
                    "Division Algorithm for Polynomials", "Pair of Linear Equations in Two Variables",
                    "Pair of Linear Equations in Two Variables", "Graphical Method of Solution of a Pair of Linear Equations",
                    "Algebraic Methods of Solving a Pair of Linear Equations", "Equations Reducible to a Pair of Linear Equations in Two Variables",
                    "Quadratic Equations", "Introduction to Quadratic Equations", "Solution of a Quadratic Equation by Factorisation",
                    "Solution of a Quadratic Equation by Completing the Square", "Nature of Roots",
                    "Arithmetic Progressions", "Introduction to Arithmetic Progressions", "nth Term of an AP",
                    "Sum of First n Terms of an AP", "Triangles", "Similar Figures", "Similarity of Triangles",
                    "Criteria for Similarity of Triangles", "Areas of Similar Triangles", "Pythagoras Theorem",
                    "Coordinate Geometry", "Distance Formula", "Section Formula", "Area of a Triangle",
                    "Introduction to Trigonometry", "Trigonometric Ratios", "Trigonometric Ratios of Some Specific Angles",
                    "Trigonometric Identities", "Some Applications of Trigonometry", "Heights and Distances",
                    "Circles", "Tangent to a Circle", "Number of Tangents from a Point to a Circle",
                    "Constructions", "Division of a Line Segment", "Construction of Tangents to a Circle",
                    "Areas Related to Circles", "Perimeter and Area of a Circle", "Areas of Sector and Segment of a Circle",
                    "Areas of Combinations of Plane Figures", "Surface Areas and Volumes",
                    "Combination of Solids", "Conversion of Solid from One Shape to Another",
                    "Frustum of a Cone", "Statistics", "Mean of Grouped Data", "Mode of Grouped Data",
                    "Median of Grouped Data", "Graphical Representation of Cumulative Frequency Distribution",
                    "Probability", "Classical Definition of Probability", "Simple Problems on Single Events"
                ],
                11: [
                    # Grade 11 Mathematics
                    "Sets", "Introduction to Sets", "Types of Sets", "Operations on Sets", "Venn Diagrams",
                    "Relations and Functions", "Cartesian Product of Sets", "Relations", "Types of Relations",
                    "Equivalence Relations", "Functions", "Types of Functions", "Composition of Functions",
                    "Inverse of a Function", "Trigonometric Functions", "Angles", "Trigonometric Functions",
                    "Trigonometric Functions of Sum and Difference of Two Angles", "Trigonometric Equations",
                    "Principle of Mathematical Induction", "Introduction", "The Principle of Mathematical Induction",
                    "Complex Numbers and Quadratic Equations", "Complex Numbers", "Algebra of Complex Numbers",
                    "The Modulus and the Conjugate of a Complex Number", "Argand Plane and Polar Representation",
                    "Quadratic Equations", "Linear Inequalities", "Inequalities", "Algebraic Solutions of Linear Inequalities in One Variable",
                    "Graphical Solution of Linear Inequalities in Two Variables", "Solution of System of Linear Inequalities in Two Variables",
                    "Permutations and Combinations", "Fundamental Principle of Counting", "Permutations", "Combinations",
                    "Binomial Theorem", "Binomial Theorem for Positive Integral Indices", "General and Middle Terms",
                    "Sequences and Series", "Sequences", "Series", "Arithmetic Progression", "Arithmetic Mean",
                    "Geometric Progression", "Geometric Mean", "Relationship between AM and GM", "Sum to n terms of Special Series",
                    "Straight Lines", "Slope of a Line", "Various Forms of the Equation of a Line", "General Equation of a Line",
                    "Distance of a Point from a Line", "Conic Sections", "Sections of a Cone", "Circle", "Parabola",
                    "Ellipse", "Hyperbola", "Introduction to Three Dimensional Geometry", "Coordinate Axes and Coordinate Planes in Three Dimensional Space",
                    "Coordinates of a Point in Space", "Distance between Two Points", "Section Formula",
                    "Limits and Derivatives", "Introduction to Limits", "Limits of Trigonometric Functions",
                    "Derivatives", "Algebra of Derivatives", "Derivative of Polynomials and Trigonometric Functions",
                    "Mathematical Reasoning", "Introduction", "Statements", "New Statements from Old",
                    "Special Words/Phrases", "Implications", "Validating Statements", "Statistics",
                    "Measures of Dispersion", "Range", "Mean Deviation", "Variance and Standard Deviation",
                    "Analysis of Frequency Distributions", "Probability", "Random Experiments", "Event",
                    "Axiomatic Approach to Probability"
                ],
                12: [
                    # Grade 12 Mathematics
                    "Relations and Functions", "Types of Functions", "Composition of Functions", "Invertible Functions",
                    "Binary Operations", "Inverse Trigonometric Functions", "Definition", "Range", "Domain",
                    "Principal Value Branch", "Graphs of Inverse Trigonometric Functions", "Elementary Properties of Inverse Trigonometric Functions",
                    "Matrices", "Introduction", "Types of Matrices", "Operations on Matrices", "Transpose of a Matrix",
                    "Symmetric and Skew Symmetric Matrices", "Elementary Operation (Transformation) of a Matrix",
                    "Invertible Matrices", "Determinants", "Determinant of a Square Matrix", "Properties of Determinants",
                    "Area of a Triangle", "Minors and Cofactors", "Adjoint and Inverse of a Matrix",
                    "Applications of Determinants and Matrices", "Solution of System of Linear Equations using Inverse of a Matrix",
                    "Continuity and Differentiability", "Continuity", "Differentiability", "Exponential and Logarithmic Functions",
                    "Logarithmic Differentiation", "Derivatives of Functions in Parametric Forms", "Second Order Derivatives",
                    "Mean Value Theorem", "Applications of Derivatives", "Rate of Change of Bodies", "Increasing and Decreasing Functions",
                    "Tangents and Normals", "Use of Derivatives in Approximation", "Maxima and Minima",
                    "Integrals", "Integration as an Inverse Process of Differentiation", "Methods of Integration",
                    "Integrals of some Particular Functions", "Integration by Partial Fractions", "Integration by Parts",
                    "Definite Integral", "Fundamental Theorem of Calculus", "Evaluation of Definite Integrals by Substitution",
                    "Some Properties of Definite Integrals", "Applications of Integrals", "Area under Simple Curves",
                    "Area between Two Curves", "Differential Equations", "Introduction", "General and Particular Solutions of a Differential Equation",
                    "Formation of a Differential Equation whose General Solution is given", "Methods of Solving First order, First degree Differential Equations",
                    "Vector Algebra", "Introduction", "Types of Vectors", "Addition of Vectors", "Multiplication of a Vector by a Scalar",
                    "Product of Two Vectors", "Three Dimensional Geometry", "Direction Cosines and Direction Ratios of a Line",
                    "Equation of a Line in Space", "Angle between Two Lines", "Shortest Distance between Two Lines",
                    "Plane", "Coplanarity of Two Lines", "Angle between Two Planes", "Distance of a Point from a Plane",
                    "Angle between a Line and a Plane", "Linear Programming", "Introduction", "Linear Programming Problem and its Mathematical Formulation",
                    "Different Types of Linear Programming Problems", "Mathematical Formulation of the problem",
                    "Graphical Method of Solution", "Probability", "Conditional Probability", "Multiplication Theorem on Probability",
                    "Independent Events", "Bayes' Theorem", "Random Variables and its Probability Distributions",
                    "Binomial Probability Distribution"
                ]
            },
            
            "English": {
                1: [
                    # Grade 1 English
                    "Alphabet Recognition - Capital Letters", "Alphabet Recognition - Small Letters", "Alphabet Writing Practice",
                    "Vowels and Consonants", "Letter Sounds - Phonics", "Simple Three Letter Words", "CVC Words - Consonant Vowel Consonant",
                    "Sight Words - Common Words", "Reading Simple Sentences", "Picture Reading and Description",
                    "Rhyming Words", "Simple Poems and Rhymes", "Story Listening", "Character Identification in Stories",
                    "Simple Questions and Answers", "Listening Skills - Following Instructions", "Speaking Practice - Show and Tell",
                    "Basic Grammar - Naming Words (Nouns)", "Action Words (Verbs)", "Describing Words (Adjectives)",
                    "This, That, These, Those", "He, She, It", "Simple Sentence Formation",
                    "Capital Letters and Full Stops", "Question Mark", "Writing Simple Words",
                    "Copying Sentences", "Picture Composition", "My Family - Vocabulary",
                    "Parts of Body - Vocabulary", "Animals and Birds - Names", "Fruits and Vegetables - Names",
                    "Colors - Names and Recognition", "Numbers in Words", "Days of the Week",
                    "Good Manners and Polite Words", "Greetings", "Opposites - Big/Small, Hot/Cold"
                ],
                2: [
                    # Grade 2 English
                    "Reading Comprehension - Simple Passages", "Silent Reading", "Loud Reading with Expression",
                    "Phonics - Blending Sounds", "Word Building", "Spelling Practice", "Dictionary Skills - Alphabetical Order",
                    "Vocabulary Building", "Synonyms - Same Meaning Words", "Antonyms - Opposite Words",
                    "Plural Forms - Adding s, es", "Past Tense - Simple Forms", "Present Tense",
                    "Sentences - Statement, Question, Exclamation", "Nouns - Common and Proper",
                    "Pronouns - I, You, We, They", "Verbs - Action Words", "Adjectives - Describing Words",
                    "Articles - A, An, The", "Prepositions - In, On, Under", "Conjunction - And, But",
                    "Paragraph Writing", "Story Writing - Beginning, Middle, End", "Letter Writing - Informal",
                    "Diary Entry - Simple", "Picture Description", "Creative Writing",
                    "Poetry Recitation", "Drama and Role Play", "Listening Comprehension",
                    "Following Complex Instructions", "Conversation Skills", "Telephone Manners",
                    "School Vocabulary", "Home and Family", "Community Helpers",
                    "Seasons and Weather", "Food and Health", "Games and Sports",
                    "Transport and Travel", "Festivals and Celebrations"
                ],
                3: [
                    # Grade 3 English
                    "Reading Skills - Fluency and Comprehension", "Reading Different Text Types",
                    "Inferential Reading", "Critical Reading", "Speed Reading Practice",
                    "Vocabulary Expansion", "Word Formation - Prefixes and Suffixes", "Root Words",
                    "Context Clues", "Homophones", "Compound Words", "Contractions",
                    "Grammar - Parts of Speech", "Nouns - Types", "Pronouns - All Types",
                    "Verbs - Helping and Main Verbs", "Adverbs", "Conjunctions", "Interjections",
                    "Sentence Types - Simple, Compound", "Subject and Predicate", "Active and Passive Voice - Introduction",
                    "Direct and Indirect Speech - Basic", "Punctuation - Comma, Semicolon, Colon",
                    "Apostrophe", "Quotation Marks", "Writing Skills - Paragraph Development",
                    "Essay Writing - Descriptive", "Narrative Writing", "Letter Writing - Formal and Informal",
                    "Application Writing", "Report Writing - Simple", "Story Writing with Dialogue",
                    "Poetry Writing - Simple Rhymes", "Biography Writing - Simple", "Book Review",
                    "Literature - Prose Analysis", "Poetry Appreciation", "Character Study",
                    "Theme Identification", "Moral Values from Stories", "Drama and Theatre",
                    "Public Speaking", "Debate Skills - Basic", "Group Discussion",
                    "Interview Skills", "Presentation Skills", "Media Literacy - Basic"
                ],
                4: [
                    # Grade 4 English
                    "Advanced Reading Comprehension", "Literary Analysis", "Non-fiction Reading",
                    "Research Skills", "Note Taking", "Summary Writing", "Paraphrasing",
                    "Advanced Vocabulary", "Figurative Language", "Metaphors and Similes",
                    "Idioms and Phrases", "Proverbs", "Etymology", "Technical Vocabulary",
                    "Complex Grammar", "Conditional Sentences", "Reported Speech",
                    "Complex and Compound Sentences", "Phrases and Clauses", "Gerunds and Participles",
                    "Infinitives", "Modal Verbs", "Advanced Punctuation", "Editing and Proofreading",
                    "Creative Writing - Short Stories", "Play Writing", "Script Writing",
                    "Feature Article Writing", "Editorial Writing", "Speech Writing",
                    "Formal Letter Writing", "Business Communication", "Resume Writing",
                    "Project Reports", "Research Papers - Introduction", "Citation and References",
                    "Literature Studies", "Novel Analysis", "Poetry Analysis", "Drama Studies",
                    "Comparative Literature", "Literary Devices", "Critical Appreciation",
                    "Communication Skills", "Advanced Speaking", "Persuasive Speaking",
                    "Argumentative Skills", "Media Analysis", "Digital Literacy",
                    "Information Evaluation", "Critical Thinking through Language"
                ],
                5: [
                    # Grade 5 English
                    "Comprehensive Reading Skills", "Speed Reading Techniques", "Analytical Reading",
                    "Critical Evaluation of Texts", "Research Methodology", "Information Synthesis",
                    "Academic Writing", "Technical Writing", "Professional Communication",
                    "Advanced Grammar Concepts", "Syntax and Semantics", "Stylistics",
                    "Register and Style", "Discourse Analysis", "Pragmatics",
                    "Sociolinguistics", "Psycholinguistics", "Applied Linguistics",
                    "Literary Criticism", "Contemporary Literature", "World Literature",
                    "Comparative Studies", "Cultural Studies through Literature", "Media Studies",
                    "Journalism", "Mass Communication", "Digital Communication",
                    "Multimedia Presentations", "Web Content Writing", "Social Media Communication",
                    "Professional Writing", "Grant Writing", "Proposal Writing",
                    "Academic Research", "Thesis Writing", "Scholarly Communication",
                    "Public Speaking - Advanced", "Rhetoric", "Debate and Discussion",
                    "Cross-cultural Communication", "Global English", "English for Specific Purposes"
                ],
                6: [
                    # Grade 6 English
                    "Reading Comprehension - Multiple Text Types", "Literary and Non-literary Texts",
                    "Inference and Analysis", "Critical Reading Skills", "Reading Strategies",
                    "Vocabulary Development", "Context Clues", "Word Analysis", "Semantic Relationships",
                    "Academic Vocabulary", "Grammar - Comprehensive Review", "Complex Sentence Structures",
                    "Voice and Mood", "Conditional Constructions", "Relative Clauses",
                    "Parallel Structure", "Modifiers", "Cohesion and Coherence",
                    "Writing Process", "Pre-writing Strategies", "Drafting and Revision",
                    "Editing Techniques", "Paragraph Development", "Essay Writing - Various Types",
                    "Descriptive Writing", "Narrative Techniques", "Expository Writing",
                    "Persuasive Writing", "Creative Writing", "Poetry Writing",
                    "Drama and Script Writing", "Formal and Informal Writing",
                    "Literature Study", "Short Stories", "Poetry Analysis", "Drama Studies",
                    "Novel Study", "Character Analysis", "Plot Development", "Setting and Atmosphere",
                    "Theme Exploration", "Literary Devices", "Figurative Language",
                    "Communication Skills", "Listening Skills", "Speaking Fluency",
                    "Presentation Skills", "Discussion Techniques", "Interview Skills",
                    "Media Literacy", "Information Literacy", "Research Skills"
                ],
                7: [
                    # Grade 7 English
                    "Advanced Reading Comprehension", "Text Analysis", "Comparative Reading",
                    "Critical Evaluation", "Research Reading", "Academic Reading Skills",
                    "Advanced Vocabulary", "Morphology", "Semantic Fields", "Collocation",
                    "Register and Style", "Advanced Grammar", "Complex Syntax",
                    "Discourse Markers", "Stylistic Devices", "Error Analysis",
                    "Writing Skills - Advanced", "Academic Writing", "Research Writing",
                    "Technical Writing", "Creative Writing Techniques", "Genre Writing",
                    "Argumentative Essays", "Analytical Writing", "Synthesis Essays",
                    "Comparative Essays", "Review Writing", "Editorial Writing",
                    "Literature Studies", "Genre Studies", "Thematic Analysis",
                    "Historical Context", "Cultural Analysis", "Biographical Studies",
                    "Literary Criticism Introduction", "Contemporary Issues in Literature",
                    "Communication Studies", "Rhetorical Analysis", "Persuasion Techniques",
                    "Public Speaking Advanced", "Debate Skills", "Group Communication",
                    "Interpersonal Communication", "Cross-cultural Communication",
                    "Media Analysis", "Digital Literacy", "Information Evaluation",
                    "Technology in Communication", "Ethics in Communication"
                ],
                8: [
                    # Grade 8 English
                    "Critical Reading Skills", "Textual Analysis", "Interpretive Reading",
                    "Evaluative Reading", "Synthesis of Multiple Sources", "Research Methodology",
                    "Academic Research Skills", "Information Literacy", "Source Evaluation",
                    "Advanced Vocabulary Studies", "Etymology", "Semantic Change",
                    "Linguistic Variation", "Grammar in Context", "Functional Grammar",
                    "Text Grammar", "Discourse Analysis", "Pragmatic Competence",
                    "Advanced Writing", "Academic Genres", "Professional Writing",
                    "Technical Communication", "Grant Writing", "Proposal Writing",
                    "Research Papers", "Thesis Statements", "Evidence and Support",
                    "Citation and Documentation", "Plagiarism Awareness", "Ethical Writing",
                    "Literature and Society", "Cultural Studies", "Postcolonial Literature",
                    "Gender Studies", "Environmental Literature", "Digital Literature",
                    "Multimedia Literature", "Performance Studies", "Oral Traditions",
                    "Advanced Communication", "Intercultural Communication", "Professional Communication",
                    "Leadership Communication", "Crisis Communication", "Negotiation Skills",
                    "Conflict Resolution", "Team Communication", "Organizational Communication",
                    "Media Literacy Advanced", "Critical Media Analysis", "Production Skills"
                ],
                9: [
                    # Grade 9 English
                    "Comprehensive Literature Study", "Drama Analysis", "Poetry Criticism",
                    "Prose Analysis", "Novel Studies", "Short Story Analysis",
                    "Comparative Literature", "World Literature", "Regional Literature",
                    "Contemporary Literature", "Classical Literature", "Modern Literature",
                    "Literary Movements", "Literary History", "Genre Studies",
                    "Critical Theory Introduction", "Feminist Criticism", "Marxist Criticism",
                    "Psychoanalytic Criticism", "New Criticism", "Reader Response Theory",
                    "Advanced Writing Skills", "Academic Essays", "Research Methodology",
                    "Thesis Writing", "Dissertation Skills", "Scholarly Writing",
                    "Creative Writing Advanced", "Fiction Writing", "Poetry Composition",
                    "Dramatic Writing", "Screenplay Writing", "Journalism",
                    "Feature Writing", "Editorial Writing", "Column Writing",
                    "Communication Theory", "Mass Communication", "Digital Media",
                    "Social Media Analysis", "Visual Communication", "Multimedia Communication",
                    "Professional Communication", "Business Writing", "Technical Documentation",
                    "Grant Proposals", "Policy Writing", "Legal Writing Introduction",
                    "Translation Studies", "Comparative Linguistics", "Sociolinguistics",
                    "Applied Linguistics", "Language Acquisition", "Second Language Studies"
                ],
                10: [
                    # Grade 10 English
                    "Advanced Literary Analysis", "Critical Theory Application", "Textual Criticism",
                    "Literary Research", "Scholarly Writing", "Academic Discourse",
                    "Thesis Development", "Research Methodology Advanced", "Primary Source Analysis",
                    "Secondary Source Integration", "Interdisciplinary Studies", "Cultural Studies",
                    "Media Studies", "Film Studies", "Visual Culture",
                    "Digital Humanities", "Corpus Linguistics", "Computational Linguistics",
                    "Professional Writing", "Technical Communication", "Science Writing",
                    "Medical Writing", "Legal Writing", "Business Communication",
                    "International Communication", "Diplomatic Language", "Cross-cultural Studies",
                    "Translation Theory", "Interpretation Skills", "Multilingual Communication",
                    "Language Policy", "Language Planning", "Educational Linguistics",
                    "Psycholinguistics", "Neurolinguistics", "Cognitive Linguistics",
                    "Pragmatics", "Discourse Analysis", "Conversation Analysis",
                    "Rhetoric and Composition", "Writing Studies", "Literacy Studies",
                    "Critical Pedagogy", "Democratic Education", "Global Citizenship",
                    "Environmental Communication", "Science Communication", "Health Communication",
                    "Political Communication", "Social Justice Communication", "Human Rights Discourse"
                ],
                11: [
                    # Grade 11 English
                    "Advanced Literary Studies", "Contemporary Critical Theory", "Postmodern Literature",
                    "Digital Literature", "Hypertext Fiction", "Interactive Media",
                    "Performance Studies", "Cultural Performance", "Oral Literature",
                    "Folk Literature", "Popular Culture Studies", "Youth Literature",
                    "Graphic Novels", "Comics Studies", "Visual Narrative",
                    "Film and Literature", "Adaptation Studies", "Transmedia Storytelling",
                    "Creative Writing Workshop", "Fiction Workshop", "Poetry Workshop",
                    "Drama Workshop", "Screenwriting", "Digital Storytelling",
                    "Podcasting", "Blogging", "Social Media Writing",
                    "Professional Development", "Career Writing", "Portfolio Development",
                    "Graduate School Preparation", "Standardized Test Preparation",
                    "Academic Conferences", "Presentation Skills Advanced", "Publication Skills",
                    "Editorial Skills", "Peer Review", "Scholarly Collaboration",
                    "International Literature", "Comparative Cultural Studies", "Diaspora Literature",
                    "Migration Literature", "Border Studies", "Transnational Literature",
                    "Ecocriticism", "Environmental Humanities", "Climate Fiction",
                    "Science Fiction Studies", "Fantasy Literature", "Speculative Fiction",
                    "Indigenous Literature", "Decolonizing Literature", "Social Justice Literature"
                ],
                12: [
                    # Grade 12 English
                    "Literary Theory and Criticism", "Advanced Critical Analysis", "Research Methodology",
                    "Scholarly Research", "Thesis Writing", "Academic Publishing",
                    "Conference Presentations", "Peer Review Process", "Grant Writing",
                    "Professional Academic Writing", "Curriculum Development", "Educational Research",
                    "Action Research", "Qualitative Research", "Quantitative Research",
                    "Mixed Methods Research", "Data Analysis", "Statistical Analysis",
                    "Creative Writing Portfolio", "Professional Writing Portfolio", "Digital Portfolio",
                    "Online Presence", "Professional Networking", "Career Preparation",
                    "Graduate Studies Preparation", "Comprehensive Examinations", "Qualifying Examinations",
                    "Teaching Preparation", "Pedagogical Theory", "Classroom Management",
                    "Assessment and Evaluation", "Curriculum Design", "Educational Technology",
                    "Distance Learning", "Online Education", "Blended Learning",
                    "Multimedia Education", "Universal Design", "Inclusive Education",
                    "Cultural Competency", "Global Awareness", "Social Responsibility",
                    "Ethical Leadership", "Community Engagement", "Public Service",
                    "Advocacy Writing", "Policy Analysis", "Government Communication",
                    "NGO Communication", "International Development", "Sustainable Communication"
                ]
            },
            
            "Mother Tongue": {
                1: [
                    # Grade 1 Mother Tongue (Regional Language)
                    "Alphabet Recognition", "Letter Writing Practice", "Basic Sounds and Pronunciation",
                    "Simple Words Reading", "Picture and Word Association", "Rhymes and Songs",
                    "Story Listening", "Simple Conversations", "Greetings and Polite Expressions",
                    "Family Members Names", "Body Parts Names", "Daily Use Objects",
                    "Colors and Numbers", "Days and Months", "Basic Grammar Introduction",
                    "Simple Sentence Formation", "Oral Expression", "Cultural Stories",
                    "Traditional Games", "Festivals and Celebrations", "Food and Customs",
                    "Regional Geography", "Local Heroes", "Folk Tales",
                    "Moral Stories", "Value Education", "Respect for Elders",
                    "Environmental Awareness", "Cleanliness", "Good Habits",
                    "Friendship and Sharing", "Helping Others", "Honesty and Truth"
                ],
                2: [
                    # Grade 2 Mother Tongue
                    "Reading Fluency", "Comprehension Skills", "Vocabulary Building",
                    "Grammar Basics", "Sentence Construction", "Story Telling",
                    "Poetry Recitation", "Creative Expression", "Letter Writing",
                    "Diary Writing", "Regional Literature", "Folk Literature",
                    "Cultural Heritage", "Traditional Arts", "Music and Dance",
                    "Historical Stories", "Biographical Sketches", "Social Values",
                    "Community Life", "Rural and Urban Life", "Occupations",
                    "Seasonal Activities", "Agricultural Practices", "Trade and Commerce",
                    "Transportation", "Communication", "Technology in Daily Life",
                    "Health and Hygiene", "Nutrition", "Exercise and Games",
                    "Environmental Conservation", "Natural Resources", "Weather and Climate"
                ],
                3: [
                    # Grade 3 Mother Tongue
                    "Advanced Reading", "Literary Appreciation", "Critical Thinking",
                    "Advanced Grammar", "Complex Sentences", "Essay Writing",
                    "Formal and Informal Writing", "Drama and Theatre", "Public Speaking",
                    "Regional History", "Cultural Movements", "Literary Giants",
                    "Classical Literature", "Modern Literature", "Contemporary Issues",
                    "Social Reform", "Women's Rights", "Education and Progress",
                    "Science and Technology", "Innovation", "Entrepreneurship",
                    "Global Awareness", "International Relations", "Cultural Exchange",
                    "Translation Skills", "Comparative Literature", "Media Literacy",
                    "Digital Communication", "Research Skills", "Information Management",
                    "Critical Analysis", "Logical Reasoning", "Problem Solving"
                ],
                4: [
                    # Grade 4 Mother Tongue
                    "Literary Analysis", "Textual Criticism", "Research Methodology",
                    "Academic Writing", "Scholarly Communication", "Professional Writing",
                    "Creative Writing", "Poetry Composition", "Fiction Writing",
                    "Drama Writing", "Journalism", "Editorial Writing",
                    "Cultural Studies", "Anthropological Studies", "Sociological Analysis",
                    "Historical Research", "Archaeological Studies", "Linguistic Studies",
                    "Dialectology", "Language Variation", "Language Change",
                    "Comparative Linguistics", "Etymology", "Morphology",
                    "Syntax", "Semantics", "Pragmatics",
                    "Discourse Analysis", "Stylistics", "Rhetoric",
                    "Translation Theory", "Interpretation", "Cross-cultural Communication"
                ],
                5: [
                    # Grade 5 Mother Tongue
                    "Advanced Literary Studies", "Critical Theory", "Postcolonial Studies",
                    "Gender Studies", "Subaltern Studies", "Dalit Literature",
                    "Tribal Literature", "Environmental Literature", "Urban Literature",
                    "Diaspora Literature", "Digital Literature", "Performance Studies",
                    "Oral Traditions", "Folk Studies", "Popular Culture",
                    "Media Studies", "Film Studies", "Visual Culture",
                    "Cultural Industries", "Heritage Studies", "Tourism Studies",
                    "Language Policy", "Language Planning", "Educational Linguistics",
                    "Applied Linguistics", "Computational Linguistics", "Corpus Linguistics",
                    "Psycholinguistics", "Neurolinguistics", "Sociolinguistics",
                    "Multilingualism", "Language Contact", "Language Maintenance",
                    "Language Revitalization", "Endangered Languages", "Language Documentation"
                ],
                6: [
                    # Grade 6 Mother Tongue
                    "Classical Literature Study", "Modern Poetry", "Contemporary Prose",
                    "Drama and Theatre Arts", "Short Story Analysis", "Novel Reading",
                    "Biography and Autobiography", "Travel Literature", "Historical Narratives",
                    "Scientific Literature", "Children's Literature", "Young Adult Fiction",
                    "Grammar and Composition", "Advanced Syntax", "Stylistic Analysis",
                    "Rhetoric and Oratory", "Public Speaking", "Debate Skills",
                    "Creative Writing", "Poetry Workshop", "Story Writing",
                    "Script Writing", "Journalism", "Feature Writing",
                    "Cultural Heritage", "Traditional Knowledge", "Folk Wisdom",
                    "Regional Geography", "Local History", "Community Studies",
                    "Social Issues", "Gender Equality", "Environmental Concerns",
                    "Human Rights", "Democratic Values", "Constitutional Principles"
                ],
                7: [
                    # Grade 7 Mother Tongue
                    "Literary Criticism", "Theoretical Frameworks", "Reader Response Theory",
                    "Feminist Criticism", "Marxist Analysis", "Postcolonial Theory",
                    "Psychoanalytic Criticism", "New Historicism", "Cultural Materialism",
                    "Deconstruction", "Formalism", "Structuralism",
                    "Advanced Writing", "Research Papers", "Thesis Writing",
                    "Academic Discourse", "Scholarly Communication", "Conference Papers",
                    "Professional Writing", "Technical Writing", "Business Communication",
                    "Administrative Writing", "Legal Writing", "Medical Writing",
                    "Language Studies", "Historical Linguistics", "Comparative Grammar",
                    "Dialectology", "Sociolinguistics", "Psycholinguistics",
                    "Applied Linguistics", "Language Teaching", "Language Learning",
                    "Translation Studies", "Interpretation", "Multilingual Communication"
                ],
                8: [
                    # Grade 8 Mother Tongue
                    "Research Methodology", "Primary Source Analysis", "Archival Research",
                    "Oral History", "Ethnographic Studies", "Field Work",
                    "Data Collection", "Qualitative Analysis", "Quantitative Methods",
                    "Statistical Analysis", "Digital Humanities", "Corpus Studies",
                    "Computational Methods", "Text Mining", "Data Visualization",
                    "Publishing Studies", "Editorial Skills", "Manuscript Preparation",
                    "Book Production", "Digital Publishing", "Open Access",
                    "Copyright Issues", "Intellectual Property", "Fair Use",
                    "Plagiarism", "Research Ethics", "Academic Integrity",
                    "Professional Ethics", "Social Responsibility", "Public Engagement",
                    "Community Outreach", "Cultural Preservation", "Heritage Conservation",
                    "Language Maintenance", "Cultural Transmission", "Intergenerational Communication"
                ],
                9: [
                    # Grade 9 Mother Tongue
                    "Advanced Literary Theory", "Contemporary Criticism", "Interdisciplinary Studies",
                    "Cultural Studies", "Media Studies", "Visual Culture",
                    "Performance Studies", "Digital Humanities", "New Media",
                    "Hypertext", "Interactive Fiction", "Virtual Reality",
                    "Augmented Reality", "Gaming Studies", "Digital Storytelling",
                    "Podcasting", "Video Production", "Multimedia Creation",
                    "Social Media", "Online Communities", "Digital Activism",
                    "Information Literacy", "Media Literacy", "Critical Media Analysis",
                    "Propaganda Analysis", "Fact Checking", "News Literacy",
                    "Global Communication", "Cross-cultural Studies", "International Literature",
                    "World Literature", "Comparative Literature", "Translation Studies",
                    "Interpreting", "Multilingual Communication", "Language Policy"
                ],
                10: [
                    # Grade 10 Mother Tongue
                    "Comprehensive Literary Analysis", "Critical Theory Application", "Research Project",
                    "Independent Study", "Capstone Project", "Portfolio Development",
                    "Professional Presentation", "Public Defense", "Peer Review",
                    "Collaborative Research", "Team Projects", "Leadership Skills",
                    "Project Management", "Grant Writing", "Funding Applications",
                    "Publication Preparation", "Journal Submission", "Editorial Process",
                    "Peer Review Process", "Academic Networking", "Professional Development",
                    "Career Preparation", "Graduate School Preparation", "Scholarship Applications",
                    "Interview Skills", "Portfolio Presentation", "Professional Writing",
                    "CV Preparation", "Cover Letter Writing", "Job Applications",
                    "Internship Preparation", "Work Experience", "Professional Mentoring"
                ],
                11: [
                    # Grade 11 Mother Tongue
                    "Specialized Literary Studies", "Genre Theory", "Narrative Theory",
                    "Poetry Theory", "Drama Theory", "Film Theory",
                    "Visual Studies", "Sound Studies", "Material Culture",
                    "Book History", "Print Culture", "Reading History",
                    "Audience Studies", "Reception Theory", "Cultural Reception",
                    "Canon Formation", "Literary Institutions", "Publishing Industry",
                    "Literary Markets", "Cultural Economics", "Creative Industries",
                    "Cultural Policy", "Arts Administration", "Cultural Management",
                    "Museum Studies", "Archive Studies", "Library Science",
                    "Information Science", "Digital Preservation", "Cultural Heritage",
                    "Tourism and Culture", "Cultural Geography", "Urban Studies",
                    "Rural Studies", "Environmental Humanities", "Sustainability Studies"
                ],
                12: [
                    # Grade 12 Mother Tongue
                    "Doctoral Preparation", "Advanced Research Methods", "Dissertation Proposal",
                    "Literature Review", "Theoretical Framework", "Methodology Design",
                    "Data Collection", "Analysis and Interpretation", "Academic Writing",
                    "Scholarly Publication", "Conference Presentation", "Professional Networking",
                    "Teaching Preparation", "Curriculum Development", "Pedagogical Theory",
                    "Classroom Practice", "Assessment Methods", "Educational Technology",
                    "Distance Learning", "Online Education", "Blended Learning",
                    "Adult Education", "Lifelong Learning", "Professional Development",
                    "Community Education", "Public Programs", "Outreach Activities",
                    "Cultural Programming", "Literary Events", "Reading Promotion",
                    "Literacy Programs", "Language Preservation", "Cultural Advocacy",
                    "Policy Development", "Social Impact", "Cultural Change"
                ]
            },
            
            "Science": {
                1: [
                    # Grade 1 Science
                    "My Body Parts", "Five Senses", "Seeing with Eyes", "Hearing with Ears", "Smelling with Nose",
                    "Tasting with Tongue", "Touching and Feeling", "Keeping Body Clean", "Healthy Habits",
                    "Good Food and Bad Food", "Living and Non-Living Things", "Animals Around Us",
                    "Wild Animals", "Domestic Animals", "Pet Animals", "Farm Animals", "Birds That Fly",
                    "Animals That Swim", "Animals That Crawl", "Baby Animals and Adult Animals",
                    "Plants Around Us", "Parts of a Plant", "Flowers and Fruits", "Trees and Shrubs",
                    "Vegetables We Eat", "Fruits We Eat", "Seeds and Seedlings", "Plants Need Water",
                    "Plants Need Sunlight", "Water in Our Life", "Sources of Water", "Uses of Water",
                    "Clean and Dirty Water", "Air Around Us", "Moving Air - Wind", "Things That Float",
                    "Things That Sink", "Hot and Cold", "Day and Night", "Sun, Moon and Stars",
                    "Weather - Sunny, Rainy, Cloudy", "Seasons - Summer, Winter, Monsoon", "My Family",
                    "Types of Houses", "Our School", "Safety Rules", "Things Made of Different Materials"
                ],
                2: [
                    # Grade 2 Science
                    "Human Body Systems", "Digestive System - Simple", "Breathing and Lungs", "Heart and Blood",
                    "Bones and Muscles", "Growing and Changing", "Food Groups", "Balanced Diet",
                    "Vitamins and Minerals", "Junk Food vs Healthy Food", "Personal Hygiene",
                    "Dental Care", "Exercise and Health", "Animal Classification", "Mammals", "Birds",
                    "Reptiles", "Fish", "Insects", "Animal Habitats", "Forest Animals", "Desert Animals",
                    "Polar Animals", "Ocean Animals", "Mountain Animals", "Animal Movement",
                    "Animal Sounds", "Animal Babies", "How Animals Protect Themselves", "Migration of Animals",
                    "Plant Classification", "Flowering and Non-flowering Plants", "Medicinal Plants",
                    "Poisonous Plants", "How Plants Make Food", "How Plants Breathe", "How Plants Reproduce",
                    "Dispersal of Seeds", "Germination", "Plant Adaptations", "Water Cycle - Simple",
                    "States of Water", "Water Conservation", "Air Pollution", "Water Pollution",
                    "Soil Types", "Layers of Earth", "Rocks and Minerals", "Volcanoes - Simple",
                    "Earthquakes - Simple", "Weather Patterns", "Clouds and Rain", "Thunder and Lightning",
                    "Solar System - Introduction", "Planets", "Satellites", "Space Travel"
                ],
                3: [
                    # Grade 3 Science
                    "Advanced Body Systems", "Circulatory System", "Respiratory System", "Nervous System",
                    "Excretory System", "Reproductive System - Basic", "Immunity and Diseases",
                    "Communicable Diseases", "Non-communicable Diseases", "Prevention of Diseases",
                    "First Aid", "Emergency Care", "Nutrition Science", "Metabolism", "Calories and Energy",
                    "Food Preservation", "Food Safety", "Advanced Animal Studies", "Vertebrates and Invertebrates",
                    "Animal Behavior", "Animal Intelligence", "Endangered Animals", "Wildlife Conservation",
                    "Animal Rights", "Domestication", "Breeding", "Genetics - Introduction",
                    "Heredity", "Variation", "Advanced Plant Studies", "Plant Physiology",
                    "Photosynthesis", "Plant Nutrition", "Plant Diseases", "Plant Breeding",
                    "Genetic Engineering - Introduction", "Biotechnology - Basic", "Agriculture Science",
                    "Crop Production", "Irrigation", "Fertilizers", "Pesticides", "Organic Farming",
                    "Environmental Science", "Ecosystem", "Food Chain", "Food Web", "Biodiversity",
                    "Conservation", "Pollution Control", "Renewable Energy", "Climate Change",
                    "Global Warming", "Sustainable Development", "Physical Science", "Matter and Energy",
                    "Properties of Matter", "Chemical Reactions", "Acids and Bases", "Metals and Non-metals"
                ],
                4: [
                    # Grade 4 Science
                    "Cell Biology", "Plant and Animal Cells", "Cell Structure", "Cell Functions",
                    "Tissues and Organs", "Organ Systems", "Microbiology", "Bacteria and Viruses",
                    "Beneficial Microorganisms", "Harmful Microorganisms", "Antibiotics", "Vaccines",
                    "Advanced Genetics", "DNA and RNA", "Chromosomes", "Genetic Disorders",
                    "Gene Therapy", "Cloning", "Stem Cells", "Evolution", "Natural Selection",
                    "Adaptation", "Speciation", "Fossil Records", "Ecology", "Population Dynamics",
                    "Community Ecology", "Ecosystem Services", "Conservation Biology", "Environmental Management",
                    "Pollution Studies", "Toxicology", "Environmental Health", "Sustainable Technologies",
                    "Green Chemistry", "Alternative Energy", "Waste Management", "Recycling Technologies",
                    "Physics Fundamentals", "Motion and Forces", "Energy Transformations", "Waves and Sound",
                    "Light and Optics", "Electricity and Magnetism", "Atomic Structure", "Radioactivity",
                    "Chemistry Fundamentals", "Periodic Table", "Chemical Bonding", "Organic Chemistry",
                    "Biochemistry", "Analytical Chemistry", "Earth Sciences", "Geology", "Meteorology",
                    "Oceanography", "Astronomy", "Space Science", "Planetary Science"
                ],
                5: [
                    # Grade 5 Science
                    "Advanced Biology", "Molecular Biology", "Genetics and Genomics", "Proteomics",
                    "Bioinformatics", "Systems Biology", "Synthetic Biology", "Developmental Biology",
                    "Neuroscience", "Cognitive Science", "Behavioral Biology", "Ecology and Evolution",
                    "Conservation Genetics", "Population Biology", "Landscape Ecology", "Climate Biology",
                    "Astrobiology", "Marine Biology", "Freshwater Biology", "Terrestrial Biology",
                    "Advanced Chemistry", "Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry",
                    "Analytical Chemistry", "Biochemistry", "Environmental Chemistry", "Materials Chemistry",
                    "Nanotechnology", "Catalysis", "Electrochemistry", "Spectroscopy",
                    "Advanced Physics", "Classical Mechanics", "Thermodynamics", "Electromagnetism",
                    "Optics", "Modern Physics", "Quantum Mechanics", "Relativity", "Particle Physics",
                    "Nuclear Physics", "Condensed Matter Physics", "Plasma Physics", "Astrophysics",
                    "Earth and Environmental Sciences", "Geophysics", "Geochemistry", "Hydrology",
                    "Atmospheric Sciences", "Climate Science", "Environmental Monitoring", "Remote Sensing",
                    "GIS Applications", "Sustainability Science", "Renewable Energy Technologies", "Carbon Sequestration"
                ],
                6: [
                    # Grade 6 Science
                    "Scientific Method", "Observation and Hypothesis", "Experimental Design", "Data Collection",
                    "Data Analysis", "Scientific Communication", "Basic Biology", "Cell Structure and Function",
                    "Plant and Animal Tissues", "Nutrition in Plants", "Nutrition in Animals", "Respiration",
                    "Transportation", "Excretion", "Control and Coordination", "Reproduction",
                    "Basic Chemistry", "Matter and its Properties", "Pure Substances and Mixtures",
                    "Elements, Compounds and Mixtures", "Acids, Bases and Salts", "Metals and Non-metals",
                    "Carbon and its Compounds", "Periodic Classification", "Chemical Reactions",
                    "Basic Physics", "Motion", "Force and Laws of Motion", "Gravitation", "Work and Energy",
                    "Sound", "Light", "Electricity", "Magnetic Effects of Electric Current",
                    "Sources of Energy", "Environmental Science", "Natural Resource Management",
                    "Water Resources", "Forest and Wildlife", "Coal and Petroleum", "Pollution",
                    "Waste Management", "Biodiversity", "Sustainable Development"
                ],
                7: [
                    # Grade 7 Science
                    "Advanced Scientific Methods", "Research Design", "Statistical Analysis", "Scientific Writing",
                    "Peer Review", "Advanced Biology", "Genetics and Inheritance", "Evolution",
                    "Classification of Living Organisms", "Structural Organization", "Life Processes",
                    "Control and Coordination in Animals", "Reproduction in Animals", "Heredity and Variation",
                    "Advanced Chemistry", "Atomic Structure", "Chemical Bonding", "Acid-Base Chemistry",
                    "Redox Reactions", "Thermochemistry", "Chemical Kinetics", "Equilibrium",
                    "Organic Chemistry Basics", "Advanced Physics", "Kinematics", "Dynamics",
                    "Work, Energy and Power", "Rotational Motion", "Gravitation", "Mechanical Properties",
                    "Thermal Properties", "Oscillations and Waves", "Ray Optics", "Wave Optics",
                    "Electric Charges and Fields", "Current Electricity", "Magnetic Field",
                    "Electromagnetic Induction", "Advanced Environmental Science", "Ecosystem Dynamics",
                    "Biogeochemical Cycles", "Environmental Impact Assessment", "Climate Change Science",
                    "Renewable Energy Systems", "Environmental Biotechnology"
                ],
                8: [
                    # Grade 8 Science
                    "Research Methodology", "Scientific Ethics", "Laboratory Safety", "Instrumentation",
                    "Data Management", "Scientific Modeling", "Advanced Cell Biology", "Molecular Biology",
                    "Biochemistry", "Biotechnology", "Genetic Engineering", "Bioinformatics",
                    "Microbiology", "Immunology", "Pharmacology", "Toxicology", "Advanced Chemistry",
                    "Quantum Chemistry", "Coordination Chemistry", "Organometallic Chemistry",
                    "Polymer Chemistry", "Materials Science", "Nanotechnology", "Analytical Techniques",
                    "Spectroscopy", "Chromatography", "Advanced Physics", "Quantum Mechanics",
                    "Statistical Mechanics", "Solid State Physics", "Nuclear Physics", "Particle Physics",
                    "Astrophysics", "Plasma Physics", "Advanced Earth Sciences", "Geophysics",
                    "Geochemistry", "Paleontology", "Stratigraphy", "Tectonics", "Volcanology",
                    "Seismology", "Hydrology", "Oceanography", "Atmospheric Physics", "Climate Modeling",
                    "Environmental Monitoring", "Remote Sensing", "GIS Applications"
                ],
                9: [
                    # Grade 9 Science
                    "Matter in Our Surroundings", "Is Matter Around Us Pure", "Atoms and Molecules",
                    "Structure of the Atom", "The Fundamental Unit of Life", "Tissues", "Diversity in Living Organisms",
                    "Motion", "Force and Laws of Motion", "Gravitation", "Work and Energy", "Sound",
                    "Why Do We Fall Ill", "Natural Resources", "Improvement in Food Resources",
                    "Atomic Structure", "Chemical Bonding", "Periodic Table", "Chemical Reactions",
                    "States of Matter", "Solutions", "Acids and Bases", "Metals and Non-metals",
                    "Cell Biology", "Plant Physiology", "Animal Physiology", "Reproduction",
                    "Heredity and Variation", "Evolution", "Classification", "Ecology",
                    "Kinematics", "Dynamics", "Energy and Power", "Oscillations", "Waves",
                    "Optics", "Electricity", "Magnetism", "Modern Physics Introduction"
                ],
                10: [
                    # Grade 10 Science
                    "Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals",
                    "Carbon and its Compounds", "Periodic Classification of Elements", "Life Processes",
                    "Control and Coordination", "How do Organisms Reproduce", "Heredity and Evolution",
                    "Light - Reflection and Refraction", "Human Eye and Colourful World", "Electricity",
                    "Magnetic Effects of Electric Current", "Sources of Energy", "Our Environment", "Management of Natural Resources",
                    "Advanced Chemical Reactions", "Electrochemistry", "Surface Chemistry", "Nuclear Chemistry",
                    "Coordination Compounds", "Biomolecules", "Polymers", "Chemistry in Everyday Life",
                    "Advanced Life Processes", "Neural Control and Coordination", "Chemical Coordination",
                    "Reproduction in Organisms", "Sexual Reproduction in Plants", "Human Reproduction",
                    "Reproductive Health", "Principles of Inheritance", "Molecular Basis of Inheritance",
                    "Evolution", "Human Health and Disease", "Microbes in Human Welfare",
                    "Biotechnology Principles", "Biotechnology Applications", "Organisms and Populations",
                    "Ecosystem", "Biodiversity and Conservation", "Environmental Issues"
                ],
                11: [
                    # Grade 11 Science
                    "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements",
                    "Chemical Bonding and Molecular Structure", "States of Matter", "Thermodynamics",
                    "Equilibrium", "Redox Reactions", "Hydrogen", "s-Block Elements", "p-Block Elements",
                    "Organic Chemistry - Basic Principles", "Hydrocarbons", "Environmental Chemistry",
                    "The Living World", "Biological Classification", "Plant Kingdom", "Animal Kingdom",
                    "Morphology of Flowering Plants", "Anatomy of Flowering Plants", "Structural Organization in Animals",
                    "Cell - The Unit of Life", "Biomolecules", "Cell Cycle and Cell Division",
                    "Transport in Plants", "Mineral Nutrition", "Photosynthesis in Higher Plants",
                    "Respiration in Plants", "Plant Growth and Development", "Digestion and Absorption",
                    "Breathing and Exchange of Gases", "Body Fluids and Circulation", "Excretory Products and Elimination",
                    "Locomotion and Movement", "Neural Control and Coordination", "Chemical Coordination and Integration",
                    "Physical World", "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane",
                    "Laws of Motion", "Work, Energy and Power", "System of Particles and Rotational Motion",
                    "Gravitation", "Mechanical Properties of Solids", "Mechanical Properties of Fluids",
                    "Thermal Properties of Matter", "Thermodynamics", "Kinetic Theory", "Oscillations",
                    "Waves"
                ],
                12: [
                    # Grade 12 Science
                    "Solid State", "Solutions", "Electrochemistry", "Chemical Kinetics", "Surface Chemistry",
                    "General Principles and Processes of Isolation of Elements", "p-Block Elements",
                    "d and f Block Elements", "Coordination Compounds", "Haloalkanes and Haloarenes",
                    "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids",
                    "Amines", "Biomolecules", "Polymers", "Chemistry in Everyday Life",
                    "Reproduction in Organisms", "Sexual Reproduction in Flowering Plants", "Human Reproduction",
                    "Reproductive Health", "Principles of Inheritance and Variation", "Molecular Basis of Inheritance",
                    "Evolution", "Human Health and Disease", "Strategies for Enhancement in Food Production",
                    "Microbes in Human Welfare", "Biotechnology - Principles and Processes",
                    "Biotechnology and its Applications", "Organisms and Populations", "Ecosystem",
                    "Biodiversity and Conservation", "Environmental Issues", "Electric Charges and Fields",
                    "Electrostatic Potential and Capacitance", "Current Electricity", "Moving Charges and Magnetism",
                    "Magnetism and Matter", "Electromagnetic Induction", "Alternating Current",
                    "Electromagnetic Waves", "Ray Optics and Optical Instruments", "Wave Optics",
                    "Dual Nature of Radiation and Matter", "Atoms", "Nuclei", "Semiconductor Electronics",
                    "Communication Systems"
                ]
            },
            
            "Social Science": {
                1: [
                    # Grade 1 Social Science
                    "Myself and My Family", "My Name and Age", "Family Members", "Family Tree",
                    "Roles in Family", "Helping Family Members", "Family Traditions", "My Home",
                    "Types of Houses", "Rooms in a House", "Furniture and Uses", "My Neighborhood",
                    "People in Neighborhood", "Neighborhood Helpers", "Community Services", "My School",
                    "School Building", "Classroom", "School Staff", "School Rules", "Friends at School",
                    "Festivals and Celebrations", "National Festivals", "Regional Festivals", "Religious Festivals",
                    "How We Celebrate", "Special Days", "Independence Day", "Republic Day", "Gandhi Jayanti",
                    "Our Country India", "National Flag", "National Anthem", "National Animal", "National Bird",
                    "Maps and Directions", "Left and Right", "Near and Far", "Our Village/City",
                    "Means of Transport", "Land Transport", "Water Transport", "Air Transport",
                    "Communication", "Post Office", "Telephone", "Good Habits", "Cleanliness",
                    "Sharing and Caring", "Helping Others", "Saying Please and Thank You"
                ],
                2: [
                    # Grade 2 Social Science
                    "Our Heritage", "Historical Places", "Monuments", "Forts and Palaces", "Museums",
                    "Our Culture", "Languages", "Dress", "Food", "Dance and Music", "Arts and Crafts",
                    "Geography of India", "Physical Features", "Mountains", "Rivers", "Plains", "Deserts",
                    "Coastal Areas", "Climate and Seasons", "Natural Resources", "Forests", "Wildlife",
                    "States and Union Territories", "Capital Cities", "Important Cities", "Rural and Urban Areas",
                    "Agriculture", "Crops", "Farmers", "Irrigation", "Industries", "Mining", "Fishing",
                    "Government", "Local Government", "Panchayat", "Municipality", "State Government",
                    "Central Government", "Prime Minister", "President", "Democracy", "Voting",
                    "Rights and Duties", "Fundamental Rights", "Fundamental Duties", "Child Rights",
                    "Women Rights", "Equality", "Justice", "Liberty", "Economic Concepts",
                    "Needs and Wants", "Goods and Services", "Money", "Banking", "Saving", "Spending",
                    "Markets", "Trade", "Transportation of Goods", "Global Connections"
                ],
                3: [
                    # Grade 3 Social Science
                    "Ancient Indian History", "Indus Valley Civilization", "Vedic Period", "Mauryan Empire",
                    "Gupta Empire", "Medieval Indian History", "Delhi Sultanate", "Mughal Empire",
                    "Vijayanagara Empire", "Maratha Empire", "British Colonial Period", "East India Company",
                    "Sepoy Mutiny 1857", "Freedom Struggle", "Indian National Congress", "Leaders of Freedom Movement",
                    "Mahatma Gandhi", "Jawaharlal Nehru", "Subhas Chandra Bose", "Independence and Partition",
                    "Modern Indian Geography", "Political Map", "Physical Divisions", "Northern Mountains",
                    "Northern Plains", "Peninsular Plateau", "Coastal Plains", "Islands", "Climate Zones",
                    "Monsoons", "Natural Vegetation", "Soil Types", "Water Resources", "River Systems",
                    "Drainage Patterns", "Natural Disasters", "Population", "Demographics", "Migration",
                    "Urbanization", "Rural Development", "Political Science", "Constitution of India",
                    "Fundamental Rights", "Fundamental Duties", "Directive Principles", "Federal Structure",
                    "Parliamentary System", "Judiciary", "Elections", "Political Parties", "Governance",
                    "Economic Development", "Planning", "Five Year Plans", "Agriculture", "Industry",
                    "Services Sector", "Trade and Commerce", "Banking and Finance", "International Relations"
                ],
                4: [
                    # Grade 4 Social Science
                    "Advanced Indian History", "Regional Kingdoms", "Cultural Synthesis", "Art and Architecture",
                    "Literature and Philosophy", "Science and Technology", "Social Reforms", "Religious Movements",
                    "Colonial Resistance", "Tribal Uprisings", "Peasant Movements", "Worker's Movements",
                    "Women's Movements", "Nationalist Literature", "Revolutionary Activities", "Non-violent Resistance",
                    "Constitutional Development", "Government of India Acts", "Cabinet Mission", "Integration of States",
                    "Advanced Geography", "Physiographic Divisions", "Geological Structure", "Mineral Resources",
                    "Energy Resources", "Industrial Geography", "Agricultural Geography", "Transportation Networks",
                    "Communication Systems", "Trade Patterns", "Regional Development", "Environmental Geography",
                    "Human Geography", "Settlement Patterns", "Cultural Geography", "Economic Geography",
                    "Political Geography", "International Boundaries", "Geopolitics", "Advanced Political Science",
                    "Constitutional Law", "Administrative System", "Public Policy", "International Relations",
                    "Diplomacy", "Global Organizations", "Regional Cooperation", "Security Issues",
                    "Human Rights", "Social Justice", "Advanced Economics", "Development Economics",
                    "Public Finance", "Monetary Policy", "Fiscal Policy", "International Trade",
                    "Globalization", "Economic Planning", "Sustainable Development", "Environmental Economics"
                ],
                5: [
                    # Grade 5 Social Science
                    "Research Methodology in Social Sciences", "Historiography", "Archaeological Methods",
                    "Anthropological Studies", "Sociological Research", "Political Analysis", "Economic Research",
                    "Geographical Information Systems", "Remote Sensing", "Cartography", "Statistical Methods",
                    "Comparative Studies", "Cross-cultural Analysis", "Interdisciplinary Approaches",
                    "Contemporary Issues", "Gender Studies", "Environmental Studies", "Urban Studies",
                    "Rural Studies", "Development Studies", "International Studies", "Area Studies",
                    "Cultural Studies", "Media Studies", "Public Administration", "Social Policy",
                    "Welfare Economics", "Labor Economics", "Agricultural Economics", "Industrial Economics",
                    "Service Economics", "Digital Economy", "Knowledge Economy", "Innovation Studies",
                    "Technology and Society", "Science Policy", "Education Policy", "Health Policy",
                    "Social Movements", "Civil Society", "Non-governmental Organizations", "Community Development",
                    "Participatory Development", "Sustainable Development Goals", "Climate Change",
                    "Environmental Justice", "Social Entrepreneurship", "Corporate Social Responsibility",
                    "Ethical Leadership", "Global Citizenship", "Peace Studies", "Conflict Resolution"
                ],
                6: [
                    # Grade 6 Social Science
                    "Introduction to History", "What is History", "Sources of History", "Timeline and Chronology",
                    "Prehistoric Times", "Stone Age", "Agriculture and Settlement", "Early Civilizations",
                    "Harappan Civilization", "Mesopotamian Civilization", "Egyptian Civilization", "Chinese Civilization",
                    "Vedic Period", "Mauryan Empire", "Gupta Period", "Introduction to Geography",
                    "Earth as a Planet", "Globe and Maps", "Latitude and Longitude", "Physical Features",
                    "Continents and Oceans", "Climate and Weather", "Natural Vegetation", "Wildlife",
                    "Human Settlement", "Rural and Urban Settlement", "Introduction to Civics",
                    "Government", "Levels of Government", "Local Government", "Democracy", "Equality",
                    "Introduction to Economics", "Economic Activities", "Primary Activities", "Secondary Activities",
                    "Tertiary Activities", "Economy of India", "Agriculture in India", "Industries in India"
                ],
                7: [
                    # Grade 7 Social Science
                    "Medieval History", "Delhi Sultanate", "Mughal Empire", "Regional Kingdoms", "Vijayanagara Empire",
                    "Bahmani Kingdom", "Maratha Empire", "Sikh Empire", "European Companies", "Portuguese",
                    "Dutch", "French", "British", "Our Environment", "Environment and its Components",
                    "Natural Environment", "Human Environment", "Human-Environment Interaction", "Life on Earth",
                    "Landforms", "Water Bodies", "Air", "Natural Regions", "Tropical Rainforests",
                    "Tropical Grasslands", "Temperate Grasslands", "Deserts", "Equality in Indian Democracy",
                    "Indian Constitution", "Key Features of Constitution", "Equality and Justice", "Role of Government",
                    "How State Government Works", "Growing up as Boys and Girls", "Women Change the World",
                    "Struggles for Equality", "Economic Systems", "Production and Exchange", "Markets Around Us",
                    "Advertising", "Weekly Markets and Shopping Complexes"
                ],
                8: [
                    # Grade 8 Social Science
                    "Modern History", "Advent of Europeans", "British Conquest", "Economic Impact", "Social and Cultural Changes",
                    "Revolt of 1857", "Growth of Nationalism", "Freedom Movement", "Partition and Independence",
                    "Resources", "Natural Resources", "Land Resources", "Water Resources", "Mineral and Power Resources",
                    "Agriculture", "Industries", "Human Resources", "Population", "Indian Constitution",
                    "Secularism", "Parliament and Making of Laws", "Judiciary", "Understanding Marginalisation",
                    "Confronting Marginalisation", "Public Facilities", "Law and Social Justice", "Economic Presence of Government",
                    "Understanding Development", "Rural Livelihoods", "Urban Livelihoods", "New Kings and Kingdoms",
                    "The Delhi Sultans", "The Mughal Empire", "Rulers and Buildings", "Men, Women and Society"
                ],
                9: [
                    # Grade 9 Social Science
                    "The French Revolution", "Socialism in Europe and the Russian Revolution", "Nazism and the Rise of Hitler",
                    "Forest Society and Colonialism", "Pastoralists in the Modern World", "Peasants and Farmers",
                    "History and Sport", "Clothing: A Social History", "India - Size and Location", "Physical Features of India",
                    "Drainage", "Climate", "Natural Vegetation and Wildlife", "Population", "What is Democracy",
                    "Constitutional Design", "Electoral Politics", "Working of Institutions", "Democratic Rights",
                    "The Story of Village Palampur", "People as Resource", "Poverty as a Challenge", "Food Security in India"
                ],
                10: [
                    # Grade 10 Social Science
                    "The Rise of Nationalism in Europe", "Nationalism in India", "The Making of a Global World",
                    "The Age of Industrialisation", "Print Culture and the Modern World", "Resources and Development",
                    "Forest and Wildlife Resources", "Water Resources", "Agriculture", "Minerals and Energy Resources",
                    "Manufacturing Industries", "Lifelines of National Economy", "Power Sharing", "Federalism",
                    "Democracy and Diversity", "Gender, Religion and Caste", "Popular Struggles and Movements",
                    "Challenges to Democracy", "Development", "Sectors of Indian Economy", "Money and Credit",
                    "Globalisation and the Indian Economy"
                ],
                11: [
                    # Grade 11 Social Science
                    "From the Beginning of Time", "Writing and City Life", "An Empire Across Three Continents",
                    "The Central Islamic Lands", "Nomadic Empires", "The Three Orders", "Changing Cultural Traditions",
                    "Confrontation of Cultures", "Paths to Modernisation", "Displacing Indigenous Peoples",
                    "Native Peoples of America", "India - Physical Environment", "Land and People",
                    "Human Development", "Human Settlements", "Land Resources and Agriculture", "Water Resources",
                    "Mineral and Energy Resources", "Planning and Sustainable Development", "Transport and Communication",
                    "International Trade", "Geographical Perspective on Selected Issues", "Constitution as a Living Document",
                    "Political Theory", "Freedom", "Equality", "Social Justice", "Rights", "Citizenship", "Nationalism",
                    "Secularism", "Peace", "Development", "Indian Economy on the Eve of Independence",
                    "Five Year Plans", "Liberalisation, Privatisation and Globalisation", "Poverty", "Human Capital Formation",
                    "Rural Development", "Employment", "Infrastructure", "Environment and Sustainable Development"
                ],
                12: [
                    # Grade 12 Social Science
                    "The Mughal Empire", "Kings, Farmers and Towns", "Kinship, Caste and Class", "Thinkers, Beliefs and Buildings",
                    "Through the Eyes of Travellers", "Bhakti-Sufi Traditions", "An Imperial Capital", "Peasants, Zamindars and the State",
                    "Kings and Chronicles", "Colonialism and the Countryside", "Rebels and the Raj", "Colonial Cities",
                    "Mahatma Gandhi and the Nationalist Movement", "Partition of India", "Framing the Constitution",
                    "Human Geography", "People and Environment", "The World Population", "Population Composition",
                    "Human Development", "Primary Activities", "Secondary Activities", "Tertiary and Quaternary Activities",
                    "Transport and Communication", "International Trade", "Human Settlements", "Contemporary World Politics",
                    "The Cold War Era", "End of Bipolarity", "US Hegemony", "Alternative Centres of Power",
                    "Contemporary South Asia", "International Organisations", "Security in Contemporary World",
                    "Environment and Natural Resources", "Human Rights", "Globalisation", "Planning and Sustainable Development",
                    "Employment", "Infrastructure", "Human Capital Formation", "Rural Development", "Food Security",
                    "Sustainable Development", "Development Experience of India"
                ]
            },
            
            "EVS (Environmental Studies)": {
                1: [
                    # Grade 1 EVS
                    "My Body", "Care of Body Parts", "My Food", "Healthy Food", "Junk Food",
                    "Water - Need and Sources", "Clean and Dirty Water", "Our Clothes",
                    "Different Types of Clothes", "Seasonal Clothes", "Our House", "Types of Houses",
                    "Rooms in House", "My Family", "Family Members", "Helping at Home",
                    "My School", "School Building", "Classroom", "School Staff", "School Rules",
                    "Safety Rules", "Plants Around Us", "Parts of Plant", "Trees and Bushes",
                    "Flowers and Fruits", "Animals Around Us", "Pet Animals", "Farm Animals",
                    "Wild Animals", "Birds", "Insects", "Means of Transport", "Land Transport",
                    "Water Transport", "Air Transport", "Communication", "Post Office", "Telephone",
                    "Good Habits", "Bad Habits", "Cleanliness", "Personal Hygiene", "Our Helpers",
                    "Doctor", "Teacher", "Police", "Farmer", "Shopkeeper", "Postman",
                    "Festivals", "National Festivals", "Local Festivals", "Celebration"
                ],
                2: [
                    # Grade 2 EVS
                    "Our Body Systems", "Digestive System", "Breathing", "Heart and Blood",
                    "Sense Organs", "Eye and Sight", "Ear and Hearing", "Nose and Smell",
                    "Tongue and Taste", "Skin and Touch", "Nutrition", "Balanced Diet",
                    "Food Groups", "Vitamins and Minerals", "Food Safety", "Food Preservation",
                    "Housing", "Building Materials", "Kutcha and Pucca Houses", "House for Different Climates",
                    "Ventilation", "Sanitation", "Family Life", "Types of Families", "Family Relationships",
                    "Responsibilities", "Community Life", "Neighborhood", "Community Helpers",
                    "Public Places", "Market", "Hospital", "School Community", "Plant Life",
                    "Life Cycle of Plants", "Seed Germination", "Plant Nutrition", "Photosynthesis",
                    "Plant Products", "Medicinal Plants", "Animal Life", "Animal Habitats",
                    "Animal Babies", "Animal Movement", "Animal Sounds", "Animal Products",
                    "Domestic vs Wild Animals", "Environment", "Living and Non-living",
                    "Interdependence", "Food Chain", "Pollution", "Waste Management"
                ],
                3: [
                    # Grade 3 EVS
                    "Advanced Body Care", "First Aid", "Common Diseases", "Prevention of Diseases",
                    "Exercise and Health", "Mental Health", "Stress Management", "Advanced Nutrition",
                    "Traditional Food", "Regional Cuisine", "Cooking Methods", "Food Wastage",
                    "Organic Farming", "Kitchen Gardening", "Housing and Settlement", "Urban Planning",
                    "Rural vs Urban", "Migration", "Slums and Housing", "Smart Cities",
                    "Water Conservation", "Rainwater Harvesting", "Water Pollution", "Water Treatment",
                    "Groundwater", "River Conservation", "Advanced Plant Studies", "Plant Adaptations",
                    "Desert Plants", "Aquatic Plants", "Carnivorous Plants", "Plant Diseases",
                    "Forest Conservation", "Deforestation", "Afforestation", "Biodiversity",
                    "Wildlife Conservation", "Endangered Species", "National Parks", "Wildlife Sanctuaries",
                    "Zoo and Conservation", "Animal Rights", "Climate and Weather", "Seasons",
                    "Global Warming", "Climate Change", "Natural Disasters", "Disaster Management",
                    "Environmental Laws", "Pollution Control", "Sustainable Development"
                ],
                4: [
                    # Grade 4 EVS
                    "Ecosystem Studies", "Forest Ecosystem", "Desert Ecosystem", "Aquatic Ecosystem",
                    "Grassland Ecosystem", "Mountain Ecosystem", "Energy Flow", "Nutrient Cycles",
                    "Ecological Balance", "Human Impact on Environment", "Resource Management",
                    "Renewable Resources", "Non-renewable Resources", "Resource Depletion",
                    "Sustainable Use", "Traditional Knowledge", "Indigenous Practices", "Folk Medicine",
                    "Traditional Architecture", "Cultural Heritage", "Environmental Ethics",
                    "Conservation Philosophy", "Green Living", "Eco-friendly Practices",
                    "Carbon Footprint", "Waste Reduction", "Recycling", "Upcycling",
                    "Composting", "Vermiculture", "Advanced Agriculture", "Crop Rotation",
                    "Mixed Farming", "Sustainable Agriculture", "Biotechnology in Agriculture",
                    "Environmental Technology", "Solar Energy", "Wind Energy", "Biogas",
                    "Water Wheels", "Environmental Monitoring", "Air Quality", "Water Quality",
                    "Soil Health", "Noise Pollution", "Light Pollution", "Global Environmental Issues"
                ],
                5: [
                    # Grade 5 EVS
                    "Environmental Science Research", "Data Collection", "Environmental Monitoring",
                    "Scientific Method in Environmental Studies", "Laboratory Techniques",
                    "Field Studies", "Environmental Impact Assessment", "Life Cycle Analysis",
                    "Environmental Economics", "Cost-benefit Analysis", "Green Accounting",
                    "Environmental Policies", "International Environmental Law", "Climate Agreements",
                    "Environmental Governance", "Community Participation", "Environmental Education",
                    "Awareness Programs", "Environmental Journalism", "Green Communications",
                    "Environmental Technology", "Clean Technologies", "Waste Treatment Technologies",
                    "Pollution Control Technologies", "Environmental Biotechnology", "Bioremediation",
                    "Phytoremediation", "Green Chemistry", "Sustainable Materials", "Green Building",
                    "LEED Certification", "Environmental Psychology", "Pro-environmental Behavior",
                    "Environmental Health", "Occupational Health", "Public Health", "One Health Approach",
                    "Planetary Health", "Environmental Justice", "Climate Justice", "Intergenerational Equity"
                ]
            },
            
            "GK (General Knowledge)": {
                1: [
                    # Grade 1 GK
                    "My Country India", "National Flag", "National Anthem", "National Song",
                    "National Animal - Tiger", "National Bird - Peacock", "National Flower - Lotus",
                    "National Tree - Banyan", "National Fruit - Mango", "National Game - Hockey",
                    "Capital of India - New Delhi", "Currency - Rupee", "President of India",
                    "Prime Minister of India", "Important Festivals", "Diwali", "Holi", "Eid",
                    "Christmas", "Dussehra", "Independence Day", "Republic Day", "Gandhi Jayanti",
                    "Colors", "Primary Colors", "Secondary Colors", "Rainbow Colors",
                    "Shapes", "Circle", "Square", "Triangle", "Rectangle", "Numbers 1 to 10",
                    "Days of Week", "Months of Year", "Seasons", "Summer", "Winter", "Monsoon",
                    "Body Parts", "Animals and Babies", "Fruits", "Vegetables", "Vehicles",
                    "Good Manners", "Magic Words", "Safety Rules"
                ],
                2: [
                    # Grade 2 GK
                    "States of India", "Union Territories", "Major Cities", "Rivers of India",
                    "Ganga", "Yamuna", "Narmada", "Godavari", "Krishna", "Mountains of India",
                    "Himalayas", "Western Ghats", "Eastern Ghats", "Famous Monuments",
                    "Taj Mahal", "Red Fort", "Qutub Minar", "Gateway of India", "India Gate",
                    "Important Personalities", "Mahatma Gandhi", "Jawaharlal Nehru", "Dr. APJ Abdul Kalam",
                    "Rabindranath Tagore", "Swami Vivekananda", "Sports and Games", "Cricket",
                    "Football", "Hockey", "Badminton", "Tennis", "Famous Sports Persons",
                    "Inventions and Inventors", "Telephone", "Television", "Computer", "Internet",
                    "Transportation", "Roadways", "Railways", "Airways", "Waterways",
                    "Solar System", "Sun", "Moon", "Earth", "Planets", "Stars",
                    "Health and Hygiene", "Balanced Diet", "Exercise", "Cleanliness"
                ],
                3: [
                    # Grade 3 GK
                    "World Geography", "Continents", "Countries", "Capitals", "Currencies",
                    "World Leaders", "United Nations", "UNESCO", "UNICEF", "WHO",
                    "World Heritage Sites", "Wonders of World", "Great Wall of China",
                    "Pyramids of Egypt", "Statue of Liberty", "Eiffel Tower", "Machu Picchu",
                    "International Organizations", "Olympic Games", "Nobel Prize", "Pulitzer Prize",
                    "Science and Technology", "Recent Discoveries", "Space Exploration",
                    "NASA", "ISRO", "Satellites", "Space Missions", "Mars Mission",
                    "Current Affairs", "Recent Events", "Awards and Honors", "Books and Authors",
                    "Environmental Issues", "Global Warming", "Climate Change", "Pollution",
                    "Conservation", "Renewable Energy", "Economic Terms", "GDP", "Inflation",
                    "Stock Market", "Banking", "Digital India", "Startup India", "Make in India"
                ],
                4: [
                    # Grade 4 GK
                    "Advanced Current Affairs", "National Politics", "International Relations",
                    "Economic Developments", "Scientific Achievements", "Cultural Events",
                    "Sports Updates", "Award Functions", "Government Schemes", "Policy Changes",
                    "Technological Advancements", "AI and Machine Learning", "Robotics",
                    "Biotechnology", "Nanotechnology", "Quantum Computing", "Blockchain",
                    "Cryptocurrency", "IoT", "5G Technology", "Smart Cities", "Digital Transformation",
                    "Sustainable Development", "Green Technologies", "Electric Vehicles",
                    "Solar Power", "Wind Energy", "Hydroelectric Power", "Nuclear Energy",
                    "Environmental Policies", "International Cooperation", "Trade Agreements",
                    "Economic Partnerships", "Cultural Exchange", "Educational Reforms",
                    "Health Initiatives", "Social Welfare", "Women Empowerment", "Youth Development"
                ],
                5: [
                    # Grade 5 GK
                    "Contemporary Global Issues", "Geopolitics", "International Conflicts",
                    "Peace Initiatives", "Humanitarian Crises", "Migration Issues", "Refugee Problems",
                    "Human Rights", "Gender Equality", "Social Justice", "Economic Inequality",
                    "Development Goals", "Sustainable Development Goals", "Climate Action",
                    "Biodiversity Conservation", "Ocean Conservation", "Space Exploration",
                    "Mars Colonization", "Asteroid Mining", "Space Tourism", "Satellite Technology",
                    "Communication Revolution", "Internet Governance", "Cybersecurity", "Data Privacy",
                    "Digital Rights", "Future Technologies", "Artificial General Intelligence",
                    "Quantum Internet", "Brain-Computer Interface", "Gene Editing", "Personalized Medicine",
                    "Regenerative Medicine", "Longevity Research", "Bioethics", "Technology Ethics",
                    "Environmental Ethics", "Corporate Responsibility", "Social Entrepreneurship",
                    "Impact Investing", "Circular Economy", "Sharing Economy", "Gig Economy"
                ]
            },
            
            "Art & Craft": {
                1: [
                    # Grade 1 Art & Craft
                    "Drawing with Crayons", "Coloring Inside Lines", "Free Hand Drawing",
                    "Finger Painting", "Thumb Printing", "Hand Printing", "Vegetable Printing",
                    "Sponge Painting", "Basic Shapes Drawing", "Circle Drawing", "Square Drawing",
                    "Triangle Drawing", "Line Drawing", "Straight Lines", "Curved Lines",
                    "Dot Patterns", "Simple Patterns", "Border Designs", "Paper Folding",
                    "Origami Basics", "Paper Tearing", "Paper Cutting", "Collage Making",
                    "Clay Modeling", "Play Dough", "Simple Sculptures", "Rolling", "Flattening",
                    "Basic Pottery", "Decorating Objects", "Rangoli Patterns", "Festival Crafts",
                    "Greeting Cards", "Gift Wrapping", "Nature Crafts", "Leaf Printing",
                    "Flower Arrangements", "Seed Art", "Shell Crafts", "Stone Painting",
                    "Mask Making", "Puppet Making", "Simple Toys", "Recycled Crafts"
                ],
                2: [
                    # Grade 2 Art & Craft
                    "Advanced Drawing", "Pencil Shading", "Color Mixing", "Primary Colors",
                    "Secondary Colors", "Color Wheel", "Warm and Cool Colors", "Brush Techniques",
                    "Watercolor Painting", "Acrylic Painting", "Oil Pastels", "Chalk Pastels",
                    "Texture Creation", "Smooth Textures", "Rough Textures", "Fabric Textures",
                    "Advanced Paper Crafts", "Quilling", "Paper Mache", "Pop-up Cards",
                    "3D Paper Models", "Bookmaking", "Advanced Clay Work", "Pottery Wheel",
                    "Glazing", "Firing", "Ceramic Painting", "Sculpture Techniques", "Carving",
                    "Embossing", "Traditional Crafts", "Regional Handicrafts", "Folk Art",
                    "Madhubani Painting", "Warli Art", "Gond Art", "Tanjore Painting",
                    "Block Printing", "Tie and Dye", "Batik", "Embroidery", "Cross Stitch",
                    "Macrame", "Weaving", "Basketry", "Jewelry Making", "Bead Work"
                ],
                3: [
                    # Grade 3 Art & Craft
                    "Fine Arts", "Realistic Drawing", "Portrait Drawing", "Landscape Painting",
                    "Still Life", "Figure Drawing", "Perspective Drawing", "Composition",
                    "Art History", "Famous Artists", "Art Movements", "Renaissance Art",
                    "Modern Art", "Contemporary Art", "Digital Art", "Computer Graphics",
                    "Photo Editing", "Animation Basics", "Graphic Design", "Logo Design",
                    "Poster Design", "Brochure Design", "Typography", "Calligraphy",
                    "Lettering", "Advanced Sculpture", "Metal Work", "Wood Work", "Stone Carving",
                    "Installation Art", "Mixed Media", "Assemblage", "Collage Art", "Mosaic",
                    "Stained Glass", "Glass Painting", "Fabric Art", "Textile Design",
                    "Fashion Design", "Costume Design", "Interior Design", "Architecture",
                    "Industrial Design", "Product Design", "Packaging Design", "Exhibition Design"
                ],
                4: [
                    # Grade 4 Art & Craft
                    "Professional Art Techniques", "Oil Painting", "Canvas Preparation", "Color Theory",
                    "Advanced Composition", "Golden Ratio", "Rule of Thirds", "Visual Balance",
                    "Art Criticism", "Art Analysis", "Aesthetic Theory", "Cultural Context",
                    "Art Business", "Gallery Management", "Art Marketing", "Art Valuation",
                    "Art Conservation", "Restoration Techniques", "Museum Studies", "Curatorial Studies",
                    "Contemporary Issues", "Public Art", "Community Art", "Social Art",
                    "Environmental Art", "Sustainable Art", "Eco-friendly Materials", "Recycled Art",
                    "Digital Innovation", "Virtual Reality Art", "Augmented Reality", "Interactive Art",
                    "Projection Mapping", "Sound Art", "Performance Art", "Video Art",
                    "Conceptual Art", "Minimalism", "Abstract Expressionism", "Pop Art",
                    "Street Art", "Graffiti", "Mural Painting", "Public Installations",
                    "Art Therapy", "Healing Arts", "Mindfulness Art", "Meditation Art"
                ],
                5: [
                    # Grade 5 Art & Craft
                    "Master's Level Techniques", "Advanced Oil Painting", "Fresco", "Tempera",
                    "Encaustic", "Printmaking", "Etching", "Lithography", "Screen Printing",
                    "Monotype", "Advanced Sculpture", "Bronze Casting", "Marble Carving",
                    "Contemporary Materials", "Art Research", "Thesis Projects", "Independent Study",
                    "Art Theory", "Semiotics", "Iconography", "Psychoanalytic Theory",
                    "Feminist Art Theory", "Postcolonial Art", "Decolonizing Art", "Indigenous Art",
                    "Global Art Practices", "Cross-cultural Art", "Art and Technology",
                    "Bioart", "Genetic Art", "Artificial Intelligence Art", "Machine Learning Art",
                    "Algorithmic Art", "Generative Art", "Data Visualization", "Scientific Art",
                    "Medical Art", "Astronomical Art", "Ecological Art", "Climate Art",
                    "Art and Social Justice", "Activist Art", "Protest Art", "Documentary Art",
                    "Narrative Art", "Storytelling Art", "Memory Art", "Identity Art"
                ]
            },
            
            "Agriculture": {
                6: [
                    # Grade 6 Agriculture
                    "Introduction to Agriculture", "History of Agriculture", "Types of Agriculture",
                    "Subsistence Agriculture", "Commercial Agriculture", "Intensive Agriculture",
                    "Extensive Agriculture", "Organic Agriculture", "Crop Science", "Plant Biology",
                    "Plant Nutrition", "Soil Science", "Soil Types", "Soil Testing", "Soil Health",
                    "Soil Conservation", "Erosion Control", "Fertility Management", "Composting",
                    "Organic Fertilizers", "Chemical Fertilizers", "Micronutrients", "Seed Science",
                    "Seed Selection", "Seed Treatment", "Germination", "Plant Breeding", "Hybridization",
                    "Crop Varieties", "High Yielding Varieties", "Weather and Climate", "Rainfall",
                    "Temperature", "Humidity", "Seasonal Crops", "Kharif Crops", "Rabi Crops",
                    "Zaid Crops", "Irrigation", "Irrigation Methods", "Water Management", "Crop Protection",
                    "Pest Management", "Disease Management", "Weed Control", "Harvesting", "Post-harvest"
                ],
                7: [
                    # Grade 7 Agriculture
                    "Advanced Crop Production", "Precision Agriculture", "GPS Technology", "Remote Sensing",
                    "Drone Technology", "Satellite Imagery", "Variable Rate Technology", "Soil Mapping",
                    "Yield Mapping", "Crop Monitoring", "Plant Pathology", "Disease Diagnosis",
                    "Integrated Pest Management", "Biological Control", "Pesticide Resistance",
                    "Biotechnology in Agriculture", "Genetic Engineering", "GMO Crops", "Gene Editing",
                    "CRISPR Technology", "Tissue Culture", "Micropropagation", "Hydroponics",
                    "Aeroponics", "Vertical Farming", "Greenhouse Technology", "Controlled Environment",
                    "Climate Smart Agriculture", "Carbon Sequestration", "Sustainable Practices",
                    "Conservation Agriculture", "No-till Farming", "Cover Crops", "Crop Rotation",
                    "Agroforestry", "Silviculture", "Agro-ecology", "Permaculture", "Biodynamic Farming",
                    "Natural Farming", "Organic Certification", "Farm Management", "Economics"
                ],
                8: [
                    # Grade 8 Agriculture
                    "Agricultural Research", "Experimental Design", "Statistical Analysis", "Data Collection",
                    "Field Trials", "Laboratory Techniques", "Plant Physiology", "Photosynthesis",
                    "Respiration", "Transpiration", "Plant Hormones", "Growth Regulators", "Flowering",
                    "Fruit Development", "Stress Physiology", "Drought Stress", "Salt Stress",
                    "Heat Stress", "Cold Stress", "Molecular Biology", "Plant Genomics", "Proteomics",
                    "Metabolomics", "Bioinformatics", "Marker Assisted Selection", "Quantitative Genetics",
                    "Population Genetics", "Evolutionary Biology", "Biodiversity", "Genetic Resources",
                    "Seed Banks", "Conservation", "Climate Change", "Adaptation", "Mitigation",
                    "Carbon Farming", "Renewable Energy", "Biofuels", "Biomass", "Biogas",
                    "Solar Energy", "Wind Energy", "Water Conservation", "Rainwater Harvesting",
                    "Drip Irrigation", "Sprinkler Irrigation", "Fertigation", "Aquaculture", "Fisheries"
                ],
                9: [
                    # Grade 9 Agriculture
                    "Agricultural Extension", "Technology Transfer", "Farmer Education", "Rural Development",
                    "Cooperative Farming", "Self Help Groups", "Microfinance", "Crop Insurance",
                    "Market Linkages", "Value Addition", "Food Processing", "Supply Chain Management",
                    "Cold Storage", "Warehousing", "Transportation", "Quality Control", "Food Safety",
                    "HACCP", "Traceability", "Certification", "Export Agriculture", "International Trade",
                    "WTO Agreements", "Sanitary Standards", "Phytosanitary Measures", "Organic Export",
                    "Contract Farming", "Corporate Agriculture", "Agricultural Policies", "Government Schemes",
                    "Subsidies", "Price Support", "Minimum Support Price", "Agricultural Credit",
                    "Crop Loan", "Investment Support", "Infrastructure Development", "Rural Infrastructure",
                    "Road Connectivity", "Electricity", "Internet Connectivity", "Digital Agriculture",
                    "E-commerce", "Online Marketing", "Digital Payments", "Precision Agriculture"
                ],
                10: [
                    # Grade 10 Agriculture
                    "Sustainable Agriculture", "Agroecology", "Ecosystem Services", "Natural Capital",
                    "Circular Economy", "Zero Waste Agriculture", "Regenerative Agriculture", "Soil Health",
                    "Carbon Sequestration", "Biodiversity Conservation", "Pollinator Conservation",
                    "Integrated Farming Systems", "Mixed Farming", "Livestock Integration", "Aquaponics",
                    "Urban Agriculture", "Rooftop Farming", "Community Gardens", "School Gardens",
                    "Therapeutic Agriculture", "Social Agriculture", "Inclusive Agriculture", "Gender",
                    "Women in Agriculture", "Youth in Agriculture", "Tribal Agriculture", "Marginal Farmers",
                    "Small Holder Agriculture", "Family Farming", "Subsistence Farming", "Commercial Farming",
                    "Corporate Farming", "Large Scale Agriculture", "Plantation Agriculture", "Horticulture",
                    "Floriculture", "Viticulture", "Sericulture", "Apiculture", "Mushroom Cultivation",
                    "Medicinal Plants", "Aromatic Plants", "Spice Production", "Beverage Crops"
                ]
            },
            
            "Home Science": {
                6: [
                    # Grade 6 Home Science
                    "Introduction to Home Science", "Scope of Home Science", "Importance in Daily Life",
                    "Human Development", "Child Development", "Adolescent Development", "Adult Development",
                    "Elderly Care", "Life Span Development", "Nutrition and Health", "Balanced Diet",
                    "Nutrients", "Vitamins", "Minerals", "Proteins", "Carbohydrates", "Fats",
                    "Water", "Fiber", "Meal Planning", "Menu Planning", "Food Groups", "Cooking Methods",
                    "Food Safety", "Food Hygiene", "Food Preservation", "Food Storage", "Kitchen Management",
                    "Kitchen Equipment", "Cooking Utensils", "Kitchen Safety", "Personal Hygiene",
                    "Body Care", "Skin Care", "Hair Care", "Dental Care", "Eye Care", "Clothing",
                    "Fabrics", "Textile Fibers", "Clothing Care", "Laundry", "Ironing", "Storage",
                    "Family Living", "Family Types", "Family Functions", "Family Relationships"
                ],
                7: [
                    # Grade 7 Home Science
                    "Advanced Nutrition", "Nutritional Disorders", "Malnutrition", "Obesity", "Anemia",
                    "Diabetes", "Hypertension", "Therapeutic Nutrition", "Diet Therapy", "Special Diets",
                    "Pregnancy Nutrition", "Lactation Nutrition", "Infant Nutrition", "Child Nutrition",
                    "Geriatric Nutrition", "Sports Nutrition", "Food Science", "Food Chemistry",
                    "Food Microbiology", "Food Technology", "Food Processing", "Food Fortification",
                    "Functional Foods", "Nutraceuticals", "Organic Foods", "Food Quality", "Food Standards",
                    "Food Laws", "Food Additives", "Food Contamination", "Foodborne Diseases",
                    "Advanced Textiles", "Textile Chemistry", "Fabric Construction", "Weaving", "Knitting",
                    "Dyeing", "Printing", "Finishing", "Fashion Design", "Clothing Construction",
                    "Pattern Making", "Sewing Techniques", "Embroidery", "Tailoring", "Alteration"
                ],
                8: [
                    # Grade 8 Home Science
                    "Community Nutrition", "Public Health Nutrition", "Nutrition Programs", "Mid-day Meal",
                    "ICDS", "Nutrition Education", "Nutrition Counseling", "Behavior Change", "Extension",
                    "Rural Development", "Women Empowerment", "Self Help Groups", "Microenterprise",
                    "Entrepreneurship", "Business Planning", "Financial Management", "Marketing",
                    "Product Development", "Quality Control", "Hospitality Management", "Hotel Management",
                    "Restaurant Management", "Catering", "Event Management", "Tourism", "Recreation",
                    "Leisure", "Interior Design", "Space Planning", "Color Schemes", "Furniture",
                    "Lighting", "Ventilation", "Acoustics", "Ergonomics", "Universal Design",
                    "Barrier Free Design", "Sustainable Design", "Green Building", "Energy Efficiency",
                    "Water Conservation", "Waste Management", "Environmental Health", "Occupational Health"
                ],
                9: [
                    # Grade 9 Home Science
                    "Research in Home Science", "Research Methods", "Data Collection", "Statistical Analysis",
                    "Survey Methods", "Experimental Design", "Action Research", "Participatory Research",
                    "Community Based Research", "Applied Research", "Basic Research", "Interdisciplinary Research",
                    "Technology Transfer", "Innovation", "Product Development", "Process Development",
                    "Quality Assurance", "Standards", "Certification", "Testing", "Evaluation",
                    "Impact Assessment", "Social Impact", "Economic Impact", "Environmental Impact",
                    "Policy Analysis", "Program Evaluation", "Monitoring", "Documentation", "Reporting",
                    "Communication", "Media", "Information Technology", "Digital Literacy", "E-learning",
                    "Distance Education", "Online Resources", "Mobile Technology", "Apps", "Social Media",
                    "Digital Marketing", "E-commerce", "Online Business", "Digital Payments", "Fintech"
                ],
                10: [
                    # Grade 10 Home Science
                    "Advanced Home Science", "Specialization Areas", "Career Options", "Professional Development",
                    "Higher Education", "Research Opportunities", "Industry Connections", "Internships",
                    "Practicum", "Field Experience", "Community Service", "Extension Work", "Outreach",
                    "Social Work", "NGO Work", "Government Programs", "International Programs", "Global Health",
                    "Global Nutrition", "International Development", "Cross-cultural Studies", "Comparative Studies",
                    "Cultural Competency", "Diversity", "Inclusion", "Equity", "Social Justice", "Human Rights",
                    "Ethics", "Professional Ethics", "Research Ethics", "Environmental Ethics", "Bioethics",
                    "Consumer Rights", "Consumer Protection", "Consumer Education", "Advocacy", "Policy Advocacy",
                    "Social Advocacy", "Community Advocacy", "Leadership", "Team Work", "Collaboration",
                    "Networking", "Partnerships", "Stakeholder Engagement", "Public-Private Partnerships"
                ]
            },
            
            "Computer Science": {
                6: [
                    # Grade 6 Computer Science
                    "Introduction to Computers", "What is a Computer", "Types of Computers", "Desktop, Laptop, Tablet",
                    "Smartphone as Computer", "History of Computers", "Generations of Computers", "Computer System",
                    "Hardware and Software", "Input Devices", "Output Devices", "Processing Unit", "Memory and Storage",
                    "Operating System", "Windows Operating System", "File Management", "Folders and Files",
                    "Creating, Copying, Moving Files", "Desktop and Icons", "Start Menu", "Control Panel",
                    "Introduction to Internet", "What is Internet", "World Wide Web", "Web Browser",
                    "Search Engines", "Email", "Creating Email Account", "Sending and Receiving Emails",
                    "Email Etiquette", "Online Safety", "Password Security", "Cyber Bullying",
                    "Digital Citizenship", "Word Processing", "MS Word Introduction", "Creating Documents",
                    "Formatting Text", "Insert Pictures", "Save and Print", "Paint Program",
                    "Drawing Tools", "Coloring", "Basic Shapes", "Educational Games and Software"
                ],
                7: [
                    # Grade 7 Computer Science
                    "Advanced Computer Concepts", "Computer Networks", "LAN, WAN, Internet", "Network Devices",
                    "Router, Switch, Modem", "Network Security", "Firewall", "Antivirus", "Data and Information",
                    "Data vs Information", "Data Types", "Database Introduction", "Spreadsheet Software",
                    "MS Excel Introduction", "Cells, Rows, Columns", "Data Entry", "Basic Formulas",
                    "SUM, AVERAGE Functions", "Charts and Graphs", "Presentation Software", "MS PowerPoint",
                    "Creating Presentations", "Slides and Layouts", "Animations", "Slide Transitions",
                    "Internet Services", "Search Techniques", "Online Research", "Digital Libraries",
                    "E-learning Platforms", "Video Conferencing", "Social Media", "Online Shopping",
                    "Digital Payments", "Multimedia", "Audio and Video Files", "Image Formats",
                    "Basic Photo Editing", "Introduction to Programming", "What is Programming", "Programming Languages",
                    "Scratch Programming", "Block-based Coding", "Algorithms", "Flowcharts", "Problem Solving"
                ],
                8: [
                    # Grade 8 Computer Science
                    "Advanced Programming Concepts", "Scratch Advanced", "Variables and Operations", "Loops and Conditions",
                    "Functions and Procedures", "Event Handling", "Game Development", "Animation Programming",
                    "Introduction to Text-based Programming", "Python Programming Language", "Python Syntax",
                    "Variables and Data Types", "Input and Output", "Operators", "Conditional Statements",
                    "Loops", "Functions", "Lists and Strings", "File Handling", "Error Handling",
                    "Advanced Internet Concepts", "Cloud Computing", "Cloud Storage", "Google Drive, OneDrive",
                    "Collaborative Tools", "Google Docs, Sheets", "Version Control", "Web Technologies",
                    "HTML Introduction", "Web Page Structure", "Basic HTML Tags", "CSS Introduction",
                    "Styling Web Pages", "JavaScript Introduction", "Interactive Web Pages", "Database Concepts",
                    "Database Management", "Tables, Records, Fields", "Queries", "Database Design",
                    "Digital Media", "Audio Editing", "Video Editing", "Graphics Design", "Vector vs Raster",
                    "Artificial Intelligence", "Machine Learning Introduction", "Robotics", "Automation"
                ],
                9: [
                    # Grade 9 Computer Science
                    "Advanced Programming", "Python Advanced Concepts", "Object-Oriented Programming", "Classes and Objects",
                    "Inheritance", "Polymorphism", "Encapsulation", "Modules and Packages", "Libraries",
                    "GUI Programming", "Tkinter", "Event-driven Programming", "Database Programming",
                    "SQL Introduction", "Database Operations", "Web Development", "HTML5", "CSS3",
                    "Responsive Design", "JavaScript Programming", "DOM Manipulation", "AJAX",
                    "Web Frameworks", "Server-side Programming", "Client-server Architecture", "APIs",
                    "Data Structures", "Arrays", "Lists", "Stacks", "Queues", "Trees", "Graphs",
                    "Algorithms", "Searching Algorithms", "Sorting Algorithms", "Complexity Analysis",
                    "Computer Networks", "OSI Model", "TCP/IP", "Network Protocols", "Network Security",
                    "Cryptography", "Digital Signatures", "Blockchain Introduction", "Cryptocurrency",
                    "Artificial Intelligence", "Machine Learning", "Neural Networks", "Deep Learning",
                    "Natural Language Processing", "Computer Vision", "Data Science", "Big Data"
                ],
                10: [
                    # Grade 10 Computer Science
                    "Advanced Software Development", "Software Engineering", "SDLC", "Agile Methodology",
                    "Version Control Systems", "Git and GitHub", "Testing and Debugging", "Documentation",
                    "Mobile App Development", "Android Programming", "iOS Programming", "Cross-platform Development",
                    "Game Development", "Unity Engine", "2D and 3D Graphics", "Physics Engines",
                    "Advanced Web Development", "Full-stack Development", "Frontend Frameworks", "Backend Development",
                    "Database Design", "Normalization", "Advanced SQL", "NoSQL Databases", "MongoDB",
                    "Cloud Technologies", "AWS", "Azure", "Google Cloud", "Microservices", "Containerization",
                    "Docker", "Kubernetes", "DevOps", "CI/CD", "Advanced AI/ML", "Deep Learning Frameworks",
                    "TensorFlow", "PyTorch", "Computer Vision", "NLP", "Robotics Programming",
                    "IoT Development", "Embedded Systems", "Arduino", "Raspberry Pi", "Sensors and Actuators",
                    "Cybersecurity", "Ethical Hacking", "Penetration Testing", "Security Frameworks",
                    "Data Privacy", "GDPR", "Cybersecurity Laws", "Digital Forensics"
                ],
                11: [
                    # Grade 11 Computer Science
                    "Computer System Architecture", "CPU Architecture", "Memory Hierarchy", "Cache Memory",
                    "Virtual Memory", "Instruction Set Architecture", "RISC vs CISC", "Parallel Processing",
                    "Multicore Systems", "Operating Systems", "Process Management", "Memory Management",
                    "File Systems", "I/O Management", "Concurrency", "Synchronization", "Deadlocks",
                    "Advanced Programming", "System Programming", "Compiler Design", "Interpreter",
                    "Assembly Language", "Low-level Programming", "Advanced Data Structures", "B-Trees",
                    "Hash Tables", "Graph Algorithms", "Dynamic Programming", "Greedy Algorithms",
                    "Network Programming", "Socket Programming", "Distributed Systems", "Middleware",
                    "Web Services", "REST APIs", "GraphQL", "Database Systems", "Transaction Processing",
                    "Concurrency Control", "Database Recovery", "Distributed Databases", "Data Warehousing",
                    "OLAP", "Data Mining", "Machine Learning Advanced", "Supervised Learning", "Unsupervised Learning",
                    "Reinforcement Learning", "Feature Engineering", "Model Selection", "Hyperparameter Tuning"
                ],
                12: [
                    # Grade 12 Computer Science
                    "Advanced Computer Science Theory", "Computational Complexity", "P vs NP", "Approximation Algorithms",
                    "Quantum Computing", "Cryptography Advanced", "Public Key Cryptography", "Digital Certificates",
                    "Computer Graphics", "3D Rendering", "Ray Tracing", "Animation", "Virtual Reality",
                    "Augmented Reality", "Human-Computer Interaction", "UI/UX Design", "Accessibility",
                    "Software Architecture", "Design Patterns", "Microservices Architecture", "Event-driven Architecture",
                    "Research Methodology", "Technical Writing", "Research Paper Writing", "Literature Review",
                    "Experimental Design", "Statistical Analysis", "Data Visualization", "Advanced AI",
                    "Artificial General Intelligence", "Expert Systems", "Knowledge Representation", "Reasoning Systems",
                    "Multi-agent Systems", "Swarm Intelligence", "Evolutionary Algorithms", "Quantum Machine Learning",
                    "Bioinformatics", "Computational Biology", "Scientific Computing", "High-Performance Computing",
                    "Parallel Algorithms", "GPU Programming", "CUDA", "OpenMP", "MPI", "Ethics in Computing",
                    "AI Ethics", "Algorithmic Bias", "Privacy by Design", "Sustainable Computing", "Green IT"
                ]
            },
            
            "Physical Education": {
                6: [
                    # Grade 6 Physical Education
                    "Introduction to Physical Education", "Importance of Physical Fitness", "Components of Physical Fitness",
                    "Health vs Fitness", "Exercise vs Physical Activity", "Basic Anatomy", "Skeletal System",
                    "Muscular System", "Cardiovascular System", "Respiratory System", "Warm-up and Cool-down",
                    "Stretching Exercises", "Flexibility Training", "Basic Motor Skills", "Running Techniques",
                    "Jumping Techniques", "Throwing Techniques", "Catching Techniques", "Fundamental Sports Skills",
                    "Basketball Basics", "Football Basics", "Volleyball Basics", "Cricket Basics", "Hockey Basics",
                    "Badminton Basics", "Table Tennis Basics", "Athletics Events", "Track Events", "Field Events",
                    "Gymnastics Introduction", "Balance and Coordination", "Rhythmic Activities", "Dance Forms",
                    "Traditional Games", "Yoga Introduction", "Basic Asanas", "Breathing Exercises", "Meditation",
                    "Nutrition for Athletes", "Hydration", "Rest and Recovery", "Sports Psychology", "Goal Setting",
                    "Motivation", "Team Spirit", "Leadership", "Fair Play", "Sports Ethics", "Rules and Regulations"
                ],
                7: [
                    # Grade 7 Physical Education
                    "Advanced Fitness Concepts", "Aerobic vs Anaerobic Exercise", "Heart Rate Training", "Target Heart Rate",
                    "Fitness Testing", "BMI Calculation", "Fitness Assessment", "Training Principles", "Overload Principle",
                    "Specificity Principle", "Recovery Principle", "Advanced Sports Techniques", "Basketball Advanced",
                    "Football Advanced", "Volleyball Advanced", "Cricket Advanced", "Hockey Advanced", "Badminton Advanced",
                    "Table Tennis Advanced", "Swimming Strokes", "Freestyle", "Backstroke", "Breaststroke", "Butterfly",
                    "Water Safety", "Athletic Training", "Sprint Training", "Endurance Training", "Strength Training",
                    "Power Training", "Speed Training", "Agility Training", "Plyometric Training", "Circuit Training",
                    "Interval Training", "Advanced Gymnastics", "Floor Exercises", "Apparatus Training", "Tumbling",
                    "Martial Arts", "Self-defense", "Karate", "Judo", "Taekwondo", "Boxing", "Wrestling",
                    "Adventure Sports", "Trekking", "Camping", "Rock Climbing", "Cycling", "Sports Medicine",
                    "Common Sports Injuries", "Injury Prevention", "First Aid", "RICE Protocol", "Rehabilitation"
                ],
                8: [
                    # Grade 8 Physical Education
                    "Exercise Physiology", "Energy Systems", "Aerobic Energy System", "Anaerobic Energy Systems",
                    "Lactic Acid System", "ATP-PC System", "Muscle Fiber Types", "Fast Twitch vs Slow Twitch",
                    "Training Adaptations", "Cardiovascular Adaptations", "Muscular Adaptations", "Neural Adaptations",
                    "Advanced Training Methods", "Periodization", "Macrocycles", "Mesocycles", "Microcycles",
                    "Peaking and Tapering", "Overtraining", "Recovery Strategies", "Sports Nutrition Advanced",
                    "Carbohydrate Loading", "Protein Requirements", "Fat Metabolism", "Vitamins and Minerals",
                    "Sports Supplements", "Hydration Strategies", "Weight Management", "Eating Disorders",
                    "Sports Psychology Advanced", "Mental Training", "Visualization", "Concentration", "Confidence Building",
                    "Stress Management", "Anxiety Control", "Team Dynamics", "Communication Skills", "Leadership Styles",
                    "Biomechanics", "Movement Analysis", "Force and Motion", "Leverage", "Centre of Gravity",
                    "Balance and Stability", "Technique Analysis", "Performance Enhancement", "Technology in Sports",
                    "Video Analysis", "Wearable Technology", "Sports Analytics", "Performance Monitoring"
                ],
                9: [
                    # Grade 9 Physical Education
                    "Advanced Exercise Science", "Metabolic Training", "High-Intensity Interval Training", "Functional Training",
                    "Cross-training", "Sport-specific Training", "Advanced Strength Training", "Olympic Lifts",
                    "Powerlifting", "Bodybuilding", "Calisthenics", "Flexibility and Mobility", "Dynamic Stretching",
                    "Static Stretching", "PNF Stretching", "Foam Rolling", "Massage Therapy", "Professional Sports",
                    "Career in Sports", "Sports Management", "Sports Marketing", "Sports Journalism", "Sports Medicine",
                    "Physical Therapy", "Athletic Training", "Coaching Science", "Talent Identification",
                    "Long-term Athlete Development", "Specialization vs Diversification", "Youth Sports", "Masters Sports",
                    "Paralympic Sports", "Adaptive Sports", "Inclusive Physical Education", "Cultural Sports",
                    "Indigenous Games", "Olympic Movement", "History of Olympics", "Olympic Values", "International Sports",
                    "Sports Governance", "Anti-doping", "WADA Code", "Ethics in Sports", "Gender in Sports",
                    "Sports and Society", "Sports and Politics", "Sports and Economics", "Sports Tourism"
                ],
                10: [
                    # Grade 10 Physical Education
                    "Research in Physical Education", "Scientific Method", "Data Collection", "Statistical Analysis",
                    "Research Design", "Literature Review", "Exercise Testing", "VO2 Max Testing", "Lactate Testing",
                    "Strength Testing", "Flexibility Testing", "Body Composition Analysis", "Advanced Coaching",
                    "Coaching Philosophy", "Coaching Methods", "Practice Design", "Game Analysis", "Scouting",
                    "Team Selection", "Player Development", "Tactical Training", "Technical Training", "Mental Coaching",
                    "Sports Technology", "Motion Capture", "Force Plates", "Heart Rate Monitors", "GPS Tracking",
                    "Virtual Reality Training", "Artificial Intelligence in Sports", "Big Data in Sports", "Sports Broadcasting",
                    "Media Relations", "Social Media in Sports", "Sports Sponsorship", "Event Management",
                    "Facility Management", "Risk Management", "Legal Issues in Sports", "Contracts", "Liability",
                    "Insurance", "Sports Law", "Intellectual Property", "Image Rights", "International Sports Law",
                    "Sports Diplomacy", "Sports for Development", "Peace through Sports", "Environmental Sustainability"
                ],
                11: [
                    # Grade 11 Physical Education
                    "Advanced Sports Science", "Exercise Biochemistry", "Molecular Exercise Physiology", "Genetics and Performance",
                    "Epigenetics", "Personalized Training", "Precision Medicine", "Biomarkers", "Advanced Biomechanics",
                    "3D Motion Analysis", "Computational Biomechanics", "Modeling and Simulation", "Injury Biomechanics",
                    "Equipment Design", "Performance Optimization", "Advanced Sports Psychology", "Cognitive Psychology",
                    "Social Psychology", "Developmental Psychology", "Personality Psychology", "Motivational Theories",
                    "Flow Theory", "Self-Determination Theory", "Achievement Goal Theory", "Social Cognitive Theory",
                    "Advanced Sports Medicine", "Exercise Immunology", "Exercise Endocrinology", "Exercise Neuroscience",
                    "Sports Cardiology", "Sports Orthopedics", "Concussion Management", "Return to Play Protocols",
                    "Sports Pharmacology", "Ergogenic Aids", "Anti-doping Science", "Advanced Sports Nutrition",
                    "Nutrigenomics", "Metabolomics", "Precision Nutrition", "Clinical Sports Nutrition", "Research Methods",
                    "Experimental Design", "Statistical Analysis", "Meta-analysis", "Systematic Reviews", "Publication Process"
                ],
                12: [
                    # Grade 12 Physical Education
                    "Professional Development", "Career Planning", "Graduate School Preparation", "Professional Certifications",
                    "Continuing Education", "Professional Organizations", "Networking", "Mentorship", "Leadership Development",
                    "Entrepreneurship in Sports", "Innovation in Sports", "Technology Transfer", "Intellectual Property",
                    "Business Planning", "Market Analysis", "Financial Management", "Sports Startups", "Venture Capital",
                    "Global Sports Industry", "International Markets", "Cultural Considerations", "Sports Diplomacy",
                    "Mega-events", "Legacy Planning", "Sustainability", "Social Impact", "Community Development",
                    "Ethical Leadership", "Moral Decision Making", "Corporate Social Responsibility", "Stakeholder Management",
                    "Crisis Management", "Change Management", "Strategic Planning", "Policy Development", "Advocacy",
                    "Public Health", "Physical Activity Promotion", "Health Behavior Change", "Population Health",
                    "Health Disparities", "Social Determinants of Health", "Health Equity", "Global Health",
                    "Future of Physical Education", "Emerging Trends", "Technology Integration", "Virtual Coaching",
                    "Personalized Learning", "Inclusive Design", "Universal Access", "Lifelong Learning"
                ]
            }
        }
         
    }

def test_claude_api():
    """Test Claude API connection with better error handling"""
    try:
        if not CLAUDE_API_KEY or CLAUDE_API_KEY == "":
            return False, "API key not configured"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Test"}]
        }
        
        response = requests.post(CLAUDE_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, "API connection successful"
        elif response.status_code == 401:
            return False, f"API Authentication failed - check your API key"
        elif response.status_code == 429:
            return False, f"API rate limit exceeded - try again later"
        else:
            try:
                error_detail = response.json()
                return False, f"API Error {response.status_code}: {error_detail.get('error', {}).get('message', 'Unknown error')}"
            except:
                return False, f"API Error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def verify_api_key():
    """Verify API key with details"""
    st.write("🔍 **API Key Verification:**")
    
    if not CLAUDE_API_KEY or CLAUDE_API_KEY == "":
        st.error("❌ API key not configured")
        return False
    
    if not CLAUDE_API_KEY.startswith("sk-ant-api03-"):
        st.error("❌ Invalid API key format")
        return False
    
    st.success("✅ API key format is correct")
    
    # Test connection
    working, message = test_claude_api()
    if working:
        st.success(f"✅ {message}")
    else:
        st.error(f"❌ {message}")
    
    return working

def get_topics_by_board_grade_subject(board, grade, subject):
    """NEW FUNCTION: Get specific topics for board, grade, and subject"""
    curriculum_topics = get_comprehensive_curriculum_topics()
    
    # Handle IB grade format
    if board == "IB" and isinstance(grade, str) and "Grade" in grade:
        try:
            grade_num = int(grade.split()[1])
        except (IndexError, ValueError):
            return []
    else:
        grade_num = grade if isinstance(grade, int) else grade
    
    # Get topics from curriculum database
    board_data = curriculum_topics.get(board, {})
    subject_data = board_data.get(subject, {})
    topics = subject_data.get(grade_num, [])
    
    return topics

def validate_topic_against_curriculum(board, grade, subject, user_topic):
    """Validate against exact curriculum topics from your comprehensive database"""
    if not user_topic:
        return False, []
    
    curriculum_topics = get_topics_by_board_grade_subject(board, grade, subject)
    
    if not curriculum_topics:
        return True, []  # Allow if no curriculum data
    
    user_topic_clean = user_topic.lower().strip()
    
    for curriculum_topic in curriculum_topics:
        curriculum_clean = str(curriculum_topic).lower().strip()
        
        # 1. Exact match
        if user_topic_clean == curriculum_clean:
            return True, curriculum_topics
        
        # 2. Substring match (either direction)
        if user_topic_clean in curriculum_clean or curriculum_clean in user_topic_clean:
            return True, curriculum_topics
        
        # 3. Word overlap matching
        user_words = set(user_topic_clean.split())
        curriculum_words = set(curriculum_clean.split())
        
        # Remove common stop words
        stop_words = {'and', 'or', 'of', 'in', 'on', 'the', 'a', 'an', 'to', 'for', 'with'}
        user_words -= stop_words
        curriculum_words -= stop_words
        
        # Check if majority of words match
        if user_words and curriculum_words:
            overlap = len(user_words.intersection(curriculum_words))
            min_words = min(len(user_words), len(curriculum_words))
            
            # If 60% or more words match, consider it valid
            if overlap / min_words >= 0.6:
                return True, curriculum_topics
        
        # 4. Partial word matching
        if any(word in curriculum_clean for word in user_words if len(word) > 3):
            return True, curriculum_topics
    
    return False, curriculum_topics

def clean_json_response(response_text):
    """Enhanced JSON cleaning function to handle Claude's response format"""
    try:
        # Remove any markdown code blocks
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            if end != -1:
                response_text = response_text[start:end]
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            if end != -1:
                response_text = response_text[start:end]
        
        # Clean up the text
        response_text = response_text.strip()
        
        # Remove any leading/trailing non-JSON content
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx + 1]
        
        # Try to parse the JSON
        parsed_json = json.loads(response_text)
        return parsed_json, None
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON Parse Error at position {e.pos}: {e.msg}"
        return None, error_msg
    except Exception as e:
        return None, f"Error cleaning JSON: {str(e)}"

def generate_questions(board, grade, subject, topic, paper_type, include_answers_on_screen):
    """FIXED: Generate board-specific, grade-specific questions using Claude AI with enhanced error handling"""
    
    # Enhanced question count logic based on all board paper types
    mcq_count = 0
    short_count = 0
    long_count = 0
    
    # Primary Grades (1-5) for all boards
    if "Primary Assessment" in paper_type or "Foundation Test" in paper_type or "State Pattern Test" in paper_type:
        mcq_count = 15
        short_count = 5
    elif "Activity" in paper_type or "Skills" in paper_type:
        mcq_count = 0
        short_count = 15
    elif "Oral Assessment" in paper_type:
        mcq_count = 0
        short_count = 10
    
    # Middle Grades (6-8) for all boards
    elif "Periodic Test" in paper_type or "Class Test" in paper_type or "State Board Format" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Unit Test" in paper_type or "Term Examination" in paper_type or "Quarterly Test" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Annual Practice" in paper_type or "Annual Assessment" in paper_type or "Half-yearly Pattern" in paper_type:
        mcq_count = 25
        short_count = 15
    
    # High School Grades (9-10) for all boards
    elif "Board Pattern Paper 1" in paper_type or "ICSE Board Format Paper 1" in paper_type or "State Board Paper 1" in paper_type:
        mcq_count = 25
        short_count = 15
    elif "Board Pattern Paper 2" in paper_type or "ICSE Board Format Paper 2" in paper_type or "State Board Paper 2" in paper_type:
        mcq_count = 0
        short_count = 10
        long_count = 10
    elif "Sample Paper Format" in paper_type or "Mock ICSE Paper" in paper_type or "Annual Exam Pattern" in paper_type:
        mcq_count = 25
        short_count = 10
        long_count = 5
    
    # Senior Secondary (11-12) for all boards
    elif "Board Exam Pattern" in paper_type or "ISC Board Pattern" in paper_type or "HSC Board Pattern" in paper_type:
        mcq_count = 25
        short_count = 10
        long_count = 5
    elif "Practice Test Series" in paper_type or "Practice Assessment" in paper_type or "State Higher Secondary" in paper_type:
        mcq_count = 30
        short_count = 10
    elif "Mock Board Paper" in paper_type or "Mock ISC Paper" in paper_type or "Board Exam Format" in paper_type:
        mcq_count = 30
        short_count = 15
        long_count = 5
    
    # IB Specific Papers
    elif "Formative Assessment" in paper_type:
        mcq_count = 15
        short_count = 5
    elif "Skills Practice" in paper_type:
        mcq_count = 0
        short_count = 15
    elif "Inquiry Tasks" in paper_type:
        mcq_count = 0
        short_count = 25
    elif "Practice Assessment" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Criterion-Based Test" in paper_type:
        mcq_count = 15
        short_count = 10
    elif "Personal Project Prep" in paper_type:
        mcq_count = 0
        short_count = 15
    elif "MYP Certificate Practice" in paper_type:
        mcq_count = 30
        short_count = 10
    elif "Paper 1 (40 MCQs)" in paper_type:
        mcq_count = 40
        short_count = 0
    elif "Paper 2 (15 Short + 15 Long" in paper_type:
        mcq_count = 0
        short_count = 15
        long_count = 15
    elif "Paper 3 (Data Analysis" in paper_type:
        mcq_count = 15
        short_count = 10
    
    # Cambridge IGCSE Specific Papers
    elif "Cambridge Primary Test" in paper_type or "Lower Secondary Assessment" in paper_type:
        mcq_count = 15
        short_count = 10
    elif "Checkpoint Practice" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Paper 1 (30 MCQs)" in paper_type:
        mcq_count = 30
        short_count = 0
    elif "Paper 2 (Theory" in paper_type:
        mcq_count = 10
        short_count = 15
        long_count = 5
    elif "Paper 3 (Practical" in paper_type or "Paper 4 (Alternative" in paper_type:
        mcq_count = 15
        short_count = 10
    elif "A-Level AS Paper" in paper_type:
        mcq_count = 20
        short_count = 15
    elif "A-Level A2 Paper" in paper_type:
        mcq_count = 25
        short_count = 15
    elif "Cambridge Advanced Test" in paper_type:
        mcq_count = 30
        short_count = 15
    
    # Default fallback
    else:
        mcq_count = 20
        short_count = 10
    
    total_questions = mcq_count + short_count + long_count
    
    # Get curriculum topics for enhanced context
    curriculum_topics = get_topics_by_board_grade_subject(board, grade, subject)
    curriculum_context = ""
    if curriculum_topics:
        curriculum_context = f"\nCURRICULUM TOPICS for {board} Grade {grade} {subject}: {', '.join(curriculum_topics[:10])}"
    
    # Enhanced prompt with board and grade specific context
    board_context = get_board_specific_guidelines(board, grade, subject, topic)
    
    prompt = f"""Create a {board} Grade {grade} {subject} test on "{topic}" using {paper_type} format.

{board_context}
{curriculum_context}

Generate exactly:
- {mcq_count} multiple choice questions (if any)
- {short_count} short answer questions (if any)
- {long_count} long answer questions (if any)

IMPORTANT: All questions MUST be specifically about "{topic}" as taught in {board} Grade {grade} {subject} curriculum. Use examples, terminology, and difficulty level appropriate for {board} Grade {grade} students.

Question Types:
- MCQ: 4 options (A, B, C, D) with one correct answer
- Short Answer: 2-5 sentence responses
- Long Answer: Detailed explanations or essay-type responses

CRITICAL: Respond with ONLY valid JSON. No markdown, no extra text, no explanations - just pure JSON.

{{
    "test_info": {{
        "board": "{board}",
        "grade": "{grade}",
        "subject": "{subject}",
        "topic": "{topic}",
        "paper_type": "{paper_type}",
        "total_questions": {total_questions},
        "mcq_count": {mcq_count},
        "short_count": {short_count},
        "long_count": {long_count},
        "show_answers_on_screen": {str(include_answers_on_screen).lower()}
    }},
    "questions": [
        {{
            "question_number": 1,
            "type": "mcq",
            "question": "Sample MCQ question about {topic}?",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Brief explanation"
        }},
        {{
            "question_number": 2,
            "type": "short",
            "question": "Sample short answer question about {topic}?",
            "sample_answer": "Expected short answer",
            "marks": 3
        }},
        {{
            "question_number": 3,
            "type": "long",
            "question": "Sample long answer question about {topic}?",
            "sample_answer": "Expected detailed answer",
            "marks": 6
        }}
    ]
}}"""

    try:
        # Enhanced error handling and API validation
        if not CLAUDE_API_KEY or CLAUDE_API_KEY == "REPLACE_WITH_YOUR_API_KEY":
            st.error("❌ API key not configured. Please check your API configuration.")
            return None
        
        
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
       
        
        try:
            response = requests.post(CLAUDE_API_URL, headers=headers, json=data, timeout=120)
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error. Please check your internet connection.")
            return None
        
        
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'content' not in result or not result['content']:
                    st.error("❌ Invalid response format from Claude API")
                    return None
                
                content = result['content'][0]['text']
                
                
                # Enhanced JSON cleaning and parsing
                cleaned_json, error = clean_json_response(content)
                
                if cleaned_json is None:
                    st.error(f"❌ {error}")
                    st.error("📝 Raw response for debugging:")
                    st.code(content[:500] + "..." if len(content) > 500 else content)
                    return None
                
                # Validate the JSON structure
                if 'test_info' not in cleaned_json or 'questions' not in cleaned_json:
                    st.error("❌ Invalid test data structure")
                    return None
                
                # Ensure test_info has required fields
                if 'test_info' in cleaned_json:
                    cleaned_json['test_info']['show_answers_on_screen'] = include_answers_on_screen
                    cleaned_json['test_info']['curriculum_standard'] = f"{board} Grade {grade} {subject}"
                
                st.success("✅ Test generated successfully!")
                return cleaned_json
                
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON Parse Error: {str(e)}")
                st.error("📝 Raw response for debugging:")
                result = response.json()
                content = result['content'][0]['text'] if 'content' in result else str(result)
                st.code(content[:500] + "..." if len(content) > 500 else content)
                return None
            except Exception as e:
                st.error(f"❌ Error processing response: {str(e)}")
                return None
            
        elif response.status_code == 401:
            st.error("❌ API Authentication failed. Please check your API key.")
            return None
        elif response.status_code == 429:
            st.error("❌ API rate limit exceeded. Please try again later.")
            return None
        elif response.status_code == 400:
            try:
                error_detail = response.json()
                st.error(f"❌ API Request Error: {error_detail.get('error', {}).get('message', 'Bad request')}")
            except:
                st.error("❌ Bad request to API")
            return None
        else:
            try:
                error_detail = response.json()
                error_msg = error_detail.get('error', {}).get('message', 'Unknown error')
                st.error(f"❌ API Error {response.status_code}: {error_msg}")
            except:
                st.error(f"❌ API Error: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def check_topic_relevance(topic, subject):
    """Simplified topic relevance check without keywords database"""
    if not topic or not subject:
        return True, []
    
    return True, []
    
   
    

def get_available_subjects(board, grade):
    """Get available subjects for board and grade"""
    subjects_data = get_subjects_by_board()
    board_data = subjects_data.get(board, {})
    
    # For IB, extract numeric grade from string like "Grade 5 (PYP)"
    if board == "IB" and isinstance(grade, str):
        try:
            grade_num = int(grade.split()[1])
            return board_data.get(grade_num, [])
        except (IndexError, ValueError):
            return []
    
    return board_data.get(grade, [])

def create_questions_pdf(test_data, filename="questions.pdf"):
    """Create PDF with questions only"""
    if not PDF_AVAILABLE:
        st.error("PDF generation not available. Please install reportlab: pip install reportlab")
        return None
    
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # II Tuition Title style
        tuitions_title_style = ParagraphStyle(
            'TuitionsTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=10,
            alignment=1,  # Center
            textColor=colors.darkblue
        )
        
        test_info = test_data.get('test_info', {})
        questions = test_data.get('questions', [])
        
        # II Tuition Header
        story.append(Paragraph("🎓 II Tuition Mock Test Generated", tuitions_title_style))
        story.append(Paragraph(f"{test_info.get('subject', 'Subject')} Mock Test", tuitions_title_style))
        story.append(Paragraph(f"Board: {test_info.get('board', 'N/A')} | Grade: {test_info.get('grade', 'N/A')} | Topic: {test_info.get('topic', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Instructions
        story.append(Paragraph("Instructions:", styles['Heading2']))
        story.append(Paragraph("• Read all questions carefully", styles['Normal']))
        story.append(Paragraph("• Choose the best answer for multiple choice questions", styles['Normal']))
        story.append(Paragraph("• Write clearly for descriptive answers", styles['Normal']))
        story.append(Paragraph("• Manage your time effectively", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Questions
        for i, question in enumerate(questions, 1):
            story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", styles['Normal']))
            
            if question.get('type') == 'mcq' and 'options' in question:
                options = question['options']
                for option_key, option_text in options.items():
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{option_key})</b> {option_text}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def create_answers_pdf(test_data, filename="answers.pdf"):
    """Create PDF with answers only"""
    if not PDF_AVAILABLE:
        st.error("PDF generation not available. Please install reportlab: pip install reportlab")
        return None
    
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        test_info = test_data.get('test_info', {})
        questions = test_data.get('questions', [])
        
        # Header
        story.append(Paragraph("🎓 II Tuition Mock Test - Answer Key", styles['Heading1']))
        story.append(Paragraph(f"{test_info.get('subject', 'Subject')} Mock Test Answers", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Answers
        for i, question in enumerate(questions, 1):
            story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", styles['Normal']))
            
            # Show the correct answer
            if 'correct_answer' in question and question['correct_answer']:
                story.append(Paragraph(f"<b>Correct Answer:</b> {question['correct_answer']}", styles['Normal']))
            elif 'sample_answer' in question and question['sample_answer']:
                story.append(Paragraph(f"<b>Sample Answer:</b> {question['sample_answer']}", styles['Normal']))
            
            # Show explanation if available
            if 'explanation' in question and question['explanation']:
                story.append(Paragraph(f"<b>Explanation:</b> {question['explanation']}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def show_test_creator(navigate_to=None):
    """
    FIXED: Test creator page content for II Tuitions Mock Test Generator
    Fixed paper type selection UI spacing and JSON parse errors
    """
    
    # Page Header - Using centralized styling
    st.markdown('<h1 style="color: #2c3e50; text-align: center; font-size: 2.5rem; margin-bottom: 1rem;">🎯 Create Mock Test</h1>', unsafe_allow_html=True)
    
    # API Test Section
    st.markdown("### 🔍 Claude AI Configuration Test")
    
    # Show API key status
    st.write("**Current API Key Status:**")
    if CLAUDE_API_KEY and CLAUDE_API_KEY != "REPLACE_WITH_YOUR_API_KEY":
        key_preview = CLAUDE_API_KEY[:15] + "..." + CLAUDE_API_KEY[-8:]
        st.success(f"✅ API Key configured: {key_preview}")
    else:
        st.error("❌ API Key not configured")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Test Claude API Connection", key="test_api_btn"):
            with st.spinner("Testing API connection..."):
                working, message = test_claude_api()
                if working:
                    st.success(f"✅ {message}")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")
                    if "401" in message:
                        st.info("🔧 **Troubleshooting Tips:**")
                        st.info("1. Check if your API key is correct")
                        st.info("2. Verify you have Claude API credits remaining")
                        st.info("3. Make sure the API key hasn't expired")
    
    with col2:
        if st.button("📋 Detailed API Verification", key="verify_api_btn"):
            verify_api_key()
    
    st.markdown("---")
    
    # Step 1: Board Selection - Using centralized CSS classes
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">1</div>
        <div class="step-title">SELECT EDUCATION BOARD:</div>
    </div>
    """, unsafe_allow_html=True)
    
    board_options = ["Select Board", "CBSE", "ICSE", "IB", "Cambridge IGCSE", "State Board"]
    selected_board = st.selectbox(
        "Choose from major education boards recognized globally", 
        board_options, 
        index=0,
        key="board_select"
    )
    
    if selected_board != "Select Board":
        board = selected_board
    else:
        board = ''
    
    # Step 2: Grade Selection - Dynamic based on board
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">2</div>
        <div class="step-title">SELECT GRADE LEVEL:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if board:
        if board == "IB":
            grade_options = ["Select Grade"] + get_ib_grade_options()
            selected_grade = st.selectbox(
                "Select your current IB programme and grade", 
                grade_options, 
                index=0,
                key=f"grade_select_{board}"
            )
            
            if selected_grade != "Select Grade":
                grade = selected_grade
            else:
                grade = 0
        else:
            grade_options = ["Select Grade"] + [f"Grade {i}" for i in range(1, 13)]
            selected_grade = st.selectbox(
                "Select your current academic grade (1-12)", 
                grade_options, 
                index=0,
                key=f"grade_select_{board}"
            )
            
            if selected_grade != "Select Grade":
                try:
                    grade_text = str(selected_grade)
                    grade_num = int(grade_text.replace("Grade ", ""))
                    grade = grade_num
                except (ValueError, AttributeError):
                    grade = 0
            else:
                grade = 0
    else:
        st.selectbox(
            "Select your current academic grade (1-12)", 
            ["Please select Board first"], 
            disabled=True,
            key="grade_disabled"
        )
        grade = 0
    
    # Step 3: Subject Selection - Using centralized CSS classes
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">3</div>
        <div class="step-title">SELECT SUBJECT:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if board and grade:
        available_subjects = get_available_subjects(board, grade)
        
        if available_subjects:
            subject_options = ["Select Subject"] + available_subjects
            selected_subject = st.selectbox(
                "Choose the subject for which you want to generate the mock test", 
                subject_options, 
                index=0,
                key=f"subject_select_{board}_{grade}"
            )
            
            if selected_subject != "Select Subject":
                subject = selected_subject
                if board == "IB":
                    st.success(f"✅ Selected: {subject} for {board} {grade}")
                else:
                    st.success(f"✅ Selected: {subject} for {board} Grade {grade}")
            else:
                subject = ''
        else:
            st.error(f"❌ No subjects available for {board} Grade {grade}")
            subject = ''
    else:
        st.selectbox(
            "Choose the subject for which you want to generate the mock test", 
            ["Please select Board and Grade first"], 
            disabled=True,
            key=f"subject_placeholder"
        )
        subject = ''
    
    # Step 4: Topic Input with Enhanced Curriculum Validation
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">4</div>
        <div class="step-title">ENTER TOPIC:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if subject:
        # Show curriculum topics for the selected combination
        curriculum_topics = get_topics_by_board_grade_subject(board, grade, subject)
        
        if curriculum_topics:
            st.info(f"📚 **{board} Grade {grade} {subject} Curriculum Topics:**")
            
            # Display topics in columns for better organization
            cols = st.columns(3)
            for i, topic in enumerate(curriculum_topics[:15]):  # Show first 15 topics
                with cols[i % 3]:
                    st.write(f"• {topic}")
            
            if len(curriculum_topics) > 15:
                st.info(f"📖 And {len(curriculum_topics) - 15} more...")
        
        topic_input = st.text_input(
            "Specify the exact topic or chapter you want to focus on", 
            placeholder=f"e.g., {', '.join(curriculum_topics[:3]) if curriculum_topics else 'Enter topic name'}", 
            key=f"topic_input_{subject}"
        )
        
        if topic_input:
            topic = topic_input.strip()
        else:
            topic = ''
    else:
        st.text_input(
            "Specify the exact topic or chapter you want to focus on", 
            placeholder="Please select a subject first", 
            disabled=True,
            key="topic_disabled"
        )
        topic = ''
    
    # Enhanced Topic validation with comprehensive database
    topic_valid = True
    
    if topic and subject and board and grade:
        # Use new curriculum validation function
        is_relevant, curriculum_topics = validate_topic_against_curriculum(board, grade, subject, topic)
        
        if not is_relevant:
            topic_valid = False
            st.error(f"⚠️ Topic '{topic}' doesn't match {board} Grade {grade} {subject} curriculum")
            
            # Show curriculum-based suggestions
            if curriculum_topics:
                st.info(f"💡 **Suggested topics from {board} Grade {grade} {subject} curriculum:**")
                
                col1, col2 = st.columns(2)
                topics_count = len(curriculum_topics)
                mid_point = min(topics_count // 2, 8)  # Limit to 8 suggestions per column
                
                with col1:
                    st.write("**Primary Topics:**")
                    for i in range(min(mid_point, len(curriculum_topics))):
                        curriculum_topic = str(curriculum_topics[i])
                        st.write(f"• {curriculum_topic}")
                
                with col2:
                    st.write("**Additional Topics:**")
                    start_idx = mid_point
                    for i in range(start_idx, min(start_idx + 8, len(curriculum_topics))):
                        if i < len(curriculum_topics):
                            curriculum_topic = str(curriculum_topics[i])
                            st.write(f"• {curriculum_topic}")
                            
                # Show that there are more topics available
                if len(curriculum_topics) > 16:
                    st.info(f"📚 And {len(curriculum_topics) - 16} more topics in {board} Grade {grade} {subject} curriculum")
        else:
            st.success(f"✅")
            # Show matched curriculum topics for confirmation
            matched_topics = [t for t in curriculum_topics if topic.lower() in t.lower() or t.lower() in topic.lower()]
            if matched_topics:
                st.info(f"🎯 **Matched curriculum topics:** {', '.join(matched_topics[:3])}")
    elif topic and not (subject and board and grade):
        st.warning("⚠️ Please select board, grade, and subject first to validate your topic")
        topic_valid = False
    
    # Validation Summary - Using centralized CSS classes
    st.markdown("""
    <div class="validation-box">
        <div class="validation-title">📋 VALIDATION SUMMARY</div>
    </div>
    """, unsafe_allow_html=True)
    
    validation_results = []
    
    if board:
        validation_results.append((f"✅ BOARD: {board} Selected", "success"))
    else:
        validation_results.append(("❌ BOARD: Please select a board", "error"))
    
    if grade:
        if board == "IB":
            validation_results.append((f"✅ GRADE: {grade} Selected", "success"))
        else:
            validation_results.append((f"✅ GRADE: Grade {grade} Selected", "success"))
    else:
        validation_results.append(("❌ GRADE: Please select a grade", "error"))
    
    if subject:
        validation_results.append((f"✅ SUBJECT: {subject} Selected", "success"))
    else:
        validation_results.append(("❌ SUBJECT: Please select a subject", "error"))
    
    if topic and topic_valid:
        validation_results.append((f"✅ TOPIC: '{topic}' is Valid", "success"))
    elif topic and not topic_valid:
        validation_results.append(("❌ TOPIC: Topic doesn't match curriculum", "error"))
    else:
        validation_results.append(("❌ TOPIC: Please enter a topic", "error"))
    
    # Display validation results
    for message, msg_type in validation_results:
        if msg_type == "success":
            st.success(message)
        else:
            st.error(message)
    
    # Check if all validations pass
    valid_count = sum(1 for result in validation_results if result[0].startswith("✅"))
    all_valid = (valid_count == 4)
    
    if all_valid:
        st.success("🎉 All validations passed! Ready to create curriculum-aligned mock test.")
    
    # Step 5: Test Configuration - FIXED UI with proper spacing
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">5</div>
        <div class="step-title">SELECT PAPER TYPE:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if board and grade:
        # Get paper types based on board and grade
        paper_options = get_paper_types_by_board_and_grade(board, grade)
        
        if paper_options:
            st.markdown("### 📝 Choose your preferred paper format:")
            
            # FIXED: Better spacing for paper type selection
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                <h4 style="color: #495057; margin-bottom: 15px;">📋 Paper Type Options:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Create columns for better layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # FIXED: Add spacing between radio options
                paper_type = st.radio(
                    "Select paper format:",
                    paper_options,
                    key="paper_type_radio",
                    help="Choose the examination format that matches your requirements"
                )
            
            with col2:
                st.markdown("### ℹ️ Paper Details:")
                # Enhanced descriptions based on paper type
                if "40 MCQs" in paper_type:
                    st.info("📊 40 Multiple Choice Questions\n⏱️ Duration: 1 minutes")
                elif "30 MCQs" in paper_type:
                    st.info("📊 30 Multiple Choice Questions\n⏱️ Duration: 1 minutes")
                elif "25 MCQs" in paper_type or "25 MCQ" in paper_type:
                    st.info("📊 25 Multiple Choice Questions\n⏱️ Duration: 1 minutes")
                elif "20 Mixed" in paper_type:
                    st.info("📊 20 Mixed Questions (MCQ + Short)\n⏱️ Duration: 1 minutes")
                elif "15 Short + 15 Long" in paper_type:
                    st.info("📝 15 Short + 15 Long Answer Questions\n⏱️ Duration: 1 minutes")
                elif "15 Activity" in paper_type or "Skills Practice" in paper_type:
                    st.info("🎯 15 Hands-on Activity Tasks\n⏱️ Duration: 1 minutes")
                elif "25 Exploration" in paper_type or "Inquiry Tasks" in paper_type:
                    st.info("🔍 25 Inquiry-based Questions\n⏱️ Duration: 1 minutes")
                elif "Primary Assessment" in paper_type or "Foundation Test" in paper_type:
                    st.info("👶 20 Age-appropriate Mixed Questions\n⏱️ Duration: 1 minutes")
                elif "Board Pattern Paper 1" in paper_type:
                    st.info("📋 25 MCQs + 15 Short Answers\n⏱️ Duration: 1 minutes")
                elif "Board Pattern Paper 2" in paper_type:
                    st.info("📝 10 Short + 10 Long Answer Questions\n⏱️ Duration: 1 minutes")
                elif "Sample Paper Format" in paper_type or "Mock" in paper_type:
                    st.info("📋 Full Board Exam Pattern\n⏱️ Duration: 1 minutes")
                else:
                    st.info("📝 Custom Question Format\n⏱️ Duration: Varies")
        else:
            st.error("❌ No paper types available for this grade")
            paper_type = ""
    else:
        st.markdown("### 📝 Paper Type Selection")
        st.info("⚠️ Please select Board and Grade first to see available paper types")
        paper_type = ""
    
    # Additional options
    st.markdown("### ⚙️ Additional Options")
    include_answers = st.checkbox(
        "Show answers on screen after generation", 
        value=False, 
        key="show_answers_checkbox",
        help="Enable this to see correct answers immediately after test generation"
    )
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        create_btn = st.button(
            "🚀 CREATE CURRICULUM-ALIGNED MOCK TEST", 
            use_container_width=True, 
            key="create_test_btn",
            help="Generate AI-powered test questions based on your selections"
        )
        
        if create_btn:
            if not all_valid or not paper_type:
                st.error("❌ Please fix validation errors and select paper type before creating the test")
            else:
                with st.spinner("🤖 Generating curriculum-aligned questions..."):
                    test_data = generate_questions(board, grade, subject, topic, paper_type, include_answers)
                    
                    if test_data:
                        st.success("✅ Curriculum-aligned test generated successfully!")
                        st.balloons()
                        st.session_state.generated_test = test_data
                        if navigate_to:
                            navigate_to('test_display')
                        else:
                            st.session_state.current_page = 'test_display'
                            st.rerun()
                    else:
                        st.error("❌ Failed to generate test. Please check your API connection and try again.")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, key="back_home_btn"):
            if navigate_to:
                navigate_to('home')
            else:
                st.session_state.current_page = 'home'
                st.rerun()

# Alternative function names for backward compatibility
def show_mock_test_creator(navigate_to=None):
    """Alternative function name for test creator"""
    show_test_creator(navigate_to)

def main():
    """Main function for standalone testing"""
    show_test_creator()

if __name__ == "__main__":
    main()
