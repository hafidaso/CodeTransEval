"""
Enterprise Security Features Module
Phase 2 Implementation - Code Project Converter

This module provides role-based access control (RBAC), audit logging,
secure code scanning, and data encryption features.
"""

import os
import json
import hashlib
import hmac
import base64
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import re
from collections import defaultdict

class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserRole(Enum):
    """User roles for RBAC."""
    VIEWER = "viewer"
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class RBACManager:
    """Role-Based Access Control manager."""
    
    def __init__(self, db_path: str = "instance/security.db"):
        self.db_path = db_path
        self.users = {}
        self.roles = {}
        self.permissions = self._load_permissions()
        self._load_data()
    
    def _load_permissions(self) -> Dict[str, List[str]]:
        """Load permission definitions for each role."""
        return {
            UserRole.VIEWER: [
                'read:projects',
                'read:conversions',
                'read:results'
            ],
            UserRole.USER: [
                'read:projects',
                'read:conversions',
                'read:results',
                'create:conversions',
                'upload:files',
                'download:results'
            ],
            UserRole.DEVELOPER: [
                'read:projects',
                'read:conversions',
                'read:results',
                'create:conversions',
                'upload:files',
                'download:results',
                'modify:conversions',
                'delete:own_conversions',
                'access:api'
            ],
            UserRole.ADMIN: [
                'read:projects',
                'read:conversions',
                'read:results',
                'create:conversions',
                'upload:files',
                'download:results',
                'modify:conversions',
                'delete:conversions',
                'access:api',
                'manage:users',
                'manage:roles',
                'view:audit_logs',
                'manage:security'
            ],
            UserRole.SUPER_ADMIN: [
                'read:projects',
                'read:conversions',
                'read:results',
                'create:conversions',
                'upload:files',
                'download:results',
                'modify:conversions',
                'delete:conversions',
                'access:api',
                'manage:users',
                'manage:roles',
                'view:audit_logs',
                'manage:security',
                'system:admin',
                'manage:encryption'
            ]
        }
    
    def _load_data(self):
        """Load user and role data from storage."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.roles = data.get('roles', {})
        except Exception as e:
            logging.error(f"Error loading RBAC data: {e}")
            self.users = {}
            self.roles = {}
    
    def _save_data(self):
        """Save user and role data to storage."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump({
                    'users': self.users,
                    'roles': self.roles
                }, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving RBAC data: {e}")
    
    def create_user(self, user_id: str, username: str, email: str, 
                   role: UserRole = UserRole.USER) -> bool:
        """Create a new user with specified role."""
        try:
            if user_id in self.users:
                return False
            
            self.users[user_id] = {
                'username': username,
                'email': email,
                'role': role.value,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'active': True
            }
            
            self._save_data()
            return True
            
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return False
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user's role."""
        try:
            if user_id not in self.users:
                return False
            
            self.users[user_id]['role'] = new_role.value
            self.users[user_id]['updated_at'] = datetime.now().isoformat()
            
            self._save_data()
            return True
            
        except Exception as e:
            logging.error(f"Error updating user role: {e}")
            return False
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        try:
            if user_id not in self.users:
                return False
            
            user_role = UserRole(self.users[user_id]['role'])
            user_permissions = self.permissions.get(user_role, [])
            
            return permission in user_permissions
            
        except Exception as e:
            logging.error(f"Error checking permission: {e}")
            return False
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user."""
        try:
            if user_id not in self.users:
                return []
            
            user_role = UserRole(self.users[user_id]['role'])
            return self.permissions.get(user_role, [])
            
        except Exception as e:
            logging.error(f"Error getting user permissions: {e}")
            return []

class AuditLogger:
    """Audit logging system for compliance and security."""
    
    def __init__(self, log_path: str = "instance/audit.log"):
        self.log_path = log_path
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup audit logger."""
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger
    
    def log_event(self, user_id: str, action: str, resource: str, 
                  details: Dict[str, Any] = None, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """Log an audit event."""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'security_level': security_level.value,
                'details': details or {},
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent()
            }
            
            self.logger.info(f"AUDIT: {json.dumps(event)}")
            
        except Exception as e:
            logging.error(f"Error logging audit event: {e}")
    
    def _get_client_ip(self) -> str:
        """Get client IP address (placeholder)."""
        return "127.0.0.1"  # In real implementation, get from request
    
    def _get_user_agent(self) -> str:
        """Get user agent (placeholder)."""
        return "CodeConverter/1.0"  # In real implementation, get from request
    
    def get_audit_logs(self, start_date: datetime = None, end_date: datetime = None,
                      user_id: str = None, action: str = None) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filtering."""
        try:
            logs = []
            
            if not os.path.exists(self.log_path):
                return logs
            
            with open(self.log_path, 'r') as f:
                for line in f:
                    if 'AUDIT:' in line:
                        try:
                            # Extract JSON from log line
                            json_str = line.split('AUDIT: ')[1].strip()
                            log_entry = json.loads(json_str)
                            
                            # Apply filters
                            if start_date and datetime.fromisoformat(log_entry['timestamp']) < start_date:
                                continue
                            if end_date and datetime.fromisoformat(log_entry['timestamp']) > end_date:
                                continue
                            if user_id and log_entry['user_id'] != user_id:
                                continue
                            if action and log_entry['action'] != action:
                                continue
                            
                            logs.append(log_entry)
                            
                        except json.JSONDecodeError:
                            continue
            
            return logs
            
        except Exception as e:
            logging.error(f"Error retrieving audit logs: {e}")
            return []

class SecureCodeScanner:
    """Secure code scanning for vulnerabilities."""
    
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.security_rules = self._load_security_rules()
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load vulnerability detection patterns."""
        return {
            'sql_injection': [
                r'execute\s*\(\s*[\'"][^\'"]*\+.*[\'"]',
                r'query\s*\(\s*[\'"][^\'"]*\+.*[\'"]',
                r'cursor\.execute\s*\(\s*[\'"][^\'"]*\+.*[\'"]',
            ],
            'xss': [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'eval\s*\(',
                r'setTimeout\s*\(\s*[\'"][^\'"]*\+.*[\'"]',
            ],
            'path_traversal': [
                r'open\s*\(\s*[\'"][^\'"]*\.\./',
                r'readFile\s*\(\s*[\'"][^\'"]*\.\./',
                r'fs\.readFile\s*\(\s*[\'"][^\'"]*\.\./',
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'exec\s*\(',
                r'child_process\.exec\s*\(',
            ],
            'weak_crypto': [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'base64\.encode\s*\(',
                r'crypto\.createHash\s*\(\s*[\'"]md5[\'"]',
            ]
        }
    
    def _load_security_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load security rules and severity levels."""
        return {
            'sql_injection': {
                'severity': SecurityLevel.CRITICAL,
                'description': 'SQL injection vulnerability detected',
                'mitigation': 'Use parameterized queries or ORM'
            },
            'xss': {
                'severity': SecurityLevel.HIGH,
                'description': 'Cross-site scripting vulnerability detected',
                'mitigation': 'Sanitize user input and use proper output encoding'
            },
            'path_traversal': {
                'severity': SecurityLevel.HIGH,
                'description': 'Path traversal vulnerability detected',
                'mitigation': 'Validate and sanitize file paths'
            },
            'command_injection': {
                'severity': SecurityLevel.CRITICAL,
                'description': 'Command injection vulnerability detected',
                'mitigation': 'Avoid executing user input as commands'
            },
            'weak_crypto': {
                'severity': SecurityLevel.MEDIUM,
                'description': 'Weak cryptographic algorithm detected',
                'mitigation': 'Use strong cryptographic algorithms (SHA-256, bcrypt)'
            }
        }
    
    def scan_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """Scan a file for security vulnerabilities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vulnerabilities = []
            
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        vulnerability = {
                            'type': vuln_type,
                            'line': content[:match.start()].count('\n') + 1,
                            'column': match.start() - content.rfind('\n', 0, match.start()),
                            'code': match.group(),
                            'severity': self.security_rules[vuln_type]['severity'].value,
                            'description': self.security_rules[vuln_type]['description'],
                            'mitigation': self.security_rules[vuln_type]['mitigation']
                        }
                        vulnerabilities.append(vulnerability)
            
            return {
                'file_path': file_path,
                'language': language,
                'vulnerabilities': vulnerabilities,
                'total_vulnerabilities': len(vulnerabilities),
                'risk_score': self._calculate_risk_score(vulnerabilities)
            }
            
        except Exception as e:
            logging.error(f"Error scanning file {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e)
            }
    
    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> int:
        """Calculate overall risk score for vulnerabilities."""
        score = 0
        severity_weights = {
            SecurityLevel.LOW: 1,
            SecurityLevel.MEDIUM: 3,
            SecurityLevel.HIGH: 7,
            SecurityLevel.CRITICAL: 10
        }
        
        for vuln in vulnerabilities:
            severity = SecurityLevel(vuln['severity'])
            score += severity_weights.get(severity, 1)
        
        return min(score, 100)  # Cap at 100
    
    def scan_project(self, project_path: str, language: str) -> Dict[str, Any]:
        """Scan entire project for security vulnerabilities."""
        try:
            project_scan = {
                'project_path': project_path,
                'language': language,
                'files_scanned': 0,
                'total_vulnerabilities': 0,
                'vulnerabilities_by_type': defaultdict(int),
                'files_with_vulnerabilities': [],
                'overall_risk_score': 0
            }
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if self._is_source_file(file, language):
                        file_path = os.path.join(root, file)
                        file_scan = self.scan_file(file_path, language)
                        
                        project_scan['files_scanned'] += 1
                        
                        if 'vulnerabilities' in file_scan:
                            project_scan['total_vulnerabilities'] += file_scan['total_vulnerabilities']
                            project_scan['overall_risk_score'] += file_scan['risk_score']
                            
                            if file_scan['vulnerabilities']:
                                project_scan['files_with_vulnerabilities'].append(file_scan)
                                
                                for vuln in file_scan['vulnerabilities']:
                                    project_scan['vulnerabilities_by_type'][vuln['type']] += 1
            
            # Normalize risk score
            if project_scan['files_scanned'] > 0:
                project_scan['overall_risk_score'] = min(
                    project_scan['overall_risk_score'] // project_scan['files_scanned'], 
                    100
                )
            
            return project_scan
            
        except Exception as e:
            logging.error(f"Error scanning project: {e}")
            return {
                'project_path': project_path,
                'error': str(e)
            }
    
    def _is_source_file(self, filename: str, language: str) -> bool:
        """Check if file is a source file for the given language."""
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'c': ['.c', '.h', '.cpp', '.hpp']
        }
        
        if language in extensions:
            return any(filename.endswith(ext) for ext in extensions[language])
        return False

