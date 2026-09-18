import streamlit as st
from agents.coordinator import classify_query, ask_coordinator


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f6f8fb;
}

/* Remove default top padding */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}


/* ============================================================
   TOP NAVIGATION
   ============================================================ */

.topbar {
    background: #ffffff;
    border: 1px solid #e5e9f0;
    border-radius: 14px;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: #172554;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
}

.brand-title {
    font-size: 17px;
    font-weight: 700;
    color: #172033;
}

.brand-subtitle {
    font-size: 11px;
    color: #7b8494;
    margin-top: 2px;
}

.status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #667085;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    background: linear-gradient(135deg, #172554 0%, #1e3a8a 100%);
    border-radius: 18px;
    padding: 38px 42px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(30, 58, 138, 0.16);
}

.hero-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    opacity: 0.72;
    margin-bottom: 10px;
}

.hero h1 {
    font-size: 32px;
    margin: 0;
    font-weight: 700;
    letter-spacing: -0.7px;
}

.hero p {
    font-size: 14px;
    margin-top: 10px;
    margin-bottom: 0;
    opacity: 0.82;
    max-width: 700px;
    line-height: 1.6;
}


/* ============================================================
   SECTION
   ============================================================ */

.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #172033;
    margin: 8px 0 12px 2px;
}


/* ============================================================
   SERVICE CARDS
   ============================================================ */

.service-card {
    background: white;
    border: 1px solid #e5e9f0;
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.035);
}

.service-icon {
    font-size: 20px;
    margin-bottom: 12px;
}

.service-title {
    font-size: 14px;
    font-weight: 650;
    color: #172033;
    margin-bottom: 5px;
}

.service-text {
    font-size: 12px;
    line-height: 1.5;
    color: #727b8c;
}


/* ============================================================
   CHAT AREA
   ============================================================ */

.chat-panel {
    background: white;
    border: 1px solid #e5e9f0;
    border-radius: 16px;
    padding: 24px;
    margin-top: 24px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.035);
}

.chat-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.chat-title {
    font-size: 17px;
    font-weight: 700;
    color: #172033;
}

.chat-description {
    color: #7b8494;
    font-size: 12px;
    margin-bottom: 18px;
}


/* ============================================================
   EXAMPLES
   ============================================================ */

.example-box {
    background: #f8fafc;
    border: 1px solid #e8edf3;
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 12px;
    color: #475467;
    margin-bottom: 8px;
}


/* ============================================================
   RESPONSE
   ============================================================ */

.response-card {
    background: #ffffff;
    border: 1px solid #dfe5ec;
    border-left: 4px solid #1e3a8a;
    border-radius: 12px;
    padding: 20px 22px;
    margin-top: 20px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
}

.response-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #7b8494;
    font-weight: 600;
    margin-bottom: 9px;
}

.response-text {
    color: #263247;
    font-size: 14px;
    line-height: 1.7;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    text-align: center;
    color: #98a2b3;
    font-size: 11px;
    margin-top: 35px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# TOP BAR
# ============================================================

st.markdown("""
<div class="topbar">

    <div class="brand">
        <div class="brand-icon">◈</div>

        <div>
            <div class="brand-title">AI HR Assistant</div>
            <div class="brand-subtitle">Enterprise Employee Support</div>
        </div>
    </div>

    <div class="status">
        <span class="status-dot"></span>
        HR Services Online
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

    <div class="hero-label">Employee Services</div>

    <h1>How can we help you today?</h1>

    <p>
        Get quick answers about company policies, leave, attendance,
        work-from-home guidelines, employee information and other
        HR-related services.
    </p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SERVICES
# ============================================================

st.markdown(
    '<div class="section-title">HR SERVICES</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="service-card">
        <div class="service-icon">▣</div>
        <div class="service-title">Company Policies</div>
        <div class="service-text">
            Find information about attendance, working hours,
            benefits and workplace policies.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="service-card">
        <div class="service-icon">◷</div>
        <div class="service-title">Leave & Attendance</div>
        <div class="service-text">
            Get information about leave types, leave balance,
            approvals and related policies.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="service-card">
        <div class="service-icon">◎</div>
        <div class="service-title">Employee Services</div>
        <div class="service-text">
            Access supported employee information and
            general HR assistance.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CHAT PANEL
# ============================================================

st.markdown("""
<div class="chat-panel">

    <div class="chat-title">Ask HR</div>

    <div class="chat-description">
        Enter your HR-related question below.
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about HR policies, leave, attendance..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    question = question.strip()

    if not question:
        st.warning("Please enter a question.")
        st.stop()

    # Save employee question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user question
    with st.chat_message("user"):
        st.write(question)

    # Process request
    with st.chat_message("assistant"):

        with st.spinner("Processing your request..."):

            try:

                # First classify the request
                category = classify_query(question)

                category = category.strip().upper()

                # ------------------------------------------------
                # Reject irrelevant questions BEFORE calling agents
                # ------------------------------------------------

                if "IRRELEVANT" in category:

                    response = (
                        "I’m here to assist with HR-related matters such as "
                        "company policies, leave, attendance, work-from-home "
                        "guidelines, and employee information."
                    )

                # ------------------------------------------------
                # Valid HR request
                # ------------------------------------------------

                elif category in ["POLICY", "LEAVE", "GENERAL"]:

                    response = ask_coordinator(question)

                else:

                    response = (
                        "I’m unable to determine whether this request "
                        "falls within the available HR services. "
                        "Please rephrase your question."
                    )

            except Exception:

                response = (
                    "I’m sorry, but the HR service is temporarily "
                    "unavailable. Please try again in a moment."
                )

        # Clean response
        st.markdown(
            f"""
            <div class="response-card">

                <div class="response-label">
                    HR Assistant
                </div>

                <div class="response-text">
                    {response}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# ============================================================
# PREVIOUS CONVERSATION
# ============================================================

if len(st.session_state.messages) > 1:

    st.markdown(
        '<div class="section-title" style="margin-top:30px;">RECENT CONVERSATION</div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.messages[:-1]:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="example-box">
                    <strong>You:</strong> {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="example-box">
                    <strong>HR Assistant:</strong> {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    AI HR Assistant &nbsp;•&nbsp; Enterprise HR Support
    <br>
    For official employment decisions, please contact your HR department.
</div>
""", unsafe_allow_html=True)