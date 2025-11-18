"""Direct AI Adapter using copied CLI modules."""

import asyncio
import json
import logging
import os
from typing import Dict, Any, AsyncGenerator, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DirectAIAdapter:
    """Direct AI adapter that uses copied CLI modules for proper streaming."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.agent = None
        self.model = None
        self.memory_dir = Path("workspaces") / session_id / "memories"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Try to import and initialize CLI components
        self._initialize_cli_components()

    def _initialize_cli_components(self):
        """Initialize CLI components directly."""
        try:
            # Add CLI directory to path as the highest priority
            import sys
            cli_path = Path(__file__).parent.parent.parent / "cli"
            if str(cli_path) not in sys.path:
                sys.path.insert(0, str(cli_path))

            # Add parent directories to sys.path to handle imports
            parent_path = Path(__file__).parent.parent.parent
            if str(parent_path) not in sys.path:
                sys.path.insert(0, str(parent_path))

            # Add original Fix Agent src directory to path (not web_app/src)
            src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))

            # Set environment to disable relative imports
            os.environ["CLI_DIRECT_MODE"] = "1"

            print(f"🔧 添加路径到sys.path:")
            print(f"   CLI路径: {cli_path}")
            print(f"   父路径: {parent_path}")
            print(f"   SRC路径: {src_path}")

            # Now use standard imports - the CLI modules should be importable
            # Import CLI modules as if they were in the Python path
            import cli.agents.agent as agents_module
            import cli.config.config as config_module
            import cli.tools.tools as tools_module

            create_agent_with_config = agents_module.create_agent_with_config
            create_model = config_module.create_model
            get_all_tools = tools_module.get_all_tools

            print(f"✅ 成功导入CLI模块")

            # Initialize model
            self.model = create_model()
            print(f"✅ 模型初始化成功")

            # Initialize tools
            tools = get_all_tools()
            print(f"✅ 工具初始化成功，共 {len(tools)} 个工具")

            # Create agent
            self.agent = create_agent_with_config(
                model=self.model,
                assistant_id=self.session_id,
                tools=tools,
                memory_mode="hybrid"
            )

            print(f"✅ Direct AI Adapter initialized for session {self.session_id}")

        except Exception as e:
            print(f"❌ Failed to initialize CLI components: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to initialize CLI components: {e}")
            self.agent = None
            self.model = None

    async def stream_response(self, message: str, file_references: List[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream AI response using direct CLI agent."""
        print(f"🔥 Direct AI Adapter: stream_response called with message: {message[:50]}...")

        if not self.agent:
            yield {
                "type": "error",
                "content": "AI Agent not initialized",
                "session_id": self.session_id
            }
            return

        # Send thinking status
        yield {
            "type": "status",
            "content": "AI正在思考...",
            "session_id": self.session_id,
            "timestamp": self._get_timestamp(),
            "metadata": {
                "state": "thinking",
                "phase": "analysis",
                "progress": 0.1,
                "details": self._get_thinking_details("analysis", message)
            }
        }

        try:
            print(f"🎯 开始调用CLI Agent流式响应...")

            # Send preparation status
            yield {
                "type": "status",
                "content": "正在准备处理请求...",
                "session_id": self.session_id,
                "timestamp": self._get_timestamp(),
                "metadata": {
                    "state": "preparing",
                    "phase": "setup",
                    "progress": 0.2,
                    "details": {"step": "正在配置AI代理和工具"}
                }
            }

            # Prepare the input for the agent
            inputs = {
                "messages": [
                    {"role": "user", "content": message}
                ]
            }

            # Configure the agent
            config = {
                "configurable": {
                    "thread_id": self.session_id,
                },
                "metadata": {
                    "session_id": self.session_id,
                    "source": "web"
                }
            }

            print(f"🚀 开始流式调用agent.stream...")

            # Send execution status
            yield {
                "type": "status",
                "content": "AI正在执行分析和推理...",
                "session_id": self.session_id,
                "timestamp": self._get_timestamp(),
                "metadata": {
                    "state": "processing",
                    "phase": "execution",
                    "progress": 0.4,
                    "details": {"step": "正在调用AI模型进行智能分析"}
                }
            }

            # Stream the response
            chunk_count = 0
            processing_started = False
            async for chunk in self.agent.stream(
                inputs,
                config=config,
                stream_mode=["messages", "updates"],
                subgraphs=True,
                durability="exit",
            ):
                chunk_count += 1
                print(f"📦 收到chunk #{chunk_count}: type={type(chunk)}, len={len(chunk) if hasattr(chunk, '__len__') else 'N/A'}")

                # First real chunk indicates processing has started
                if not processing_started and chunk_count > 1:
                    processing_started = True
                    yield {
                        "type": "status",
                        "content": "AI正在生成响应...",
                        "session_id": self.session_id,
                        "timestamp": self._get_timestamp(),
                        "metadata": {
                            "state": "generating",
                            "phase": "response",
                            "progress": 0.7,
                            "details": {"step": "正在生成智能回复"}
                        }
                    }

                # Send intermediate progress updates for longer operations
                if chunk_count % 10 == 0 and chunk_count > 0:
                    progress = min(0.7 + (chunk_count / 100) * 0.2, 0.9)
                    yield {
                        "type": "status",
                        "content": f"继续处理中... (已处理 {chunk_count} 个数据块)",
                        "session_id": self.session_id,
                        "timestamp": self._get_timestamp(),
                        "metadata": {
                            "state": "processing",
                            "phase": "streaming",
                            "progress": progress,
                            "details": {"chunks_processed": chunk_count}
                        }
                    }

                # Process the chunk and yield appropriate response
                processed_response = self._process_chunk(chunk)
                if processed_response:
                    print(f"📤 发送处理后的响应: {processed_response.get('type', 'unknown')}")
                    yield processed_response

            # Send completion status
            yield {
                "type": "status",
                "content": "响应生成完成",
                "session_id": self.session_id,
                "timestamp": self._get_timestamp(),
                "metadata": {
                    "state": "completed",
                    "phase": "finished",
                    "progress": 1.0,
                    "details": {"total_chunks": chunk_count}
                }
            }

            print(f"✅ 流式响应完成，总共处理了 {chunk_count} 个chunk")

        except Exception as e:
            print(f"❌ 流式响应出错: {e}")
            logger.error(f"Error in streaming response: {e}")
            yield {
                "type": "error",
                "content": f"AI响应出错: {str(e)}",
                "session_id": self.session_id
            }

    def _process_chunk(self, chunk) -> Optional[Dict[str, Any]]:
        """Process a chunk from the agent stream."""
        try:
            print(f"🔍 处理chunk: {type(chunk)}, content={str(chunk)[:100] if hasattr(chunk, '__str__') else 'N/A'}")

            # Handle different chunk types
            if isinstance(chunk, tuple) and len(chunk) >= 3:
                namespace, stream_mode, data = chunk[:3]
                print(f"📋 Chunk详情: namespace={namespace}, stream_mode={stream_mode}")

                if stream_mode == "messages":
                    if isinstance(data, tuple) and len(data) == 2:
                        message, metadata = data

                        # Handle message content
                        if hasattr(message, 'content'):
                            content = message.content
                            if content:
                                return {
                                    "type": "message",
                                    "content": content,
                                    "session_id": self.session_id,
                                    "is_stream": True
                                }

                        # Handle tool calls
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            tool_calls_data = []
                            for tool_call in message.tool_calls:
                                function_info = tool_call.get("function", {})
                                tool_name = function_info.get("name", "")
                                arguments = function_info.get("arguments", "")

                                # Parse arguments for better display
                                parsed_args = {}
                                try:
                                    import json
                                    if arguments:
                                        parsed_args = json.loads(arguments)
                                except:
                                    parsed_args = {"raw": arguments}

                                tool_calls_data.append({
                                    "id": tool_call.get("id", ""),
                                    "name": tool_name,
                                    "arguments": arguments,
                                    "parsed_args": parsed_args,
                                    "display_info": self._format_tool_call_display(tool_name, parsed_args)
                                })

                            return {
                                "type": "tool_call",
                                "tool_calls": tool_calls_data,
                                "session_id": self.session_id,
                                "timestamp": self._get_timestamp()
                            }

                elif stream_mode == "updates":
                    # Handle metadata updates
                    if isinstance(data, dict):
                        if "interrupt" in data:
                            # Handle user approval requests
                            interrupt_data = data["interrupt"]
                            return {
                                "type": "approval_request",
                                "approval_data": interrupt_data,
                                "session_id": self.session_id,
                                "timestamp": self._get_timestamp(),
                                "approval_info": self._format_approval_request(interrupt_data)
                            }

                        if "values" in data:
                            # Handle tool results
                            values = data["values"]
                            if isinstance(values, dict) and "messages" in values:
                                # Extract tool result content
                                for msg in values["messages"]:
                                    if hasattr(msg, 'content') and msg.content:
                                        content = str(msg.content)
                                        return {
                                            "type": "tool_result",
                                            "content": content,
                                            "session_id": self.session_id,
                                            "timestamp": self._get_timestamp(),
                                            "result_info": self._format_tool_result(content)
                                        }

            # Handle other chunk formats
            elif hasattr(chunk, 'content'):
                content = chunk.content
                if content:
                    return {
                        "type": "message",
                        "content": content,
                        "session_id": self.session_id,
                        "is_stream": True
                    }

            print(f"⚠️ 未能处理chunk格式: {type(chunk)}")
            return None

        except Exception as e:
            print(f"❌ 处理chunk时出错: {e}")
            logger.error(f"Error processing chunk: {e}")
            return None

    def get_memory_files(self) -> List[str]:
        """Get list of memory files."""
        try:
            if self.memory_dir.exists():
                return [f.name for f in self.memory_dir.rglob("*") if f.is_file()]
            return []
        except Exception as e:
            logger.error(f"Error getting memory files: {e}")
            return []

    def read_memory_file(self, file_path: str) -> str:
        """Read content from a memory file."""
        try:
            full_path = self.memory_dir / file_path
            if full_path.exists() and full_path.is_file():
                return full_path.read_text(encoding='utf-8')
            return ""
        except Exception as e:
            logger.error(f"Error reading memory file: {e}")
            return ""

    def write_memory_file(self, file_path: str, content: str):
        """Write content to a memory file."""
        try:
            full_path = self.memory_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f"Error writing memory file: {e}")

    async def handle_approval_response(self, approval_index: int, decision: str, user_id: str = None):
        """Handle user approval response for tool calls."""
        try:
            if self.agent:
                # Create a human message to resume execution
                from langchain_core.messages import HumanMessage

                human_message = HumanMessage(
                    content=f"User has {decision}d tool operation (index: {approval_index})",
                    name="human_approver"
                )

                # Resume agent execution
                config = {
                    "configurable": {"thread_id": self.session_id},
                    "metadata": {"session_id": self.session_id, "source": "web", "approval": True},
                }

                results = []
                async for chunk in self.agent.stream(
                    {"messages": [human_message]},
                    stream_mode=["messages", "updates"],
                    subgraphs=True,
                    config=config,
                    durability="exit",
                ):
                    processed = self._process_chunk(chunk)
                    if processed:
                        results.append(processed)

                return results
            else:
                raise Exception("Agent not available")

        except Exception as e:
            logger.error(f"Error handling approval response: {e}")
            raise e

    def _format_tool_call_display(self, tool_name: str, args: dict) -> dict:
        """Format tool call information for better display."""
        display_info = {
            "tool_name": tool_name,
            "description": self._get_tool_description(tool_name),
            "formatted_args": self._format_tool_args(tool_name, args),
            "risk_level": self._get_tool_risk_level(tool_name, args)
        }
        return display_info

    def _get_tool_description(self, tool_name: str) -> str:
        """Get a human-readable description for a tool."""
        descriptions = {
            "write_file": "写入文件内容",
            "edit_file": "编辑文件内容",
            "read_file": "读取文件内容",
            "bash": "执行Shell命令",
            "web_search": "网络搜索",
            "task": "调用子代理任务",
            "analyze_project": "分析项目结构",
            "explore_code": "探索代码库",
            "glob": "搜索文件模式",
            "grep": "搜索文本内容",
            "list_files": "列出文件和目录"
        }
        return descriptions.get(tool_name, f"使用工具: {tool_name}")

    def _format_tool_args(self, tool_name: str, args: dict) -> str:
        """Format tool arguments for display."""
        if tool_name == "write_file":
            file_path = args.get("file_path", "未知路径")
            content = args.get("content", "")
            lines = len(content.splitlines()) if content else 0
            return f"文件: {file_path}, 行数: {lines}"

        elif tool_name == "edit_file":
            file_path = args.get("file_path", "未知路径")
            return f"文件: {file_path}"

        elif tool_name == "bash":
            command = args.get("command", "")
            return f"命令: {command[:100]}{'...' if len(command) > 100 else ''}"

        elif tool_name == "web_search":
            query = args.get("query", "")
            max_results = args.get("max_results", 5)
            return f"查询: {query[:80]}{'...' if len(query) > 80 else ''}, 最大结果数: {max_results}"

        elif tool_name == "read_file":
            file_path = args.get("file_path", "未知路径")
            return f"文件: {file_path}"

        elif tool_name == "task":
            description = args.get("description", "")
            return f"任务: {description[:80]}{'...' if len(description) > 80 else ''}"

        else:
            # Generic formatting for other tools
            arg_list = []
            for key, value in args.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                arg_list.append(f"{key}={value}")
            return ", ".join(arg_list)

    def _get_tool_risk_level(self, tool_name: str, args: dict) -> str:
        """Determine the risk level of a tool call."""
        high_risk_tools = {"bash", "write_file", "edit_file"}
        medium_risk_tools = {"web_search", "task"}

        if tool_name in high_risk_tools:
            if tool_name == "bash" and any(dangerous in args.get("command", "").lower()
                                           for dangerous in ["rm", "sudo", "chmod", "chown", "mv"]):
                return "high"
            return "medium"
        elif tool_name in medium_risk_tools:
            return "medium"
        else:
            return "low"

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        import datetime
        return datetime.datetime.now().isoformat()

    def _format_tool_result(self, content: str) -> dict:
        """Format tool result information for better display."""
        result_info = {
            "content_length": len(content),
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "has_error": self._detect_error_in_result(content),
            "result_type": self._classify_result_type(content)
        }
        return result_info

    def _detect_error_in_result(self, content: str) -> bool:
        """Detect if the tool result contains an error."""
        error_indicators = [
            "error:", "failed", "exception", "traceback", "❌",
            "permission denied", "not found", "no such file",
            "command not found", "syntax error"
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in error_indicators)

    def _classify_result_type(self, content: str) -> str:
        """Classify the type of tool result."""
        if content.strip().startswith("```"):
            return "code"
        elif any(c in content for c in ["├", "─", "│", "└"]):
            return "tree"
        elif len(content.splitlines()) > 10:
            return "long_text"
        elif content.strip().isdigit() or content.strip().replace(".", "").isdigit():
            return "numeric"
        else:
            return "text"

    def _format_approval_request(self, interrupt_data: dict) -> dict:
        """Format approval request information for better display."""
        approval_info = {
            "title": "工具执行审批",
            "description": self._extract_approval_description(interrupt_data),
            "risk_level": self._assess_approval_risk(interrupt_data),
            "allowed_actions": self._extract_allowed_actions(interrupt_data),
            "tool_details": self._extract_tool_details(interrupt_data)
        }
        return approval_info

    def _extract_approval_description(self, interrupt_data: dict) -> str:
        """Extract and format the approval description."""
        # Try to get description from interrupt data
        if isinstance(interrupt_data, dict):
            if "description" in interrupt_data:
                return interrupt_data["description"]
            elif "tool_call" in interrupt_data:
                tool_call = interrupt_data["tool_call"]
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name", "未知工具")
                    args = tool_call.get("args", {})
                    return f"即将执行工具: {tool_name} - {self._format_tool_args(tool_name, args)}"

        # Fallback description
        return "等待用户审批工具执行"

    def _assess_approval_risk(self, interrupt_data: dict) -> str:
        """Assess the risk level of the approval request."""
        if isinstance(interrupt_data, dict) and "tool_call" in interrupt_data:
            tool_call = interrupt_data["tool_call"]
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "")
                args = tool_call.get("args", {})
                return self._get_tool_risk_level(tool_name, args)
        return "medium"

    def _extract_allowed_actions(self, interrupt_data: dict) -> list:
        """Extract allowed actions from interrupt data."""
        if isinstance(interrupt_data, dict) and "allowed_decisions" in interrupt_data:
            return interrupt_data["allowed_decisions"]
        return ["approve", "reject"]

    def _extract_tool_details(self, interrupt_data: dict) -> dict:
        """Extract detailed tool information for approval display."""
        tool_details = {}

        if isinstance(interrupt_data, dict) and "tool_call" in interrupt_data:
            tool_call = interrupt_data["tool_call"]
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "")
                args = tool_call.get("args", {})

                tool_details = {
                    "name": tool_name,
                    "description": self._get_tool_description(tool_name),
                    "formatted_args": self._format_tool_args(tool_name, args),
                    "risk_level": self._get_tool_risk_level(tool_name, args),
                    "raw_args": args
                }

        return tool_details

    def _get_thinking_details(self, phase: str, message: str) -> dict:
        """Get detailed thinking status information based on phase and message."""
        base_details = {
            "message_preview": message[:100] + "..." if len(message) > 100 else message,
            "message_length": len(message),
            "estimated_complexity": self._estimate_complexity(message)
        }

        if phase == "analysis":
            base_details.update({
                "current_step": "分析用户意图",
                "next_steps": ["理解上下文", "确定所需工具", "制定执行计划"],
                "estimated_duration": "2-5秒"
            })
        elif phase == "planning":
            base_details.update({
                "current_step": "制定执行计划",
                "next_steps": ["选择合适的工具", "安排执行顺序", "准备参数"],
                "estimated_duration": "1-3秒"
            })
        elif phase == "execution":
            base_details.update({
                "current_step": "执行计划",
                "next_steps": ["调用工具", "处理结果", "生成回复"],
                "estimated_duration": "3-10秒"
            })

        return base_details

    def _estimate_complexity(self, message: str) -> str:
        """Estimate the complexity of processing the message."""
        message_lower = message.lower()

        # Count complexity indicators
        complexity_score = 0

        # Task indicators
        if any(word in message_lower for word in ["创建", "写", "实现", "开发"]):
            complexity_score += 2
        elif any(word in message_lower for word in ["修改", "更新", "改进"]):
            complexity_score += 1
        elif any(word in message_lower for word in ["分析", "查看", "检查", "搜索"]):
            complexity_score += 0.5

        # Technical indicators
        if any(word in message_lower for word in ["代码", "文件", "项目", "数据库"]):
            complexity_score += 1
        if any(word in message_lower for word in ["测试", "部署", "配置"]):
            complexity_score += 1

        # Length factor
        if len(message) > 200:
            complexity_score += 0.5
        elif len(message) > 500:
            complexity_score += 1

        # Classify complexity
        if complexity_score >= 3:
            return "高复杂度"
        elif complexity_score >= 1.5:
            return "中等复杂度"
        elif complexity_score >= 0.5:
            return "低复杂度"
        else:
            return "简单"