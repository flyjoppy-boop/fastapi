
import os
import time
import secrets
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Remote Lab")

# 테스트 장치의 마지막 접속 시각
last_heartbeat = 0.0

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remote Lab</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 20px;
            background: #f1f5f9;
            font-family: Arial, sans-serif;
            color: #1e293b;
        }
        main {
            max-width: 480px;
            margin: 25px auto;
        }
        h1 { font-size: 26px; margin-bottom: 5px; }
        h3 { margin-top: 0; }
        .subtitle { color: #64748b; }
        .card {
            background: white;
            padding: 22px;
            border-radius: 14px;
            margin-top: 16px;
            box-shadow: 0 2px 8px #0000000d;
        }
        .online { color: #16a34a; font-weight: bold; }
        .offline { color: #dc2626; font-weight: bold; }
        .muted { color: #64748b; }
        button {
            width: 100%;
            padding: 15px;
            background: #2563eb;
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .note { font-size: 13px; color: #64748b; }
    </style>
</head>
<body>
    <main>
        <h1>Remote Lab</h1>
        <p class="subtitle">모바일 테스트 관리 시스템</p>

        <div class="card">
            <h3>Render 서버</h3>
            <p>연결 상태: <span id="server">확인 중</span></p>
        </div>

        <div class="card">
            <h3>테스트 PC</h3>
            <p>연결 상태: <span id="pc">확인 중</span></p>
            <p class="note" id="last-seen"></p>
        </div>

        <div class="card">
            <button onclick="checkStatus()">연결 상태 새로고침</button>
            <p class="note">10초마다 자동 갱신됩니다.</p>
        </div>
    </main>

    <script>
        async function checkStatus() {
            const server = document.getElementById("server");
            const pc = document.getElementById("pc");
            const lastSeen = document.getElementById("last-seen");

            try {
                const response = await fetch("/api/status", {
                    cache: "no-store"
                });
                if (!response.ok) throw new Error("HTTP error");
                const data = await response.json();

                server.textContent = "정상 작동";
                server.className = "online";

                pc.textContent = data.pc_online ? "온라인" : "오프라인";
                pc.className = data.pc_online ? "online" : "offline";

                lastSeen.textContent = data.last_seen
                    ? "마지막 접속: " + new Date(data.last_seen).toLocaleString("ko-KR")
                    : "아직 연결된 기록이 없습니다.";
            } catch (error) {
                server.textContent = "연결 실패";
                server.className = "offline";
                pc.textContent = "확인 불가";
                pc.className = "muted";
                lastSeen.textContent = "";
            }
        }

        checkStatus();
        setInterval(checkStatus, 10000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE

@app.get("/health")
async def health():
    return {"status": "online", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/heartbeat")
async def heartbeat(x_device_token: str | None = Header(default=None)):
    global last_heartbeat

    expected_token = os.environ.get("DEVICE_TOKEN")
    if not expected_token or not x_device_token or not secrets.compare_digest(x_device_token, expected_token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    last_heartbeat = time.time()
    return {"status": "received"}

@app.get("/api/status")
async def status():
    online = last_heartbeat > 0 and time.time() - last_heartbeat < 45
    last_seen = datetime.fromtimestamp(last_heartbeat, timezone.utc).isoformat() if last_heartbeat else None
    return {"pc_online": online, "last_seen": last_seen}
