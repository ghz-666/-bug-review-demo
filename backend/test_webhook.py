import json
import hmac
import hashlib
import urllib.request
secret = "local-test-secret"
payload = {
    "action": "opened",
    "pull_request": {
        "number": 12,
        "title": "fix: 修复 Token 过期问题",
        "body": "Token 过期后返回 500",
        "head": {
            "sha": "abc123"
        }
    },
    "repository": {
        "full_name": "demo/todo"
    }
}
body = json.dumps(payload).encode("utf-8")
signature = "sha256=" + hmac.new(
    secret.encode("utf-8"),
    body,
    hashlib.sha256
).hexdigest()
request = urllib.request.Request(
    url="http://127.0.0.1:8000/webhooks/git",
    data=body,
    method="POST",
    headers={
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature
    }
)
with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())
print(json.dumps(result, indent=2, ensure_ascii=False))