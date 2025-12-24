
import streamlit as st
import random

# --- Configuration ---
MASTERY_SCORE = 10
TARGET_NAME = "Ashley"
MAX_QUESTIONS_PER_GAME = 20

def initialize_game():
    """Initialize the session state variables."""
    if 'scores' not in st.session_state:
        # Tracks mastery for each number pair over time (long-term memory)
        st.session_state.scores = {(i, j): 0 for i in range(1, 10) for j in range(1, 10)}
    
    # Session specific variables (reset every time the page is reloaded or game restarts)
    if 'game_active' not in st.session_state:
        st.session_state.game_active = True
        st.session_state.questions_played = 0
        st.session_state.session_score = 0  # Total correct answers this session
        st.session_state.current_question = None
        st.session_state.feedback = ""
        st.session_state.feedback_type = "info"

def reset_session():
    """Resets only the current game session, keeping mastery scores."""
    st.session_state.game_active = True
    st.session_state.questions_played = 0
    st.session_state.session_score = 0
    st.session_state.current_question = None
    st.session_state.feedback = ""
    st.session_state.feedback_type = "info"

def get_valid_pairs():
    """Return pairs that haven't reached mastery score (10)."""
    return [pair for pair, score in st.session_state.scores.items() if score < MASTERY_SCORE]

def generate_visuals(a, b):
    """Creates a visual grid string of icons."""
    # We use a simple unicode icon. 
    icon = "🍎" 
    visual_rows = []
    for _ in range(a):
        visual_rows.append(icon * b)
    return "\n".join(visual_rows)

def generate_question():
    """Generate a question with visuals."""
    valid_pairs = get_valid_pairs()
    
    if not valid_pairs:
        return None  # All mastered!
    
    a, b = random.choice(valid_pairs)
    correct_answer = a * b
    
    # Generate distractors
    wrong_answers = set()
    while len(wrong_answers) < 3:
        distractor = random.randint(1, 81)
        if distractor != correct_answer:
            wrong_answers.add(distractor)
            
    options = list(wrong_answers)
    options.append(correct_answer)
    random.shuffle(options)
    
    return {
        "a": a,
        "b": b,
        "correct": correct_answer,
        "options": options,
        "visual": generate_visuals(a, b)
    }

def check_answer(selected_option):
    q = st.session_state.current_question
    pair = (q['a'], q['b'])
    
    st.session_state.questions_played += 1
    
    if selected_option == q['correct']:
        # Correct
        st.session_state.scores[pair] += 1
        st.session_state.session_score += 1
        st.session_state.feedback = f"Good job {TARGET_NAME}! ({q['a']} × {q['b']} = {q['correct']})"
        st.session_state.feedback_type = "success"
    else:
        # Incorrect
        st.session_state.scores[pair] -= 1
        st.session_state.feedback = f"Practice more, {TARGET_NAME}. The answer was {q['correct']}."
        st.session_state.feedback_type = "error"
    
    # Check if game over
    if st.session_state.questions_played >= MAX_QUESTIONS_PER_GAME:
        st.session_state.game_active = False
    
    st.session_state.current_question = None

# --- Main App Layout ---
st.set_page_config(page_title="Math with Apples", page_icon="🍎")

st.title("🍎 Apple Math for Ashley")
initialize_game()

# 1. Game Over Screen
if not st.session_state.game_active:
    st.balloons()
    st.header("🎉 Game Over!")
    
    score = st.session_state.session_score
    total = MAX_QUESTIONS_PER_GAME
    
    st.subheader(f"You got {score} out of {total} right!")
    
    if score == total:
        st.write("🌟 Perfect Score! You are a Math Wizard! 🌟")
    elif score >= 15:
        st.write("✨ Amazing work! You are getting very good at this!")
    else:
        st.write("Keep practicing, you will get there!")

    if st.button("Play Again"):
        reset_session()
        st.rerun()

# 2. Active Game Screen
else:
    # Progress Bar for the 20 questions
    progress = st.session_state.questions_played / MAX_QUESTIONS_PER_GAME
    st.progress(progress)
    st.caption(f"Question {st.session_state.questions_played + 1} of {MAX_QUESTIONS_PER_GAME}")

    # Display Feedback
    if st.session_state.feedback:
        if st.session_state.feedback_type == "success":
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)

    # Generate Question
    if st.session_state.current_question is None:
        st.session_state.current_question = generate_question()

    # Handle case where everything is mastered
    if st.session_state.current_question is None:
        st.success("You have mastered EVERY single number! Incredible!")
        st.stop()

    q = st.session_state.current_question

    # --- Display The Question & Visuals ---
    col_text, col_visual = st.columns([1, 1])
    
    with col_text:
        st.markdown(f"## {q['a']} × {q['b']} = ?")
        st.write("Count the apples if you need help!")
    
    with col_visual:
        # Display the grid of apples centered
        st.text(q['visual'])

    # --- Answer Buttons ---
    st.markdown("---")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    cols = [c1, c2, c3, c4]

    for i, option in enumerate(q['options']):
        with cols[i]:
            st.button(
                f"{option}", 
                key=f"opt_{i}", 
                use_container_width=True, 
                on_click=check_answer, 
                args=(option,)
            )

# Optional: Reset Long-term Memory (for dad to reset mastery)
with st.sidebar:
    st.write(f"Session Score: {st.session_state.session_score}")
    if st.button("Reset Ashley's Mastery Level"):
        st.session_state.scores = {(i, j): 0 for i in range(1, 10) for j in range(1, 10)}
        st.rerun()
        
