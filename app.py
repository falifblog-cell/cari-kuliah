import streamlit as st
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
import re

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Cari Kuliah", page_icon="🔍", layout="wide")

# --- Fungsi Helper: Ekstrak ID Video ---
def get_video_id(url):
    # Support format youtu.be dan youtube.com
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

# --- Fungsi Helper: Format Masa ---
def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02}:{secs:02}"

# --- UI Layout ---
st.title("🔍 Cari Isi Kuliah/Ceramah")
st.markdown("Masukkan link YouTube (yang ada caption/CC), cari keyword, dan tonton.")

# --- Sidebar ---
with st.sidebar:
    st.header("Langkah 1: Masukkan Link")
    video_url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    
    # Butang Reset/Proses
    if st.button("Proses Video"):
        if video_url:
            video_id = get_video_id(video_url)
            if video_id:
                st.session_state['video_id'] = video_id
                st.session_state['transcript'] = None 
                
                try:
                    # Kita guna format standard library
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ms', 'id', 'en'])
                    st.session_state['transcript'] = transcript
                    st.success("✅ Sari kata berjaya!")
                except youtube_transcript_api.TranscriptsDisabled:
                    st.error("❌ Video ini owner dia tutup function CC/Subtitle.")
                except youtube_transcript_api.NoTranscriptFound:
                    st.error("❌ Tiada sari kata Bahasa Melayu/Indo/English dalam video ni.")
                except Exception as e:
                    st.error(f"❌ Error pelik: {e}")
            else:
                st.warning("⚠️ Link tak betul tu.")

# --- Main Screen ---
if 'video_id' in st.session_state:
    # Set masa mula default
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = 0

    # Player Video
    st.video(f"https://youtu.be/{st.session_state['video_id']}", start_time=st.session_state['start_time'])
    
    st.divider()
    st.header("Langkah 2: Cari Keyword")
    
    # Check kalau transcript wujud
    if st.session_state.get('transcript'):
        search_query = st.text_input("Cari perkataan (Contoh: solat, puasa, rasuah)", "")
        
        if search_query:
            # Filter cari perkataan
            results = [t for t in st.session_state['transcript'] if search_query.lower() in t['text'].lower()]
            
            st.write(f"Jumpa **{len(results)}** tempat:")
            
            # Loop untuk paparkan hasil
            for item in results:
                c1, c2, c3 = st.columns([1, 4, 2])
                
                start_sec = int(item['start'])
                txt = item['text']
                
                with c1:
                    st.code(format_time(start_sec))
                with c2:
                    st.write(txt.replace(search_query, f"**{search_query}**"))
                with c3:
                    if st.button(f"▶️ Tonton ({format_time(start_sec)})", key=f"btn_{start_sec}"):
                        st.session_state['start_time'] = start_sec
                        st.rerun()
        else:
            st.info("Taip sesuatu untuk cari.")
    else:
        st.warning("Video ada, tapi transcript tak dapat ditarik. Cuba video lain.")
        
else:
    st.info("👈 Mula dengan masukkan link di menu sebelah kiri (Sidebar).")
