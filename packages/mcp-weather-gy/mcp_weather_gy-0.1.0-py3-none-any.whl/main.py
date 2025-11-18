import json
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP
from typing import Annotated
import  requests
# 初始化 MCP服务器
mcp = FastMCP("WeatherServer")

@mcp.tool()
async def query_weather(city: str) -> str:
    """
    查询指定城市的天气信息。

    参数:
    city (str): 城市名称

    返回:
    str: 天气信息的字符串表示
    """
    key_selection = {
        "current_condition:": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"]
    }
    resp = requests.get(f"https://wttr.in/{city}?format=j1")
    resp.raise_for_status()

    data = resp.json()
    ret = {k: data["current_condition"][0][k] for k in key_selection["current_condition:"]}
    return str(ret)


def main():
    "主函数，用于启动MCP服务器"
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

 