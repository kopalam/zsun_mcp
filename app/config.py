"""
配置文件
管理FastMCP WebSocket服务器的配置
"""

import os
from typing import Dict, Any


class Config:
    """配置管理类"""

    def __init__(self):
        # 服务器配置
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "7100"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # WebSocket配置
        self.server_key = os.getenv("SERVER_KEY", "v%2BGNdYhqHQJ1drrKS6JJ3W12I2tAWMmimVUgyDHs%2FpFuup38CTerac1ML7TeIgmI")
        self.enable_cors = os.getenv("ENABLE_CORS", "true").lower() == "true"
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # 插件配置
        self.weather_api_base = os.getenv("WEATHER_API_BASE", "https://api.open-meteo.com/v1")
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.geocoding_api_base = os.getenv("GEOCODING_API_BASE", "https://geocoding-api.open-meteo.com/v1")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "server_key": self.server_key,
            "enable_cors": self.enable_cors,
            "allowed_origins": self.allowed_origins,
            "log_level": self.log_level,
            "weather_api_base": self.weather_api_base,
            "weather_api_key": self.weather_api_key,
            "geocoding_api_base": self.geocoding_api_base,
        }

    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(host={self.host}, port={self.port}, debug={self.debug})"


# 全局配置实例
config = Config()
