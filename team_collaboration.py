#!/usr/bin/env python3
"""
Team Collaboration Module for Code Converter
Provides basic team features like project sharing, comments, and approval workflows
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os

class UserRole(Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"

class CommentStatus(Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    REJECTED = "rejected"

@dataclass
class User:
    id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime
    last_active: datetime

@dataclass
class Project:
    id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    conversion_type: str
    source_language: str
    target_language: str
    status: str  # 'converting', 'completed', 'reviewing', 'approved'
    shared_with: List[str]  # user IDs

@dataclass
class Comment:
    id: str
    project_id: str
    user_id: str
    file_path: str
    line_number: Optional[int]
    content: str
    status: CommentStatus
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]

@dataclass
class ApprovalRequest:
    id: str
    project_id: str
    requester_id: str
    approver_id: str
    status: str  # 'pending', 'approved', 'rejected'
    created_at: datetime
    resolved_at: Optional[datetime]
    comments: str

class TeamCollaboration:
    def __init__(self, data_dir: str = "team_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files
        self.users_file = os.path.join(data_dir, "users.json")
        self.projects_file = os.path.join(data_dir, "projects.json")
        self.comments_file = os.path.join(data_dir, "comments.json")
        self.approvals_file = os.path.join(data_dir, "approvals.json")
        
        # Load existing data
        self.users = self._load_data(self.users_file, {})
        self.projects = self._load_data(self.projects_file, {})
        self.comments = self._load_data(self.comments_file, {})
        self.approvals = self._load_data(self.approvals_file, {})
    
    def _load_data(self, file_path: str, default: Any) -> Any:
        """Load data from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
        return default
    
    def _save_data(self, file_path: str, data: Any):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    
    def create_user(self, username: str, email: str, role: UserRole = UserRole.VIEWER) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        now = datetime.now()
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            created_at=now,
            last_active=now
        )
        
        self.users[user_id] = asdict(user)
        self._save_data(self.users_file, self.users)
        return user_id
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        if user_id in self.users:
            user_data = self.users[user_id]
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                role=UserRole(user_data['role']),
                created_at=datetime.fromisoformat(user_data['created_at']),
                last_active=datetime.fromisoformat(user_data['last_active'])
            )
        return None
    
    def create_project(self, name: str, description: str, owner_id: str, 
                      conversion_type: str, source_lang: str, target_lang: str) -> str:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        now = datetime.now()
        
        project = Project(
            id=project_id,
            name=name,
            description=description,
            owner_id=owner_id,
            created_at=now,
            updated_at=now,
            conversion_type=conversion_type,
            source_language=source_lang,
            target_language=target_lang,
            status='converting',
            shared_with=[owner_id]
        )
        
        self.projects[project_id] = asdict(project)
        self._save_data(self.projects_file, self.projects)
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        if project_id in self.projects:
            project_data = self.projects[project_id]
            return Project(
                id=project_data['id'],
                name=project_data['name'],
                description=project_data['description'],
                owner_id=project_data['owner_id'],
                created_at=datetime.fromisoformat(project_data['created_at']),
                updated_at=datetime.fromisoformat(project_data['updated_at']),
                conversion_type=project_data['conversion_type'],
                source_language=project_data['source_language'],
                target_language=project_data['target_language'],
                status=project_data['status'],
                shared_with=project_data['shared_with']
            )
        return None
    
    def share_project(self, project_id: str, user_id: str, role: UserRole = UserRole.VIEWER) -> bool:
        """Share a project with a user"""
        if project_id not in self.projects:
            return False
        
        project_data = self.projects[project_id]
        if user_id not in project_data['shared_with']:
            project_data['shared_with'].append(user_id)
            project_data['updated_at'] = datetime.now().isoformat()
            self._save_data(self.projects_file, self.projects)
        
        return True
    
    def add_comment(self, project_id: str, user_id: str, file_path: str, 
                   content: str, line_number: Optional[int] = None) -> str:
        """Add a comment to a project"""
        comment_id = str(uuid.uuid4())
        now = datetime.now()
        
        comment = Comment(
            id=comment_id,
            project_id=project_id,
            user_id=user_id,
            file_path=file_path,
            line_number=line_number,
            content=content,
            status=CommentStatus.PENDING,
            created_at=now,
            resolved_at=None,
            resolved_by=None
        )
        
        self.comments[comment_id] = asdict(comment)
        self._save_data(self.comments_file, self.comments)
        return comment_id
    
    def get_project_comments(self, project_id: str) -> List[Comment]:
        """Get all comments for a project"""
        comments = []
        for comment_data in self.comments.values():
            if comment_data['project_id'] == project_id:
                comment = Comment(
                    id=comment_data['id'],
                    project_id=comment_data['project_id'],
                    user_id=comment_data['user_id'],
                    file_path=comment_data['file_path'],
                    line_number=comment_data.get('line_number'),
                    content=comment_data['content'],
                    status=CommentStatus(comment_data['status']),
                    created_at=datetime.fromisoformat(comment_data['created_at']),
                    resolved_at=datetime.fromisoformat(comment_data['resolved_at']) if comment_data.get('resolved_at') else None,
                    resolved_by=comment_data.get('resolved_by')
                )
                comments.append(comment)
        
        return sorted(comments, key=lambda x: x.created_at)
    
    def resolve_comment(self, comment_id: str, user_id: str, status: CommentStatus) -> bool:
        """Resolve a comment"""
        if comment_id not in self.comments:
            return False
        
        comment_data = self.comments[comment_id]
        comment_data['status'] = status.value
        comment_data['resolved_at'] = datetime.now().isoformat()
        comment_data['resolved_by'] = user_id
        
        self._save_data(self.comments_file, self.comments)
        return True
    
    def create_approval_request(self, project_id: str, requester_id: str, 
                              approver_id: str, comments: str = "") -> str:
        """Create an approval request"""
        approval_id = str(uuid.uuid4())
        now = datetime.now()
        
        approval = ApprovalRequest(
            id=approval_id,
            project_id=project_id,
            requester_id=requester_id,
            approver_id=approver_id,
            status='pending',
            created_at=now,
            resolved_at=None,
            comments=comments
        )
        
        self.approvals[approval_id] = asdict(approval)
        self._save_data(self.approvals_file, self.approvals)
        return approval_id
    
    def approve_project(self, approval_id: str, approved: bool, comments: str = "") -> bool:
        """Approve or reject a project"""
        if approval_id not in self.approvals:
            return False
        
        approval_data = self.approvals[approval_id]
        approval_data['status'] = 'approved' if approved else 'rejected'
        approval_data['resolved_at'] = datetime.now().isoformat()
        approval_data['comments'] = comments
        
        # Update project status
        project_id = approval_data['project_id']
        if project_id in self.projects:
            self.projects[project_id]['status'] = 'approved' if approved else 'rejected'
            self.projects[project_id]['updated_at'] = datetime.now().isoformat()
            self._save_data(self.projects_file, self.projects)
        
        self._save_data(self.approvals_file, self.approvals)
        return True
    
    def get_user_projects(self, user_id: str) -> List[Project]:
        """Get all projects accessible to a user"""
        projects = []
        for project_data in self.projects.values():
            if user_id in project_data['shared_with']:
                project = Project(
                    id=project_data['id'],
                    name=project_data['name'],
                    description=project_data['description'],
                    owner_id=project_data['owner_id'],
                    created_at=datetime.fromisoformat(project_data['created_at']),
                    updated_at=datetime.fromisoformat(project_data['updated_at']),
                    conversion_type=project_data['conversion_type'],
                    source_language=project_data['source_language'],
                    target_language=project_data['target_language'],
                    status=project_data['status'],
                    shared_with=project_data['shared_with']
                )
                projects.append(project)
        
        return sorted(projects, key=lambda x: x.updated_at, reverse=True)
    
    def get_pending_approvals(self, user_id: str) -> List[ApprovalRequest]:
        """Get pending approval requests for a user"""
        approvals = []
        for approval_data in self.approvals.values():
            if (approval_data['approver_id'] == user_id and 
                approval_data['status'] == 'pending'):
                approval = ApprovalRequest(
                    id=approval_data['id'],
                    project_id=approval_data['project_id'],
                    requester_id=approval_data['requester_id'],
                    approver_id=approval_data['approver_id'],
                    status=approval_data['status'],
                    created_at=datetime.fromisoformat(approval_data['created_at']),
                    resolved_at=datetime.fromisoformat(approval_data['resolved_at']) if approval_data.get('resolved_at') else None,
                    comments=approval_data['comments']
                )
                approvals.append(approval)
        
        return sorted(approvals, key=lambda x: x.created_at, reverse=True)

# Global team collaboration instance
team_collab = TeamCollaboration()

def get_team_collaboration() -> TeamCollaboration:
    """Get the global team collaboration instance"""
    return team_collab 