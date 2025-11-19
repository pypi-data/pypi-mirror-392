"""
LiveChat API Client - Primitive Layer
Provides direct access to LiveChat API endpoints with minimal abstraction
"""
import base64
import os
from typing import Dict, Optional

from httpx import Client as HTTPXClient
from dotenv import load_dotenv
from cachetools import TTLCache, cached

from livechat_webservice.config import Config
from livechat_webservice.logger import logger

# Load environment variables (force .env to take precedence over existing variables)
load_dotenv(override=True)


class LiveChatClient:
    """
    Primitive client for LiveChat API v3.6
    
    Provides direct endpoint access with caching but no business logic.
    Use the params module for building filters and utils module for business operations.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        access_token: str = None,
        account_id: str = None,
        base_url: str = Config.LIVECHAT_BASE_URL,
    ):
        if getattr(self, "_initialized", False):
            return

        self.access_token = access_token or os.getenv("LIVECHAT_ACCESS_TOKEN")
        self.account_id = account_id or os.getenv("LIVECHAT_ACCOUNT_ID")
        self.base_url = base_url

        if not self.access_token:
            raise ValueError("LiveChat access token required")
        
        if not self.account_id:
            raise ValueError("LiveChat account ID required")

        # Create Basic Auth credentials (account_id:PAT encoded in base64)
        credentials = f"{self.account_id}:{self.access_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Create httpx client with Basic Auth headers
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        self.client = HTTPXClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30.0,
        )

        self._initialized = True

    # ========== PRIMITIVE CHAT METHODS ==========

    @cached(cache=TTLCache(maxsize=100, ttl=1800))
    def list_chats(self, params: Dict = None) -> Dict:
        """
        List chats with optional filters
        
        Args:
            params: Filter parameters (limit, page_id, sort_order, filters, etc.)
                   Example: {'limit': 100, 'filters': {'properties': {...}}}
        
        Returns:
            API response with chats list and pagination info
        """
        try:
            payload = params or {}
            response = self.client.post(
                "/agent/action/list_chats",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error listing chats: {e}")
            return {'chats': [], 'found_chats': 0}

    @cached(cache=TTLCache(maxsize=200, ttl=3600))
    def get_chat(self, chat_id: str, thread_id: str = None) -> Dict:
        """
        Get a specific chat by ID
        
        Args:
            chat_id: Chat ID
            thread_id: Optional thread ID to get specific thread
        
        Returns:
            Complete chat data including threads and events
        """
        try:
            payload = {'chat_id': chat_id}
            if thread_id:
                payload['thread_id'] = thread_id

            response = self.client.post(
                "/agent/action/get_chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error getting chat {chat_id}: {e}")
            return {}

    @cached(cache=TTLCache(maxsize=50, ttl=86400))
    def list_archives(self, params: Dict = None) -> Dict:
        """
        List archived chats
        
        Args:
            params: Filter parameters (filters, page_id, sort_order, limit)
        
        Returns:
            API response with archived chats
        """
        try:
            payload = params or {}
            response = self.client.post(
                "/agent/action/list_archives",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error listing archives: {e}")
            return {'chats': [], 'found_chats': 0}

    # ========== PRIMITIVE THREAD TAG METHODS ==========

    def tag_thread(self, chat_id: str, thread_id: str, tag: str) -> bool:
        """
        Add a tag to a thread
        
        Args:
            chat_id: Chat ID
            thread_id: Thread ID
            tag: Tag name to add
        
        Returns:
            True if successful
        """
        try:
            payload = {
                'chat_id': chat_id,
                'thread_id': thread_id,
                'tag': tag
            }
            response = self.client.post(
                "/agent/action/tag_thread",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"✅ Tag '{tag}' added to thread {thread_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error tagging thread {thread_id}: {e}")
            return False

    def untag_thread(self, chat_id: str, thread_id: str, tag: str) -> bool:
        """
        Remove a tag from a thread
        
        Args:
            chat_id: Chat ID
            thread_id: Thread ID
            tag: Tag name to remove
        
        Returns:
            True if successful
        """
        try:
            payload = {
                'chat_id': chat_id,
                'thread_id': thread_id,
                'tag': tag
            }
            response = self.client.post(
                "/agent/action/untag_thread",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"✅ Tag '{tag}' removed from thread {thread_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error untagging thread {thread_id}: {e}")
            return False

    # ========== PRIMITIVE CUSTOMER METHODS ==========

    @cached(cache=TTLCache(maxsize=200, ttl=3600))
    def get_customer(self, customer_id: str) -> Dict:
        """
        Get customer information
        
        Args:
            customer_id: Customer ID
        
        Returns:
            Customer data
        """
        try:
            payload = {'id': customer_id}
            response = self.client.post(
                "/agent/action/get_customer",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error getting customer {customer_id}: {e}")
            return {}

    # ========== UTILITY METHODS ==========

    def test_connection(self) -> bool:
        """Test the connection to LiveChat API"""
        try:
            result = self.list_chats({'limit': 1})
            if result and 'chats' in result:
                logger.info("✅ LiveChat API connection successful")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error connecting to LiveChat API: {e}")
            return False