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
        mean_pct = 1.15
        std_dev_pct = 0.08
    else:
        mean_pct = 0.65
        std_dev_pct = 0.12

    target_pct = random.gauss(mean_pct, std_dev_pct)
    target_pct = max(0.35, min(target_pct, 1.45))

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

        total_watch_time = calculate_organic_watch_time(video_length, is_extended_view)
        retention_pct = int((total_watch_time / video_length) * 100)
        mode_tag = f"🔥 Retention ({retention_pct}%)" if is_extended_view else f"Standard ({retention_pct}%)"

        status_box.text(f"Session #{session_id} [{platform}] ({mode_tag}): Playing {total_watch_time}s...")

        elapsed = 0
        while elapsed < total_watch_time:
            if st.session_state.get("stop_requested", False):
                break

            if elapsed % random.choice([2, 3, 4]) == 0:
                human_bezier_mouse_move(driver)
                driver.execute_script("window.dispatchEvent(new Event('mousemove'));")

            time.sleep(1)
            elapsed += 1
            progress_val = min(1.0, elapsed / total_watch_time)
            progress_bar.progress(
                progress_val,
                text=f"Session #{session_id} | Elapsed: {elapsed}s / {total_watch_time}s ({mode_tag})"
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
st.markdown("### Anti-Detect Shielded Traffic & View Generator")
st.write("Supports **YouTube Shorts**, **TikTok Reels**, and **Instagram Reels**.")

with st.sidebar:
    st.header("⚙️ Configuration")
    platform = st.selectbox("Select Platform", ["YouTube Shorts", "TikTok Reel", "Instagram Reel"])
    target_url = st.text_input("Target URL", placeholder="https://www.youtube.com/shorts/...")
    total_views = st.number_input("Target Views Count", min_value=1, max_value=100, value=5)
    
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

# Main Dashboard layout & Thumbnail preview
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    views_metric = st.metric(label="Views Generated", value="0 / 0")
with col2:
    eta_metric = st.metric(label="Order ETA", value="--:--:--")
with col3:
    if platform == "YouTube Shorts" and target_url:
        yt_id = extract_youtube_id(target_url)
        if yt_id:
            st.image(f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg", width=140, caption="Target Thumbnail")

st.markdown("### 📊 Live Session Dashboard")
status_box = st.empty()
status_box.info("Status: Ready to initialize tasks.")
progress_bar = st.progress(0, text="Progress: Waiting for initiation...")

# Execution Trigger
if start_clicked:
    st.session_state["stop_requested"] = False
    
    if not target_url.strip():
        st.error("Please enter a valid target URL!")
    elif not validate_url_for_platform(target_url, platform):
        st.error(f"URL Mismatch Error! The URL does not match the selected platform: {platform}")
    else:
        if platform == "YouTube Shorts":
            video_length = random.randint(15, 30)
        elif platform == "TikTok Reel":
            video_length = random.randint(15, 25)
        else:
            video_length = random.randint(15, 30)

        successful_views = 0
        extended_count = int(total_views * 0.20)
        extended_indices = set(random.sample(range(total_views), extended_count)) if total_views > 0 else set()

        avg_view_duration = (video_length * 0.70) + 8
        total_estimated_seconds = int(total_views * avg_view_duration)
        completion_timestamp = time.time() + total_estimated_seconds
        completion_time_str = time.strftime("%I:%M:%S %p", time.localtime(completion_timestamp))
        eta_metric.metric(label="Order ETA", value=completion_time_str)

        status_box.warning(f"Running task for {platform} | Target: {total_views} views...")

        for i in range(total_views):
            if st.session_state.get("stop_requested", False):
                status_box.error("🛑 Task stopped by user.")
                break

            is_extended_view = (i in extended_indices)
            
            success = run_single_social_session(
                session_id=i + 1,
                target_url=target_url,
                platform=platform,
                is_headless=is_headless,
                is_extended_view=is_extended_view,
                video_length=video_length,
                proxy_list=proxy_list,
                status_box=status_box,
                progress_bar=progress_bar
            )

            if success:
                successful_views += 1

            views_metric.metric(label="Views Generated", value=f"{successful_views} / {total_views}")

            if i + 1 < total_views and not st.session_state.get("stop_requested", False):
                organic_delay = random.uniform(2.5, 6.0)
                status_box.text(f"Transitioning: Next session in {organic_delay:.1f}s...")
                time.sleep(organic_delay)

        if not st.session_state.get("stop_requested", False):
            status_box.success(f"Task completed successfully! Generated {successful_views}/{total_views} views.")
            st.balloons()
