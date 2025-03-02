import streamlit as st
import sqlite3
import bcrypt
import cohere

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password):
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    user = c.fetchone()
    if user and check_password(password, user[0]):
        return True
    return False

# Rule-based recommendation system
def rule_based_recommendations(interest, level):
    pathways = {
        "Machine Learning": {
            "Beginner": ["Python Basics", "Statistics", "Scikit-learn", "Intro to ML"],
            "Intermediate": ["TensorFlow Basics", "Neural Networks", "Feature Engineering", "Hyperparameter Tuning"],
            "Advanced": ["Deep Learning", "Reinforcement Learning", "MLOps", "Transformer Models"]
        },
        "Data Science": {
            "Beginner": ["Python Basics", "Data Analysis with Pandas", "SQL Basics", "Data Visualization"],
            "Intermediate": ["Machine Learning", "Time Series Analysis", "Big Data", "Deep Learning"],
            "Advanced": ["AI Ethics", "Data Engineering", "NLP", "Computer Vision"]
        },
        "Artificial Intelligence": {
            "Beginner": ["Introduction to AI", "Python for AI", "Search Algorithms", "Basic AI Ethics"],
            "Intermediate": ["Neural Networks", "Computer Vision", "NLP Basics", "Game AI"],
            "Advanced": ["Deep Reinforcement Learning", "Generative AI", "Advanced NLP", "AI Security"]
        },
        "Robotics": {
            "Beginner": ["Introduction to Robotics", "Arduino Basics", "Basic Electronics", "Simple Robot Projects"],
            "Intermediate": ["ROS (Robot Operating System)", "Sensors and Actuators", "Path Planning", "Robot Perception"],
            "Advanced": ["Humanoid Robotics", "Autonomous Navigation", "Robot Swarms", "AI in Robotics"]
        },
        "Cyber Security": {
            "Beginner": ["Cybersecurity Fundamentals", "Networking Basics", "Cryptography Basics", "Ethical Hacking Intro"],
            "Intermediate": ["Penetration Testing", "Malware Analysis", "Network Security", "Cloud Security"],
            "Advanced": ["Cyber Threat Intelligence", "Reverse Engineering", "Incident Response", "Red Teaming"]
        },
        "Web Development": {
            "Beginner": ["HTML & CSS", "JavaScript Basics", "Responsive Design", "Intro to GitHub"],
            "Intermediate": ["Frontend Frameworks (React, Vue)", "Backend Development (Node.js, Django)", "APIs", "Databases"],
            "Advanced": ["Progressive Web Apps", "Performance Optimization", "Security Best Practices", "Scalability"]
        },
        "Big Data Analytics": {
            "Beginner": ["Introduction to Big Data", "Hadoop Basics", "SQL & NoSQL", "Data Warehousing"],
            "Intermediate": ["Apache Spark", "Data Lakes", "ETL Pipelines", "Data Governance"],
            "Advanced": ["Real-time Analytics", "Predictive Analytics", "AI & Big Data", "Scalability Techniques"]
        },
        "Game Development": {
            "Beginner": ["Game Design Basics", "Unity Basics", "C# for Game Dev", "2D Game Development"],
            "Intermediate": ["3D Game Development", "Physics Engines", "Multiplayer Game Dev", "AI in Games"],
            "Advanced": ["Game Optimization", "VR & AR Development", "Advanced AI in Games", "Game Monetization"]
        },
        "Cloud Computing": {
            "Beginner": ["Cloud Basics", "AWS/GCP/Azure Intro", "Virtualization", "Storage & Databases"],
            "Intermediate": ["Cloud Security", "Kubernetes & Docker", "Serverless Computing", "Cost Optimization"],
            "Advanced": ["Cloud Architecture", "DevOps in Cloud", "Multi-cloud Strategies", "AI in Cloud"]
        }
    }
    return pathways.get(interest, {}).get(level, [])[:15]

# AI-based recommendations using Cohere
def ai_recommendations(api_key, interest, level):
    prompt = f"Suggest a comprehensive learning pathway for {interest} at {level} level with 15 topics."

    try:
        cohere_client = cohere.Client(api_key)
        response = cohere_client.generate(
            model="command",
            prompt=prompt,
            max_tokens=250
        )
        ai_results = response.generations[0].text.strip().split("\n")

        formatted_results = [f"**{rec.strip()}**" for rec in ai_results if rec.strip()]
        return formatted_results[:15]
    except Exception as e:
        st.error(f"❌ AI recommendation failed: {e}")
        return []

# Streamlit UI
def main():
    st.set_page_config(page_title="SkillPilot", page_icon="🚀", layout="wide")
    
    st.title("🚀 SkillPilot: Personalized Learning Journey Recommender")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("🎉 Registered successfully! You can now login.")
            else:
                st.error("🚫 Username already exists. Try another.")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("🚫 Invalid username or password")

    if "logged_in" in st.session_state:
        st.subheader("🎯 Choose your field of interest:")
        
        available_interests = [
            "Machine Learning", "Data Science", "Artificial Intelligence", "Robotics",
            "Cyber Security", "Web Development", "Cloud Computing", "Big Data Analytics",
            "Game Development", "Information Systems", "Graphic Design", 
            "User Interface Design", "Digital Marketing", "IoT"
        ]
        interest = st.selectbox("Select Interest", available_interests)
        level = st.selectbox("📊 Select your experience level:", ["Beginner", "Intermediate", "Advanced"])

        st.subheader("📚 Rule-Based Learning Pathway:")
        rule_recommendations = rule_based_recommendations(interest, level)
        for rec in rule_recommendations:
            st.write(f"**{rec}**")

        use_ai = st.checkbox("🔮 Not satisfied? Get AI-based recommendations")
        if use_ai:
            api_key = st.text_input("🔑 Enter AI API Key", type="password")
            if st.button("Get AI Recommendations") and api_key:
                ai_results = ai_recommendations(api_key, interest, level)
                if ai_results:
                    st.subheader("🤖 AI-Based Learning Pathway:")
                    for rec in ai_results:
                        st.write(rec)

if __name__ == "__main__":
    main()
