from fastapi import FastAPI, HTTPException
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
    return {"message": "Premium Uncompressed 10MB+ Raw Engine is Live!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")

    # METHOD 1: Direct TikTok CDN Extraper (Pulls 100% Original Raw 10MB+ File)
    try:
        api_url = f"https://api.tiklydown.eu.org/api/download?url={requests.utils.quote(tiktok_url)}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Grabbing the uncompressed source link directly from TikTok's servers
            cdn_link = data.get("video", {}).get("noWatermark") or data.get("video", {}).get("noWatermark2")
            if cdn_link:
                return {
                    "url": cdn_link,
                    "title": data.get("title", "TikTok Premium Max-Bitrate Video"),
                    "thumbnail": data.get("author", {}).get("avatar", "")
                }
    except Exception as e:
        print(f"Method 1 failed, trying fallback: {e}")

    # METHOD 2: Forced High-Bitrate Bridge
    try:
        fallback_url = "https://tikwm.com/api/"
        response = requests.post(fallback_url, data={"url": tiktok_url, "hd": 1}, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                video_info = res_data["data"]
                # hdplay gives the raw uncompressed stream link
                cdn_link = video_info.get("hdplay") or video_info.get("play")
                if cdn_link:
                    if not cdn_link.startswith("http"):
                        cdn_link = "https://tikwm.com" + cdn_link
                    return {
                        "url": cdn_link,
                        "title": video_info.get("title", "TikTok Premium Video"),
                        "thumbnail": video_info.get("cover", "")
                    }
    except Exception as e:
        print(f"Method 2 failed: {e}")

    raise HTTPException(status_code=404, detail="Unable to retrieve original high-bitrate video asset.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
