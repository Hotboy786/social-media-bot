import sys
import types

# --- Python 3.12+ Compatibility Fix for distutils ---
try:
    import distutils
except ImportError:
    distutils = types.ModuleType('distutils')
    sys.modules['distutils'] = distutils

try:
    from distutils.version import LooseVersion
except (ImportError, ModuleNotFoundError):
    class LooseVersion:
        def __init__(self, vstring):
            self.vstring = vstring
        def __str__(self):
            return self.vstring
        def _parse(self, vstring):
            return tuple(int(x) for x in vstring.split('.') if x.isdigit())
        def __lt__(self, other): return self._parse(self.vstring) < self._parse(other.vstring)
        def __le__(self, other): return self._parse(self.vstring) <= self._parse(other.vstring)
        def __eq__(self, other): return self._parse(self.vstring) == self._parse(other.vstring)
        def __ge__(self, other): return self._parse(self.vstring) >= self._parse(other.vstring)
        def __gt__(self, other): return self._parse(self.vstring) > self._parse(other.vstring)
        def __ne__(self, other): return self._parse(self.vstring) != self._parse(other.vstring)
    
    dv_mod = types.ModuleType('distutils.version')
    dv_mod.LooseVersion = LooseVersion
    sys.modules['distutils.version'] = dv_mod
# ----------------------------------------------------

import os
import re
import random
import time
import shutil
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import urllib.request

# Page Configuration
st.set_page_config(
    page_title="Social Media Traffic Bot [Shielded]",
    page_icon="🛡️",
    layout="centered"
)

# --- Hide Streamlit Header, Footer, and Share/Deploy Toolbar via CSS ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {visibility: hidden; display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- CONFIGURATION ---
ADMIN_EMAIL = "kingtechnical421@gmail.com"
ADMIN_PASSCODE = "Madara786@@"

# Your Gmail SMTP Configuration
SMTP_SENDER_EMAIL = "kingtechnical421@gmail.com"
SMTP_APP_PASSWORD = "bipnuhzbuakxihih"

if "registered_users" not in st.session_state:
    st.session_state["registered_users"] = {}

if "order_history" not in st.session_state:
    st.session_state["order_history"] = []
# ----------------------------------------------------


