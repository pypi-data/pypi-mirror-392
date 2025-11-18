import requests
import zipfile
import os
from io import BytesIO
import re

class fdtGit:
    def set_github(self, repo_owner="", repo_name="", branch="", folder_prefix="", github_token=""):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.folder_prefix = folder_prefix
        self.github_token = github_token

    def download_folder_as_zip(self, repo_owner, repo_name, output_zip, branch="main", folder_to_extract="src",  folder_prefix = "", github_token = ""):
        # Construct the URL for the GitHub API to download the repository as a zip file
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/zipball/{branch}"
        headers = None

        if github_token is not None and github_token != "":
        # Replace with your actual GitHub token
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        folder_to_extract = f"/{folder_to_extract}" if folder_to_extract[0] != "/" else folder_to_extract
        
        # Ensure the directory for the output zip file exists
        os.makedirs(os.path.dirname(output_zip), exist_ok=True)
        
        # Create a zip file in memory
        with zipfile.ZipFile(BytesIO(response.content)) as zipf:
            with zipfile.ZipFile(output_zip, 'w') as output_zipf:
                for file_info in zipf.infolist():
                    parts = file_info.filename.split('/')
                    if  re.sub(r'^.*?/', '/', file_info.filename).startswith(folder_to_extract): 
                        # Extract only the specified folder
                        file_data = zipf.read(file_info.filename)  
                        if folder_prefix != "":
                            for remove_folder_prefix_folder in folder_prefix.split('/'):
                                parts.remove(remove_folder_prefix_folder)
                        output_zipf.writestr(('/'.join(parts[1:])), file_data)

    def uncompress_zip_to_folder(self, zip_path, extract_to):
        # Ensure the directory for extraction exists
        os.makedirs(extract_to, exist_ok=True)
        
        # Uncompress all files from the zip into the specified folder
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Delete the original zip file
        os.remove(zip_path)