import streamlit as st
import random

# --- Configuration ---
MASTERY_SCORE = 10
TARGET_NAME = "Ashley"

def initialize_game():
    """Initialize the session state variables if they don't exist."""
    # Create a dictionary to track the score for every pair (1x1 to 9x9)
    # Key is a tuple (a, b), Value is the current score
    if 'scores' not in st.session_state:
        st.session_state.scores = {(i, j): 0 for i in range(1, 10) for j in range(1, 10)}
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
        
    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""
        
    if 'feedback_type' not in st.session_state:
        st.session_state.feedback_type = "info"  # can be 'success' or 'error'

def get_valid_pairs():
    """Return a list of number pairs that haven't reached the mastery score yet."""
    return [pair for pair, score in st.session_state.scores.items() if score < MASTERY_SCORE]

def generate_question():
    """Generate a new question from the list of valid pairs."""
    valid_pairs = get_valid_pairs()
    
    if not valid_pairs:
        return None  # Game Completed
    
    # Pick a random pair
    a, b = random.choice(valid_pairs)
    correct_answer = a * b
    
    # Generate 3 unique incorrect answers (distractors)
    wrong_answers = set()
    while len(wrong_answers) < 3:
        # Create distractors that are somewhat plausible (within the 1-81 range)
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
        "options": options
    }

def check_answer(selected_option):
    """Callback function to handle the user's answer."""
    q = st.session_state.current_question
    pair = (q['a'], q['b'])
    
    if selected_option == q['correct']:
        # Correct Answer
        st.session_state.scores[pair] += 1
        st.session_state.feedback = f"Good job {TARGET_NAME}! ({q['a']} × {q['b']} = {q['correct']})"
        st.session_state.feedback_type = "success"
    else:
        # Wrong Answer
        st.session_state.scores[pair] -= 1
        # Prevent score from going below 0 (optional, remove max(0, ...) if you want negative scores)
        # Based on your prompt, simple minus 1 is requested, so we allow negatives:
        # st.session_state.scores[pair] = st.session_state.scores[pair]
        
        st.session_state.feedback = f"Practice more, {TARGET_NAME}. The correct answer for {q['a']} × {q['b']} was {q['correct']}."
        st.session_state.feedback_type = "error"
    
    # Force generation of a new question next rerun
    st.session_state.current_question = None

# --- Main App Layout ---
st.set_page_config(page_title="Ashley's Math Game", page_icon="✖️")

st.title("✖️ 九九乘法表 Challenge")
initialize_game()

# 1. Check Progress
valid_pairs = get_valid_pairs()
total_pairs = 81
mastered_pairs = total_pairs - len(valid_pairs)
progress = mastered_pairs / total_pairs

st.progress(progress)
st.caption(f"Progress: {mastered_pairs} pairs mastered out of {total_pairs}. Keep going, {TARGET_NAME}!")

# 2. Display Feedback from previous turn
if st.session_state.feedback:
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)

# 3. Game Loop
if not valid_pairs:
    st.balloons()
    st.success(f"CONGRATULATIONS {TARGET_NAME}! You have mastered the entire Multiplication Table!")
    if st.button("Reset Game"):
        for k in st.session_state.scores:
            st.session_state.scores[k] = 0
        st.rerun()
else:
    # Generate a new question if one isn't currently active
    if st.session_state.current_question is None:
        st.session_state.current_question = generate_question()
    
    q = st.session_state.current_question
    
    # Display the Question
    st.markdown(f"### What is **{q['a']} × {q['b']}** ?")
    
    # Display Score for this specific pair
    current_pair_score = st.session_state.scores[(q['a'], q['b'])]
    st.markdown(f"*Current Score for this question: {current_pair_score}/{MASTERY_SCORE}*")

    # Display Buttons in a grid for better layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    cols = [col1, col2, col3, col4]
    
    for i, option in enumerate(q['options']):
        with cols[i]:
            # The on_click parameter ensures the logic runs before the page reloads
            st.button(
                str(option), 
                key=f"btn_{i}", 
                use_container_width=True, 
                on_click=check_answer, 
                args=(option,)
            )

# --- Optional: Sidebar for Debugging/Monitoring ---
with st.sidebar:
    st.header("Mastery Tracker")
    st.write("Pairs with Score >= 10 are hidden.")
    if st.checkbox("Show all scores"):
        st.write(st.session_state.scores)
      
