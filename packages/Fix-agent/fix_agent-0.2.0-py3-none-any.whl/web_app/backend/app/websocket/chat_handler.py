"""WebSocket chat handler for real-time AI communication."""

import json
import logging
from typing import Dict, Any, List

from fastapi import WebSocket, WebSocketDisconnect, Depends

from ..services.direct_session_service import DirectSessionService
from .connection_manager import manager

logger = logging.getLogger(__name__)


class ChatHandler:
    """Handles WebSocket chat communication."""

    def __init__(self, session_service: DirectSessionService):
        self.session_service = session_service

    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: int = None
    ):
        """Handle a new WebSocket connection."""
        print(f"🔗 WebSocket连接请求: session_id={session_id}")
        await manager.connect(websocket, session_id, user_id)
        print(f"✅ WebSocket已连接: session_id={session_id}")

        try:
            # Get AI adapter for this session
            ai_adapter = self.session_service.get_ai_adapter(session_id)
            if not ai_adapter:
                await manager.send_personal_message({
                    "type": "error",
                    "content": "Session not found or inactive",
                    "session_id": session_id
                }, websocket)
                return

            # Send welcome message
            await manager.send_personal_message({
                "type": "status",
                "content": "Connected to Fix Agent",
                "session_id": session_id,
                "metadata": {
                    "model": "AI Agent Ready",
                    "tools_available": True
                }
            }, websocket)

            # Handle messages
            print(f"📨 开始处理消息: session_id={session_id}")
            await self._handle_messages(websocket, session_id, ai_adapter)
            print(f"🏁 消息处理结束: session_id={session_id}")

        except Exception as e:
            logger.error(f"Error in chat handler: {e}")
            await manager.send_personal_message({
                "type": "error",
                "content": f"Internal error: {str(e)}",
                "session_id": session_id
            }, websocket)

        finally:
            manager.disconnect(websocket)

    async def _handle_messages(
        self,
        websocket: WebSocket,
        session_id: str,
        ai_adapter
    ):
        """Handle incoming WebSocket messages."""
        print(f"🔥 _handle_messages方法被调用！session_id={session_id}")
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                print(f"📥 收到原始消息: {data[:100]}...")
                message_data = json.loads(data)
                print(f"📋 解析后消息: type={message_data.get('type', 'chat')}, content={message_data.get('content', '')[:50]}...")

                message_type = message_data.get("type", "chat")

                if message_type == "chat":
                    print(f"💬 处理chat消息: session_id={session_id}")
                    await self._handle_chat_message(
                        websocket, session_id, ai_adapter, message_data
                    )
                    print(f"✅ chat消息处理完成")
                elif message_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "session_id": session_id
                    }, websocket)
                elif message_type == "memory_list":
                    await self._handle_memory_list(websocket, session_id, ai_adapter)
                elif message_type == "memory_read":
                    await self._handle_memory_read(
                        websocket, session_id, ai_adapter, message_data
                    )
                elif message_type == "memory_write":
                    await self._handle_memory_write(
                        websocket, session_id, ai_adapter, message_data
                    )
                elif message_type == "approval_response":
                    await self._handle_approval_response(
                        websocket, session_id, ai_adapter, message_data
                    )
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "content": f"Unknown message type: {message_type}",
                        "session_id": session_id
                    }, websocket)

            except WebSocketDisconnect:
                print(f"🔌 WebSocket断开连接: session_id={session_id}")
                break
            except Exception as e:
                print(f"❌ 处理消息时发生错误: {e}")
                logger.error(f"Error handling message: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "content": f"Error processing message: {str(e)}",
                    "session_id": session_id
                }, websocket)

    async def _handle_chat_message(
        self,
        websocket: WebSocket,
        session_id: str,
        ai_adapter,
        message_data: Dict[str, Any]
    ):
        """Handle chat message and stream AI response."""
        print(f"🔥 _handle_chat_message被调用！session_id={session_id}")
        content = message_data.get("content", "")
        file_references = message_data.get("file_references", [])
        print(f"📝 消息内容: {content[:50]}...")

        if not content.strip():
            await manager.send_personal_message({
                "type": "error",
                "content": "Message content cannot be empty",
                "session_id": session_id
            }, websocket)
            return

        # Save user message to database
        self.session_service.add_message(
            session_id=session_id,
            content=content,
            role="user",
            metadata={"file_references": file_references}
        )

        # Send "thinking" status
        await manager.send_personal_message({
            "type": "status",
            "content": "AI is thinking...",
            "session_id": session_id,
            "metadata": {"state": "thinking"}
        }, websocket)

        try:
            print(f"🎯 WebSocket: 开始AI流式响应，内容: {content[:50]}...")
            # Stream AI response
            full_response = ""
            chunk_count = 0
            async for chunk in ai_adapter.stream_response(content, file_references):
                chunk_count += 1
                print(f"📤 WebSocket: 收到chunk #{chunk_count}: {chunk.get('type', 'unknown')}")

                # Send chunk to client
                await manager.send_personal_message(chunk, websocket)
                print(f"📡 WebSocket: chunk已发送到客户端")

                # Collect full response for database storage
                if chunk.get("type") == "message" and chunk.get("content"):
                    full_response += chunk.get("content", "")

            # Save AI response to database
            if full_response:
                self.session_service.add_message(
                    session_id=session_id,
                    content=full_response,
                    role="assistant",
                    metadata={"streamed": True}
                )

            # Send completion status
            await manager.send_personal_message({
                "type": "status",
                "content": "Response complete",
                "session_id": session_id,
                "metadata": {"state": "complete"}
            }, websocket)

        except Exception as e:
            logger.error(f"Error in AI streaming: {e}")
            await manager.send_personal_message({
                "type": "error",
                "content": f"AI response error: {str(e)}",
                "session_id": session_id
            }, websocket)

    async def _handle_memory_list(
        self,
        websocket: WebSocket,
        session_id: str,
        ai_adapter
    ):
        """Handle memory list request."""
        try:
            memory_files = ai_adapter.get_memory_files()
            await manager.send_personal_message({
                "type": "memory_list",
                "files": memory_files,
                "session_id": session_id
            }, websocket)
        except Exception as e:
            await manager.send_personal_message({
                "type": "error",
                "content": f"Error listing memory files: {str(e)}",
                "session_id": session_id
            }, websocket)

    async def _handle_memory_read(
        self,
        websocket: WebSocket,
        session_id: str,
        ai_adapter,
        message_data: Dict[str, Any]
    ):
        """Handle memory file read request."""
        file_path = message_data.get("file_path", "")
        if not file_path:
            await manager.send_personal_message({
                "type": "error",
                "content": "File path is required",
                "session_id": session_id
            }, websocket)
            return

        try:
            content = ai_adapter.read_memory_file(file_path)
            await manager.send_personal_message({
                "type": "memory_content",
                "file_path": file_path,
                "content": content,
                "session_id": session_id
            }, websocket)
        except Exception as e:
            await manager.send_personal_message({
                "type": "error",
                "content": f"Error reading memory file: {str(e)}",
                "session_id": session_id
            }, websocket)

    async def _handle_memory_write(
        self,
        websocket: WebSocket,
        session_id: str,
        ai_adapter,
        message_data: Dict[str, Any]
    ):
        """Handle memory file write request."""
        file_path = message_data.get("file_path", "")
        content = message_data.get("content", "")

        if not file_path:
            await manager.send_personal_message({
                "type": "error",
                "content": "File path is required",
                "session_id": session_id
            }, websocket)
            return

        try:
            ai_adapter.write_memory_file(file_path, content)
            await manager.send_personal_message({
                "type": "status",
                "content": f"Memory file saved: {file_path}",
                "session_id": session_id
            }, websocket)
        except Exception as e:
            await manager.send_personal_message({
                "type": "error",
                "content": f"Error writing memory file: {str(e)}",
                "session_id": session_id
            }, websocket)
    async def _handle_approval_response(
        self,
        websocket: WebSocket,
        session_id: str,
        ai_adapter,
        message_data: Dict[str, Any]
    ):
        """Handle user approval/rejection response for tool calls."""
        approval_index = message_data.get("approval_index")
        decision = message_data.get("decision")  # 'approve' or 'reject'

        if approval_index is None or decision not in ['approve', 'reject']:
            await manager.send_personal_message({
                "type": "error",
                "content": "Invalid approval response",
                "session_id": session_id
            }, websocket)
            return

        try:
            # Get AI agent to handle approval response
            if ai_adapter and hasattr(ai_adapter, 'agent') and ai_adapter.agent:
                # Create a message to resume agent with approval decision
                from langgraph.prebuilt import HumanMessage

                # Create a human message with approval decision
                human_message = HumanMessage(
                    content=f"User has {decision}d tool operation (index: {approval_index})",
                    name="human_approver"
                )

                # Send human message to continue agent execution
                config = {
                    "configurable": {"thread_id": session_id},
                    "metadata": {"session_id": session_id, "source": "web", "approval": True},
                }

                # Resume agent execution
                async for chunk in ai_adapter.agent.stream(
                    {"messages": [human_message]},
                    stream_mode=["messages", "updates"],
                    subgraphs=True,
                    config=config,
                    durability="exit",
                ):
                    # Process streaming response
                    processed_chunk = ai_adapter._process_stream_chunk(chunk)
                    if processed_chunk:
                        await manager.send_personal_message(processed_chunk, websocket)

                # Send completion status
                await manager.send_personal_message({
                    "type": "status",
                    "content": f"Tool operation {decision}d",
                    "session_id": session_id,
                    "metadata": {"approval": True, "decision": decision}
                }, websocket)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "content": "AI agent not available for approval processing",
                    "session_id": session_id
                }, websocket)

        except Exception as e:
            logger.error(f"Error processing approval response: {e}")
            await manager.send_personal_message({
                "type": "error",
                "content": f"Error processing approval: {str(e)}",
                "session_id": session_id
            }, websocket)
