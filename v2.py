import streamlit as st
import os
import time
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai

# === CONFIG AND INITIALIZATION ===
st.set_page_config(page_title="TOEFL Exam Trainer", layout="centered")
load_dotenv()  # Load environment variables

# API configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash"  # Corrected model name

# Initialize API
if not API_KEY:
    st.error("GEMINI_API_KEY not found in .env file. Please make sure it's set correctly.")
    st.stop()

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)
    # Quick test
    model.generate_content("Test", generation_config=genai.types.GenerationConfig(max_output_tokens=10))
    st.success("Gemini API initialized successfully.")
except Exception as e:
    st.error(f"Failed to initialize Gemini API: {e}")
    st.stop()

# === HELPER FUNCTIONS ===
def call_gemini(prompt, max_tokens=2000, temperature=0.7):
    """Call Gemini API and extract response text"""
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        # Extract text from response
        if hasattr(response, "text") and response.text:
            return response.text
        
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                return "".join(part.text for part in candidate.content.parts if hasattr(part, "text"))
        
        return "Error: Could not extract text from API response"
    except Exception as e:
        print(f"API ERROR: {str(e)}")
        return f"Error: {str(e)}"

def start_timer(duration_secs):
    """Set a timer in session state"""
    st.session_state.timer_end = time.time() + duration_secs

def format_time(seconds):
    """Format seconds into minutes:seconds"""
    mins, secs = divmod(max(0, seconds), 60)
    return f"{int(mins):02d}:{int(secs):02d}"

def is_timer_expired():
    """Check if timer has expired"""
    if "timer_end" not in st.session_state:
        return False
    return time.time() >= st.session_state.timer_end

def get_reading_topic():
    """Select a reading topic with rotation to ensure diversity"""
    # Comprehensive list of academic topics that appear in TOEFL
    all_topics = [
        # Natural Sciences
        {"category": "Biology", "topics": ["Evolutionary Biology", "Ecosystems", "Cell Biology", "Genetics", "Microbiology"]},
        {"category": "Environmental Science", "topics": ["Climate Change", "Conservation", "Sustainable Development", "Biodiversity", "Natural Resources"]},
        {"category": "Astronomy", "topics": ["Stellar Evolution", "Planetary Science", "Cosmology", "Space Exploration", "Astrophysics"]},
        {"category": "Geology", "topics": ["Plate Tectonics", "Mineralogy", "Natural Disasters", "Earth's History", "Geological Formations"]},
        
        # Social Sciences
        {"category": "Anthropology", "topics": ["Cultural Anthropology", "Archaeological Discoveries", "Human Evolution", "Indigenous Cultures", "Social Structures"]},
        {"category": "Psychology", "topics": ["Cognitive Development", "Behavioral Psychology", "Memory Formation", "Social Psychology", "Psychological Disorders"]},
        {"category": "Economics", "topics": ["Economic Systems", "Market Structures", "International Trade", "Economic Development", "Monetary Policy"]},
        {"category": "Sociology", "topics": ["Social Movements", "Urbanization", "Social Institutions", "Demographic Change", "Cultural Norms"]},
        
        # Humanities
        {"category": "History", "topics": ["Ancient Civilizations", "Industrial Revolution", "Social Movements", "Cultural Exchange", "Political Systems"]},
        {"category": "Arts", "topics": ["Art History", "Artistic Movements", "Architecture", "Music History", "Cultural Expression"]},
        {"category": "Philosophy", "topics": ["Ethics", "Logic", "Metaphysics", "Political Philosophy", "Eastern Philosophy"]},
        
        # Technology
        {"category": "Technology", "topics": ["Artificial Intelligence", "Biotechnology", "Information Technology", "Renewable Energy", "Transportation Technology"]},
        {"category": "Agriculture", "topics": ["Sustainable Farming", "Food Systems", "Agricultural History", "Crop Development", "Farming Technologies"]}
    ]
    
    # Check if we've used all topics
    used = st.session_state.used_topics
    if len(used) >= sum(len(cat["topics"]) for cat in all_topics):
        # Reset if we've used all topics
        st.session_state.used_topics = []
        used = []
    
    # Find categories with unused topics
    available_topics = []
    for category in all_topics:
        for topic in category["topics"]:
            full_topic = f"{category['category']}: {topic}"
            if full_topic not in used:
                available_topics.append(full_topic)
    
    # If somehow we have no available topics, reset
    if not available_topics:
        st.session_state.used_topics = []
        return get_reading_topic()
    
    # Select a topic randomly from available options
    import random
    selected = random.choice(available_topics)
    
    # Add to used topics
    st.session_state.used_topics.append(selected)
    
    return selected

