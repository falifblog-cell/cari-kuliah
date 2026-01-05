import streamlit as st
import whisper
import yt_dlp
import os
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Cari Kuliah (AI Whisper)", page_icon="🎙️", layout="wide")

# --- Fungsi: Download Audio dari YouTube ---
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio_temp',  # Nama fail sementara
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "audio_temp.mp3"

# --- Fungsi: Format Masa ---
def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02}:{secs:02}"

# --- Fungsi: Extract Video ID ---
def get_video_id(url):
    # Cara simple extract ID untuk display player
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

# --- UI Layout ---
st.title("🎙️ Cari Kuliah (Tanpa CC)")
st.markdown("Versi ini menggunakan **AI Whisper**. Ia boleh baca video walaupun TIADA subtitle.")
st.warning("⚠️ Proses mungkin ambil masa 1-3 minit bergantung panjang video.")

# --- Sidebar ---
with st.sidebar:
    st.header("1. Masukkan Link")
    url = st.text_input("YouTube URL")
    
    # Pilihan Model (Tiny laju tapi kurang tepat, Base lambat sikit tapi okay)
    model_type = st.radio("Pilih Ketelitian AI:", ["tiny", "base"], index=0, help="'tiny' laju, 'base' lebih pandai.")

    if st.button("Mula Proses (AI Dengar)"):
        if url:
            st.session_state['transcript'] = None
            video_id = get_video_id(url)
            st.session_state['video_id'] = video_id
            
            status = st.empty()
            try:
                # 1. Download Audio
                status.info("📥 Sedang download audio dari YouTube...")
                audio_file = download_audio(url)
                
                # 2. Load AI Model
                status.info(f"🤖 Sedang loading otak AI ({model_type})...")
                model = whisper.load_model(model_type)
                
                # 3. Transcribe
                status.info("👂 AI sedang mendengar dan menyalin... (Sila tunggu)")
                result = model.transcribe(audio_file)
                
                # Simpan result
                st.session_state['transcript'] = result['segments']
                status.success("✅ Siap! AI dah habis dengar.")
                
                # Buang fail audio untuk jimat space
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    
            except Exception as e:
                status.error(f"❌ Error: {e}")
        else:
            st.warning("Masukkan link dulu.")

# --- Main Area ---
if 'video_id' in st.session_state and st.session_state.get('video_id'):
    
    # Player Video
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = 0
        
    st.video(f"https://youtu.be/{st.session_state['video_id']}", start_time=st.session_state['start_time'])
    
    st.divider()
    
    # Bahagian Carian
    if 'transcript' in st.session_state and st.session_state['transcript']:
        st.header("2. Cari Keyword")
        search_query = st.text_input("Cari apa ustaz cakap:", "")
        
        if search_query:
            results = [s for s in st.session_state['transcript'] if search_query.lower() in s['text'].lower()]
            st.write(f"Jumpa **{len(results)}** ayat:")
            
            for segment in results:
                col1, col2, col3 = st.columns([1, 4, 2])
                start_sec = int(segment['start'])
                text = segment['text']
                
                with col1: st.code(format_time(start_sec))
                with col2: st.write(text.replace(search_query, f"**{search_query}**"))
                with col3:
                    if st.button(f"▶️ Dengar", key=f"btn_{start_sec}"):
                        st.session_state['start_time'] = start_sec
                        st.rerun()
        else:
            # Show full transcript option
            with st.expander("Lihat Transkrip Penuh"):
                for segment in st.session_state['transcript']:
                    st.write(f"[{format_time(segment['start'])}] {segment['text']}")
