
# 启动命令：python -m uvicorn main:app --reload
import os
import hmac
import hashlib
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
load_dotenv()
app = FastAPI()
# ==============================
# 1. GitHub 事件解析函数
# ==============================
def parse_github_event(event_type, payload):
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "")
    if not repo_name:
        return None
    # ① PR 事件
    if event_type == "pull_request":
        action = payload.get("action")
        # 过滤暂时不处理的事件动作
        if action not in (
            "opened",
            "reopened",
            "synchronize",
            "closed"
        ):
            return None
        pr = payload.get("pull_request", {})
        # PR 关闭但未合并，不作为本次修复事件处理
        if action == "closed" and not pr.get("merged", False):
            return None
        if not pr.get("number") or not pr.get("head", {}).get("sha"):
            return None
        bug_report = {
            "id": f"gh-pr-{repo_name.replace('/', '-')}-{pr['number']}",
            "title": pr.get("title", ""),
            "description": pr.get("body") or "",
            "pr_id": pr["number"],
            "commit_sha": pr["head"]["sha"],
            "repo": repo_name,
            "source_type": "pull_request",
            "action": action,
            "logs": "",
            "changed_files": []
        }
        return bug_report
    # 其他事件不处理
    return None


# ==============================
# 2. FastAPI Webhook 接口
# ==============================

@app.post("/webhooks/git")
async def github_webhook(request: Request):
    # ① 获取原始请求体
    body = await request.body()
    # ② 获取 GitHub 发送的签名
    signature = request.headers.get(
        "X-Hub-Signature-256", ""
    )

    # ③ HMAC-SHA256 签名校验
    secret = os.environ["GITHUB_WEBHOOK_SECRET"]

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=401,
            detail="签名验证失败"
        )

    # ④ 读取事件类型
    event_type = request.headers.get(
        "X-GitHub-Event", ""
    )

    # ⑤ 解析 JSON 请求体
    payload = await request.json()

    # ⑥ 调用事件解析函数
    bug_report = parse_github_event(
        event_type,
        payload
    )

    # ⑦ 判断是否需要处理
    if bug_report is None:
        return {"status": "ignored"}

    return {
        "status": "accepted",
        "bug_report": bug_report
    }
