"""MemV API Client for video processing and knowledge management."""

import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin


class MemVClientError(Exception):
    """Base exception for MemV client errors."""
    pass


class MemVAuthenticationError(MemVClientError):
    """Raised when API key authentication fails."""
    pass


class MemVAPIError(MemVClientError):
    """Raised when API returns an error response."""
    pass


class MemVClient:
    """
    MemV API client for accessing video processing and AI features.
    
    This client provides programmatic access to MemV's video processing,
    transcript analysis, knowledge graph search, and AI chat capabilities.
    
    Example:
        client = MemVClient("your-api-key")
        user_info = client.get_user_info()
        search_results = client.search_knowledge_graph("machine learning")
    """
    
    def __init__(self, api_key: str, base_url: str = "https://base.memv.ai"):
        """
        Initialize the MemV client.
        
        Args:
            api_key: Your MemV API key
            base_url: Base URL for the MemV API server (default: https://base.memv.ai)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API with error handling."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 401:
                raise MemVAuthenticationError("Invalid API key")
            elif response.status_code == 403:
                raise MemVAuthenticationError("Access denied")
            elif not response.ok:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                except:
                    error_detail = response.text or f"HTTP {response.status_code}"
                raise MemVAPIError(f"API error ({response.status_code}): {error_detail}")
            
            return response.json()
            
        except requests.RequestException as e:
            raise MemVClientError(f"Network error: {e}")
    
    def health_check(self) -> Dict[str, str]:
        """
        Check if the API server is healthy.
        
        Returns:
            Health status information
        """
        return self._make_request("GET", "/health")
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information based on API key.
        
        Returns:
            User information including ID, email, and account details
        """
        return self._make_request("GET", "/api/user")
    
    def get_user_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user's complete data summary including video indexes, counts, and storage.
        
        Args:
            user_id: User ID (if None, uses current user from API key)
            
        Returns:
            Complete user data including video indexes, total videos, and storage used
        """
        if user_id is None:
            user_info = self.get_user_info()
            user_id = str(user_info["id"])
        
        return self._make_request("GET", f"/api/user/{user_id}/data")
    
    def get_video_indexes(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all video indexes for a user.
        
        Args:
            user_id: User ID (if None, uses current user from API key)
            
        Returns:
            List of video indexes with metadata
        """
        if user_id is None:
            user_info = self.get_user_info()
            user_id = str(user_info["id"])
        
        return self._make_request("GET", f"/api/user/{user_id}/indexes")
    
    def get_videos(self, index_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all videos in a specific index.
        
        Args:
            index_id: Video index ID
            user_id: User ID (if None, uses current user from API key)
            
        Returns:
            List of videos with full metadata, transcripts, and analysis
        """
        if user_id is None:
            user_info = self.get_user_info()
            user_id = str(user_info["id"])
        
        return self._make_request("GET", f"/api/user/{user_id}/indexes/{index_id}/videos")
    
    def search_knowledge_graph(
        self, 
        query: str, 
        group_id: Optional[str] = None, 
        max_facts: int = 10
    ) -> Dict[str, Any]:
        """
        Search the knowledge graph for relevant facts.
        
        Args:
            query: Search query
            group_id: Optional group ID to filter results
            max_facts: Maximum number of facts to return (default: 10)
            
        Returns:
            Search results with facts and total count
        """
        payload = {
            "query": query,
            "group_id": group_id,
            "max_facts": max_facts
        }
        return self._make_request("POST", "/api/search", json=payload)
    
    def chat_with_ai(
        self, 
        messages: List[Dict[str, str]], 
        group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with AI using knowledge graph context.
        
        Args:
            messages: List of chat messages with 'role' and 'content' keys
            group_id: Optional group ID for context filtering
            
        Returns:
            AI response with content and metadata
            
        Example:
            response = client.chat_with_ai([
                {"role": "user", "content": "What can you tell me about neural networks?"}
            ])
        """
        payload = {
            "messages": messages,
            "group_id": group_id
        }
        return self._make_request("POST", "/api/chat", json=payload)
    
    def get_chat_capability(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check user's chat capabilities and enabled features.
        
        Args:
            user_id: User ID (if None, uses current user from API key)
            
        Returns:
            Information about enabled chat and search features
        """
        if user_id is None:
            user_info = self.get_user_info()
            user_id = str(user_info["id"])
        
        return self._make_request("GET", f"/api/user/{user_id}/chat")
    
    def simple_search(self, query: str, max_results: int = 5) -> List[str]:
        """
        Simple search method that returns just the fact content as strings.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 5)
            
        Returns:
            List of fact content strings
        """
        results = self.search_knowledge_graph(query, max_facts=max_results)
        return [fact.get("content", "") for fact in results.get("facts", [])]
    
    def ask(self, question: str, group_id: Optional[str] = None) -> str:
        """
        Simple method to ask a question and get a text response.
        
        Args:
            question: Question to ask
            group_id: Optional group ID for context
            
        Returns:
            AI response as a string
        """
        messages = [{"role": "user", "content": question}]
        response = self.chat_with_ai(messages, group_id)
        return response.get("content", "")