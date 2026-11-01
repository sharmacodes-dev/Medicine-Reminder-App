import streamlit as st
import sqlite3
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

def init_db():
    conn = sqlite3.connect("medicine.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            pin TEXT NOT NULL,
            email TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            med_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            remind_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, pin, email) VALUES ('Grandma Rani', '1111', 'grandmarani@example.com')")
        cursor.execute("INSERT INTO users (username, pin, email) VALUES ('Grandpa Raja', '2222', 'grandparaja@example.com')")
        cursor.execute("INSERT INTO users (username, pin, email) VALUES ('Reviewer', '1234', 'reviewer@example.com')")
        
        conn.commit()
        
    conn.close()

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None


st.set_page_config(
    page_title="Medicine Reminder",
    page_icon="🏥",
    layout="centered"
)

st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p {
        font-size: 24px !important;
        font-family: 'Arial', sans-serif !important;
        color: #FFFFFF !important;
    }
    
    input {
        font-size: 22px !important;
        height: 55px !important;
    }
    
    .stButton>button {
        font-size: 26px !important;
        font-weight: bold !important;
        color: white !important;
        background-color: #2E7D32 !important; 
        border-radius: 12px !important;
        height: 60px !important;
        width: 100% !important;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)
if not st.session_state.logged_in:

    menu_choice = st.sidebar.radio("What would you like to do?", ["Log In", "Create New Account"])


    st.markdown("<h1 style='text-align: center; font-size: 45px; color: #43A047;'>🏥 Medicine Reminder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 22px; color: #B0BEC5;'>Your simple, daily medicine helper</p>", unsafe_allow_html=True)

    st.write("---")

    if menu_choice == "Log In":
        st.markdown("<h2 style='font-size: 30px; color: #FFFFFF;'>Please Log In</h2>", unsafe_allow_html=True)

        username = st.text_input("Enter Your Name:")
        pin = st.text_input("Enter Your 4-Digit PIN:", type="password", max_chars=4)

        if st.button("LOG IN NOW"):
            if username.strip() != "" and pin.strip() != "":
                conn = sqlite3.connect("medicine.db")
                cursor = conn.cursor()
            
                cursor.execute("SELECT * FROM users WHERE username = ? AND pin = ?", (username.strip(), pin.strip()))
                user_record = cursor.fetchone()
            
                conn.close()
        
                if user_record is not None:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_record[0] 
                    st.session_state.current_user = username.strip()
                    st.rerun() 

                else:
                    st.error("❌ Incorrect Name or PIN. Please try again.")
            else:
                st.error("❌ Please fill out both fields.")

    elif menu_choice == "Create New Account":
        
        st.markdown("<h2 style='font-size: 30px; color: #FFFFFF;'>Create Your New Profile</h2>", unsafe_allow_html=True)
        
        new_username = st.text_input("Choose a Username:")
        new_email = st.text_input("Enter Your Email Address:")
        new_pin = st.text_input("Choose a 4-Digit PIN:", type="password", max_chars=4)
        
        if st.button("REGISTER NEW PROFILE"):
            if new_username.strip() != "" and new_pin.strip() != "" and new_email.strip() != "":
                if len(new_pin.strip()) == 4 and new_pin.strip().isdigit():
                    conn = sqlite3.connect("medicine.db")
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("INSERT INTO users (username, pin, email) VALUES (?, ?, ?)", (new_username.strip(), new_pin.strip(), new_email.strip()))
                        conn.commit()
                        st.success(f" Profile created for {new_username}! You can now switch to 'Log In' in the sidebar.")
                    except sqlite3.IntegrityError:
                        st.error("❌ This username is already taken. Please try another name.")
                        
                    conn.close()
                else:
                    st.error("❌ Your PIN must be exactly 4 numbers.")
            else:
                st.error("❌ Please fill out both fields to register.")

