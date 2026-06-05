from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import re
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
    return {"message": "Premium Raw Uncompressed Engine is Live!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")

    # ENGINE 1: COBALT PREMIUM API (Returns 100% Raw Uncompressed 10MB+ High-Bitrate File)
    try:
        cobalt_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        payload = {
            "url": tiktok_url,
            "videoQuality": "max",  # Forces maximum available quality/bitrate
            "filenamePattern": "basic"
        }
        response = requests.post(cobalt_url, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            hd_link = res_data.get("url")
            if hd_link:
                return {
                    "url": hd_link,
                    "title": "TikTok Premium Max-Bitrate HD Video",
                    "thumbnail": ""
                }
    except Exception as e:
        print(f"Engine 1 (Cobalt) skipped: {e}")

    # ENGINE 2: DIRECT SSSTIK.IO SCRAPER (Pure Regex Extraction - Avoids Missing Library Crash)
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Pull page tokens
        home_res = session.get("https://ssstik.io/en", headers=headers, timeout=10)
        tt_token = "0"
        token_match = re.search(r's_tt\s*=\s*["\']([^"\']+)["\']', home_res.text)
        if token_match:
            tt_token = token_match.group(1)
        
        ajax_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "HX-Request": "true",
            "HX-Trigger": "_tt-form",
            "HX-Target": "target",
            "HX-Current-URL": "https://ssstik.io/en"
        }
        payload = {
            "id": tiktok_url,
            "locale": "en",
            "tt": tt_token
        }
        
        post_res = session.post("https://ssstik.io/abc?url=dl", data=payload, headers=ajax_headers, timeout=12)
        if post_res.status_code == 200:
            # Parse raw download urls via regex directly
            links = re.findall(r'href=["\']([^"\']+)["\']', post_res.text)
            hd_link = None
            for link in links:
                if "without_watermark" in link or "/abc/dl/" in link or "dl.ssstik" in link:
                    hd_link = link
                    break
            
            if hd_link:
                title_match = re.search(r'<p class=["\']maintext["\']>(.*?)</p>', post_res.text)
                title = title_match.group(1).strip() if title_match else "TikTok Premium Raw Video"
                return {
                    "url": hd_link,
                    "title": title,
                    "thumbnail": ""
                }
    except Exception as e:
        print(f"Engine 2 (SSSTik Scraper) skipped: {e}")

    # ENGINE 3: HIGH-BITRATE FALLBACK BRIDGE
    try:
        fallback_url = "https://tikwm.com/api/"
        response = requests.post(fallback_url, data={"url": tiktok_url, "hd": 1}, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("code") == 0 and "data" in res_data:
                video_info = res_data["data"]
                hd_link = video_info.get("hdplay") or video_info.get("play")
                if hd_link:
                    return {
                        "url": hd_link,
                        "title": video_info.get("title", "TikTok Premium Video"),
                        "thumbnail": video_info.get("cover", "")
                    }
    except Exception as e:
        print(f"Engine 3 fallback failed: {e}")

    raise HTTPException(status_code=404, detail="Unable to retrieve original high-bitrate video asset.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
