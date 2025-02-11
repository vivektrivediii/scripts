########This file is use to create simple fiel in all azuredevops repo

import requests
import base64

# Azure DevOps Configuration
ORG_NAME = "my-ai"  # Replace with your Azure DevOps org name
PAT = "1WKWGmfNAyQd9SxiS72nXoUcnc7aX6ux7SLSxf627AsfewrfdgbnfBAACAAAAAiZXJJAAASAZDOZ5Dw"  # Replace with your PAT
API_VERSION = "7.1-preview.1"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.b64encode(f":{PAT}".encode()).decode()
}

# Function to get all projects in the organization
def get_projects():
    url = f"https://dev.azure.com/{ORG_NAME}/_apis/projects?api-version={API_VERSION}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print("Error fetching projects:", response.json())
        return []

# Function to get all repositories in a given project
def get_repositories(project_id):
    url = f"https://dev.azure.com/{ORG_NAME}/{project_id}/_apis/git/repositories?api-version={API_VERSION}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Error fetching repositories for project {project_id}:", response.json())
        return []

# Function to commit a file to a repository
def commit_file(project_id, repo_name, file_path, file_content):
    # url = f"https://dev.azure.com/{ORG_NAME}/{project_id}/_apis/git/repositories/{repo_name}/pushes?api-version={API_VERSION}"
    url = f"https://dev.azure.com/{ORG_NAME}/{project_id}/_apis/git/repositories/{repo_name}/pushes?api-version=7.1-preview"

    commit_data = {
        "refUpdates": [{"name": "refs/heads/main", "oldObjectId": "0000000000000000000000000000000000000000"}],
        "commits": [{
            "comment": "Auto-created README.md",
            "changes": [{
                "changeType": "add",
                "item": {"path": f"/{file_path}"},
                "newContent": {
                    "content": file_content,
                    "contentType": "rawtext"
                }
            }]
        }]
    }

    response = requests.post(url, json=commit_data, headers=HEADERS)
    if response.status_code == 201:
        print(f"✅ Successfully created {file_path} in {repo_name}")
    else:
        print(f"❌ Failed to create {file_path} in {repo_name}: {response.json()}")

# Main function to iterate over all projects and repositories
def main():
    projects = get_projects()
    for project in projects:
        project_id = project["id"]
        project_name = project["name"]
        print(f"🔍 Checking project: {project_name} ({project_id})")

        repositories = get_repositories(project_id)
        for repo in repositories:
            repo_name = repo["name"]
            print(f"📁 Processing repo: {repo_name}")

            # File to be added
            file_path = "README.md"
            file_content = f"This is an auto-created README for {repo_name}"

            commit_file(project_id, repo_name, file_path, file_content)

# Run the script
if __name__ == "__main__":
    main()
