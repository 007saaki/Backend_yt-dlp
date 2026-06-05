from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel

app = FastAPI()

# CORS configured for your Netlify frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "ssstik Style Premium Raw Proxy Engine is Live!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Step 1: Grab the absolute raw 10MB+ TikTok CDN link via high-bitrate bridge
    try:
        api_url = "https://tikwm.com/api/"
        response = requests.post(api_url, data={"url": tiktok_url, "hd": 1}, timeout=12)
        
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                video_info = res_data["data"]
                
                # This is the real raw high-bitrate source link from TikTok
                raw_cdn_url = video_info.get("hdplay") or video_info.get("play")
                
                if raw_cdn_url:
                    if not raw_cdn_url.startswith("http"):
                        raw_cdn_url = "https://tikwm.com" + raw_cdn_url
                    
                    title = video_info.get("title", "video")
                    clean_title = "".join([c for c in title if c.isalnum() or c==' ']).strip()
                    if not clean_title:
                        clean_title = "tiktok_premium_video"
                    
                    # STEP 2: Instead of giving the raw link to browser (which causes compression/403),
                    # We generate a direct streaming download link from YOUR OWN Render server!
                    your_render_proxy_url = f"https://tiktokbestever.onrender.com/stream_video?cdn_url={requests.utils.quote(raw_cdn_url)}&filename={requests.utils.quote(clean_title)}"
                    
                    return {
                        "url": your_render_proxy_url,
                        "title": video_info.get("title", "TikTok Premium Master HD"),
                        "thumbnail": video_info.get("cover", "")
                    }
    except Exception as e:
        print(f"Proxy generation failed: {e}")

    raise HTTPException(status_code=404, detail="Unable to extract high-bitrate master stream.")

@app.get("/stream_video")
def stream_video(cdn_url: str = Query(...), filename: str = Query(...)):
    # STEP 3: Your Render server acts exactly like v16.tokcdn.com here.
    # It fetches the full 10MB+ raw file and streams it byte-for-byte to the browser.
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        # Fetching raw video stream with stream=True to avoid server RAM crashes
        req = requests.get(cdn_url, headers=headers, stream=True, timeout=30)
        
        if req.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to bridge video file from source.")
            
        def iterfile():
            for chunk in req.iter_content(chunk_size=8192):
                yield chunk
                
        # Force browser to download it as an uncompressed .mp4 file attachment, just like ssstik!
        return StreamingResponse(
            iterfile(), 
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={filename}_original.mp4"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
