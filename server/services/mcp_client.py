"""
MCP 客户端 - 与 MCP 服务器（hotnews）通信
通过 stdio 与 npx 启动的 MCP 服务器交互
"""
import json
import os
import subprocess
import logging
from threading import Thread

logger = logging.getLogger(__name__)

NODE_PATH = r"C:\Program Files\nodejs\node-v20.14.0-win-x64"
MCP_SERVER_COMMAND = [os.path.join(NODE_PATH, "npx.cmd"), "-y", "@wopal/mcp-server-hotnews"]


class MCPClient:
    def __init__(self):
        self.process = None
        self.request_id = 0
        self._stderr_lines = []

    def start(self):
        try:
            env = os.environ.copy()
            env["PATH"] = NODE_PATH + os.pathsep + env.get("PATH", "")
            self.process = subprocess.Popen(
                MCP_SERVER_COMMAND,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env
            )
            # 启动 stderr 读取线程
            self._stderr_thread = Thread(target=self._read_stderr, daemon=True)
            self._stderr_thread.start()

            result = self._initialize()
            if result and "result" in result:
                logger.info("MCP hotnews 服务器连接成功")
                return True
            logger.warning("MCP 初始化失败")
            return False
        except Exception as e:
            logger.warning(f"MCP 服务器启动失败: {e}")
            return False

    def _read_stderr(self):
        try:
            for line in self.process.stderr:
                self._stderr_lines.append(line.strip())
                if len(self._stderr_lines) > 50:
                    self._stderr_lines.pop(0)
        except Exception:
            pass

    def _send_request(self, method, params=None, expect_response=True):
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        request_str = json.dumps(request) + "\n"
        try:
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            logger.error("MCP 进程已断开")
            return None

        if not expect_response:
            return None

        try:
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
        except (ValueError, json.JSONDecodeError):
            pass
        except Exception as e:
            logger.error(f"MCP 读取响应失败: {e}")
        return None

    def _send_notification(self, method, params=None):
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        try:
            self.process.stdin.write(json.dumps(notification) + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def _initialize(self):
        response = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "blog-agent", "version": "1.0.0"}
        })
        if response and "result" in response:
            self._send_notification("notifications/initialized")
        return response

    def list_tools(self):
        response = self._send_request("tools/list")
        if response and "result" in response:
            return response["result"].get("tools", [])
        return []

    def call_tool(self, tool_name, arguments=None):
        response = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
        if response and "result" in response:
            content = response["result"].get("content", [])
            for item in content:
                if item.get("type") == "text":
                    return item.get("text")
                if item.get("type") == "resource":
                    return item
            return content
        if response and "error" in response:
            logger.error(f"MCP 调用失败: {response['error']}")
        return None

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def close(self):
        if self.process:
            try:
                self.process.stdin.close()
                self.process.stdout.close()
                self.process.stderr.close()
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None


mcp_client = MCPClient()
