import re
from urllib.parse import urlsplit

import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def normalize_instagram_url(value):
    value = value.strip()
    if "://" not in value:
        value = "https://" + value
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in {
        "instagram.com", "www.instagram.com", "m.instagram.com"
    }:
        raise ValueError("Paste a link to an Instagram Reel or video post.")

    match = re.fullmatch(
        r"/(?:[A-Za-z0-9._]+/)?(reels?|p|tv)/([A-Za-z0-9_-]+)/?", parsed.path
    )
    if not match:
        raise ValueError("Paste a direct Reel or video post link from Instagram.")
    kind, shortcode = match.groups()
    if kind == "reels":
        kind = "reel"
    return f"https://www.instagram.com/{kind}/{shortcode}/"


def fetch_metadata(url):
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "socket_timeout": 10,
        "extractor_retries": 0,
    }
    with YoutubeDL(options) as extractor:
        return extractor.extract_info(url, download=False, ie_key="Instagram")


def format_count(value):
    return f"{value:,}" if type(value) is int and value >= 0 else "Unavailable"


def main():
    st.set_page_config(page_title="Instagram Video Lookup", layout="centered")
    st.title("Instagram Video Lookup")
    st.caption("Check a Reel or video post, then open it on Instagram to like it manually.")

    with st.form("lookup"):
        value = st.text_input("Instagram link", placeholder="https://www.instagram.com/reel/…/")
        submitted = st.form_submit_button("Fetch details")

    if submitted:
        st.session_state.pop("lookup_result", None)
        try:
            url = normalize_instagram_url(value)
        except ValueError as error:
            st.error(str(error))
        else:
            with st.spinner("Fetching Instagram details…"):
                try:
                    metadata = fetch_metadata(url)
                except DownloadError:
                    metadata = None
            st.session_state.lookup_result = (url, metadata)

    if "lookup_result" not in st.session_state:
        return

    url, metadata = st.session_state.lookup_result
    if metadata is None:
        st.warning("Instagram did not return video details. The post may be private, unavailable, or require sign-in.")
        metadata = {}
    elif metadata.get("_type") in {"playlist", "multi_video"}:
        st.caption("Counts below apply to the post as a whole where available.")

    st.subheader(metadata.get("title") or "Instagram video")
    creator = metadata.get("channel") or metadata.get("uploader")
    if creator:
        st.text(creator)
    if metadata.get("thumbnail"):
        st.image(metadata["thumbnail"], width=320)
    views, likes = st.columns(2)
    views.metric("Views", format_count(metadata.get("view_count")))
    likes.metric("Likes", format_count(metadata.get("like_count")))
    if metadata.get("description"):
        with st.expander("Caption"):
            st.text(metadata["description"])
    st.link_button("Open on Instagram", url, type="primary")


if __name__ == "__main__":
    main()