def send_verification_email(receiver_email, code):
    """Sends a real 6-digit verification code email displaying 'Madara Uchiha' as the sender."""
    message = MIMEMultipart("alternative")
    message["Subject"] = "🔒 Your Social Media Bot Verification Code"
    
    message["From"] = formataddr((str(Header("Madara Uchiha", "utf-8")), SMTP_SENDER_EMAIL))
    message["To"] = receiver_email

    text_content = f"Hello,\n\nMadara Uchiha sent you a 6-digit verification code: {code}\n\nEnter this code on the registration page to verify your email."
    html_content = f"""
    <html>
      <body>
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
          <h2 style="color: #ff4b4b;">Social Media Traffic Bot</h2>
          <p>Hello,</p>
          <p><strong>Madara Uchiha</strong> sent you a 6-digit verification code:</p>
          <h1 style="background: #f0f2f6; padding: 10px; text-align: center; letter-spacing: 5px; color: #31333f;">{code}</h1>
          <p>Please enter this code in the portal to verify your email address.</p>
        </div>
      </body>
    </html>
    """

    message.attach(MIMEText(text_content, "plain"))
    message.attach(MIMEText(html_content, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SMTP_SENDER_EMAIL, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_SENDER_EMAIL, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False


# --- Authentication Gate ---
def check_authentication():
    if st.session_state.get("auth_role") in ["admin", "user"]:
        return True

    st.markdown("## 🔒 Bot Security Gateway")
    
    tab_user, tab_admin = st.tabs(["👤 User Portal", "👑 Admin Portal"])

    with tab_user:
        st.subheader("User Portal")
        
        with st.expander("📖 How to Register & Login (Click to read guide)", expanded=True):
            st.markdown("""
            Welcome! Follow these simple steps to access your account:
            1. **First-Time Users:** Enter your email address below and click **Continue**. 
            2. Check your inbox (or spam folder) for an email from **Madara Uchiha** containing your 6-digit verification code.
            3. Enter the 6-digit code on the screen and click **Verify Code**.
            4. Create and confirm your own **personal passcode** (this is a one-time process!).
            5. **Future Logins:** Whenever you return, just type your email and your created passcode to log in instantly.
            """)
        st.markdown("---")
        
        if "user_flow_step" not in st.session_state:
            st.session_state["user_flow_step"] = "input_email"
        if "flow_email" not in st.session_state:
            st.session_state["flow_email"] = ""

        users_db = st.session_state["registered_users"]

        if st.session_state["user_flow_step"] == "input_email":
            email_input = st.text_input("Enter Your Email Address", key="portal_email_input")
            
            if st.button("Continue", type="primary", key="portal_continue_btn"):
                if not email_input.strip():
                    st.error("Please enter your email address.")
                elif email_input.strip().lower() == ADMIN_EMAIL.lower():
                    st.warning("Please use the Admin Portal tab for Admin login.")
                else:
                    clean_email = email_input.strip().lower()
                    st.session_state["flow_email"] = clean_email

                    if clean_email in users_db and users_db[clean_email].get("registered", False):
                        st.session_state["user_flow_step"] = "login"
                        st.rerun()
                    else:
                        gen_code = str(random.randint(100000, 999999))
                        if clean_email not in users_db:
                            users_db[clean_email] = {}
                        users_db[clean_email]["code"] = gen_code
                        
                        with st.spinner("Sending 6-digit verification code..."):
                            success = send_verification_email(clean_email, gen_code)
                            if success:
                                st.session_state["user_flow_step"] = "verify_code"
                                st.success(f"📧 Verification code sent from **Madara Uchiha** to **{clean_email}**. Check your inbox/spam.")
                                st.rerun()
                            else:
                                st.error("❌ Failed to send email. Check your SMTP settings.")

        elif st.session_state["user_flow_step"] == "verify_code":
            st.info(f"Verifying email: **{st.session_state['flow_email']}**")
            entered_code = st.text_input("Enter 6-Digit Verification Code", max_chars=6, key="portal_verify_input")
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                if st.button("Verify Code", type="primary", key="portal_verify_btn"):
                    target_email = st.session_state["flow_email"]
                    saved_code = users_db.get(target_email, {}).get("code")
                    if entered_code.strip() == saved_code:
                        st.session_state["user_flow_step"] = "set_passcode"
                        st.success("✅ Email verified successfully! Now set your personal passcode.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid 6-digit verification code.")
            with col_v2:
                if st.button("Back / Change Email", key="portal_back_email"):
                    st.session_state["user_flow_step"] = "input_email"
                    st.rerun()

        elif st.session_state["user_flow_step"] == "set_passcode":
            st.info(f"Set a personal passcode for **{st.session_state['flow_email']}** (You will use this to log in hereafter).")
            new_pass = st.text_input("Create Passcode", type="password", key="portal_new_pass")
            confirm_pass = st.text_input("Confirm Passcode", type="password", key="portal_confirm_pass")

            if st.button("Save Passcode & Complete Registration", type="primary", key="portal_save_pass_btn"):
                if not new_pass or not confirm_pass:
                    st.error("Please fill in both fields.")
                elif new_pass != confirm_pass:
                    st.error("❌ Passcodes do not match.")
                else:
                    target_email = st.session_state["flow_email"]
                    users_db[target_email]["passcode"] = new_pass
                    users_db[target_email]["registered"] = True
                    
                    st.session_state["auth_role"] = "user"
                    st.session_state["user_email"] = target_email
                    st.session_state["user_flow_step"] = "input_email"
                    st.success("🎉 Registration complete! You are now logged in.")
                    st.rerun()

        elif st.session_state["user_flow_step"] == "login":
            st.info(f"Welcome back, **{st.session_state['flow_email']}**! Enter your custom passcode to log in.")
            login_pass = st.text_input("Your Passcode", type="password", key="portal_login_pass")

            col_l1, col_l2 = st.columns(2)
            with col_l1:
                if st.button("Login", type="primary", key="portal_login_btn"):
                    target_email = st.session_state["flow_email"]
                    saved_pass = users_db.get(target_email, {}).get("passcode")
                    if login_pass == saved_pass:
                        st.session_state["auth_role"] = "user"
                        st.session_state["user_email"] = target_email
                        st.session_state["user_flow_step"] = "input_email"
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect passcode.")
            with col_l2:
                if st.button("Use Different Email", key="portal_change_email_login"):
                    st.session_state["user_flow_step"] = "input_email"
                    st.rerun()

    with tab_admin:
        st.subheader("Admin Login")
        admin_email_input = st.text_input("Admin Email", key="admin_email_field")
        admin_pass_input = st.text_input("Admin Password / Passcode", type="password", key="admin_pass_field")

        if st.button("Login as Admin", type="primary", key="admin_login_btn"):
            if admin_email_input.strip().lower() == ADMIN_EMAIL.lower() and admin_pass_input == ADMIN_PASSCODE:
                st.session_state["auth_role"] = "admin"
                st.session_state["user_email"] = ADMIN_EMAIL
                st.rerun()
            else:
                st.error("❌ Unauthorized: Invalid Admin credentials.")

    return False

if not check_authentication():
    st.stop()
# -----------------------------------------------

if "stop_requested" not in st.session_state:
    st.session_state["stop_requested"] = False

current_role = st.session_state.get("auth_role", "user")
logged_in_email = st.session_state.get("user_email", "")

os.makedirs("./images", exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

uc.Chrome.__del__ = lambda self: None


def validate_url_for_platform(url, platform):
    url = url.lower()
    if platform == "YouTube Shorts":
        return "youtube.com" in url or "youtu.be" in url
    elif platform == "TikTok Reel":
        return "tiktok.com" in url
    elif platform == "Instagram Reel":
        return "instagram.com" in url
    return False


def extract_youtube_id(url):
    patterns = [
        r'(?:v=|/v/|embed/|shorts/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_video_metadata(url, platform):
    meta = {"thumb": None}
    if platform == "YouTube Shorts":
        yt_id = extract_youtube_id(url)
        if yt_id:
            meta["thumb"] = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
            
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            html = response.read().decode('utf-8', errors='ignore')
            thumb_match = re.search(r'property="og:image"\s+content="([^"]+)"', html)
            if thumb_match:
                meta["thumb"] = thumb_match.group(1)
    except Exception:
        pass
        
    return meta


def human_bezier_mouse_move(driver):
    try:
        actions = ActionChains(driver)
        steps = random.randint(4, 8)
        for _ in range(steps):
            dx = random.randint(-25, 25)
            dy = random.randint(-25, 25)
            actions.move_by_offset(dx, dy)
            actions.pause(random.uniform(0.03, 0.12))
        actions.perform()
    except Exception:
        pass


def run_single_social_session(
    session_id, target_url, platform, is_headless, proxy_list, status_box, progress_bar
):
    driver = None
    profile_dir = os.path.abspath(f"./temp_profile_{session_id}_{random.randint(1000,9999)}")
    try:
        options = uc.ChromeOptions()
        options.add_argument("--mute-audio")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        selected_ua = random.choice(USER_AGENTS)
        options.add_argument(f"--user-agent={selected_ua}")

        if proxy_list and len(proxy_list) > 0:
            chosen_proxy = random.choice(proxy_list).strip()
            if chosen_proxy:
                if not chosen_proxy.startswith("http://") and not chosen_proxy.startswith("https://"):
                    chosen_proxy = f"http://{chosen_proxy}"
                options.add_argument(f"--proxy-server={chosen_proxy}")

        if is_headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

        status_box.text(f"Session #{session_id} [{platform}]: Launching browser session...")
        driver = uc.Chrome(options=options, version_main=155, use_subprocess=True)
        driver.set_page_load_timeout(30)

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("""
            Object.defineProperty(document, 'hidden', {get: () => false});
            Object.defineProperty(document, 'visibilityState', {get: () => 'visible'});
            window.dispatchEvent(new Event('focus'));
        """)

        status_box.text(f"Session #{session_id} [{platform}]: Navigating to link...")
        driver.get(target_url)
        time.sleep(random.uniform(3.5, 5.2))

        try:
            scroll_amount = random.randint(150, 350)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.8, 1.5))
            
            video_element = driver.find_element(By.TAG_NAME, "video")
            actions = ActionChains(driver)
            actions.move_to_element(video_element).click().perform()
        except Exception:
            try:
                if platform == "YouTube Shorts":
                    driver.find_element(By.CLASS_NAME, "ytp-play-button").click()
                elif platform == "TikTok Reel":
                    driver.find_element(By.TAG_NAME, "button").click()
                elif platform == "Instagram Reel":
                    driver.find_element(By.TAG_NAME, "section").click()
            except Exception:
                pass

        total_watch_time = random.randint(10, 17)
        status_box.text(f"Session #{session_id} [{platform}]: Watching for {total_watch_time}s...")

        elapsed = 0
        while elapsed < total_watch_time:
            if st.session_state.get("stop_requested", False):
                break

            if elapsed % 2 == 0:
                human_bezier_mouse_move(driver)
                driver.execute_script("window.dispatchEvent(new Event('mousemove'));")

            time.sleep(1)
            elapsed += 1
            progress_val = min(1.0, elapsed / total_watch_time)
            progress_bar.progress(
                progress_val,
                text=f"Session #{session_id} | Elapsed: {elapsed}s / {total_watch_time}s"
            )

        return True

    except Exception as e:
        print(f"Session #{session_id} Error: {str(e)}")
        status_box.text(f"Status: Error in Session #{session_id} - {str(e)[:50]}...")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
            driver = None
        try:
            if os.path.exists(profile_dir):
                shutil.rmtree(profile_dir, ignore_errors=True)
        except Exception:
            pass


# --- Streamlit UI Layout ---
st.title("🛡️ Social Media Organic Traffic Bot")

if current_role == "admin":
    st.success(f"👑 Logged in as **Admin** ({logged_in_email})")
else:
    st.info(f"👤 Logged in as **User** ({logged_in_email})")

st.markdown("### Anti-Detect Shielded Traffic & View Generator")
st.write("Supports **YouTube Shorts**, **TikTok Reels**, and **Instagram Reels**.")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    if "show_share_box" not in st.session_state:
        st.session_state["show_share_box"] = False

    if st.button("🔗 Share Bot Link", use_container_width=True):
        st.session_state["show_share_box"] = not st.session_state["show_share_box"]

    if st.session_state["show_share_box"]:
        st.markdown("**Copy your bot link below to share:**")
        st.code("https://social-media-bot.streamlit.app", language="text")
        st.caption("Tell your friends to open this link, enter their email, verify with the 6-digit code sent by Madara Uchiha, and create their own personal passcode!")
        
    st.markdown("---")

    platform = st.selectbox("Select Platform", ["YouTube Shorts", "TikTok Reel", "Instagram Reel"])
    target_url = st.text_input("Target URL", placeholder="https://www.youtube.com/shorts/...")
    
    if "fetched_metadata" not in st.session_state:
        st.session_state["fetched_metadata"] = None

    if st.button("🔍 Fetch Details", use_container_width=True):
        if not target_url.strip():
            st.error("Please enter a target URL first!")
        elif not validate_url_for_platform(target_url, platform):
            st.error(f"URL does not match selected platform: {platform}")
        else:
            with st.spinner("Fetching thumbnail..."):
                st.session_state["fetched_metadata"] = fetch_video_metadata(target_url, platform)
                st.success("✅ Thumbnail fetched successfully!")

    max_allowed_views = 500
    total_views = st.number_input(
        f"Target Views Count (Max: {max_allowed_views})", 
        min_value=1, 
        max_value=max_allowed_views, 
        value=10
    )
    
    st.markdown("---")
    st.header("🌐 Proxy Pool Options")
    use_proxy = st.checkbox("Enable Proxy Pool", value=False)
    proxy_input = ""
    proxy_list = []
    
    if use_proxy:
        proxy_input = st.text_area(
            "Proxy List (One per line)", 
            placeholder="192.168.1.1:8080\nusername:password@192.168.1.2:8080",
            help="Paste your list of proxies here. A random proxy will be picked for each view session."
        )
        if proxy_input:
            proxy_list = [line.strip() for line in proxy_input.split("\n") if line.strip()]
        st.caption(f"Loaded proxies in pool: {len(proxy_list)}")

    is_headless = st.checkbox("Run in Background (Headless)", value=True)
    
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start_clicked = st.button("▶ Start Bot", type="primary", use_container_width=True)
    with col_btn2:
        stop_clicked = st.button("⏹ Stop Task", type="secondary", use_container_width=True)

    if stop_clicked:
        st.session_state["stop_requested"] = True

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["auth_role"] = None
        st.session_state["user_email"] = None
        st.rerun()

# Dashboard View Layout
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    views_metric_placeholder = st.empty()
    views_metric_placeholder.metric(label="Views Generated", value="0 / 0")
with col2:
    eta_metric_placeholder = st.empty()
    eta_metric_placeholder.metric(label="Order ETA", value="~0 min")
with col3:
    meta = st.session_state.get("fetched_metadata")
    if meta and meta.get("thumb"):
        st.image(meta["thumb"], width=130, caption="Target Thumbnail")
    elif platform == "YouTube Shorts" and target_url:
        yt_id = extract_youtube_id(target_url)
        if yt_id:
            st.image(f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg", width=130, caption="Target Thumbnail")

st.markdown("### 📊 Live Session Dashboard")
status_box = st.empty()
status_box.info("Status: Ready to initialize tasks.")
progress_bar = st.progress(0, text="Progress: Waiting for initiation...")

# --- Order & View History Section ---
st.markdown("---")
st.markdown("### 📜 Order & View History Ledger")
if st.session_state["order_history"]:
    # Display table/list of previous orders
    for idx, order in enumerate(reversed(st.session_state["order_history"])):
        with st.expander(f"Order #{len(st.session_state['order_history']) - idx} | {order['platform']} - {order['timestamp']} ({order['user']})"):
            st.write(f"🔗 **Target URL:** {order['url']}")
            st.markdown(f"""
            * **Requested Views:** `{order['requested']}`
            * **Generated Views:** `{order['generated']}`
            * **Success Rate:** `{(order['generated'] / order['requested']) * 100:.1f}%` if order['requested'] > 0 else `0%`
            """)
else:
    st.info("No orders placed yet in this session. Start a task to record history.")

# Execution Trigger
if start_clicked:
    st.session_state["stop_requested"] = False
    
    if not target_url.strip():
        st.error("Please enter a valid target URL!")
    elif not validate_url_for_platform(target_url, platform):
        st.error(f"URL Mismatch Error! The URL does not match the selected platform: {platform}")
    else:
        successful_views = 0
        
        total_estimated_seconds = int(total_views * 16)
        total_minutes = int(total_estimated_seconds / 60)
        if total_minutes >= 60:
            hours = round(total_minutes / 60, 1)
            if hours.is_integer():
                eta_str = f"~{int(hours)} hour{'s' if int(hours) > 1 else ''}"
            else:
                eta_str = f"~{hours} hours"
        else:
            eta_str = f"~{max(1, total_minutes)} min"

        eta_metric_placeholder.metric(label="Order ETA", value=eta_str)

        st.success("🚀 **Order Submitted Successfully!** You can now safely leave this web page or shut down your device—the bot will continue processing your views in the background.")

        status_box.warning(f"Running task for {platform} | Target: {total_views} views (10-17s watch times)...")

        for i in range(total_views):
            if st.session_state.get("stop_requested", False):
                status_box.error("🛑 Task stopped by user.")
                break
            
            success = run_single_social_session(
                session_id=i + 1,
                target_url=target_url,
                platform=platform,
                is_headless=is_headless,
                proxy_list=proxy_list,
                status_box=status_box,
                progress_bar=progress_bar
            )

            if success:
                successful_views += 1

            # LIVE UPDATE PLACEHOLDER
            views_metric_placeholder.metric(label="Views Generated", value=f"{successful_views} / {total_views}")

            if i + 1 < total_views and not st.session_state.get("stop_requested", False):
                organic_delay = random.uniform(2.5, 6.0)
                status_box.text(f"Transitioning: Next session in {organic_delay:.1f}s...")
                time.sleep(organic_delay)

        # Log order details into history ledger upon completion or cancellation
        order_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
            "user": logged_in_email,
            "platform": platform,
            "url": target_url,
            "requested": total_views,
            "generated": successful_views
        }
        st.session_state["order_history"].append(order_record)

        if not st.session_state.get("stop_requested", False):
            status_box.success(f"Task completed successfully! Generated {successful_views}/{total_views} views.")
            st.balloons()
            st.rerun()
