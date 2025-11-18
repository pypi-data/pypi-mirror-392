from enum import Enum


class UserIdentitiesPublicControllerListUsersIdentitiesVersionControlClientType(str, Enum):
    AWS_CODECOMMIT = "AWS_CODECOMMIT"
    AZURE_REPOS = "AZURE_REPOS"
    BITBUCKET = "BITBUCKET"
    GITHUB = "GITHUB"
    GITHUB_ENTERPRISE = "GITHUB_ENTERPRISE"
    GITLAB = "GITLAB"
    GITLAB_ON_PREM = "GITLAB_ON_PREM"

    def __str__(self) -> str:
        return str(self.value)
