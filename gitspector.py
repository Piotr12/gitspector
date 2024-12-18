import os
import click
import requests
import pandas as pd
from datetime import datetime, timedelta
import pprint

# GitHub API base URL
API_BASE_URL = "https://api.github.com"

# GitHub authentication token (read from environment variable)
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

def get_commits(repo, weeks):
    commits = []
    since_date = datetime.now() - timedelta(weeks=weeks)
    
    # Fetch commits from all branches
    branches_url = f"{API_BASE_URL}/repos/{repo}/branches"
    response = requests.get(branches_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    branches = response.json()
    
    for branch in branches:
        branch_name = branch["name"]
        commits_url = f"{API_BASE_URL}/repos/{repo}/commits?sha={branch_name}&since={since_date.isoformat()}"
        response = requests.get(commits_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        branch_commits = response.json()
        
        for commit in branch_commits:
            commit_url = commit["url"]
            commit_response = requests.get(commit_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
            commit_data = commit_response.json()
            
            additions = commit_data.get("stats", {}).get("additions", 0)
            deletions = commit_data.get("stats", {}).get("deletions", 0)
            files_touched = len(commit_data.get("files", []))
            
            commits.append({
                "sha": commit["sha"],
                "author": commit["commit"]["author"]["name"],
                "message": commit["commit"]["message"],
                "additions": additions,
                "deletions": deletions,
                "files_touched": files_touched,
                "date": commit["commit"]["author"]["date"],
                "branch": branch_name,
                "repository": repo,
                "url": commit["html_url"]
            })
    
    return commits

def get_pull_requests(repo, weeks):
    pull_requests = []
    since_date = datetime.now() - timedelta(weeks=weeks)
    
    # Fetch closed pull requests
    pulls_url = f"{API_BASE_URL}/repos/{repo}/pulls?state=closed&sort=updated&direction=desc"
    response = requests.get(pulls_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    closed_prs = response.json()
    
    for pr in closed_prs:
        if datetime.strptime(pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ") >= since_date:
            pull_requests.append({
                "number": pr["number"],
                "title": pr["title"],
                "author": pr["user"]["login"],
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "additions": pr["additions"],
                "deletions": pr["deletions"],
                "created_at": pr["created_at"],
                "closed_at": pr["closed_at"],
                "wait_time": (datetime.strptime(pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")).days
            })
    
    return pull_requests

def generate_summary(commits, pull_requests):
    summary = {}
    
    # Count commits per author
    for commit in commits:
        author = commit["author"]
        if author not in summary:
            summary[author] = {"commits": 0, "additions": 0, "deletions": 0, "files_touched": 0, "prs": 0, "working_days": set()}
        summary[author]["commits"] += 1
        summary[author]["additions"] += commit["additions"]
        summary[author]["deletions"] += commit["deletions"]
        summary[author]["files_touched"] += commit["files_touched"]
        summary[author]["working_days"].add(commit["date"][:10])
    
    # Count pull requests per author
    for pr in pull_requests:
        author = pr["author"]
        if author not in summary:
            summary[author] = {"commits": 0, "additions": 0, "deletions": 0, "files_touched": 0, "prs": 0, "working_days": set()}
        summary[author]["prs"] += 1
    
    # Convert working days set to count
    for author in summary:
        summary[author]["working_days"] = len(summary[author]["working_days"])
    
    # Convert summary dictionary to a list of dictionaries
    summary_list = []
    for author, data in summary.items():
        data["author"] = author
        summary_list.append(data)
    
    return summary_list

@click.command()
@click.option("--repos", required=True, help="Comma-separated list of repositories")
@click.option("--weeks", type=int, default=4, help="Number of weeks to analyze")
def main(repos, weeks):
    repositories = repos.split(",")
    
    commits_data = []
    prs_data = []
    summary_data = []
    
    for repo in repositories:
        commits = get_commits(repo, weeks)
        pull_requests = get_pull_requests(repo, weeks)
        summary = generate_summary(commits, pull_requests)
        
        commits_data.extend(commits)
        prs_data.extend(pull_requests)
        summary_data.extend(summary)
    
    # Create Excel writer
    writer = pd.ExcelWriter("contributions_report.xlsx", engine="xlsxwriter")
    
    # Write commits data to Excel
    commits_df = pd.DataFrame(commits_data)
    commits_df["URL"] = '=HYPERLINK("' + commits_df["url"] + '", "View Commit")'
    commits_df.to_excel(writer, sheet_name="Commits", index=False)
    
    # Write pull requests data to Excel
    prs_df = pd.DataFrame(prs_data)
    prs_df.to_excel(writer, sheet_name="Pull Requests", index=False)
    
    # Write summary data to Excel
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    
    # Close the Excel writer
    writer.close()
    
    print("Contributions report generated successfully!")

if __name__ == "__main__":
    main() 