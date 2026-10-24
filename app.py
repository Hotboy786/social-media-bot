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

# Ensure local image cache folder exists
os.makedirs("./images", exist_ok=True)

# User-Agent pool for fingerprint rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# Neutralize undetected-chromedriver's garbage collection destructor warning
uc.Chrome.__del__ = lambda self: None


def validate_url_for_platform(url, platform):
    """Strictly validates if the URL matches the selected platform."""
    url = url.lower()
    if platform == "YouTube Shorts":
        return "youtube.com" in url or "youtu.be" in url
    elif platform == "TikTok Reel":
        return "tiktok.com" in url
    elif platform == "Instagram Reel":
        return "instagram.com" in url
    return False


def human_bezier_mouse_move(driver):
    """Simulates natural human mouse movement using micro-steps."""
    try:
        actions = ActionChains(driver)
        steps = random.randint(5, 9)
        for _ in range(steps):
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)
            actions.move_by_offset(dx, dy)
            actions.pause(random.uniform(0.05, 0.15))
        actions.perform()
    except Exception:
        pass


def run_single_social_session(
    session_id, target_url, platform, is_headless, is_extended_view, video_length, proxy_str, status_box, progress_bar
):
    """Executes a single view session with WAF bypasses, isolated profile directory, and optional proxy."""
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

        # Optional Proxy Integration
        if proxy_str and proxy_str.strip():
            options.add_argument(f"--proxy-server={proxy_str.strip()}")

        if is_headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

        status_box.text(f"Session #{session_id} [{platform}]: Launching browser session...")
        driver = uc.Chrome(options=options, version_main=155, use_subprocess=True)
        driver.set_page_load_timeout(30)

        # 1. Bypass DOM/JS Inspection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 2. Force Tab Focus & Visibility
        driver.execute_script("""
            Object.defineProperty(document, 'hidden', {get: () => false});
            Object.defineProperty(document, 'visibilityState', {get: () => 'visible'});
            window.dispatchEvent(new Event('focus'));
        """)

        status_box.text(f"Session #{session_id} [{platform}]: Navigating to link...")
        driver.get(target_url)
        time.sleep(4)

        try:
            driver.execute_script("window.scrollBy(0, window.innerHeight / 4);")
            time.sleep(1)
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

        if is_extended_view:
            target_percentage = random.uniform(1.05, 1.15)
            mode_tag = "🔥 High Retention (110%)"
        else:
            target_percentage = random.uniform(0.50, 0.75)
            mode_tag = "Standard"

        total_watch_time = int(video_length * target_percentage)
        total_watch_time = max(10, total_watch_time)

        status_box.text(f"Session #{session_id} [{platform}] ({mode_tag}): Playing {total_watch_time}s...")

        elapsed = 0
        while elapsed < total_watch_time:
            if elapsed % 3 == 0:
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
        # Clean up temporary session directory
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
    st.header("🌐 Proxy Options (Optional)")
    use_proxy = st.checkbox("Enable Residential Proxy", value=False)
    proxy_str = ""
    if use_proxy:
        proxy_str = st.text_input("Proxy Server", placeholder="http://ip:port or http://user:pass@ip:port")
        st.caption("Leave empty if you want to run direct without proxies.")

    is_headless = st.checkbox("Run in Background (Headless)", value=True)
    
    st.markdown("---")
    start_clicked = st.button("▶ Start Bot Task", type="primary", use_container_width=True)

    # --- Share This Bot Section ---
    st.markdown("---")
    st.header("📤 Share This Bot")
    st.markdown("Share this live web tool with your friends or community:")
    
    live_app_url = "https://social-media-bot.streamlit.app"
    st.text_input("App Link", value=live_app_url, key="share_link")
    st.caption("Copy the link above to share anywhere!")

# Main Dashboard
col1, col2 = st.columns(2)
with col1:
    views_metric = st.metric(label="Views Generated", value="0 / 0")
with col2:
    eta_metric = st.metric(label="Order ETA", value="--:--:--")

st.markdown("### 📊 Live Session Dashboard")
status_box = st.empty()
status_box.info("Status: Ready to initialize tasks.")
progress_bar = st.progress(0, text="Progress: Waiting for initiation...")

# Execution Trigger
if start_clicked:
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

        # ETA Calculation
        avg_view_duration = (video_length * 0.70) + 8
        total_estimated_seconds = int(total_views * avg_view_duration)
        completion_timestamp = time.time() + total_estimated_seconds
        completion_time_str = time.strftime("%I:%M:%S %p", time.localtime(completion_timestamp))
        eta_metric.metric(label="Order ETA", value=completion_time_str)

        status_box.warning(f"Running task for platform | Target: {total_views} views...")

        for i in range(total_views):
            is_extended_view = (i in extended_indices)
            
            success = run_single_social_session(
                session_id=i + 1,
                target_url=target_url,
                platform=platform,
                is_headless=is_headless,
                is_extended_view=is_extended_view,
                video_length=video_length,
                proxy_str=proxy_str,
                status_box=status_box,
                progress_bar=progress_bar
            )

            if success:
                successful_views += 1

            views_metric.metric(label="Views Generated", value=f"{successful_views} / {total_views}")

            if i + 1 < total_views:
                organic_delay = random.randint(2, 4)
                status_box.text(f"Transitioning: Next session in {organic_delay}s...")
                time.sleep(organic_delay)

        status_box.success(f"Task completed successfully! Generated {successful_views}/{total_views} views.")
        st.balloons()
