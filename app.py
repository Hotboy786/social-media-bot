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
import requests
import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

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


# --- Passcode Protection Gate ---
def check_password():
    """Returns True if the user enters the correct passcode."""
    
    def password_entered():
        if st.session_state["password"] == "mysecret123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("## 🔒 Restricted Access")
        st.text_input("Enter Passcode to Unlock Bot", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("## 🔒 Restricted Access")
        st.text_input("Enter Passcode to Unlock Bot", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect passcode. Please try again.")
        return False
    else:
        return True

if not check_password():
    st.stop()
# -----------------------------------------------

# Initialize session state for cancellation control
if "stop_requested" not in st.session_state:
    st.session_state["stop_requested"] = False

# Ensure local image cache folder exists
os.makedirs("./images", exist_ok=True)

# User-Agent pool for fingerprint rotation
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


def calculate_organic_watch_time(video_length, is_extended_view):
    """Calculates organic watch duration with randomized Gaussian variation and micro-jitter."""
    if is_extended_view:
        # High retention (looped watch ~105% to 130%)
        mean_pct = 1.15
        std_dev_pct = 0.08
    else:
        # Standard organic retention (~45% to 85%)
        mean_pct = 0.65
        std_dev_pct = 0.12

    # Draw from normal distribution to mimic human behavior distribution
    target_pct = random.gauss(mean_pct, std_dev_pct)
    target_pct = max(0.35, min(target_pct, 1.45))  # Keep within human bounds

    # Calculate base watch duration + add random fractional jitter
    watch_time = (video_length * target_pct) + random.uniform(-2.0, 3.5)
    return max(8, int(watch_time))


def run_single_social_session(
    session_id, target_url, platform, is_headless, is_extended_view, video_length, proxy_list, status_box, progress_bar
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
        time.sleep(random.uniform(3.5, 5.2))  # Randomized initial page arrival pause

        try:
            # Simulate natural scroll micro-bursts
            scroll_amount = random.randint(150, 350)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.8, 1.5))
            
            video_element = driver.find_element(By