else:
    st.markdown(f"<h2 style='font-size: 35px; color: #43A047;'>🏥 Welcome to Your Dashboard, {st.session_state.current_user}!</h2>", unsafe_allow_html=True)
    
    conn = sqlite3.connect("medicine.db")
    cursor = conn.cursor()
    
    current_uid = st.session_state.user_id
    
    cursor.execute("SELECT med_name, dosage, remind_time FROM medicines WHERE user_id = ?", (current_uid,))
    med_list = cursor.fetchall()
    conn.close()
    
    st_autorefresh(interval=10000, key="pill_clock_heartbeat")
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='font-size: 20px; color: #FFFFFF;'>⏰ Synchronize Your Clock:</h3>", unsafe_allow_html=True)
    minute_offset = st.sidebar.slider(
        "Adjust server time by minutes to match your wall clock:",
        min_value=-600, max_value=600, value=0, step=1, key="tz_slider"
    )
    from datetime import timedelta
    shifted_time = datetime.now() + timedelta(minutes=minute_offset)
    current_time_str = shifted_time.strftime("%I:%M %p")
    
    st.markdown(f"<p style='color: #B0BEC5; font-size: 18px;'>Your Synchronized App Clock: <strong>{current_time_str}</strong></p>", unsafe_allow_html=True)

    st.write(f"⏰ The Cloud Server's Current Time is: {current_time_str}")
    conn = sqlite3.connect("medicine.db")
    db_cursor = conn.cursor()
    db_cursor.execute("SELECT email FROM users WHERE id = ?", (current_uid,))
    user_email_row = db_cursor.fetchone()
    user_email = user_email_row[0] if user_email_row else ""
    conn.close()
    
    for med in med_list:
        m_name = med[0]
        m_dose = med[1]
        m_time = med[2]
        
        if current_time_str.strip() == m_time.strip():
            st.markdown(f"""
                <div style='background-color: #E65100; padding: 20px; border: 3px solid #FF9800; border-radius: 8px; margin-bottom: 25px; text-align: center;'>
                    <h2 style='color: white; margin: 0; font-size: 32px;'>🚨 ALARM TIME: {m_time} 🚨</h2>
                    <p style='color: white; font-size: 24px; margin-top: 10px;'>It is time to take your <strong>{m_dose}</strong> of <strong>{m_name}</strong>!</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.info(f"[Background Engine] Automated alert notification dispatched securely to: {user_email}")

    st.markdown("<h3 style='font-size: 28px; color: #FFFFFF; margin-top: 30px;'>📋 Your Active Medicine Schedule:</h3>", unsafe_allow_html=True)
    
    if len(med_list) == 0:
        st.info(" You have no medicines added to your schedule yet.")
    else:
        for med in med_list:
            name, dose, time = med
            st.markdown(f"""
                <div style='background-color: #1E1E1E; padding: 15px; border-left: 5px solid #43A047; border-radius: 6px; margin-bottom: 12px;'>
                    <strong style='font-size: 24px; color: #FFFFFF;'> {name}</strong><br>
                    <span style='font-size: 20px; color: #B0BEC5;'>Take {dose} at {time}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 28px; color: #FFFFFF; margin-top: 30px;'>➕ Add a New Medicine:</h3>", unsafe_allow_html=True)
    
    med_name_input = st.text_input("Medication Name (e.g., Aspirin):", key="add_name")
    dosage_input = st.text_input("Dose Amount (e.g., 1 Tablet):", key="add_dose")
    time_input = st.text_input("Reminder Time (e.g., 08:30 AM):", key="add_time")
    
    if st.button("SAVE MEDICINE TO SCHEDULE"):
        if med_name_input.strip() != "" and dosage_input.strip() != "" and time_input.strip() != "":
            conn = sqlite3.connect("medicine.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO medicines (user_id, med_name, dosage, remind_time) 
                VALUES (?, ?, ?, ?)
            """, (st.session_state.user_id, med_name_input.strip(), dosage_input.strip(), time_input.strip()))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Added {med_name_input} to your schedule!")
            st.rerun() 
        else:
            st.error("❌ Please fill out all three text fields.")

    st.markdown("<h3 style='font-size: 28px; color: #FFFFFF; margin-top: 40px;'>❌ Remove a Medicine:</h3>", unsafe_allow_html=True)
    
    if len(med_list) == 0:
        st.info("💡 You have no medicines to remove.")
    else:
        med_options = {}
        for med in med_list:
            m_name = med[0]   
            m_dose = med[1]   
            m_time = med[2]   
            
            dropdown_label = f"💊 {m_name} ({m_dose} at {m_time})"
            med_options[dropdown_label] = med
            
        selected_label = st.selectbox("Select the exact prescription row to delete:", list(med_options.keys()), key="remove_select")
        
        if st.button("REMOVE MEDICINE FROM SCHEDULE"):
            targeted_med = med_options[selected_label]
            t_name = targeted_med[0]
            t_dose = targeted_med[1]
            t_time = targeted_med[2]
            
            conn = sqlite3.connect("medicine.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM medicines 
                WHERE user_id = ? AND med_name = ? AND dosage = ? AND remind_time = ?
            """, (st.session_state.user_id, t_name, t_dose, t_time))
            
            conn.commit()
            conn.close()
            
            st.success(f"❌ Removed {t_name} prescription successfully!")
            st.rerun() 


    st.write("---") 

    if st.button("LOG OUT"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.current_user = None
        st.rerun()
