#!/usr/bin/env python3
"""
Git Integration Module for Code Converter
Provides Git repository integration for version control and collaboration
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import tempfile
import shutil

class GitIntegration:
    def __init__(self):
        self.git_available = self._check_git_available()
    
    def _check_git_available(self) -> bool:
        """Check if Git is available on the system"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def initialize_repository(self, project_path: str) -> bool:
        """Initialize a Git repository in the project directory"""
        if not self.git_available:
            return False
        
        try:
            subprocess.run(['git', 'init'], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def add_files(self, project_path: str, file_pattern: str = ".") -> bool:
        """Add files to Git staging area"""
        if not self.git_available:
            return False
        
        try:
            subprocess.run(['git', 'add', file_pattern], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def commit_changes(self, project_path: str, message: str) -> bool:
        """Commit changes to Git repository"""
        if not self.git_available:
            return False
        
        try:
            subprocess.run(['git', 'commit', '-m', message], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_branch(self, project_path: str, branch_name: str) -> bool:
        """Create a new Git branch"""
        if not self.git_available:
            return False
        
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def switch_branch(self, project_path: str, branch_name: str) -> bool:
        """Switch to a different Git branch"""
        if not self.git_available:
            return False
        
        try:
            subprocess.run(['git', 'checkout', branch_name], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_current_branch(self, project_path: str) -> Optional[str]:
        """Get the current Git branch name"""
        if not self.git_available:
            return None
        
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=project_path, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_branches(self, project_path: str) -> List[str]:
        """Get all Git branches"""
        if not self.git_available:
            return []
        
        try:
            result = subprocess.run(['git', 'branch', '--list'], 
                                  cwd=project_path, capture_output=True, text=True, check=True)
            branches = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Remove the asterisk and spaces from current branch
                    branch = line.strip().replace('* ', '')
                    branches.append(branch)
            return branches
        except subprocess.CalledProcessError:
            return []
    
    def get_commit_history(self, project_path: str, limit: int = 10) -> List[Dict]:
        """Get Git commit history"""
        if not self.git_available:
            return []
        
        try:
            result = subprocess.run([
                'git', 'log', f'--max-count={limit}', 
                '--pretty=format:{"hash":"%H","author":"%an","date":"%ad","message":"%s"}'
            ], cwd=project_path, capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    try:
                        commit_data = json.loads(line)
                        commits.append(commit_data)
                    except json.JSONDecodeError:
                        continue
            
            return commits
        except subprocess.CalledProcessError:
            return []
    
    def get_file_diff(self, project_path: str, file_path: str) -> Optional[str]:
        """Get the diff for a specific file"""
        if not self.git_available:
            return None
        
        try:
            result = subprocess.run(['git', 'diff', file_path], 
                                  cwd=project_path, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return None
    
    def stage_conversion_changes(self, project_path: str, conversion_type: str) -> bool:
        """Stage all changes after a conversion"""
        if not self.git_available:
            return False
        
        try:
            # Add all converted files
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            
            # Create a meaningful commit message
            commit_message = f"Convert project from {conversion_type.replace('_', ' to ')}"
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=project_path, check=True)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_conversion_branch(self, project_path: str, conversion_type: str) -> bool:
        """Create a new branch for a conversion"""
        if not self.git_available:
            return False
        
        try:
            branch_name = f"conversion/{conversion_type.replace('_', '-')}"
            subprocess.run(['git', 'checkout', '-b', branch_name], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def setup_remote_repository(self, project_path: str, remote_url: str) -> bool:
        """Set up a remote Git repository"""
        if not self.git_available:
            return False
        
        try:
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                          cwd=project_path, check=True)
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                          cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def push_changes(self, project_path: str, branch_name: str = None) -> bool:
        """Push changes to remote repository"""
        if not self.git_available:
            return False
        
        try:
            if branch_name:
                subprocess.run(['git', 'push', 'origin', branch_name], 
                              cwd=project_path, check=True)
            else:
                subprocess.run(['git', 'push'], cwd=project_path, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_pull_request(self, project_path: str, base_branch: str, 
                          feature_branch: str, title: str, description: str) -> Dict:
        """Create a pull request (GitHub/GitLab integration)"""
        # This is a placeholder for GitHub/GitLab API integration
        # In a full implementation, this would use the GitHub/GitLab API
        return {
            'success': False,
            'message': 'Pull request creation requires GitHub/GitLab API integration'
        }
    
    def get_repository_info(self, project_path: str) -> Dict:
        """Get repository information"""
        if not self.git_available:
            return {'available': False}
        
        try:
            info = {'available': True}
            
            # Get current branch
            info['current_branch'] = self.get_current_branch(project_path)
            
            # Get all branches
            info['branches'] = self.get_branches(project_path)
            
            # Get remote URL
            try:
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      cwd=project_path, capture_output=True, text=True, check=True)
                info['remote_url'] = result.stdout.strip()
            except subprocess.CalledProcessError:
                info['remote_url'] = None
            
            # Get last commit
            try:
                result = subprocess.run(['git', 'log', '-1', '--pretty=format:%H'], 
                                      cwd=project_path, capture_output=True, text=True, check=True)
                info['last_commit'] = result.stdout.strip()
            except subprocess.CalledProcessError:
                info['last_commit'] = None
            
            return info
        except Exception as e:
            return {'available': True, 'error': str(e)}
    
    def create_conversion_workflow(self, project_path: str, conversion_type: str) -> bool:
        """Create a complete Git workflow for a conversion"""
        if not self.git_available:
            return False
        
        try:
            # Create conversion branch
            branch_name = f"conversion/{conversion_type.replace('_', '-')}"
            self.create_branch(project_path, branch_name)
            
            # Stage and commit conversion changes
            self.stage_conversion_changes(project_path, conversion_type)
            
            return True
        except Exception as e:
            print(f"Error creating conversion workflow: {e}")
            return False

# Global Git integration instance
git_integration = GitIntegration()

def get_git_integration() -> GitIntegration:
    """Get the global Git integration instance"""
    return git_integration 