def get_writing_theme():
    """Select a writing theme with rotation to ensure diversity"""
    # Independent writing task themes that match authentic TOEFL content
    independent_themes = [
        # Education and Learning
        {"category": "Education", "themes": [
            "Role of technology in education",
            "Traditional vs. modern teaching methods",
            "Value of arts education",
            "Learning from mistakes vs. learning from success",
            "Practical skills vs. theoretical knowledge"
        ]},
        
        # Society and Culture
        {"category": "Society", "themes": [
            "Urban vs. rural living",
            "Effects of social media",
            "Cultural preservation vs. adaptation",
            "Individual rights vs. community needs",
            "Generational differences"
        ]},
        
        # Work and Career
        {"category": "Career", "themes": [
            "Job satisfaction vs. high salary",
            "Working from home vs. office",
            "Career change vs. job stability",
            "Entrepreneurship vs. employment",
            "Specializing vs. generalist knowledge"
        ]},
        
        # Environment and Technology
        {"category": "Environment", "themes": [
            "Environmental protection vs. economic development",
            "Individual vs. governmental responsibility for climate",
            "Technology's impact on environment",
            "Traditional vs. alternative energy",
            "Local vs. global environmental solutions"
        ]},
        
        # Lifestyle and Personal Choices
        {"category": "Lifestyle", "themes": [
            "Travel experiences vs. material possessions",
            "Traditional vs. non-traditional lifestyle choices",
            "Planning vs. spontaneity",
            "Independence vs. interdependence",
            "Work-life balance"
        ]}
    ]
    
    # Integrated writing themes (topics where a reading and lecture might contrast)
    integrated_themes = [
        {"category": "Science", "themes": [
            "Scientific theory controversy",
            "New research findings",
            "Environmental phenomenon",
            "Medical discovery",
            "Technological innovation"
        ]},
        
        {"category": "Social Science", "themes": [
            "Historical interpretation",
            "Economic policy",
            "Psychological theory",
            "Educational approach",
            "Urban development plan"
        ]},
        
        {"category": "Academic", "themes": [
            "Research methodology",
            "Academic theory critique",
            "Campus policy change",
            "Student learning approach",
            "Academic resource allocation"
        ]}
    ]
    
    # Determine if we're selecting for independent or integrated writing
    is_integrated = "Integrated" in st.session_state.get("current_writing_task", "")
    theme_list = integrated_themes if is_integrated else independent_themes
    
    # Track used themes
    used = st.session_state.used_writing_themes
    
    # Check if we've used all themes for current type
    total_themes = sum(len(cat["themes"]) for cat in theme_list)
    themes_of_current_type = [t for t in used if (("integrated:" in t.lower()) == is_integrated)]
    
    if len(themes_of_current_type) >= total_themes:
        # Filter out themes of this type to reset them
        st.session_state.used_writing_themes = [t for t in used if (("integrated:" in t.lower()) != is_integrated)]
        themes_of_current_type = []
    
    # Find available themes
    available_themes = []
    for category in theme_list:
        for theme in category["themes"]:
            prefix = "Integrated: " if is_integrated else "Independent: "
            full_theme = f"{prefix}{category['category']}: {theme}"
            if full_theme not in used:
                available_themes.append(full_theme)
    
    # If somehow we have no available themes, reset
    if not available_themes:
        if is_integrated:
            st.session_state.used_writing_themes = [t for t in used if "integrated:" not in t.lower()]
        else:
            st.session_state.used_writing_themes = [t for t in used if "independent:" not in t.lower()]
        return get_writing_theme()
    
    # Select a theme randomly from available options
    import random
    selected = random.choice(available_themes)
    
    # Add to used themes
    st.session_state.used_writing_themes.append(selected)
    
    return selected