class DataEncryption:
    """Data encryption for sensitive information."""
    
    def __init__(self, key_file: str = "instance/encryption.key"):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate new one."""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            logging.error(f"Error with encryption key: {e}")
            return Fernet.generate_key()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logging.error(f"Error encrypting data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logging.error(f"Error decrypting data: {e}")
            return encrypted_data
    
    def encrypt_file(self, file_path: str) -> bool:
        """Encrypt a file in place."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.cipher.encrypt(data)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            logging.error(f"Error encrypting file {file_path}: {e}")
            return False
    
    def decrypt_file(self, file_path: str) -> bool:
        """Decrypt a file in place."""
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(file_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True
            
        except Exception as e:
            logging.error(f"Error decrypting file {file_path}: {e}")
            return False

# Global instances
rbac_manager = RBACManager()
audit_logger = AuditLogger()
secure_scanner = SecureCodeScanner()
data_encryption = DataEncryption()

def get_rbac_manager():
    """Get the global RBAC manager instance."""
    return rbac_manager

def get_audit_logger():
    """Get the global audit logger instance."""
    return audit_logger

def get_secure_scanner():
    """Get the global secure code scanner instance."""
    return secure_scanner

def get_data_encryption():
    """Get the global data encryption instance."""
    return data_encryption 