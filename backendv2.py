from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel

app = FastAPI()

# CORS allowed for your Netlify frontend
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
    return {"message": "Premium High-Bitrate Raw Engine is Live!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Engine 1: Pure Raw CDN Extractor (Pulls the exact 10MB+ uncompressed source)
    try:
        api_url = f"https://api.tiklydown.eu.org/api/download?url={requests.utils.quote(tiktok_url)}"
        response = requests.get(api_url, timeout=12)
        
        if response.status_code == 200:
            res_data = response.json()
            video_info = res_data.get("video", {})
            
            # 'noWatermark' contains the direct full-size TikTok CDN address
            hd_link = video_info.get("noWatermark") or video_info.get("noWatermark2")
            
            if hd_link:
                title = res_data.get("title", "TikTok Premium Raw Video")
                cover = res_data.get("author", {}).get("avatar", "")
                
                return {
                    "url": hd_link,
                    "title": title,
                    "thumbnail": cover
                }
    except Exception as e:
        print(f"Engine 1 bypass failed, trying fallback... Error: {e}")

    # Engine 2: High-Bitrate Fallback Bridge
    try:
        fallback_url = "https://tikwm.com/api/"
        response = requests.post(fallback_url, data={"url": tiktok_url, "hd": 1}, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                video_info = res_data["data"]
                # Forcing highest bitrate stream
                hd_link = video_info.get("hdplay") or video_info.get("play")
                title = video_info.get("title", "TikTok Premium Video")
                cover = video_info.get("cover", "")
                
                return {
                    "url": hd_link,
                    "title": title,
                    "thumbnail": cover
                }
    except Exception as e:
        print(f"Engine 2 failed: {e}")
        
    raise HTTPException(status_code=404, detail="Failed to fetch high-quality stream. Try again.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
