import json
import os
import httpx
from dotenv import load_dotenv
load_dotenv()
BASE_URL = "https://api.github.com"
async def github_get_all(repo, pr_number, resource):
    """获取 PR 的提交或文件信息，支持分页"""
    owner, repo_name = repo.split("/", 1)
    url = (
        f"{BASE_URL}/repos/{owner}/{repo_name}"
        f"/pulls/{pr_number}/{resource}?per_page=100"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    results = []
    async with httpx.AsyncClient(timeout=20) as client:
        while url:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            results.extend(response.json())
            # GitHub 有下一页时，继续请求
            url = response.links.get("next", {}).get("url")
            print(json.dumps(results, indent=2, ensure_ascii=False))
    return results
async def get_pr_commits(repo, pr_number):
    """获取 PR 的 Commit Message"""
    commits = await github_get_all(
        repo, pr_number, "commits"
    )
    return [
        {
            "sha": item["sha"],
            "message": item["commit"]["message"]
        }
        for item in commits
    ]
async def get_pr_files(repo, pr_number):
    """获取 PR 修改的文件和 Diff"""
    files = await github_get_all(
        repo, pr_number, "files"
    )
    return [
        {
            "filename": item["filename"],
            "status": item["status"],
            "patch": item.get("patch", "")
        }
        for item in files
    ]
