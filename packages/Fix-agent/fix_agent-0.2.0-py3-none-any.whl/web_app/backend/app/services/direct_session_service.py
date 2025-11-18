"""Direct Session management service using DirectAIAdapter."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from ..core.direct_ai_adapter import DirectAIAdapter
from ..core.config import settings
from ..models.database import Session as DBSession, Message, UploadedFile
from ..models.schemas import SessionCreate, SessionResponse


class DirectSessionService:
    """Direct session service using DirectAIAdapter."""

    def __init__(self, db: Session):
        self.db = db
        self._adapters = {}  # Cache adapters per session

    def create_session(self, session_data: SessionCreate, user_id: int = 1) -> SessionResponse:
        """Create a new session."""
        session_id = str(uuid.uuid4())

        # Create workspace directory
        workspace_path = session_data.workspace_path or f"{settings.workspace_root}/{session_id}"
        workspace = Path(workspace_path)
        workspace.mkdir(parents=True, exist_ok=True)

        # Create database record
        db_session = DBSession(
            session_id=session_id,
            user_id=user_id,
            title=session_data.title,
            workspace_path=str(workspace),
            is_active=True
        )

        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        # Initialize Direct AI adapter for this session
        print(f"🔧 初始化DirectAIAdapter for session {session_id}")
        ai_adapter = DirectAIAdapter(session_id)
        self._adapters[session_id] = ai_adapter

        return self._to_response(db_session)

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get a session by ID."""
        db_session = self.db.query(DBSession).filter(
            DBSession.session_id == session_id,
            DBSession.is_active == True
        ).first()

        if db_session:
            return self._to_response(db_session)
        return None

    def get_sessions(self, user_id: int = 1, limit: int = 50) -> List[SessionResponse]:
        """Get all active sessions for a user."""
        db_sessions = self.db.query(DBSession).filter(
            DBSession.user_id == user_id,
            DBSession.is_active == True
        ).order_by(DBSession.created_at.desc()).limit(limit).all()

        return [self._to_response(db_session) for db_session in db_sessions]

    def get_ai_adapter(self, session_id: str) -> Optional[DirectAIAdapter]:
        """Get AI adapter for a session."""
        # Return cached adapter if available
        if session_id in self._adapters:
            return self._adapters[session_id]

        # Create new adapter
        db_session = self.db.query(DBSession).filter(
            DBSession.session_id == session_id,
            DBSession.is_active == True
        ).first()

        if db_session:
            print(f"🔧 创建新的DirectAIAdapter for session {session_id}")
            ai_adapter = DirectAIAdapter(session_id)
            self._adapters[session_id] = ai_adapter
            return ai_adapter

        return None

    def add_message(self, session_id: str, content: str, role: str = "user",
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[Message]:
        """Add a message to the session."""
        db_session = self.db.query(DBSession).filter(
            DBSession.session_id == session_id,
            DBSession.is_active == True
        ).first()

        if db_session:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        return None

    def get_messages(self, session_id: str, limit: int = 100) -> List[Message]:
        """Get messages for a session."""
        return self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at.asc()).limit(limit).all()

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        db_session = self.db.query(DBSession).filter(
            DBSession.session_id == session_id
        ).first()

        if db_session:
            # Mark as inactive instead of deleting
            db_session.is_active = False
            self.db.commit()

            # Remove cached adapter
            if session_id in self._adapters:
                del self._adapters[session_id]

            return True
        return False

    def update_session_title(self, session_id: str, title: str) -> bool:
        """Update session title."""
        db_session = self.db.query(DBSession).filter(
            DBSession.session_id == session_id,
            DBSession.is_active == True
        ).first()

        if db_session:
            db_session.title = title
            self.db.commit()
            return True
        return False

    def _to_response(self, db_session: DBSession) -> SessionResponse:
        """Convert database session to response model."""
        return SessionResponse(
            session_id=db_session.session_id,
            title=db_session.title,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
            workspace_path=db_session.workspace_path,
            is_active=db_session.is_active,
            message_count=len(db_session.messages) if db_session.messages else 0
        )