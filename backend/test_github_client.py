
import asyncio

from github_client import get_pr_commits, get_pr_files


async def main():
    repo = "ghz-666/-bug-review-demo"
    pr_number = 2
    commits = await get_pr_commits(repo, pr_number)
    files = await get_pr_files(repo, pr_number)
    print("========== Commit 信息 ==========")
    for commit in commits:
        print("SHA:", commit["sha"])
        print("Message:", commit["message"])

    print("\n========== PR 文件变更 ==========")

    for file in files:
        print("文件:", file["filename"])
        print("状态:", file["status"])
        print("Diff:")
        print(file["patch"][:1500])
        print("-" * 40)


asyncio.run(main())
