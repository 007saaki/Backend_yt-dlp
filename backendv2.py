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
    return {"message": "Premium Uncompressed Raw CDN Engine is Live!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")

    # ENGINE 1: DIRECT SSSTIK RAW CDN LINK EXTRACTOR (Pulls the exact 10MB+ tokcdn/tiktokcdn link)
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        # Step 1: Fetch ssstik homepage to grab the dynamic security token
        home_res = session.get("https://ssstik.io/en", headers=headers, timeout=10)
        tt_token = "0"
        token_match = re.search(r's_tt\s*=\s*["\']([^"\']+)["\']', home_res.text)
        if token_match:
            tt_token = token_match.group(1)
        
        # Step 2: Send AJAX request exactly like ssstik frontend does
        ajax_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
            # Step 3: Extract all links from the response using Regex
            raw_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', post_res.text)
            
            hd_cdn_link = None
            # Prioritize the exact raw server links (tokcdn, tiktokcdn or direct ssstik download routes)
            for link in raw_links:
                if "tokcdn" in link or "tiktokcdn" in link or "/abc/dl/" in link or "dl.ssstik" in link:
                    hd_cdn_link = link
                    break
            
            if hd_cdn_link:
                # Extract Title if available
                title_match = re.search(r'<p class=["\']maintext["\']>(.*?)</p>', post_res.text)
                video_title = title_match.group(1).strip() if title_match else "TikTok Premium Raw HD Video"
                
                return {
                    "url": hd_cdn_link,
                    "title": video_title,
                    "thumbnail": ""
                }
    except Exception as e:
        print(f"Engine 1 (Direct CDN Scraper) skipped: {e}")

    # ENGINE 2: HIGH-BITRATE BACKUP BRIDGE (In case Engine 1 has a connection timeout)
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
        print(f"Engine 2 fallback failed: {e}")

    raise HTTPException(status_code=404, detail="Unable to retrieve original high-bitrate video asset.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