# === MAIN APP ===
def main():
    st.title("TOEFL Reading & Writing Exam Simulator")
    
    # Initialize session state variables
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []
    if "passage" not in st.session_state:
        st.session_state.passage = ""
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "writing_prompt" not in st.session_state:
        st.session_state.writing_prompt = ""
    if "writing_title" not in st.session_state:
        st.session_state.writing_title = ""
    if "essay_text" not in st.session_state:
        st.session_state.essay_text = ""
    if "submitted_essay" not in st.session_state:
        st.session_state.submitted_essay = ""
    if "feedback_result" not in st.session_state:
        st.session_state.feedback_result = ""
    if "used_topics" not in st.session_state:
        st.session_state.used_topics = []
    if "used_writing_themes" not in st.session_state:
        st.session_state.used_writing_themes = []

    # === SIDEBAR ===
    with st.sidebar:
        st.header("Navigation")
        if st.button("Home"):
            st.session_state.page = "home"
        
        if st.button("Reading Practice"):
            st.session_state.page = "reading_setup"
        
        if st.button("Writing Practice"):
            st.session_state.page = "writing_setup"
        
        # Timer display
        if "timer_end" in st.session_state:
            remaining = int(st.session_state.timer_end - time.time())
            if remaining > 0:
                st.header("Time Remaining:")
                st.subheader(format_time(remaining))
            else:
                st.header("Time's up!")
    
    # === HOME PAGE ===
    if st.session_state.page == "home":
        st.markdown("""
        ## Welcome to TOEFL Exam Simulator
        
        This app helps you practice for the TOEFL exam with:
        
        - Reading practice with generated passages and questions
        - Writing practice for both Integrated and Independent tasks
        
        Choose an option from the sidebar to begin.
        """)
    
    # === READING SETUP ===
    elif st.session_state.page == "reading_setup":
        st.header("Reading Practice Setup")
        
        # Question type selection
        st.subheader("Question Types")
        question_types = st.multiselect(
            "Select question types:",
            [
                "Factual Information", 
                "Negative Factual Information",
                "Inference",
                "Rhetorical Purpose",
                "Vocabulary",
                "Reference",
                "Sentence Insertion",
                "Summary",
                "Fill in a Table",
                "Prose Summary"
            ],
            default=["Factual Information", "Inference", "Vocabulary", "Rhetorical Purpose", "Reference"]
        )
        
        # Add a question count slider
        num_questions = st.slider("Number of questions:", min_value=4, max_value=14, value=10, 
                                  help="Real TOEFL reading passages typically have 10-14 questions")
        
        if st.button("Start Practice"):
            # Get a diverse topic based on our rotation system
            selected_topic = get_reading_topic()
            st.info(f"Generating passage about: {selected_topic}")
            
            # Generate a reading passage using Gemini
            passage_prompt = f"""
            Generate a reading passage for TOEFL practice that:
            1. Is about 400-600 words long (longer passages allow for more questions)
            2. Contains academic vocabulary appropriate for TOEFL
            3. Discusses the topic: {selected_topic}
            4. Has clear paragraph structure with 4-6 paragraphs
            5. Includes relevant examples, evidence, and supporting details
            6. Has a clear main idea and supporting points
            7. Uses an academic tone suitable for university-level readers
            8. Contains information that could be tested in different question types
            
            Format the response as plain text only with a title.
            """
            
            # Generate the passage
            passage_response = call_gemini(passage_prompt, temperature=0.8)  # Slightly higher temperature for creativity
            
            # Generate questions for the passage
            selected_types = ", ".join(question_types)
            questions_prompt = f"""
            Generate {num_questions} TOEFL-style questions for this passage:
            {passage_response}
            
            Create questions ONLY for the following selected question types: {selected_types}
            Distribute the questions evenly among these types.
            
            For each question:
            1. Include the question type (must be one from: {selected_types})
            2. Provide 4 multiple choice options that are plausible but with only one correct answer
            3. Specify the correct answer index (0-3)
            4. Make sure questions test real comprehension, not just superficial details
            5. Include vocabulary questions that test context-specific meanings
            6. For inference questions, ensure they require understanding implied information
            
            Format the response exactly as follows (valid JSON array):
            [
                {{
                    "type": "[question_type]",
                    "question": "[question_text]",
                    "options": ["[option1]", "[option2]", "[option3]", "[option4]"],
                    "correct": [correct_index]
                }},
                {{
                    "type": "[question_type]",
                    "question": "[question_text]",
                    "options": ["[option1]", "[option2]", "[option3]", "[option4]"],
                    "correct": [correct_index]
                }},
                ...
            ]
            """
            
            questions_response = call_gemini(questions_prompt, temperature=0.3)  # Lower temperature for accuracy
            
            try:
                # Debug the response
                print("Raw questions response:", questions_response)
                st.write("Generating questions...")
                
                # Clean up the response
                cleaned_response = questions_response.strip()
                
                # Try to find the JSON array
                start_idx = cleaned_response.find('[{')
                if start_idx == -1:
                    # Try alternative formats
                    start_idx = cleaned_response.find('[')
                    if start_idx == -1:
                        st.error("Could not find JSON array in response")
                        st.code(cleaned_response)  # Show the actual response for debugging
                        raise ValueError("Invalid JSON format - could not find array start")
                
                cleaned_response = cleaned_response[start_idx:]
                end_idx = cleaned_response.rfind('}]') + 2
                
                if end_idx <= 1:  # Not found or found at beginning only
                    end_idx = cleaned_response.rfind(']')
                    if end_idx == -1:
                        st.error("Could not find end of JSON array")
                        st.code(cleaned_response)  # Show the actual response for debugging
                        raise ValueError("Invalid JSON format - could not find array end")
                    cleaned_response = cleaned_response[:end_idx+1]
                else:
                    cleaned_response = cleaned_response[:end_idx]
                
                # Try parsing with error handling
                try:
                    questions = json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    st.error(f"JSON parsing error: {e}")
                    st.write("Attempting to fix common JSON formatting issues...")
                    
                    # Try to fix common Gemini JSON formatting issues
                    fixed_json = cleaned_response.replace("'", '"')  # Replace single quotes with double quotes
                    fixed_json = re.sub(r'(\w+):', r'"\1":', fixed_json)  # Convert unquoted keys to quoted keys
                    
                    try:
                        questions = json.loads(fixed_json)
                        st.success("Successfully fixed and parsed JSON")
                    except json.JSONDecodeError:
                        st.error("Could not fix JSON formatting")
                        raise
                
                # Validate the structure
                if not isinstance(questions, list):
                    st.error("Response is not a list of questions")
                    raise ValueError(f"Expected list but got {type(questions)}")
                    
                if len(questions) < 1:
                    st.error("No questions found in response")
                    raise ValueError("Empty questions list")
                    
                # If we have fewer than the requested number of questions, generate a warning but continue
                if len(questions) < num_questions:
                    st.warning(f"Only {len(questions)} questions generated (expected {num_questions})")
                
                # Validate each question's structure
                for i, q in enumerate(questions):
                    required_fields = ['type', 'question', 'options', 'correct']
                    missing_fields = [field for field in required_fields if field not in q]
                    
                    if missing_fields:
                        st.error(f"Question {i+1} is missing fields: {', '.join(missing_fields)}")
                        # Add missing fields with defaults to prevent crashes
                        for field in missing_fields:
                            if field == 'type':
                                q[field] = question_types[0] if question_types else "General"
                            elif field == 'question':
                                q[field] = f"Question {i+1}"
                            elif field == 'options':
                                q[field] = ["Option A", "Option B", "Option C", "Option D"]
                            elif field == 'correct':
                                q[field] = 0
                    
                    # Ensure options is a list with exactly 4 items
                    if not isinstance(q.get('options', []), list):
                        st.error(f"Question {i+1}: 'options' is not a list")
                        q['options'] = ["Option A", "Option B", "Option C", "Option D"]
                    elif len(q['options']) < 4:
                        st.warning(f"Question {i+1} has fewer than 4 options. Adding default options.")
                        while len(q['options']) < 4:
                            q['options'].append(f"Option {chr(65 + len(q['options']))}")
                    
                    # Ensure correct is a valid index
                    if not isinstance(q.get('correct', 0), int) or q['correct'] not in range(4):
                        st.error(f"Question {i+1}: 'correct' is not a valid index")
                        q['correct'] = 0
                
                # Store in session state
                st.session_state.passage = passage_response
                st.session_state.questions = questions
                st.session_state.user_answers = [None] * len(questions)
                
                # Start timer
                start_timer(35 * 60)
                st.session_state.page = "reading"
                st.rerun()
            except Exception as e:
                st.error(f"Error generating questions: {e}")
                st.error("Please try refreshing the page.")
                st.error("If the error persists, please check your internet connection and try again.")
    
    # === READING PAGE ===
    elif st.session_state.page == "reading":
        if is_timer_expired():
            st.error("Time's up! Please submit your answers or return to home.")
        
        st.header("Reading Passage")
        st.markdown(st.session_state.passage)
        
        st.header("Questions")
        
        # Display questions with radio buttons
        for i, question in enumerate(st.session_state.questions):
            st.markdown(f"\n### Question {i+1}: {question['question']} ({question['type']})")
            options = question['options']
            
            # Get current answer or None if not answered
            current_answer = st.session_state.user_answers[i]
            
            # Store selected answer in session state
            selected = st.radio(
                f"Question {i+1}",
                options,
                key=f"q{i}",
                index=None if current_answer is None else options.index(current_answer) if current_answer in options else None,
                label_visibility="collapsed",
                disabled=is_timer_expired()
            )
            if selected and not is_timer_expired():
                st.session_state.user_answers[i] = selected
        
        # Show submit button and handle results
        if st.button("Submit Answers", disabled=is_timer_expired()):
            # Calculate score
            score = 0
            total = len(st.session_state.questions)
            
            # Display each question result
            st.header("Your Results")
            for i, question in enumerate(st.session_state.questions):
                selected = st.session_state.user_answers[i]
                correct_answer = question['options'][question['correct']]
                
                st.markdown(f"\n### {question['type']}: {question['question']}")
                
                if selected == correct_answer:
                    score += 1
                    st.success(f"Your answer: {selected} (Correct)")
                else:
                    st.error(f"Your answer: {selected if selected else 'None'} (Incorrect)")
                    st.success(f"Correct answer: {correct_answer}")
            
            st.success(f"You scored {score}/{total} ({(score/total)*100:.1f}%)")
            
            if st.button("Return to Home"):
                for key in ["passage", "questions", "user_answers", "timer_end"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.page = "home"
                st.rerun()
            
            st.stop()
    
    # === WRITING SETUP ===
    elif st.session_state.page == "writing_setup":
        st.header("Writing Practice Setup")
        
        task_type = st.radio("Choose task type:", 
                             ["Integrated Writing (20 min)", "Independent Writing (30 min)"])
        
        if st.button("Generate Writing Task & Start Timer"):
            with st.spinner("Generating writing task..."):
                if "Integrated" in task_type:
                    prompt = (
                        "Generate a TOEFL Integrated Writing task with exactly these three sections:\n"
                        "1. '# Reading Passage' (250-word excerpt)\n"
                        "2. '# Lecture Summary' (150-200 word summary)\n"
                        "3. '# Writing Prompt'\n"
                        "Make sure to include all three section headings exactly as shown above."
                    )
                    duration = 20 * 60
                    title = "Integrated Writing Task"
                else:
                    prompt = (
                        "Generate a TOEFL Independent Writing task: one essay prompt. "
                        "Use '# Independent Writing Prompt' heading."
                    )
                    duration = 30 * 60
                    title = "Independent Writing Task"
                
                # Call API to get writing prompt
                content = call_gemini(prompt, max_tokens=2000)
                
                # Store in session state
                st.session_state.writing_prompt = content
                st.session_state.writing_title = title
                st.session_state.essay_text = ""
                
                # Start timer
                start_timer(duration)
                st.session_state.page = "writing"
                st.rerun()
    
    # === WRITING PAGE ===
    elif st.session_state.page == "writing":
        if is_timer_expired():
            st.error("Time's up! Please submit your essay or return to home.")
        
        st.header(st.session_state.writing_title)
        st.markdown("### Prompt")
        st.markdown(st.session_state.writing_prompt)
        
        st.header("Your Response")
        
        # Text area for essay
        essay = st.text_area("Type your essay here:", height=300, 
                            value=st.session_state.essay_text,
                            disabled=is_timer_expired())
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Essay", disabled=is_timer_expired()):
                if not essay.strip():
                    st.warning("Please write your essay before submitting.")
                else:
                    st.session_state.essay_text = essay
                    st.session_state.submitted_essay = essay
                    st.session_state.page = "feedback"
                    st.rerun()
        
        with col2:
            if st.button("Cancel"):
                for key in ["writing_prompt", "writing_title", "essay_text", "timer_end"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.page = "home"
                st.rerun()
    
    # === FEEDBACK PAGE ===
    elif st.session_state.page == "feedback":
        st.header("Essay Feedback")
        
        # Generate feedback if not already done
        with st.spinner("Analyzing your essay..."):
            if not st.session_state.feedback_result:
                prompt = f"""
                You are a TOEFL writing instructor. Provide detailed feedback on this essay.
                
                PROMPT:
                {st.session_state.writing_prompt}
                
                STUDENT'S ESSAY:
                {st.session_state.submitted_essay}
                
                Rate these areas on a scale of 0-5:
                - Development
                - Organization
                - Language Use
                - Relevance
                
                Then give an overall score (0-30) and specific recommendations.
                """
                feedback = call_gemini(prompt, max_tokens=2000, temperature=0.2)
                
                # Store result
                st.session_state.feedback_result = feedback
        
        # Display results
        st.subheader("Your Essay")
        st.write(st.session_state.submitted_essay)
        
        st.subheader("Feedback")
        st.markdown(st.session_state.feedback_result)
        
        if st.button("Return to Home"):
            for key in ["submitted_essay", "feedback_result", "writing_prompt", "writing_title", "essay_text", "timer_end"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "home"
            st.rerun()

if __name__ == "__main__":
    main()