"""Conversation management for LLM core service.

Manages conversation state, history, context windows,
and message threading for LLM interactions.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manage conversation state and history.
    
    Handles message storage, context windows, conversation threading,
    and session management for LLM interactions.
    """
    
    def __init__(self, config, conversation_logger=None):
        """Initialize conversation manager.
        
        Args:
            config: Configuration manager
            conversation_logger: Optional conversation logger instance
        """
        self.config = config
        self.conversation_logger = conversation_logger
        
        # Conversation state
        self.current_session_id = str(uuid4())
        self.messages = []
        self.message_index = {}  # uuid -> message lookup
        self.context_window = []
        
        # Configuration
        self.max_history = config.get("core.llm.max_history", 50)
        self.max_context_tokens = config.get("core.llm.max_context_tokens", 4000)
        self.save_conversations = config.get("core.llm.save_conversations", True)
        
        # Conversation storage
        self.conversations_dir = Path.cwd() / ".kollabor" / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        
        # Current conversation metadata
        self.current_parent_uuid = None  # Track parent UUID for message threading
        
        self.conversation_metadata = {
            "started_at": datetime.now().isoformat(),
            "message_count": 0,
            "turn_count": 0,
            "topics": [],
            "model_used": None
        }
        
        logger.info(f"Conversation manager initialized with session: {self.current_session_id}")
    
    def add_message(self, role: str, content: str, 
                   parent_uuid: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a message to the conversation.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            parent_uuid: UUID of parent message for threading
            metadata: Optional message metadata
            
        Returns:
            UUID of the added message
        """
        message_uuid = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        # Update current_parent_uuid for next message
        if parent_uuid:
            self.current_parent_uuid = parent_uuid
        
        message = {
            "uuid": message_uuid,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "parent_uuid": parent_uuid or self.current_parent_uuid,
            "metadata": metadata or {},
            "session_id": self.current_session_id
        }
        
        # Add to messages list
        self.messages.append(message)
        self.message_index[message_uuid] = message
        
        # Update context window
        self._update_context_window()
        
        # Update metadata
        self.conversation_metadata["message_count"] += 1
        if role == "user":
            self.conversation_metadata["turn_count"] += 1
        
        # Log to conversation logger if available
        if self.conversation_logger:
            self.conversation_logger.log_message(
                role=role,
                content=content,
                parent_uuid=parent_uuid,
                metadata=metadata
            )
        
        # Auto-save if configured
        if self.save_conversations and len(self.messages) % 10 == 0:
            self.save_conversation()
        
        logger.debug(f"Added {role} message: {message_uuid}")
        return message_uuid
    
    def get_context_messages(self, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get messages for LLM context.
        
        Args:
            max_messages: Maximum number of messages to return
            
        Returns:
            List of messages for context
        """
        if max_messages:
            return self.messages[-max_messages:]
        return self.context_window
    
    def _update_context_window(self):
        """Update the context window with recent messages."""
        # Simple sliding window for now
        # TODO: Implement token counting for precise context management
        self.context_window = self.messages[-self.max_history:]
        
        # Ensure we have system message if it exists
        system_messages = [m for m in self.messages if m["role"] == "system"]
        if system_messages and system_messages[0] not in self.context_window:
            # Prepend system message
            self.context_window = [system_messages[0]] + self.context_window
    
    def _get_last_message_uuid(self) -> Optional[str]:
        """Get UUID of the last message."""
        if self.messages:
            return self.messages[-1]["uuid"]
        return None
    
    def get_message_thread(self, message_uuid: str) -> List[Dict[str, Any]]:
        """Get the thread of messages leading to a specific message.
        
        Args:
            message_uuid: UUID of the target message
            
        Returns:
            List of messages in the thread
        """
        thread = []
        current_uuid = message_uuid
        
        while current_uuid:
            if current_uuid in self.message_index:
                message = self.message_index[current_uuid]
                thread.insert(0, message)
                current_uuid = message.get("parent_uuid")
            else:
                break
        
        return thread
    
    def search_messages(self, query: str, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search messages by content.
        
        Args:
            query: Search query
            role: Optional role filter
            
        Returns:
            List of matching messages
        """
        results = []
        query_lower = query.lower()
        
        for message in self.messages:
            if role and message["role"] != role:
                continue
            
            if query_lower in message["content"].lower():
                results.append(message)
        
        return results
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation.
        
        Returns:
            Conversation summary statistics
        """
        user_messages = [m for m in self.messages if m["role"] == "user"]
        assistant_messages = [m for m in self.messages if m["role"] == "assistant"]
        
        # Extract topics from messages
        topics = self._extract_topics()
        
        summary = {
            "session_id": self.current_session_id,
            "total_messages": len(self.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "turn_count": self.conversation_metadata["turn_count"],
            "started_at": self.conversation_metadata["started_at"],
            "duration": self._calculate_duration(),
            "topics": topics,
            "average_message_length": self._calculate_avg_message_length(),
            "context_usage": f"{len(self.context_window)}/{self.max_history}"
        }
        
        return summary
    
    def _extract_topics(self) -> List[str]:
        """Extract main topics from conversation."""
        # Simple keyword extraction for now
        # TODO: Implement more sophisticated topic extraction
        topics = []
        
        # Common technical keywords to look for
        keywords = ["error", "bug", "feature", "implement", "fix", "create", 
                   "update", "delete", "configure", "install", "debug"]
        
        all_content = " ".join([m["content"] for m in self.messages])
        all_content_lower = all_content.lower()
        
        for keyword in keywords:
            if keyword in all_content_lower:
                topics.append(keyword)
        
        return topics[:5]  # Return top 5 topics
    
    def _calculate_duration(self) -> str:
        """Calculate conversation duration."""
        if not self.messages:
            return "0m"
        
        start = datetime.fromisoformat(self.messages[0]["timestamp"])
        end = datetime.fromisoformat(self.messages[-1]["timestamp"])
        duration = end - start
        
        minutes = duration.total_seconds() / 60
        if minutes < 60:
            return f"{int(minutes)}m"
        else:
            hours = minutes / 60
            return f"{hours:.1f}h"
    
    def _calculate_avg_message_length(self) -> int:
        """Calculate average message length."""
        if not self.messages:
            return 0
        
        total_length = sum(len(m["content"]) for m in self.messages)
        return total_length // len(self.messages)
    
    def save_conversation(self, filename: Optional[str] = None) -> Path:
        """Save current conversation to file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved conversation file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{self.current_session_id[:8]}_{timestamp}.json"
        
        filepath = self.conversations_dir / filename
        
        conversation_data = {
            "metadata": self.conversation_metadata,
            "summary": self.get_conversation_summary(),
            "messages": self.messages
        }
        
        with open(filepath, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        logger.info(f"Saved conversation to: {filepath}")
        return filepath
    
    def load_conversation(self, filepath: Path) -> bool:
        """Load a conversation from file.
        
        Args:
            filepath: Path to conversation file
            
        Returns:
            True if loaded successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.messages = data.get("messages", [])
            self.conversation_metadata = data.get("metadata", {})
            
            # Rebuild message index
            self.message_index = {m["uuid"]: m for m in self.messages}
            
            # Update context window
            self._update_context_window()
            
            logger.info(f"Loaded conversation from: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return False
    
    def clear_conversation(self):
        """Clear current conversation and start fresh."""
        # Save current conversation if it has messages
        if self.messages and self.save_conversations:
            self.save_conversation()
        
        # Reset state
        self.current_session_id = str(uuid4())
        self.messages = []
        self.message_index = {}
        self.context_window = []
        
        # Reset metadata
        self.current_parent_uuid = None  # Track parent UUID for message threading
        
        self.conversation_metadata = {
            "started_at": datetime.now().isoformat(),
            "message_count": 0,
            "turn_count": 0,
            "topics": [],
            "model_used": None
        }
        
        logger.info(f"Cleared conversation, new session: {self.current_session_id}")
    
    def export_for_training(self) -> List[Dict[str, str]]:
        """Export conversation in format suitable for model training.
        
        Returns:
            List of message pairs for training
        """
        training_data = []
        
        for i in range(0, len(self.messages) - 1, 2):
            if (self.messages[i]["role"] == "user" and 
                i + 1 < len(self.messages) and
                self.messages[i + 1]["role"] == "assistant"):
                
                training_data.append({
                    "instruction": self.messages[i]["content"],
                    "response": self.messages[i + 1]["content"]
                })
        
        return training_data
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get detailed conversation statistics.
        
        Returns:
            Detailed statistics about the conversation
        """
        stats = {
            "session": {
                "id": self.current_session_id,
                "started": self.conversation_metadata["started_at"],
                "duration": self._calculate_duration()
            },
            "messages": {
                "total": len(self.messages),
                "by_role": {},
                "average_length": self._calculate_avg_message_length(),
                "shortest": min((len(m["content"]) for m in self.messages), default=0),
                "longest": max((len(m["content"]) for m in self.messages), default=0)
            },
            "context": {
                "window_size": len(self.context_window),
                "max_size": self.max_history,
                "utilization": f"{(len(self.context_window) / self.max_history * 100):.1f}%"
            },
            "threading": {
                "unique_threads": len(set(m.get("parent_uuid") for m in self.messages)),
                "max_thread_depth": self._calculate_max_thread_depth()
            }
        }
        
        # Count messages by role
        for message in self.messages:
            role = message["role"]
            stats["messages"]["by_role"][role] = stats["messages"]["by_role"].get(role, 0) + 1
        
        return stats
    
    def _calculate_max_thread_depth(self) -> int:
        """Calculate maximum thread depth in conversation."""
        max_depth = 0
        
        for message in self.messages:
            depth = len(self.get_message_thread(message["uuid"]))
            max_depth = max(max_depth, depth)
        
        return max_depth