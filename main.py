import json
import os
import subprocess

import requests
from dotenv import load_dotenv

from utils import utils
from utils.logger import logger as log

env_file_path = ".env"
load_dotenv(dotenv_path=env_file_path)

USERNAME = os.getenv("USER_NAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SETTINGS_GLOBAL = os.getenv("SETTINGS_GLOBAL")
DESTINATION_FOLDER = os.getenv("DESTINATION_FOLDER")
BITBUCKET_WORKSPACE = os.getenv("WORKSPACE")
BITBUCKET_PROJECT_KEYS = os.getenv("BITBUCKET_PROJECT_KEYS")

format = ["json", "cvs", "yml", "yaml", "console"]


def load_configuration(file_path):
    try:
        with open(file_path, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{file_path}': {e}")
        return None


class GitRepositoryAnalyzer:

    def __init__(self, dir, project_keys, config):
        self.dir = dir
        self.since = config.get("since", None)
        self.until = config.get("until", None)
        self.silent = config.get("silent", False)
        self.show_email = config.get("show_email", False)
        self.show_total = config.get("show_total", False)
        self.branch = config.get("branch", None)
        self.loc = config.get("loc", "ins,del")
        self.M = config.get("M", False)
        self.C = config.get("C", False)
        self.format = config.get("format", "console")
        self.out_dir = config.get("out_dir", "reports")
        self.save_data = config.get("save_data", False)

    def run_project(self, project_name):
        if utils.is_subdir(self.dir, project_name):
            p_path = os.path.join(self.dir, project_name)
            repos = utils.get_subdirs(p_path)
            for r in repos:
                repo_path = os.path.join(p_path, r, "")
                stats = self.create_statistics(repo_path)
                print(stats)
        else:
            print("Error, no existing project key found")

    def run_repository(self, project_name, repo_name):
        if utils.is_subdir(self.dir, project_name, repo_name):
            repo_path = os.path.join(self.dir, project_name, repo_name, "")
            stats = self.create_statistics(repo_path)
            print(stats)
        else:
            print("Error, no existing project key found")

    def run_cli(self):
        projects = utils.get_subdirs(self.dir)

        for p in projects:
            p_path = os.path.join(self.dir, p)
            repos = utils.get_subdirs(p_path)

            for r in repos:
                repo_path = os.path.join(p_path, r, "")
                self.create_statistics(repo_path)

    def run_json(self):
        pass

    def run(self):

        data = {
            "meta": "This fiels is not used yet",
            "date": utils.get_datetime("%Y%m%d"),
            "analyzer": "git-fame @ https://github.com/casperdcl/git-fame/tree/v2.0.1",
            "parameters": {"branch": self.branch, "since": self.since, "loc": self.loc},
            "description": "Summary of developer contribution",
        }
        data["projects"] = []
        data["project_names"] = []
        data["repository_names"] = []
        repository_count = 0
        total_loc_count = 0

        projects = utils.get_subdirs(self.dir)
        for p in projects:

            p_path = os.path.join(self.dir, p)
            repos = utils.get_subdirs(p_path)
            p_data = {
                "project_name": p,
                "repositories": [],
            }
            data["project_names"].append(p)

            for r in repos:

                repo_path = os.path.join(p_path, r, "")
                # execute analyzer
                raw = self.create_statistics(repo_path)
                stats = json.loads(raw)
                r_data = {"repository_name": r, "statistics": stats}
                if stats["total"]:
                    total_loc_count += stats["total"].get("loc", 0)
                    print(total_loc_count)
                p_data["repositories"].append(r_data)
                data["repository_names"].append(r)
                repository_count += 1
            data["projects"].append(p_data)
        data["repository_count"] = repository_count
        data["total_loc"] = total_loc_count

        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)

    def create_statistics(self, repo_path, output_file=None):
        try:
            cmd = [
                "python",
                "-m",
                "git-fame.gitfame",
            ]

            if self.M:
                cmd.append("-M")

            if self.C:
                cmd.append("-C")

            if self.loc:
                cmd.append(f"--loc={self.loc}")

            if self.branch:
                cmd.append(f"--branch={self.branch}")

            if self.since:
                cmd.append(f"--since={self.since}")

            if self.until:
                cmd.append(f"--since={self.until}")

            if self.silent:
                cmd.append("-s")

            if self.show_total:
                cmd.append("--show-total")

            if self.show_email:
                cmd.append("--show-email")

            if self.format:
                cmd.extend(["--format", self.format])

            if output_file:
                cmd.extend(["--file", output_file])

            cmd.append(str(repo_path))
            log.info("Command: %s", cmd)

            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.stderr:
                log.error(f"Analyzer Error:{result.stderr}")

            # log.info("Result: %s", result.stdout)
            return result.stdout

        except subprocess.CalledProcessError as e:
            log.error(f"Process script Error: {e}")
        except json.decoder.JSONDecodeError as e:
            log.error(f"JSON decoder Error: {e}")
        except Exception as e:
            log.error(f"Unexpected Error: {e}")


class BitbucketProjectDownloader:

    def __init__(self, username, app_password, workspace, project_keys):
        self.username = username
        self.app_password = app_password
        self.workspace = workspace
        self.base_url = "https://api.bitbucket.org/2.0/repositories"
        self.project_keys = project_keys

    def fetch_repositories(self, project_key):
        repositories = []
        url = f'{self.base_url}/{self.workspace}?q=project.key="{project_key}"'

        while url:
            response = requests.get(url, auth=(self.username, self.app_password))

            # Check if the response status code is 200 (OK)
            if response.status_code == 200:
                data = response.json()
                repositories.extend(data["values"])
                url = data.get("next", None)  # Proceed to the next page if available
            elif response.status_code == 401:
                msg = f"Authentication failed: Check if the username {self.username} and app password are correct and have sufficient permissions."
                log.error(msg)
                break
            else:
                msg = f"Failed to fetch repositories: {response.status_code} - {response.text}"
                log.error(msg)
                break

        return repositories

    def pull_repository(self, repo_name, destination_folder):
        log.info("Updating %s", repo_name)

        current_path = os.getcwd()
        try:
            os.chdir(destination_folder)
            subprocess.run(["git", "pull"], check=True)
            log.info("Repository successfully updated: %s", repo_name)
        except subprocess.CalledProcessError as e:
            log.error("Failed to update repository: %s, Error: %s", repo_name, e)
        finally:
            os.chdir(current_path)

    def clone_repository(self, repo_name, clone_url, destination_folder):
        log.info("Cloning %s", repo_name)

        try:
            subprocess.run(["git", "clone", clone_url, destination_folder], check=True)
            log.info("Repository successfully cloned: %s", repo_name)
        except subprocess.CalledProcessError as e:
            log.info("Failed to clone repository: %s, Error: %s", repo_name, e)

    def fetch_all_repositories(self):
        log.info("Fetching all repositories for project keys: %s", self.project_keys)

        repositories = {}
        for project_key in self.project_keys:
            project_repositories = self.fetch_repositories(project_key)
            repositories.update({project_key: project_repositories})
        return repositories

    def clone_or_update_repository(self, repo_name, clone_url, repo_destination):
        if os.path.exists(repo_destination):
            self.pull_repository(repo_name, repo_destination)
        else:
            self.clone_repository(repo_name, clone_url, repo_destination)

    def get_all_repositories(self, destination_folder="."):

        repositories_all = self.fetch_all_repositories()
        for project_key, project_repositories in repositories_all.items():
            log.info("Looking into project key: %s", project_key)

            utils.create_dir(destination_folder)

            for repo in project_repositories:
                log.info("Found repository %s in remote storage", repo)
                repo_name = repo["name"]
                clone_url = next(
                    (
                        link["href"]
                        for link in repo["links"]["clone"]
                        if link["name"] == "https"
                    ),
                    None,
                )
                if clone_url:
                    repo_destination = os.path.join(
                        destination_folder, project_key, repo_name
                    )
                    self.clone_or_update_repository(
                        repo_name, clone_url, repo_destination
                    )


if __name__ == "__main__":

    log.info("---START PROCESSING---")
    # User inputs
    username = USERNAME
    app_password = APP_PASSWORD
    workspace = BITBUCKET_WORKSPACE
    destination_folder = DESTINATION_FOLDER
    settings_global = SETTINGS_GLOBAL

    config = load_configuration(settings_global)
    project_keys = config[BITBUCKET_PROJECT_KEYS]

    log.info("load configuration from file: %s", settings_global)
    log.info("projects loaded: %s", project_keys)
    log.info("analyzer settings loaded: %s", config["analyzer"])

    log.info("---GRABBING PROJECTS ---")

    # Initialize the downloader and clone all repositories in the project
    downloader = BitbucketProjectDownloader(
        username, app_password, workspace, project_keys
    )
    downloader.get_all_repositories(destination_folder)

    log.info("---ANALYZING PROJECTS ---")
    analyzer = GitRepositoryAnalyzer(
        destination_folder, project_keys, config["analyzer"]
    )
    analyzer.run()

    # TEST ON SINGLE PROJECT
    # analyzer.run_project("C4C")

    # TEST ON SINGLE PROJECT AND SINGLE REPO
    # analyzer.run_repository("MOS", "mos-moadmin")
