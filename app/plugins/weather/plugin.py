from ..base import BasePlugin
import httpx
from typing import Dict, Any
from datetime import datetime

class WeatherPlugin(BasePlugin):
    """天气插件"""
    
    def __init__(self):
        super().__init__("Weather Service")
        self.API_KEY = "c4aa79ba042f46f95854c58b3161fdc3"
        self.BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    def _register_tools(self):
        """注册工具"""
        pass  # 不再在这里注册工具
    
    async def get_weather_data(self, city: str) -> Dict[str, Any]:
        """获取天气数据"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "q": city,
                    "appid": self.API_KEY,
                    "units": "metric",  # 使用摄氏度
                    "lang": "zh_cn"     # 使用中文
                }
            )
            return response.json()
    
    def format_weather_data(self, data: Dict[str, Any]) -> str:
        """格式化天气数据"""
        if "cod" not in data or data["cod"] != "200":
            return f"获取天气数据失败: {data.get('message', '未知错误')}"

        city = data["city"]["name"]
        forecast = data["list"][0]  # 获取第一个预报数据
        
        # 解析天气数据
        temp = forecast["main"]["temp"]
        feels_like = forecast["main"]["feels_like"]
        humidity = forecast["main"]["humidity"]
        weather_desc = forecast["weather"][0]["description"]
        wind_speed = forecast["wind"]["speed"]
        
        # 格式化时间
        dt = datetime.fromtimestamp(forecast["dt"])
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
{city}天气信息 ({time_str}):
温度: {temp}°C
体感温度: {feels_like}°C
湿度: {humidity}%
天气状况: {weather_desc}
风速: {wind_speed} m/s
"""
    
    async def get_weather(self, city: str) -> str:
        """获取指定城市的天气信息
        
        Args:
            city: 城市名称，例如：beijing、shanghai、guangzhou等
            
        Returns:
            格式化的天气信息字符串
        """
        try:
            data = await self.get_weather_data(city)
            return self.format_weather_data(data)
        except Exception as e:
            return f"获取天气信息失败: {str(e)}"
    
    async def get_weather_forecast(self, city: str, days: int = 3) -> str:
        """获取指定城市的天气预报
        
        Args:
            city: 城市名称，例如：beijing、shanghai、guangzhou等
            days: 预报天数（1-5天）
            
        Returns:
            格式化的天气预报信息字符串
        """
        try:
            data = await self.get_weather_data(city)
            if "cod" not in data or data["cod"] != "200":
                return f"获取天气预报失败: {data.get('message', '未知错误')}"

            city_name = data["city"]["name"]
            forecast_list = data["list"]
            
            # 每天取一个时间点的数据
            daily_forecasts = []
            current_date = None
            
            for forecast in forecast_list:
                dt = datetime.fromtimestamp(forecast["dt"])
                date_str = dt.strftime("%Y-%m-%d")
                
                if date_str != current_date:
                    current_date = date_str
                    temp = forecast["main"]["temp"]
                    weather_desc = forecast["weather"][0]["description"]
                    daily_forecasts.append(f"{date_str}: {temp}°C, {weather_desc}")
                    
                    if len(daily_forecasts) >= days:
                        break
            
            return f"{city_name}未来{days}天天气预报:\n" + "\n".join(daily_forecasts)
        except Exception as e:
            return f"获取天气预报失败: {str(e)}" 