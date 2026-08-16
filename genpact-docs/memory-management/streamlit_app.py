import uuid 
import streamlit as st

from app.memory.memory_orchestrator import MemoryOrchestrator

memory_orchestrator = MemoryOrchestrator()

st.set_page_config( page_title="Agentic AI Memory Demo", layout="wide" )

st.title("Agentic AI Memory Management Demo")

st.markdown(""" This demo shows:

Short-Term Memory (Redis)
Long-Term Memory (Vector DB)
Hybrid Agent Memory Architecture """)

if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state: st.session_state.chat_history = []

user_id = st.sidebar.text_input( "User ID", value="user_001" )

st.sidebar.markdown("---")

st.sidebar.subheader("Memory Features")

st.sidebar.markdown("""

Short-Term Memory
Session-based
Redis-backed
Stores recent interactions
Auto-expiry supported
Long-Term Memory
Vector database
Semantic retrieval
Cross-session persistence
Personalized memory """)

user_input = st.chat_input("Ask something...")

if user_input:
    result = memory_orchestrator.process_query(
        session_id=st.session_state.session_id,
        user_id=user_id,
        user_query=user_input
    )

    st.session_state.chat_history.append({
        "user": user_input,
        "assistant": result["response"],
        "short_memory": result[
            "short_term_context_used"
        ],
        "long_memory": result[
            "long_term_context_used"
        ]
    })
    
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])

    with st.chat_message("assistant"):

        st.write(chat["assistant"])

        col1, col2 = st.columns(2)

        with col1:
            if chat["short_memory"]:
                st.success(
                    "Short-Term Memory Used"
                )
            else:
                st.info(
                    "No Short-Term Memory"
                )

        with col2:
            if chat["long_memory"]:
                st.success(
                    "Long-Term Memory Used"
                )
            else:
                st.info(
                    "No Long-Term Memory"
                )