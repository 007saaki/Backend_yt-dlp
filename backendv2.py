from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel

app = FastAPI()

# CORS Middleware for Netlify connection
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
    return {"message": "Server is running perfectly!"}

@app.post("/fetch_data")
def fetch_data(request: DownloadRequest):
    tiktok_url = request.url
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Advanced anti-block bridge to bypass TikTok's 403 firewall
    api_url = "https://tikwm.com/api/"
    payload = {"url": tiktok_url}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.post(api_url, data=payload, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Bridge server connection failed")
            
        res_data = response.json()
        if res_data.get("code") == 0 and "data" in res_data:
            video_info = res_data["data"]
            
            # Extract the highest available raw HD link
            hd_link = video_info.get("hdplay") or video_info.get("play")
            title = video_info.get("title", "TikTok Premium Raw Video")
            cover = video_info.get("cover", "")
            
            # Matches your index.html expectations perfectly
            return {
                "url": hd_link,
                "title": title,
                "thumbnail": cover
            }
        else:
            raise HTTPException(status_code=400, detail=res_data.get("msg", "Invalid or Private TikTok URL"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
