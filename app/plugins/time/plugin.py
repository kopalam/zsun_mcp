"""Time plugin for FastMCP API service framework."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import pytz

from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool


class TimePlugin(MCPMixin):
    """Time plugin that provides real-time time querying functionality."""
    
    def __init__(self):
        super().__init__()
        self.name = "time"
        self.description = "Real-time time querying plugin"
        self.version = "1.0.0"
    
    @mcp_tool(name="获取当前时间", description="获取指定时区的当前时间")
    async def get_current_time(self, timezone_name: str = "UTC") -> Dict[str, Any]:
        """Get current time in specified timezone.
        
        Args:
            timezone_name: Timezone name (e.g., 'Asia/Shanghai', 'America/New_York', 'UTC')
        
        Returns:
            Dict containing time information
        """
        try:
            # Get timezone object
            if timezone_name.upper() == "UTC":
                tz = timezone.utc
            else:
                tz = pytz.timezone(timezone_name)
            
            # Get current time in specified timezone
            now = datetime.now(tz)
            
            return {
                "timezone": timezone_name,
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "iso_format": now.isoformat(),
                "timestamp": int(now.timestamp()),
                "day_of_week": now.strftime("%A"),
                "day_of_year": now.timetuple().tm_yday,
                "week_number": now.isocalendar()[1],
                "is_dst": now.dst() != timezone.utc.localize(datetime.min).dst() if hasattr(now, 'dst') else False
            }
        except Exception as e:
            return {
                "error": f"Invalid timezone '{timezone_name}': {str(e)}",
                "available_timezones": "Use 'list_timezones' to see available timezones"
            }
    
    @mcp_tool(name="列出常用时区", description="获取常用时区列表")
    async def list_common_timezones(self) -> Dict[str, Any]:
        """List common timezones.
        
        Returns:
            Dict containing common timezones grouped by region
        """
        common_timezones = {
            "Asia": [
                "Asia/Shanghai",      # 中国标准时间
                "Asia/Tokyo",         # 日本标准时间
                "Asia/Seoul",         # 韩国标准时间
                "Asia/Hong_Kong",     # 香港时间
                "Asia/Singapore",     # 新加坡时间
                "Asia/Kolkata",       # 印度标准时间
                "Asia/Dubai",         # 阿联酋时间
            ],
            "Europe": [
                "Europe/London",      # 英国时间
                "Europe/Paris",       # 法国时间
                "Europe/Berlin",      # 德国时间
                "Europe/Moscow",      # 俄罗斯时间
                "Europe/Rome",        # 意大利时间
            ],
            "America": [
                "America/New_York",   # 美国东部时间
                "America/Chicago",    # 美国中部时间
                "America/Denver",     # 美国山地时间
                "America/Los_Angeles", # 美国西部时间
                "America/Toronto",    # 加拿大东部时间
                "America/Sao_Paulo",  # 巴西时间
            ],
            "Pacific": [
                "Pacific/Auckland",   # 新西兰时间
                "Pacific/Sydney",     # 澳大利亚东部时间
                "Pacific/Honolulu",   # 夏威夷时间
            ],
            "UTC": [
                "UTC",               # 协调世界时
            ]
        }
        
        return {
            "common_timezones": common_timezones,
            "total_count": sum(len(tz_list) for tz_list in common_timezones.values()),
            "note": "Use any of these timezone names with 'get_current_time' function"
        }
    
    @mcp_tool(name="时间转换", description="将时间从一个时区转换到另一个时区")
    async def convert_time(
        self, 
        time_str: str, 
        from_timezone: str, 
        to_timezone: str,
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> Dict[str, Any]:
        """Convert time from one timezone to another.
        
        Args:
            time_str: Time string to convert
            from_timezone: Source timezone
            to_timezone: Target timezone
            format_str: Format of the input time string (default: "%Y-%m-%d %H:%M:%S")
        
        Returns:
            Dict containing converted time information
        """
        try:
            # Parse input time
            from_tz = pytz.timezone(from_timezone) if from_timezone.upper() != "UTC" else timezone.utc
            to_tz = pytz.timezone(to_timezone) if to_timezone.upper() != "UTC" else timezone.utc
            
            # Parse the input time string
            naive_time = datetime.strptime(time_str, format_str)
            
            # Localize to source timezone
            localized_time = from_tz.localize(naive_time)
            
            # Convert to target timezone
            converted_time = localized_time.astimezone(to_tz)
            
            return {
                "original_time": time_str,
                "original_timezone": from_timezone,
                "converted_time": converted_time.strftime(format_str),
                "converted_timezone": to_timezone,
                "iso_format": converted_time.isoformat(),
                "timestamp": int(converted_time.timestamp()),
                "time_difference": str(converted_time - localized_time)
            }
        except Exception as e:
            return {
                "error": f"Time conversion failed: {str(e)}",
                "supported_formats": [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d",
                    "%H:%M:%S",
                    "%H:%M"
                ]
            }
    
    @mcp_tool(name="当前实时时间", description="获取当前实时时间")
    async def calculate_time_difference(
        self,
        time1: str,
        time2: str,
        timezone1: str = "UTC",
        timezone2: str = "UTC",
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> Dict[str, Any]:
        """Calculate time difference between two times.
        
        Args:
            time1: First time string
            time2: Second time string
            timezone1: Timezone for first time
            timezone2: Timezone for second time
            format_str: Format of the time strings
        
        Returns:
            Dict containing time difference information
        """
        try:
            # Parse both times
            tz1 = pytz.timezone(timezone1) if timezone1.upper() != "UTC" else timezone.utc
            tz2 = pytz.timezone(timezone2) if timezone2.upper() != "UTC" else timezone.utc
            
            dt1 = tz1.localize(datetime.strptime(time1, format_str))
            dt2 = tz2.localize(datetime.strptime(time2, format_str))
            
            # Calculate difference
            diff = dt2 - dt1
            
            return {
                "time1": time1,
                "timezone1": timezone1,
                "time2": time2,
                "timezone2": timezone2,
                "difference_seconds": diff.total_seconds(),
                "difference_days": diff.days,
                "difference_hours": diff.total_seconds() / 3600,
                "difference_minutes": diff.total_seconds() / 60,
                "human_readable": str(diff),
                "is_positive": diff.total_seconds() > 0
            }
        except Exception as e:
            return {
                "error": f"Time difference calculation failed: {str(e)}",
                "supported_formats": [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d",
                    "%H:%M:%S",
                    "%H:%M"
                ]
            }
    
    @mcp_tool(name="获取世界时钟", description="获取多个时区的当前时间")
    async def get_world_clock(self, timezones: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get current time in multiple timezones.
        
        Args:
            timezones: List of timezone names. If None, uses common timezones.
        
        Returns:
            Dict containing current time in multiple timezones
        """
        if timezones is None:
            timezones = [
                "UTC",
                "Asia/Shanghai",
                "America/New_York",
                "Europe/London",
                "Asia/Tokyo",
                "Australia/Sydney"
            ]
        
        world_times = {}
        
        for tz_name in timezones:
            try:
                if tz_name.upper() == "UTC":
                    tz = timezone.utc
                else:
                    tz = pytz.timezone(tz_name)
                
                now = datetime.now(tz)
                world_times[tz_name] = {
                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "iso": now.isoformat(),
                    "day_of_week": now.strftime("%A")
                }
            except Exception as e:
                world_times[tz_name] = {"error": str(e)}
        
        return {
            "world_clock": world_times,
            "query_time_utc": datetime.now(timezone.utc).isoformat(),
            "total_timezones": len(timezones)
        }
