import os
import sys
import json
import time
import asyncio
import pprint
import pickle
import requests
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

import rookiepy
import browser_cookie3
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from playwright.async_api import async_playwright

# ========== CẤU HÌNH ==========
CURRENT_DIR = Path(__file__).resolve().parent
COOKIE_DOMAIN = "thanhtoanhocphi.epu.edu.vn"
COOKIE_FILE = CURRENT_DIR / "cookies.json"
RESPONSE_HTML_FILE = CURRENT_DIR / "response_preview.html"
POST_URL = f"https://{COOKIE_DOMAIN}/SinhVien/GetDanhSachLichTheoTuan"
CREDENTIALS_FILE = Path(f"{CURRENT_DIR}/credentials.json")
TOKEN_FILE = Path("token.pickle")

# Load biến môi trường từ file .env
load_dotenv(dotenv_path=CURRENT_DIR / ".env")


# ========== COOKIE HANDLING ==========
def is_cookie_expired(cookie):
    return cookie.get("expires", time.time() + 1000) < time.time()

def validate_cookies(cookies):
    auth_cookie = next((c for c in cookies if c["name"] == "ASC.AUTH"), None)
    if not auth_cookie:
        print("⚠️ Không tìm thấy cookie ASC.AUTH.")
        sys.exit(1)
    if is_cookie_expired(auth_cookie):
        print("⚠️ Cookie ASC.AUTH đã hết hạn.")
        COOKIE_FILE.unlink(missing_ok=True)
        sys.exit(1)
    print("✅ Cookie ASC.AUTH còn hiệu lực.")

def get_cookies_from_browser():
    print("📥 Đang lấy cookies từ trình duyệt...")
    browsers = [browser_cookie3.chrome, rookiepy.edge, rookiepy.firefox]
    for browser_func in browsers:
        try:
            if browser_func == browser_cookie3.chrome:
                raw = browser_func(domain_name=COOKIE_DOMAIN)
                cookies = [{"name": c.name, "value": c.value, "expires": c.expires} for c in raw]
            else:
                raw = browser_func([COOKIE_DOMAIN])
                cookies = [{"name": c["name"], "value": c["value"], "expires": c["expires"]} for c in raw]
            if any(c["name"] == "ASC.AUTH" for c in cookies):
                json.dump(cookies, open(COOKIE_FILE, "w", encoding="utf-8"), indent=2)
                print(f"✅ Cookies đã lưu vào {COOKIE_FILE}")
                return cookies
        except Exception as e:
            print(f"⚠️ Lỗi với {browser_func.__name__}: {e}")
    print("❌ Không tìm thấy cookie hợp lệ.")
    sys.exit(1)

def load_cookie_string():
    if not COOKIE_FILE.exists():
        cookies = get_cookies_from_browser()
    else:
        cookies = json.load(open(COOKIE_FILE, "r", encoding="utf-8"))
    validate_cookies(cookies)
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)


