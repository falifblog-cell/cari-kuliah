import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Cari Kuliah", page_icon="🔍", layout="wide")

# --- Fungsi Helper: Ekstrak ID Video dari URL ---
def get_video_id(url):
    """
    Mengambil ID video YouTube dari pelbagai format URL (youtube.com atau youtu.be)
    """
    # Regex untuk mencari corak ID video
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

# --- Fungsi Helper: Tukar masa (saat) ke format MM:SS ---
def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02}:{secs:02}"

# --- Title & Header ---
st.title("🔍 Cari Isi Kuliah/Ceramah")
st.markdown("Masukkan link YouTube, cari keyword, dan tonton terus pada minit tersebut.")

# --- Sidebar: Input URL ---
with st.sidebar:
    st.header("1. Masukkan Link")
    video_url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    
    if st.button("Proses Video"):
        if video_url:
            video_id = get_video_id(video_url)
            if video_id:
                st.session_state['video_id'] = video_id
                st.session_state['transcript'] = None # Reset transcript lama
                
                # Cuba dapatkan transcript
                try:
                    # Kita minta Bahasa Melayu (ms), Indonesia (id), atau English (en)
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ms', 'id', 'en'])
                    st.session_state['transcript'] = transcript
                    st.success("✅ Sari kata berjaya diambil!")
                except TranscriptsDisabled:
                    st.error("❌ Video ini tidak membenarkan sari kata (Subtitles disabled).")
                except NoTranscriptFound:
                    st.error("❌ Tiada sari kata auto-generated dijumpai untuk bahasa Melayu/Indo/English.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Link YouTube tidak sah.")

# --- Main Area ---

# 1. Setup Video Player (Default start masa 0)
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = 0

# Jika ada video ID, paparkan video player di bahagian atas
if 'video_id' in st.session_state:
    st.video(f"https://youtu.be/{st.session_state['video_id']}", start_time=st.session_state['start_time'])
    
    # 2. Bahagian Carian
    st.divider()
    st.header("2. Cari Keyword")
    
    if 'transcript' in st.session_state and st.session_state['transcript']:
        search_query = st.text_input("Taip perkataan (contoh: 'solat', 'hukum', 'niat')", "")
        
        if search_query:
            # Filter transcript berdasarkan keyword (case insensitive)
            results = [t for t in st.session_state['transcript'] if search_query.lower() in t['text'].lower()]
            
            st.write(f"Jumpa **{len(results)}** hasil carian:")
            
            # Paparkan hasil dalam bentuk senarai
            for item in results:
                col1, col2, col3 = st.columns([1, 4, 1])
                
                start_seconds = int(item['start'])
                time_str = format_time(start_seconds)
                text_content = item['text']
                
                with col1:
                    st.markdown(f"**⏱️ {time_str}**")
                
                with col2:
                    # Highlight perkataan yang dicari
                    highlighted_text = text_content.replace(search_query, f"**{search_query}**") # Simple bold
                    st.markdown(f"_{highlighted_text}_")
                
                with col3:
                    # Butang untuk lompat ke masa tersebut
                    if st.button("▶️ Main", key=f"btn_{start_seconds}"):
                        st.session_state['start_time'] = start_seconds
                        st.rerun() # Refresh page untuk update player time
        else:
            st.info("Sila taip sesuatu untuk mula mencari.")
            
    elif 'video_id' in st.session_state and st.session_state.get('transcript') is None:
        st.write("Menunggu transcript...")

else:
    st.info("👈 Sila masukkan link YouTube di sidebar sebelah kiri untuk bermula.")
