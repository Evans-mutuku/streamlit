import streamlit as st
import openai
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        margin-left: 20%;
    }
    .bot-message {
        background-color: white;
        color: #333;
        margin-right: 20%;
        border: 1px solid #ddd;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .user-avatar {
        background-color: #0056b3;
    }
    .bot-avatar {
        background-color: #28a745;
    }
    .timestamp {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI assistant. How can I help you today?", "timestamp": datetime.now()}
        ]
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "api_key_verified" not in st.session_state:
        st.session_state.api_key_verified = False

def verify_api_key(api_key):
    """Verify if the API key is valid"""
    try:
        openai.api_key = api_key
        # Make a simple API call to verify the key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        return False

def get_ai_response(messages, api_key):
    """Get response from OpenAI API"""
    try:
        openai.api_key = api_key
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=openai_messages,
            max_tokens=500,
            temperature=0.7,
            stream=False
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def display_message(message, is_user=False):
    """Display a chat message with styling"""
    role = "user" if is_user else "assistant"
    avatar = "👤" if is_user else "🤖"
    css_class = "user-message" if is_user else "bot-message"
    avatar_class = "user-avatar" if is_user else "bot-avatar"
    
    timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M")
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <div class="avatar {avatar_class}">{avatar}</div>
        <div>
            <div>{message["content"]}</div>
            <div class="timestamp">{timestamp}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.title("🤖 AI Chatbot")
        st.markdown("---")
        
        # API Key input
        st.subheader("🔑 OpenAI API Key")
        api_key_input = st.text_input(
            "Enter your OpenAI API key:",
            type="password",
            value=st.session_state.api_key,
            placeholder="sk-..."
        )
        
        if st.button("Verify API Key"):
            if api_key_input:
                with st.spinner("Verifying API key..."):
                    if verify_api_key(api_key_input):
                        st.session_state.api_key = api_key_input
                        st.session_state.api_key_verified = True
                        st.success("✅ API key verified!")
                    else:
                        st.error("❌ Invalid API key. Please check and try again.")
            else:
                st.warning("Please enter an API key.")
        
        # Display API key status
        if st.session_state.api_key_verified:
            st.success("🟢 API Key: Active")
        else:
            st.error("🔴 API Key: Not verified")
        
        st.markdown("---")
        
        # Chat settings
        st.subheader("⚙️ Settings")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your AI assistant. How can I help you today?", "timestamp": datetime.now()}
            ]
            st.rerun()
        
        # Model info
        st.info("**Model:** GPT-3.5 Turbo\n**Provider:** OpenAI")
        
        # Instructions
        st.markdown("---")
        st.subheader("📝 Instructions")
        st.markdown("""
        1. Enter your OpenAI API key above
        2. Click "Verify API Key" to validate
        3. Start chatting in the main area
        4. Use "Clear Chat" to start fresh
        """)
    
    # Main chat area
    st.title("💬 AI Chatbot")
    
    # Check if API key is verified
    if not st.session_state.api_key_verified:
        st.warning("⚠️ Please enter and verify your OpenAI API key in the sidebar to start chatting.")
        st.info("You can get your API key from: https://platform.openai.com/api-keys")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            display_message(message, is_user=True)
        else:
            display_message(message, is_user=False)
    
    # Chat input - this is the key fix
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Display user message immediately
        display_message(user_message, is_user=True)
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            ai_response = get_ai_response(st.session_state.messages, st.session_state.api_key)
        
        # Add AI response
        ai_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(ai_message)
        
        # Display AI response immediately
        display_message(ai_message, is_user=False)
        
        # Rerun to clear the input and show updated chat
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            Built with ❤️ using Streamlit and OpenAI API
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
