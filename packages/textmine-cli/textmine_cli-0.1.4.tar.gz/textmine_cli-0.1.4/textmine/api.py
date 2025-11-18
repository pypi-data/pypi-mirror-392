import requests
from typing import Optional, Dict, Any, List
from . import config


class APIClient:
    """Thin client for textmine.net backend API."""
    
    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or config.get_server_url()
        self.session = requests.Session()
        
        token = config.get_session()
        if token:
            self.session.cookies.set("connect.sid", token)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to backend."""
        url = f"{self.server_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if "connect.sid" in response.cookies:
            config.save_session(response.cookies["connect.sid"])
        
        return response
    
    def register(self, username: str, password: str, invite_code: str) -> Dict[str, Any]:
        """Register new user account."""
        response = self._request("POST", "/api/register", json={
            "username": username,
            "password": password,
            "inviteCode": invite_code
        })
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to existing account."""
        response = self._request("POST", "/api/login", json={
            "username": username,
            "password": password
        })
        response.raise_for_status()
        return response.json()
    
    def logout(self) -> None:
        """Logout and destroy session."""
        try:
            self._request("POST", "/api/logout")
        finally:
            config.clear_session()
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user info."""
        response = self._request("GET", "/api/user")
        if response.status_code == 401:
            return None
        response.raise_for_status()
        return response.json()
    
    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search for users by username."""
        response = self._request("GET", "/api/users/search", params={"q": query})
        response.raise_for_status()
        return response.json()
    
    def get_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile and statistics."""
        response = self._request("GET", f"/api/profile/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """Get list of recent conversation partners."""
        response = self._request("GET", "/api/conversations")
        response.raise_for_status()
        return response.json()
    
    def get_messages(self, user_id: int, limit: int = 50, offset: int = 0, search: Optional[str] = None) -> Dict[str, Any]:
        """Get messages with another user."""
        params = {"limit": limit, "offset": offset}
        if search:
            params["q"] = search
        
        response = self._request("GET", f"/api/messages/{user_id}", params=params)
        response.raise_for_status()
        return response.json()
    
    def send_message(self, user_id: int, content: str) -> Dict[str, Any]:
        """Send message to user."""
        response = self._request("POST", f"/api/messages/{user_id}", json={
            "content": content
        })
        response.raise_for_status()
        return response.json()
    
    def update_profile(self, bio: str) -> Dict[str, Any]:
        """Update own profile bio."""
        response = self._request("PATCH", "/api/profile", json={"bio": bio})
        response.raise_for_status()
        return response.json()
