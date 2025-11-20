#!/usr/bin/env python3
"""
Seedream 4.0 MCP工具 - SSE服务器模块

实现基于SSE的MCP协议服务器，通过HTTP提供工具调用服务。
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from aiohttp import web, WSMsgType
from aiohttp_sse import sse_response

from .server import SeedreamMCPServer
from .config import SeedreamConfig
from .utils.logging import setup_logging


class SeedreamMCP_SSEServer:
    """Seedream 4.0 MCP SSE服务器类
    
    提供基于SSE的MCP协议服务器实现，通过HTTP接口处理工具调用请求。
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """初始化MCP SSE服务器实例
        
        Args:
            host: 服务器监听地址
            port: 服务器监听端口
        """
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.mcp_server = SeedreamMCPServer()
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """设置HTTP路由"""
        self.app.router.add_get('/sse', self.handle_sse)
        self.app.router.add_post('/tool/list', self.handle_list_tools)
        self.app.router.add_post('/tool/call', self.handle_call_tool)
        self.app.router.add_get('/health', self.handle_health_check)

    async def handle_sse(self, request):
        """处理SSE连接请求"""
        async with sse_response(request) as resp:
            # 发送初始化消息
            await resp.send(json.dumps({
                "type": "init",
                "data": {
                    "server": "seedream-mcp-sse",
                    "version": "1.0.0"
                }
            }))
            
            # 这里可以添加更多SSE事件处理逻辑
            # 例如：发送工具列表更新、状态变化等
            
        return resp

    async def handle_list_tools(self, request):
        """处理工具列表请求"""
        try:
            tools = self.mcp_server.tools
            tools_data = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
            
            return web.json_response({
                "success": True,
                "data": tools_data
            })
        except Exception as e:
            self.logger.error(f"获取工具列表失败: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_call_tool(self, request):
        """处理工具调用请求"""
        try:
            data = await request.json()
            tool_name = data.get("name")
            arguments = data.get("arguments", {})
            
            if not tool_name:
                return web.json_response({
                    "success": False,
                    "error": "工具名称不能为空"
                }, status=400)
            
            # 调用MCP服务器处理工具调用
            result = await self.mcp_server.server.call_tool()(tool_name, arguments)
            
            return web.json_response({
                "success": True,
                "data": result
            })
        except Exception as e:
            self.logger.error(f"工具调用失败: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_health_check(self, request):
        """处理健康检查请求"""
        return web.json_response({
            "status": "healthy",
            "server": "seedream-mcp-sse"
        })

    async def start(self):
        """启动SSE服务器"""
        setup_logging()
        self.logger.info(f"启动Seedream MCP SSE服务器: http://{self.host}:{self.port}")
        
        # 初始化MCP服务器
        await self.mcp_server._initialize_client()
        
        # 启动Web服务器
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info("Seedream MCP SSE服务器启动成功")
        
        # 保持服务器运行
        while True:
            await asyncio.sleep(3600)  # 每小时检查一次

    async def stop(self):
        """停止服务器"""
        self.logger.info("正在停止Seedream MCP SSE服务器...")
        # 这里可以添加清理逻辑


async def main():
    """主入口函数
    
    创建并运行SeedreamMCP SSEServer实例。
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Seedream MCP SSE服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器监听地址")
    parser.add_argument("--port", type=int, default=8080, help="服务器监听端口")
    
    args = parser.parse_args()
    
    server = SeedreamMCP_SSEServer(host=args.host, port=args.port)
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())