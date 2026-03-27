import gradio as gr
import os
import uuid
import urllib.request
import subprocess

os.makedirs("results", exist_ok=True)

def create_video(image_url, audio_url):
    """Görseli sesle senkronize et - Zoom efekti"""
    video_id = str(uuid.uuid4())[:8]
    
    # Dosyaları indir
    img_path = f"img_{video_id}.png"
    aud_path = f"aud_{video_id}.mp3"
    out_path = f"results/video_{video_id}.mp4"
    
    try:
        urllib.request.urlretrieve(image_url, img_path)
        urllib.request.urlretrieve(audio_url, aud_path)
    except Exception as e:
        return None, f"İndirme hatası: {str(e)}"
    
    # FFmpeg: Ses yoğunluğuna göre zoom (basit versiyon)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-i", aud_path,
        "-vf", "zoompan=z='1+0.3*sin(t*2)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", out_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out_path, "Başarılı!"
    except subprocess.CalledProcessError as e:
        return None, f"FFmpeg hatası: {e.stderr.decode()}"

# Gradio arayüz
with gr.Blocks() as demo:
    gr.Markdown("# AI Haber Spikeri")
    
    with gr.Row():
        with gr.Column():
            img_url = gr.Textbox(label="Görsel URL", placeholder="https://...")
            aud_url = gr.Textbox(label="Ses URL", placeholder="https://...")
            btn = gr.Button("Video Oluştur", variant="primary")
        
        with gr.Column():
            video = gr.Video(label="Oluşturulan Video")
            status = gr.Textbox(label="Durum")
    
    btn.click(create_video, [img_url, aud_url], [video, status])

# API için
demo.launch()
