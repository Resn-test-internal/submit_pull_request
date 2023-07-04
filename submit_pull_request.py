import base64
import json
import os
import re
import sys

from github import Github

GITHUB_ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']
GITHUB_REF = os.environ['GITHUB_REF']
GITHUB_REPOSITORY = os.environ['GITHUB_REPOSITORY']
GITHUB_ACTOR = os.environ['GITHUB_ACTOR']

ASSIGN = os.environ['ASSIGN'].lower() == "true" if "ASSIGN" in os.environ else True
AUTHORS = os.environ['AUTHORS'] if "AUTHORS" in os.environ else "{}"
CAN_BOT_MAKE_PR = os.environ['CAN_BOT_MAKE_PR'].lower() == "true" if "CAN_BOT_MAKE_PR" in os.environ else True
DEBUG = os.environ['DEBUG'].lower() == "true" if "DEBUG" in os.environ else False
DRAFT = os.environ['DRAFT'].lower() == "true" if "DRAFT" in os.environ else False
LABEL = [x.strip() for x in os.environ['LABEL'].split(',')] if "LABEL" in os.environ else []
LABEL_SAME_AS_ISSUE = os.environ['LABEL_SAME_AS_ISSUE'].lower() == "true" if "LABEL_SAME_AS_ISSUE" in os.environ else True
MILESTONE_SAME_AS_ISSUE = os.environ['MILESTONE_SAME_AS_ISSUE'].lower() == "true" if "MILESTONE_SAME_AS_ISSUE" in os.environ else True
TEMPLATE_FILE_PATH = os.environ['TEMPLATE_FILE_PATH'] if "TEMPLATE_FILE_PATH" in os.environ else ".github/pull_request_template.md"


class SubmitPullRequest():
    def __init__(self):
        self.branch = self.parse_branch()
        self.repo = Github(self.get_access_token()).get_repo(GITHUB_REPOSITORY)
        self.pr_body = self.build_pr_body()
        self.pr = self.create_pull_request()
        self.add_label_to_pull_request()
        self.add_assignees_to_pull_request()

    def add_assignees_to_pull_request(self):
        try:
            if ASSIGN:
                self.pr.add_to_assignees(GITHUB_ACTOR)
        except:
            self.error_handler("Failed to add assignees to pull request")

    def add_label_to_pull_request(self):
        try:
            for label in (set(LABEL) & set([x.name for x in self.repo.get_labels()])):
                self.pr.add_to_labels(label)
        except:
            self.error_handler("Failed to add label to pull request")

    def build_pr_body(self):
        return self.get_template_content()

    def create_pull_request(self):
        try:
            title = self.branch
            pr = self.repo.create_pull(
                title=title,
                body=self.pr_body,
                head=GITHUB_REF,
                base=self.repo.default_branch,
                draft=DRAFT)
            return pr
        except:
            self.error_handler("Failed to create pull request")
    
    def error_handler(self, message):
        print('\033[31m' + message + '\033[0m')
        raise Exception

    def get_access_token(self):
        try:
            authors_json = json.loads(AUTHORS)
            if GITHUB_ACTOR in authors_json:
                return authors_json[GITHUB_ACTOR]
        except:
            pass
        if CAN_BOT_MAKE_PR:
            return GITHUB_ACCESS_TOKEN
        else:
            self.error_handler("Bots cannot make PR")

    def get_template_content(self):
        try:
            contents = self.repo.get_contents(TEMPLATE_FILE_PATH)
            contents = base64.b64decode(contents.content).decode('utf8', 'ignore')
            return contents
        except:
            return ''

    def message_handler(self, message):
        print('\033[32m' + message + '\033[0m')
        sys.exit()

    def parse_branch(self):
        branch = re.sub(r'^([^\/]+\/){2}', "", GITHUB_REF)
        return branch


class IssueMock:
    number = 0
    title = 'temporary title'
    labels = []
    milestone = ''


if __name__ == '__main__':
    SubmitPullRequest()
