import streamlit as st

# Import centralized styles - CSS is handled by main.py
# No CSS imports needed here as styles are centralized

def display_generated_test(test_data):
    """Display the generated test in a formatted way with support for all question types"""
    if not test_data:
        st.error("No test data to display")
        return
    
    test_info = test_data.get('test_info', {})
    questions = test_data.get('questions', [])
    show_answers_on_screen = test_info.get('show_answers_on_screen', False)
    
    # Test header - Using centralized styling
    st.markdown(f"""
    <h1 style="text-align: center; color: #2c3e50; font-size: 2.5rem; margin-bottom: 1rem;">🎓 II Tuition Mock Test Generated</h1>
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="color: #333; font-size: 1.5rem;">{test_info.get('subject', 'Subject')} Mock Test</h2>
        <p><strong>Board:</strong> {test_info.get('board', 'N/A')} | 
        <strong>Grade:</strong> {test_info.get('grade', 'N/A')} | 
        <strong>Topic:</strong> {test_info.get('topic', 'N/A')}</p>
        <p><strong>Paper Type:</strong> {test_info.get('paper_type', 'N/A')} | 
        <strong>Total Questions:</strong> {test_info.get('total_questions', len(questions))}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced test statistics display
    mcq_count = test_info.get('mcq_count', 0)
    short_count = test_info.get('short_count', 0)
    long_count = test_info.get('long_count', 0)
    
    if mcq_count + short_count + long_count > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            if mcq_count > 0:
                st.metric("Multiple Choice", mcq_count, "questions")
        with col2:
            if short_count > 0:
                st.metric("Short Answer", short_count, "questions")
        with col3:
            if long_count > 0:
                st.metric("Long Answer", long_count, "questions")
        st.markdown("---")
    
    # Instructions section - Using centralized CSS classes
    st.markdown("### 📋 Instructions:")
    st.markdown("""
    <div class="instructions-box" style="height: 120px; max-height: 120px; overflow: hidden;">
        <h4 class="instructions-title">📖 Test Guidelines</h4>
        <p style="color: #2c3e50; margin-bottom: 0;">This test is designed according to your curriculum standards. Read questions carefully and choose the best answers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    instructions_col1, instructions_col2 = st.columns(2)
    
    with instructions_col1:
        st.markdown("""
        - Read all questions carefully before answering
        - For multiple choice questions, select the best option
        - Take your time to understand each question
        """)
    
    with instructions_col2:
        st.markdown("""
        - Show all working for calculation problems
        - Write clearly for descriptive answers
        - Manage your time effectively
        """)
    
    st.markdown("---")
    
    # Questions display with enhanced formatting for different question types
    for i, question in enumerate(questions, 1):
        question_type = question.get('type', 'mcq')
        
        # Question header with type indicator
        if question_type == 'mcq':
            type_badge = "🔘 Multiple Choice"
            type_color = "#667eea"
        elif question_type == 'short':
            type_badge = "📝 Short Answer"
            type_color = "#f093fb"
            marks = question.get('marks', 3)
        elif question_type == 'long':
            type_badge = "📋 Long Answer"
            type_color = "#4facfe"
            marks = question.get('marks', 6)
        else:
            type_badge = "❓ Question"
            type_color = "#667eea"
        
        st.markdown(f"""
        <div class="question-box" style="min-height: 120px; max-height: auto; overflow: visible;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h4 style="color: {type_color}; margin: 0;">Question {i}</h4>
                <span style="background-color: {type_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{type_badge}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display question text
        st.markdown(f"**{question.get('question', 'Question text missing')}**")
        
        # Handle different question types
        if question_type == 'mcq' and 'options' in question:
            # Multiple Choice Question
            options = question['options']
            for option_key, option_text in options.items():
                st.write(f"**{option_key})** {option_text}")
            
            # Show correct answer if enabled
            if show_answers_on_screen and 'correct_answer' in question and question['correct_answer']:
                st.success(f"**✅ Correct Answer: {question['correct_answer']}**")
                # Show explanation if available
                if 'explanation' in question and question['explanation']:
                    st.info(f"**💡 Explanation:** {question['explanation']}")
        
        elif question_type == 'short':
            # Short Answer Question
            marks = question.get('marks', 3)
            st.markdown(f"**📝 [Short Answer Question - {marks} marks]**")
            st.markdown("*Write your answer in 2-5 sentences below:*")
            
            # Show sample answer if enabled
            if show_answers_on_screen and 'sample_answer' in question and question['sample_answer']:
                st.success(f"**✅ Sample Answer:** {question['sample_answer']}")
        
        elif question_type == 'long':
            # Long Answer Question
            marks = question.get('marks', 6)
            st.markdown(f"**📋 [Long Answer Question - {marks} marks]**")
            st.markdown("*Write a detailed answer with explanations and examples:*")
            
            # Show sample answer if enabled
            if show_answers_on_screen and 'sample_answer' in question and question['sample_answer']:
                st.success(f"**✅ Sample Answer:** {question['sample_answer']}")
        
        else:
            # Legacy support for old question format
            if 'options' in question:
                options = question['options']
                for option_key, option_text in options.items():
                    st.write(f"**{option_key})** {option_text}")
                
                if show_answers_on_screen and 'correct_answer' in question and question['correct_answer']:
                    st.success(f"**✅ Correct Answer: {question['correct_answer']}**")
                    if 'explanation' in question and question['explanation']:
                        st.info(f"**💡 Explanation:** {question['explanation']}")
            else:
                st.write("**[Answer space provided below]**")
                if show_answers_on_screen and 'sample_answer' in question and question['sample_answer']:
                    st.info(f"**Sample Answer:** {question['sample_answer']}")
        
        st.markdown("---")

def create_enhanced_questions_pdf(test_data, filename="questions.pdf"):
    """Create PDF with questions supporting all question types"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        test_info = test_data.get('test_info', {})
        questions = test_data.get('questions', [])
        
        # Enhanced title styling
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=10,
            alignment=1,
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=1,
            textColor=colors.darkblue
        )
        
        # Header
        story.append(Paragraph("🎓 II Tuition Mock Test", title_style))
        story.append(Paragraph(f"{test_info.get('subject', 'Subject')} - {test_info.get('topic', 'Topic')}", subtitle_style))
        story.append(Paragraph(f"Board: {test_info.get('board', 'N/A')} | Grade: {test_info.get('grade', 'N/A')} | Paper: {test_info.get('paper_type', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Test statistics
        mcq_count = test_info.get('mcq_count', 0)
        short_count = test_info.get('short_count', 0)
        long_count = test_info.get('long_count', 0)
        
        if mcq_count + short_count + long_count > 0:
            stats_text = f"Question Distribution: "
            if mcq_count > 0:
                stats_text += f"MCQ: {mcq_count} | "
            if short_count > 0:
                stats_text += f"Short Answer: {short_count} | "
            if long_count > 0:
                stats_text += f"Long Answer: {long_count}"
            
            story.append(Paragraph(stats_text.rstrip(" | "), styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Instructions
        story.append(Paragraph("Instructions:", styles['Heading3']))
        story.append(Paragraph("• Read all questions carefully", styles['Normal']))
        story.append(Paragraph("• Choose the best answer for multiple choice questions", styles['Normal']))
        story.append(Paragraph("• Write clearly for descriptive answers", styles['Normal']))
        story.append(Paragraph("• Show all working for calculation problems", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Questions
        for i, question in enumerate(questions, 1):
            question_type = question.get('type', 'mcq')
            
            # Question header with type
            if question_type == 'mcq':
                type_text = "[Multiple Choice]"
            elif question_type == 'short':
                marks = question.get('marks', 3)
                type_text = f"[Short Answer - {marks} marks]"
            elif question_type == 'long':
                marks = question.get('marks', 6)
                type_text = f"[Long Answer - {marks} marks]"
            else:
                type_text = ""
            
            story.append(Paragraph(f"<b>Question {i}: {type_text}</b>", styles['Normal']))
            story.append(Paragraph(question.get('question', ''), styles['Normal']))
            
            # Handle different question types
            if question_type == 'mcq' and 'options' in question:
                options = question['options']
                for option_key, option_text in options.items():
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{option_key})</b> {option_text}", styles['Normal']))
            elif question_type == 'short':
                story.append(Paragraph("Answer:", styles['Normal']))
                story.append(Spacer(1, 30))  # Space for writing
            elif question_type == 'long':
                story.append(Paragraph("Answer:", styles['Normal']))
                story.append(Spacer(1, 60))  # More space for long answers
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def create_enhanced_answers_pdf(test_data, filename="answers.pdf"):
    """Create PDF with answers supporting all question types"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        test_info = test_data.get('test_info', {})
        questions = test_data.get('questions', [])
        
        # Header
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=10,
            alignment=1,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("🎓 II Tuition Mock Test - Answer Key", title_style))
        story.append(Paragraph(f"{test_info.get('subject', 'Subject')} Answers", styles['Heading2']))
        story.append(Paragraph(f"Board: {test_info.get('board', 'N/A')} | Grade: {test_info.get('grade', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Answers
        for i, question in enumerate(questions, 1):
            question_type = question.get('type', 'mcq')
            
            story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", styles['Normal']))
            
            # Show answers based on question type
            if question_type == 'mcq' and 'correct_answer' in question and question['correct_answer']:
                story.append(Paragraph(f"<b>Correct Answer:</b> {question['correct_answer']}", styles['Normal']))
                if 'explanation' in question and question['explanation']:
                    story.append(Paragraph(f"<b>Explanation:</b> {question['explanation']}", styles['Normal']))
            
            elif (question_type in ['short', 'long']) and 'sample_answer' in question and question['sample_answer']:
                marks = question.get('marks', 3 if question_type == 'short' else 6)
                story.append(Paragraph(f"<b>Sample Answer ({marks} marks):</b> {question['sample_answer']}", styles['Normal']))
            
            # Legacy support
            elif 'correct_answer' in question and question['correct_answer']:
                story.append(Paragraph(f"<b>Correct Answer:</b> {question['correct_answer']}", styles['Normal']))
            elif 'sample_answer' in question and question['sample_answer']:
                story.append(Paragraph(f"<b>Sample Answer:</b> {question['sample_answer']}", styles['Normal']))
            
            if 'explanation' in question and question['explanation'] and question_type != 'mcq':
                story.append(Paragraph(f"<b>Explanation:</b> {question['explanation']}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def show_test_display(navigate_to=None):
    """
    Test display page for II Tuitions Mock Test Generator
    Shows generated test results and provides navigation options
    Uses centralized exam pad styling from styles/exam_pad_styles.py
    """
    
    # Check if test data exists
    if 'generated_test' in st.session_state and st.session_state.generated_test:
        test_data = st.session_state.generated_test
        
        # Header with navigation buttons
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            if st.button("← Back to Create Test", key="back_to_create"):
                if navigate_to:
                    navigate_to('create_test')
                else:
                    st.session_state.current_page = 'create_test'
                    st.rerun()
        
        with col2:
            if st.button("🏠 Home", key="home_btn"):
                if navigate_to:
                    navigate_to('home')
                else:
                    st.session_state.current_page = 'home'
                    st.rerun()
        
        with col3:
            if st.button("📄 Questions PDF", key="questions_pdf_btn"):
                try:
                    with st.spinner("Generating enhanced questions PDF..."):
                        filename = create_enhanced_questions_pdf(test_data, "questions.pdf")
                        if filename:
                            # Download button
                            with open(filename, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Questions PDF",
                                    data=pdf_file.read(),
                                    file_name=f"mock_test_questions_{test_data.get('test_info', {}).get('subject', 'test')}_grade_{test_data.get('test_info', {}).get('grade', 'X')}.pdf",
                                    mime="application/pdf",
                                    key="download_questions"
                                )
                        
                except ImportError:
                    st.error("📋 PDF generation not available. Please install reportlab: `pip install reportlab`")
        
        with col4:
            if st.button("📝 Answers PDF", key="answers_pdf_btn"):
                try:
                    with st.spinner("Generating enhanced answers PDF..."):
                        filename = create_enhanced_answers_pdf(test_data, "answers.pdf")
                        if filename:
                            # Download button
                            with open(filename, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Answers PDF",
                                    data=pdf_file.read(),
                                    file_name=f"mock_test_answers_{test_data.get('test_info', {}).get('subject', 'test')}_grade_{test_data.get('test_info', {}).get('grade', 'X')}.pdf",
                                    mime="application/pdf",
                                    key="download_answers"
                                )
                        
                except ImportError:
                    st.error("📋 PDF generation not available. Please install reportlab: `pip install reportlab`")
        
        with col5:
            if st.button("🔄 Generate New", key="generate_new_btn"):
                if navigate_to:
                    navigate_to('create_test')
                else:
                    st.session_state.current_page = 'create_test'
                    st.rerun()
        
        # PDF Installation Notice
        try:
            import reportlab
        except ImportError:
            st.warning("📋 **PDF functionality requires additional package.** Run: `pip install reportlab` to enable PDF downloads.")
        
        # Display the generated test using enhanced formatting
        display_generated_test(test_data)
        
    else:
        # No test data available - Using centralized CSS classes
        st.markdown("""
        <div class="validation-box" style="height: 150px; max-height: 150px; overflow: hidden;">
            <div class="validation-title">⚠️ NO TEST DATA FOUND</div>
            <p style="color: #667eea; text-align: center; margin: 20px 0;">
                No mock test has been generated yet. Please create a test first to view results here.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("← Back to Create Test", use_container_width=True, key="back_to_create_no_data"):
                if navigate_to:
                    navigate_to('create_test')
                else:
                    st.session_state.current_page = 'create_test'
                    st.rerun()

def show_mock_test_generator(navigate_to=None):
    """
    Main mock test generator/display function
    Uses centralized exam pad styling from styles/exam_pad_styles.py
    All content styling comes from the centralized CSS system
    """
    
    # Header - Using centralized styling
    st.markdown('<h1 style="color: #2c3e50; text-align: center; font-size: 2.5rem; margin-bottom: 1rem;">📊 Mock Test Results</h1>', unsafe_allow_html=True)
    
    # Info section - Using centralized CSS classes
    st.markdown("""
    <div class="instructions-box" style="height: 120px; max-height: 120px; overflow: hidden;">
        <div class="instructions-title">🎯 Test Generation Complete!</div>
        <div style="color: #2c3e50; font-size: 1rem; line-height: 1.6;">
            This page displays your generated mock test with all questions and answers.
            Supports MCQ, Short Answer, and Long Answer question types.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced features section
    st.markdown("""
    <div class="validation-box" style="height: 280px; max-height: 280px; overflow: hidden;">
        <div class="validation-title">📚 ENHANCED FEATURES</div>
        <div style="color: #667eea; font-size: 1rem; line-height: 1.8; text-align: left;">
            <strong>✅ Current Features:</strong><br>
            • Multiple question types (MCQ, Short, Long Answer)<br>
            • Board-specific paper formats<br>
            • Grade-appropriate difficulty levels<br>
            • Enhanced PDF generation with question types<br>
            • Comprehensive answer keys<br>
            • Topic-specific question generation<br><br>
            <strong>🚧 Coming Soon:</strong><br>
            • Interactive test taking interface<br>
            • Timer functionality for timed tests<br>
            • Student performance analytics<br>
            • Question-wise difficulty analysis<br>
            • Detailed score reports<br>
            • Progress tracking across multiple tests
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Call the main test display function
    show_test_display(navigate_to)

# Alternative function names for backward compatibility and flexibility
def show_test_generator(navigate_to=None):
    """Alternative function name for test generator"""
    show_mock_test_generator(navigate_to)

def show_results_page(navigate_to=None):
    """Alternative function name for results page"""
    show_test_display(navigate_to)

def main():
    """Main function for standalone testing"""
    show_mock_test_generator()

if __name__ == "__main__":
    main()
