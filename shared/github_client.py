import requests
from github import Github


class GitHubClient:
    def __init__(self, token: str, repo: str):
        self._token = token
        self._gh = Github(token)
        self._repo = self._gh.get_repo(repo)

    def get_pr_diff(self, pr_number: int) -> str:
        pr = self._repo.get_pull(pr_number)
        resp = requests.get(
            pr.url,
            headers={
                "Authorization": f"token {self._token}",
                "Accept": "application/vnd.github.v3.diff",
            },
        )
        resp.raise_for_status()
        return resp.text

    def post_review(
        self,
        pr_number: int,
        body: str,
        comments: list[dict],
    ) -> None:
        pr = self._repo.get_pull(pr_number)
        pr.create_review(
            body=body,
            event="COMMENT",
            comments=comments,
        )