# ========== REQUEST & LƯU HTML ==========
def get_next_week_date():
    return (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")

def send_post_request(cookie_string):
    headers = {
        "cookie": cookie_string,
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        "referer": f"https://{COOKIE_DOMAIN}/lich-theo-tuan.html"
    }
    data = {"pNgayHienTai": get_next_week_date()}
    print("🚀 Đang gửi POST request...")
    resp = requests.post(POST_URL, headers=headers, data=data)
    print("✅ Status Code:", resp.status_code)

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        pprint.pprint(resp.json(), depth=3)
    elif "text/html" in content_type:
        html = resp.text
        RESPONSE_HTML_FILE.write_text(get_styles() + html, encoding="utf-8")
        print(f"✅ Đã lưu HTML: {RESPONSE_HTML_FILE}")
    else:
        print("📦 Nội dung không xác định:", resp.text[:500])
    return resp

def get_styles():
    # (Bạn có thể chuyển đoạn CSS trong file gốc vào đây)
    return """
            <style>
              .fl-table .content.color-lichhoc {
                  background-color: #e7ecf0;
                  border: 1px solid #c9d0db;
              }
              .fl-table .content {
                  background-color: #fdff9a;
                  border: 1px solid #edaf00;
                  color: #003763;
                  padding: 5px;
                  margin-bottom: 5px;
                  font-size: 13px;
                  border-radius: 4px !important;
                  position: relative;
              }
              .fl-table {
                  border-collapse: collapse;
                  width: 100%;
                  font-size: 14px;
                  background: #fff;
                  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
              }
              .fl-table th, .fl-table td {
                  border: 1px solid #e0e0e0;
                  padding: 12px 8px;
                  text-align: center;
                  vertical-align: middle;
              }
              .fl-table thead th {
                  background: #f5f7fa;
                  color: #333;
                  font-weight: 600;
              }
              .fl-table tbody tr:nth-child(even) {
                  background: #f9f9f9;
              }
              .fl-table tbody tr:hover td {
                  background: #e6f7ff;
                  transition: background 0.2s;
              }
              .fl-table td[lang] b {
                  color: #397fae;
                  font-size: 15px;
              }

              /* Responsive table */
              @media (max-width: 768px) {
                  .table-responsive {
                      overflow-x: auto;
                  }
                  .fl-table th, .fl-table td {
                      padding: 8px 4px;
                      font-size: 12px;
                  }
              }

              /* Legend styling */
              .tableGC {
                  margin-top: 18px;
                  background: #f5f7fa;
                  border-radius: 8px;
                  padding: 12px 18px;
                  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
                  max-width: 500px;
              }
              .tableGC ul {
                  list-style: none;
                  padding: 0;
                  margin: 0;
                  display: flex;
                  flex-wrap: wrap;
                  gap: 12px;
              }
              .tableGC li {
                  display: flex;
                  align-items: center;
                  margin-bottom: 6px;
                  min-width: 180px;
              }
              .colorSTLichHoc, .colorSTLichThi, .colorSTTamNgung {
                  display: inline-block;
                  width: 18px;
                  height: 18px;
                  border-radius: 4px;
                  margin-right: 8px;
                  background: #c9d0db;
                  border: 2px solid #e8ffe1;
              }
              .colorSTLichThi {
                  background: #fdff9a;
                  border-color: #edaf00;
              }
              .colorSTTamNgung {
                  background: linear-gradient(#f14f3f 0, #cb4335 100%);
                  border-color: #c0392b;
              }
              .tableGC label {
                  font-size: 13px;
                  color: #444;
                  margin-bottom: 0;
              }
            </style>
            """


# ========== CHỤP ẢNH ==========
def get_week_range_filename():
    start = (datetime.now() + timedelta(days=7)).replace(hour=0, minute=0, second=0)
    start = start - timedelta(days=start.weekday())
    end = start + timedelta(days=6)
    return CURRENT_DIR / f"{start:%d-%m-%Y}-{end:%d-%m-%Y}.png"

async def html_to_image(html_file, output_image):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{html_file}")
        await page.screenshot(path=output_image, full_page=True)
        await browser.close()
        print(f"✅ Đã lưu ảnh: {output_image}")


# ========== UPLOAD GOOGLE DRIVE ==========
def upload_to_drive(file_path, file_name=None, folder_id=None):
    creds = None
    if TOKEN_FILE.exists():
        creds = pickle.load(open(TOKEN_FILE, 'rb'))
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/drive.file'])
            creds = flow.run_local_server(port=0)
        pickle.dump(creds, open(TOKEN_FILE, 'wb'))

    service = build('drive', 'v3', credentials=creds)
    file_metadata = {"name": file_name or os.path.basename(file_path)}
    if folder_id:
        file_metadata["parents"] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    print(f"✅ File đã upload: {uploaded.get('webViewLink')}")


# ========== MAIN ==========
def main():
    cookie_string = load_cookie_string()
    send_post_request(cookie_string)
    image_path = get_week_range_filename()
    asyncio.run(html_to_image(RESPONSE_HTML_FILE, image_path))
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")  # lấy từ .env
    upload_to_drive(image_path, folder_id=GOOGLE_DRIVE_FOLDER_ID)

if __name__ == "__main__":
    main()
