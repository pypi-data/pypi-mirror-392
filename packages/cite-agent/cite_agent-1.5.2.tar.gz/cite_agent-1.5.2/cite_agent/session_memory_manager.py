#!/usr/bin/env python3
"""
Session Memory Manager for Cite-Agent
Prevents memory leaks by archiving old conversation history and managing session state
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Tracks state for a single user session"""
    user_id: str
    conversation_id: str
    message_count: int = 0
    token_count: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_message_count: int = 0
    memory_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "message_count": self.message_count,
            "token_count": self.token_count,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "archived_message_count": self.archived_message_count,
            "memory_mb": self.memory_mb,
            "duration_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
        }


class SessionMemoryManager:
    """
    Manages conversation history memory to prevent leaks in long-running sessions

    Features:
    - Automatic archival after N messages or time threshold
    - Keeps recent context in memory (configurable window)
    - Summarizes old context for continuity
    - Tracks memory usage per session
    - Cleanup of inactive sessions
    """

    def __init__(
        self,
        max_messages_in_memory: int = 50,
        max_session_duration_hours: float = 24.0,
        archive_threshold_messages: int = 100,
        archive_threshold_hours: float = 1.0,
        recent_context_window: int = 10,
        archive_dir: Optional[Path] = None
    ):
        """
        Initialize session memory manager

        Args:
            max_messages_in_memory: Max messages to keep in memory before archiving
            max_session_duration_hours: Max session duration before forcing archive
            archive_threshold_messages: Archive when messages exceed this
            archive_threshold_hours: Archive when session exceeds this duration
            recent_context_window: Number of recent messages to keep after archival
            archive_dir: Directory for archived sessions
        """
        self.max_messages_in_memory = max_messages_in_memory
        self.max_session_duration_hours = max_session_duration_hours
        self.archive_threshold_messages = archive_threshold_messages
        self.archive_threshold_hours = archive_threshold_hours
        self.recent_context_window = recent_context_window

        # Archive directory
        if archive_dir is None:
            archive_dir = Path.home() / ".cite_agent" / "session_archives"
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Track session states
        self.sessions: Dict[str, SessionState] = {}

        # Memory usage tracking
        self.total_archived_messages = 0
        self.total_archived_sessions = 0

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        logger.info(
            f"SessionMemoryManager initialized: "
            f"max_messages={max_messages_in_memory}, "
            f"archive_threshold={archive_threshold_messages}, "
            f"recent_window={recent_context_window}"
        )

    def _get_session_key(self, user_id: str, conversation_id: str) -> str:
        """Generate unique session key"""
        return f"{user_id}:{conversation_id}"

    def register_session(self, user_id: str, conversation_id: str) -> SessionState:
        """Register a new session or get existing one"""
        key = self._get_session_key(user_id, conversation_id)

        if key not in self.sessions:
            self.sessions[key] = SessionState(
                user_id=user_id,
                conversation_id=conversation_id
            )
            logger.info(f"Registered new session: {key}")

        return self.sessions[key]

    def update_session_activity(
        self,
        user_id: str,
        conversation_id: str,
        message_count: int,
        token_count: int = 0,
        memory_mb: float = 0.0
    ):
        """Update session activity metrics"""
        session = self.register_session(user_id, conversation_id)
        session.message_count = message_count
        session.token_count += token_count
        session.last_activity = datetime.now(timezone.utc)
        session.memory_mb = memory_mb

    def should_archive(
        self,
        user_id: str,
        conversation_id: str,
        current_message_count: int
    ) -> bool:
        """
        Determine if session should be archived

        Returns True if any threshold is exceeded:
        - Message count exceeds archive_threshold_messages
        - Session duration exceeds archive_threshold_hours
        - Message count exceeds max_messages_in_memory (hard limit)
        """
        session = self.register_session(user_id, conversation_id)

        # Check message count thresholds
        if current_message_count >= self.archive_threshold_messages:
            logger.info(
                f"Session {self._get_session_key(user_id, conversation_id)} "
                f"exceeded message threshold: {current_message_count} >= {self.archive_threshold_messages}"
            )
            return True

        if current_message_count >= self.max_messages_in_memory:
            logger.warning(
                f"Session {self._get_session_key(user_id, conversation_id)} "
                f"exceeded hard memory limit: {current_message_count} >= {self.max_messages_in_memory}"
            )
            return True

        # Check duration threshold
        duration = datetime.now(timezone.utc) - session.start_time
        if duration.total_seconds() / 3600 >= self.archive_threshold_hours:
            logger.info(
                f"Session {self._get_session_key(user_id, conversation_id)} "
                f"exceeded duration threshold: {duration.total_seconds()/3600:.2f}h >= {self.archive_threshold_hours}h"
            )
            return True

        return False

    async def archive_session(
        self,
        user_id: str,
        conversation_id: str,
        conversation_history: List[Dict[str, Any]],
        keep_recent: bool = True
    ) -> Dict[str, Any]:
        """
        Archive conversation history to disk

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            conversation_history: Full conversation history
            keep_recent: If True, return recent context window for memory

        Returns:
            Dict with:
                - archived_count: Number of messages archived
                - kept_messages: Recent messages to keep in memory (if keep_recent=True)
                - archive_path: Path to archive file
                - summary: Optional summary of archived content
        """
        session = self.register_session(user_id, conversation_id)
        key = self._get_session_key(user_id, conversation_id)

        # Determine what to archive vs keep
        total_messages = len(conversation_history)

        if keep_recent and total_messages > self.recent_context_window:
            # Archive all but recent window
            to_archive = conversation_history[:-self.recent_context_window]
            to_keep = conversation_history[-self.recent_context_window:]
        else:
            # Archive everything
            to_archive = conversation_history
            to_keep = []

        archived_count = len(to_archive)

        if archived_count == 0:
            logger.info(f"No messages to archive for session {key}")
            return {
                "archived_count": 0,
                "kept_messages": to_keep,
                "archive_path": None,
                "summary": None
            }

        # Create archive file
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_filename = f"{user_id}_{conversation_id}_{timestamp}.json"
        archive_path = self.archive_dir / archive_filename

        # Prepare archive data
        archive_data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "message_count": archived_count,
            "session_info": session.to_dict(),
            "conversation_history": to_archive
        }

        # Write to disk
        try:
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Archived {archived_count} messages for session {key} to {archive_path}"
            )

            # Update session state
            session.archived_message_count += archived_count
            self.total_archived_messages += archived_count
            self.total_archived_sessions += 1

            # Generate summary of archived content
            summary = self._generate_archive_summary(to_archive)

            return {
                "archived_count": archived_count,
                "kept_messages": to_keep,
                "archive_path": str(archive_path),
                "summary": summary
            }

        except Exception as e:
            logger.error(f"Failed to archive session {key}: {e}")
            raise

    def _generate_archive_summary(self, archived_messages: List[Dict[str, Any]]) -> str:
        """
        Generate a brief summary of archived content

        This summary can be included in system prompt to maintain continuity
        """
        if not archived_messages:
            return ""

        # Count messages by role
        user_messages = [m for m in archived_messages if m.get("role") == "user"]
        assistant_messages = [m for m in archived_messages if m.get("role") == "assistant"]

        # Extract key topics (simple keyword extraction)
        # In production, could use LLM to generate better summary
        summary_parts = [
            f"[Archived {len(archived_messages)} messages: "
            f"{len(user_messages)} user, {len(assistant_messages)} assistant]"
        ]

        # Include first and last user message for context
        if user_messages:
            first_user = user_messages[0].get("content", "")[:100]
            summary_parts.append(f"Started with: {first_user}...")

            if len(user_messages) > 1:
                last_user = user_messages[-1].get("content", "")[:100]
                summary_parts.append(f"Last topic: {last_user}...")

        return " ".join(summary_parts)

    async def load_archived_session(
        self,
        user_id: str,
        conversation_id: str,
        archive_filename: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Load archived session from disk

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            archive_filename: Specific archive file, or None for most recent

        Returns:
            Archived conversation history or None if not found
        """
        key = self._get_session_key(user_id, conversation_id)

        if archive_filename:
            archive_path = self.archive_dir / archive_filename
        else:
            # Find most recent archive for this session
            pattern = f"{user_id}_{conversation_id}_*.json"
            archives = sorted(self.archive_dir.glob(pattern), reverse=True)

            if not archives:
                logger.info(f"No archives found for session {key}")
                return None

            archive_path = archives[0]

        try:
            with open(archive_path, 'r', encoding='utf-8') as f:
                archive_data = json.load(f)

            logger.info(f"Loaded archive for session {key} from {archive_path}")
            return archive_data.get("conversation_history", [])

        except Exception as e:
            logger.error(f"Failed to load archive {archive_path}: {e}")
            return None

    async def cleanup_inactive_sessions(self, inactive_threshold_hours: float = 24.0):
        """
        Remove sessions that have been inactive for too long

        Args:
            inactive_threshold_hours: Hours of inactivity before cleanup
        """
        now = datetime.now(timezone.utc)
        threshold = timedelta(hours=inactive_threshold_hours)

        to_remove = []
        for key, session in self.sessions.items():
            if now - session.last_activity > threshold:
                to_remove.append(key)

        for key in to_remove:
            del self.sessions[key]
            logger.info(f"Cleaned up inactive session: {key}")

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive sessions")

    async def start_background_cleanup(self, interval_seconds: float = 3600.0):
        """Start background task for periodic cleanup"""
        if self._running:
            logger.warning("Background cleanup already running")
            return

        self._running = True

        async def cleanup_loop():
            while self._running:
                try:
                    await asyncio.sleep(interval_seconds)
                    await self.cleanup_inactive_sessions()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info(f"Started background cleanup task (interval={interval_seconds}s)")

    async def stop_background_cleanup(self):
        """Stop background cleanup task"""
        if self._cleanup_task:
            self._running = False
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Stopped background cleanup task")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics"""
        return {
            "active_sessions": len(self.sessions),
            "total_archived_messages": self.total_archived_messages,
            "total_archived_sessions": self.total_archived_sessions,
            "archive_dir": str(self.archive_dir),
            "config": {
                "max_messages_in_memory": self.max_messages_in_memory,
                "archive_threshold_messages": self.archive_threshold_messages,
                "archive_threshold_hours": self.archive_threshold_hours,
                "recent_context_window": self.recent_context_window
            }
        }

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"SessionMemoryManager("
            f"active_sessions={len(self.sessions)}, "
            f"archived_messages={self.total_archived_messages})"
        )


# Singleton instance for easy access
_global_memory_manager: Optional[SessionMemoryManager] = None


def get_memory_manager() -> SessionMemoryManager:
    """Get global memory manager instance"""
    global _global_memory_manager

    if _global_memory_manager is None:
        # Read config from environment variables
        max_messages = int(os.getenv("CITE_AGENT_MAX_MESSAGES_IN_MEMORY", "50"))
        archive_threshold = int(os.getenv("CITE_AGENT_ARCHIVE_THRESHOLD", "100"))
        archive_hours = float(os.getenv("CITE_AGENT_ARCHIVE_HOURS", "1.0"))
        recent_window = int(os.getenv("CITE_AGENT_RECENT_CONTEXT_WINDOW", "10"))

        _global_memory_manager = SessionMemoryManager(
            max_messages_in_memory=max_messages,
            archive_threshold_messages=archive_threshold,
            archive_threshold_hours=archive_hours,
            recent_context_window=recent_window
        )

    return _global_memory_manager
