import streamlit as st
import whisper
import yt_dlp
import os
import glob

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Cari Kuliah (AI Whisper)", page_icon="🎙️", layout="wide")

# --- Fungsi: Download Audio (Versi Anti-Block 403) ---
def download_audio(url):
    # Padam fail lama jika ada
    if os.path.exists("audio_temp.mp3"):
        os.remove("audio_temp.mp3")
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio_temp.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'nocheckcertificate': True,
        # --- TEKNIK MENYAMAR (SPOOFING) ---
        # Kita beritahu YouTube kita ni Android Phone, bukan Python Script
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs', 'js'], 
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return "audio_temp.mp3"

# --- Fungsi Helper Lain ---
def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02}:{secs:02}"

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

# --- UI Layout ---
st.title("🎙️ Cari Kuliah (Tanpa CC)")
st.caption("Versi: Anti-Block 403 (Menyamar sebagai Android Client)")

# --- Sidebar ---
with st.sidebar:
    st.header("1. Masukkan Link")
    url = st.text_input("YouTube URL")
    
    model_type = st.radio("Pilih Ketelitian AI:", ["tiny", "base"], index=0)

    if st.button("Mula Proses (AI Dengar)"):
        if url:
            st.session_state['transcript'] = None
            video_id = get_video_id(url)
            st.session_state['video_id'] = video_id
            
            status = st.empty()
            try:
                # 1. Download
                status.info("📥 Sedang 'curi' audio dari YouTube (Mode Android)...")
                audio_file = download_audio(url)
                
                # 2. Load AI
                status.info(f"🤖 Sedang loading otak AI ({model_type})...")
                model = whisper.load_model(model_type)
                
                # 3. Transcribe
                status.info("👂 AI sedang mendengar... (Boleh ambil masa 2-3 minit)")
                result = model.transcribe(audio_file)
                
                st.session_state['transcript'] = result['segments']
                status.success("✅ Siap!")
                
                # Cleanup
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    
            except Exception as e:
                status.error(f"❌ Masih Error: {e}")
                st.error("Jika error 403 keluar juga, maksudnya YouTube dah ban IP server Streamlit ni. Kena cuba esok atau run di laptop sendiri.")
        else:
            st.warning("Masukkan link dulu.")

# --- Main Area ---
if 'video_id' in st.session_state and st.session_state.get('video_id'):
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = 0
        
    st.video(f"https://youtu.be/{st.session_state['video_id']}", start_time=st.session_state['start_time'])
    
    st.divider()
    
    if 'transcript' in st.session_state and st.session_state['transcript']:
        st.header("2. Cari Keyword")
        search_query = st.text_input("Cari apa ustaz cakap:", "")
        
        if search_query:
            results = [s for s in st.session_state['transcript'] if search_query.lower() in s['text'].lower()]
            st.write(f"Jumpa **{len(results)}** ayat:")
            
            for segment in results:
                c1, c2, c3 = st.columns([1, 4, 2])
                start_sec = int(segment['start'])
                
                with c1: st.code(format_time(start_sec))
                with c2: st.write(segment['text'].replace(search_query, f"**{search_query}**"))
                with c3:
                    if st.button(f"▶️ Dengar", key=f"btn_{start_sec}"):
                        st.session_state['start_time'] = start_sec
                        st.rerun()
        else:
            with st.expander("Lihat Transkrip Penuh"):
                for segment in st.session_state['transcript']:
                    st.write(f"[{format_time(segment['start'])}] {segment['text']}")
