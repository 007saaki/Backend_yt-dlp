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
    return {"message": "Premium Uncompressed Master HD Engine is Live!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://lovetik.com/"
    }

    # ENGINE 1: LOVETIK UNCOMPRESSED HD EXTRACTOR (Pulls the exact 10MB+ Master Asset File)
    try:
        api_url = "https://lovetik.com/api/ajax/search"
        payload = {"query": tiktok_url}
        
        response = requests.post(api_url, data=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            
            if res_data.get("status") == "ok":
                links = res_data.get("links", [])
                hd_link = None
                
                # First, try to grab the absolute highest quality HD option available
                for link in links:
                    if "hd" in link.get("t", "").lower():
                        hd_link = link.get("a")
                        break
                
                # If separate HD tag isn't found, pick the main watermark-less master stream
                if not hd_link and links:
                    hd_link = links[0].get("a")
                
                if hd_link:
                    return {
                        "url": hd_link,
                        "title": res_data.get("title", "TikTok Premium Master HD Video"),
                        "thumbnail": res_data.get("cover", "")
                    }
    except Exception as e:
        print(f"Engine 1 failed, trying backup engine... Error: {e}")

    # ENGINE 2: TIKWM PREMIUM HIGH-BITRATE BRIDGE (FALLBACK)
    try:
        fallback_url = "https://tikwm.com/api/"
        response = requests.post(fallback_url, data={"url": tiktok_url, "hd": 1}, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                video_info = res_data["data"]
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
        print(f"Engine 2 failed: {e}")

    raise HTTPException(status_code=404, detail="Unable to retrieve original high-bitrate video asset.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
