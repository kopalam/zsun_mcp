# SmartTime 智能时间管理系统

## 系统概述

SmartTime 是一个基于 LLM Agent 和 MCP Server 的智能时间管理系统，能够解析用户意图并自动创建任务（task）和计划（plan）。系统已集成到现有的 FastMCP API 服务框架中，并使用 MySQL 数据库进行数据持久化存储。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Agent     │    │   FastMCP API   │    │   SmartTime     │    │   MySQL         │
│                 │    │   Server        │    │   Plugins       │    │   Database      │
│ 输出结构化JSON   │───▶│  接收JSON数据    │───▶│  处理业务逻辑    │───▶│  数据持久化      │
│ 包含intent字段   │    │  路由到插件      │    │  存储数据       │    │  阿里云RDS      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 目录结构

```
app/
├── run.py                    # 主服务器启动文件（已集成SmartTime）
├── database.py               # 数据库连接和配置模块（已优化）
├── smart_time_client.py      # SmartTime客户端示例
├── test_connection.py        # 连接测试脚本
├── plugins/
│   ├── base.py              # 插件基类
│   ├── weather/             # 天气插件（参考）
│   └── smart/               # 智能时间管理插件
│       ├── __init__.py      # 插件包初始化
│       ├── models.py        # 数据模型定义（已修复JSON序列化）
│       ├── task.py          # 任务处理插件（MySQL）
│       ├── plan.py          # 计划处理插件（MySQL）
│       ├── processor.py     # 智能处理器
│       └── examples.py      # 使用示例

.env.example                 # 环境变量示例文件
README_SmartTime.md          # 系统说明文档
```

## 数据库配置

SmartTime 系统使用阿里云 RDS MySQL 数据库进行数据持久化存储。

### 数据库表结构

#### plugin_smart_tasks（任务表）
- `id`: 任务ID（INT，自增主键）
- `uuid`: 用户唯一标识（VARCHAR(255)）
- `title`: 任务标题（VARCHAR(500)）
- `description`: 任务描述（TEXT）
- `source_type`: 任务创建来源（ENUM: manual/agent/import）
- `status`: 任务状态（ENUM: todo/in_progress/completed/cancelled）
- `priority`: 优先级（ENUM: low/medium/high/urgent）
- `estimated_duration`: 预估耗时（分钟，INT）
- `deadline`: 截止时间（DATETIME）
- `tags`: 任务标签（VARCHAR(500)，逗号分隔）
- `parent_task_id`: 父任务ID（INT，支持子任务结构）
- `agent_origin`: 由哪个Agent创建（VARCHAR(255)）
- `is_recurring_template`: 是否为重复任务的模板（BOOLEAN）
- `created_time`: 创建时间（TIMESTAMP）
- `updated_time`: 更新时间（TIMESTAMP）
- `is_deleted`: 是否已删除（BOOLEAN，软删除）     

#### plugin_smart_plans（计划表）
- `id`: 计划ID（INT，自增主键）
- `uuid`: 用户唯一标识（VARCHAR(255)）
- `title`: 计划标题（VARCHAR(500)）
- `description`: 可选说明（TEXT）
- `start_time`: 计划开始时间（DATETIME）
- `end_time`: 计划结束时间（DATETIME）
- `task_id`: 关联的任务ID（INT，可为空，纯事件）
- `is_all_day`: 是否为全天事件（BOOLEAN）
- `tags`: 标签（VARCHAR(500)，如"会议,健身"）
- `repeat_rule`: 重复规则（VARCHAR(255)，如"daily"、"weekly:5"）
- `repeat_end_date`: 重复截止时间（DATE）
- `reminder_minutes`: 提前提醒时间（分钟，INT，默认30）
- `reminder_type`: 提醒类型（ENUM: push/email/sms，默认push）
- `status`: 计划执行状态（ENUM: scheduled/in_progress/completed/cancelled）
- `plan_source`: 生成来源（ENUM: manual/agent/import）
- `agent_origin`: 触发该计划的Agent名（VARCHAR(255)）
- `pomodoro_count`: 完成的番茄钟次数（INT，25分钟为单位）
- `actual_start_time`: 实际开始时间（DATETIME，用于行为分析）
- `actual_end_time`: 实际结束时间（DATETIME）
- `created_time`: 创建时间（TIMESTAMP）
- `updated_time`: 更新时间（TIMESTAMP）
- `is_deleted`: 是否已删除（BOOLEAN，软删除）

## 快速开始

### 1. 环境配置

复制环境变量示例文件：
```bash
cp .env.example .env
```

根据需要修改 `.env` 文件中的数据库配置。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务器

```bash
# 启动包含SmartTime功能的FastMCP服务器
python app/run.py
```

服务器将在 `http://localhost:8010` 启动，提供以下功能：
- 天气查询功能（原有）
- SmartTime 智能时间管理功能（新增，使用MySQL数据库）

### 4. 运行客户端测试

```bash
# 运行SmartTime客户端测试
python app/smart_time_client.py
```

### 5. 连接测试

```bash
# 运行连接测试脚本
python app/test_connection.py
```

## 可用的MCP工具

SmartTime 系统提供以下 MCP 工具：

### 核心功能
- `process_agent_intent`: 处理Agent意图JSON数据
- `get_task_info`: 获取任务详情
- `get_plan_info`: 获取计划详情
- `list_user_tasks`: 获取用户任务列表
- `list_user_plans`: 获取用户计划列表
- `get_upcoming_plans`: 获取即将到来的计划
- `update_task`: 更新任务
- `update_plan`: 更新计划
- `delete_task`: 删除任务（软删除）
- `delete_plan`: 删除计划（软删除）

## Agent 输出 JSON 格式

### 1. 安排计划（plan_time）

```json
{
  "intent": "plan_time",
  "uuid": "用户唯一uuid",
  "title": "撰写MVP项目计划书",
  "description": "明天下午三点到四点完成项目的MVP项目计划书，请准备好相关资料和工具。",
  "start_time": "2025-07-13 15:00:00",
  "end_time": "2025-07-13 16:00:00",
  "task_id": null,
  "is_all_day": false,
  "tags": "项目计划,工作",
  "repeat_rule": null,
  "repeat_end_date": null,
  "reminder_minutes": 30,
  "reminder_type": "push",
  "status": "scheduled",
  "plan_source": "agent",
  "agent_origin": "PlanningAgent",
  "pomodoro_count": 0
}
```

### 2. 添加任务（add_schedule）

```json
{
  "intent": "add_schedule",
  "uuid": "用户唯一uuid",
  "title": "与甘总面谈",
  "description": "与甘总约了下周四到公司面谈，时间为下午两点。请提前准备相关资料并准时参加。",
  "source_type": "agent",
  "status": "todo",
  "priority": "medium",
  "estimated_duration": 60,
  "deadline": "2025-07-18 14:00:00",
  "tags": "会议,工作",
  "parent_task_id": null,
  "agent_origin": "ScheduleAgent"
}
```

## 使用方法

### 1. 使用 FastMCP 客户端

```python
import asyncio
import json
from fastmcp import Client

async def example():
    async with Client("http://localhost:8010/sse") as client:
        # 处理Agent意图
        task_data = {
            "intent": "add_schedule",
            "uuid": "user_12345",
            "title": "完成项目文档",
            "description": "编写项目技术文档",
            "priority": "high",
            "deadline": "2025-07-15 18:00:00"
        }
        
        result = await client.call_tool("process_agent_intent", {
            "json_data": json.dumps(task_data)
        })
        print(json.loads(result))

# 运行示例
asyncio.run(example())
```

### 2. 直接使用插件

```python
import json
from app.plugins.smart import smart_processor

# 处理Agent意图
task_json = json.dumps({
    "intent": "add_schedule",
    "uuid": "user_12345",
    "title": "完成项目文档",
    "description": "编写项目技术文档",
    "priority": "high",
    "deadline": "2025-07-15 18:00:00"
})

result = await smart_processor.process_agent_json(task_json)
print(json.loads(result))
```

### 3. 运行示例代码

```bash
# 运行内置示例
python -m app.plugins.smart.examples
```

## 核心组件

### 1. 数据模型 (`models.py`)

定义了系统的核心数据模型，**已修复JSON序列化问题**：

- **Task**: 任务数据模型（支持datetime自动序列化）
- **Plan**: 计划数据模型（支持datetime自动序列化）
- **AgentIntent**: Agent意图数据模型
- **ProcessingResult**: 处理结果数据模型
- **TaskStatus**: 任务状态枚举（todo/in_progress/completed/cancelled）
- **TaskPriority**: 任务优先级枚举（low/medium/high/urgent）
- **TaskSourceType**: 任务来源类型枚举（manual/agent/import）
- **PlanStatus**: 计划状态枚举（scheduled/in_progress/completed/cancelled）
- **ReminderType**: 提醒类型枚举（push/email/sms）
- **PlanSource**: 计划来源枚举（manual/agent/import）

### 2. 数据库管理 (`database.py`)

提供 MySQL 数据库连接和管理功能，**已优化事件循环处理**：

- **DatabaseConfig**: 数据库配置类
- **DatabaseManager**: 数据库管理器（支持懒加载）
- 连接池管理（自动重连和验证）
- 自动创建表结构
- 支持INSERT返回最后插入ID
- **事件循环兼容性**：支持在FastMCP事件循环中正确运行

### 3. 任务插件 (`task.py`)

处理任务相关的业务逻辑，使用 MySQL 数据库：

- 创建任务（返回自增ID）
- 获取任务详情
- 更新任务
- 软删除任务
- 获取任务列表

### 4. 计划插件 (`plan.py`)

处理计划相关的业务逻辑，使用 MySQL 数据库：

- 创建计划（返回自增ID）
- 获取计划详情
- 更新计划
- 软删除计划
- 获取计划列表
- 获取即将到来的计划

### 5. 智能处理器 (`processor.py`)

核心路由和处理逻辑：

- 解析Agent输出的JSON数据
- 根据intent类型路由到对应插件
- 统一错误处理和日志记录

## 技术优化

### 1. 事件循环问题解决

**问题**：之前存在"Event loop is closed"和"Future attached to a different loop"错误。

**解决方案**：
- 采用懒加载机制，数据库连接池在第一次使用时才初始化
- 确保所有数据库操作都在FastMCP的事件循环内执行
- 移除了run.py中的主动数据库初始化，避免事件循环冲突

### 2. JSON序列化优化

**问题**：datetime对象无法直接序列化为JSON。

**解决方案**：
- 为Task和Plan模型添加自定义`dict()`方法
- 自动将datetime对象转换为ISO格式字符串
- 支持date对象的序列化

### 3. 数据库连接优化

**改进**：
- 连接池自动重连机制
- 连接有效性验证
- 更好的错误处理和日志记录
- 支持连接池状态检查

## 扩展性设计

### 1. 插件化架构

系统采用插件化设计，可以轻松添加新的功能模块：

1. 继承 `BasePlugin` 类
2. 实现具体的业务逻辑
3. 在 `app/run.py` 中注册新的工具

### 2. 数据库扩展

当前使用 MySQL 数据库，可以轻松扩展：

1. 修改 `database.py` 中的表结构
2. 添加新的数据库操作方法
3. 在插件中使用新的数据库功能

### 3. 新的意图类型

添加新的意图类型：

1. 在 `models.py` 中定义新的数据模型
2. 创建对应的插件
3. 在 `processor.py` 中注册处理器
4. 在 `app/run.py` 中添加工具

## 配置说明

### 1. 数据库配置

通过环境变量配置数据库连接：

```bash
# 数据库主机
DB_HOST=rm-7xv1g24h1bgmdp0464o.mysql.rds.aliyuncs.com
# 数据库端口
DB_PORT=3306
# 数据库用户名
DB_USERNAME=contract
# 数据库密码
DB_PASSWORD=rapidBuilder!
# 数据库名称
DB_DATABASE=contract
```

### 2. 时间格式

系统支持多种时间格式：
- ISO格式：`2025-07-13T15:00:00`
- 标准格式：`2025-07-13 15:00:00`

### 3. 状态枚举

**任务状态**：
- `todo`: 待办
- `in_progress`: 进行中
- `completed`: 已完成
- `cancelled`: 已取消

**计划状态**：
- `scheduled`: 已安排
- `in_progress`: 进行中
- `completed`: 已完成
- `cancelled`: 已取消

**任务优先级**：
- `low`: 低
- `medium`: 中
- `high`: 高
- `urgent`: 紧急

**任务来源类型**：
- `manual`: 手动创建
- `agent`: Agent创建
- `import`: 导入

**提醒类型**：
- `push`: 推送通知
- `email`: 邮件通知
- `sms`: 短信通知

**计划来源**：
- `manual`: 手动创建
- `agent`: Agent创建
- `import`: 导入

## 错误处理

系统提供统一的错误处理机制：

1. **JSON解析错误**：处理格式错误的JSON数据
2. **字段验证错误**：验证必要字段是否存在
3. **业务逻辑错误**：处理业务规则违反的情况
4. **数据库错误**：处理数据库连接和操作异常
5. **系统错误**：处理系统级别的异常
6. **事件循环错误**：处理异步操作中的循环冲突

所有错误都会返回标准的 `ProcessingResult` 格式。

## 日志记录

系统使用Python标准logging模块记录日志：

- 错误日志：记录异常和错误信息
- 信息日志：记录业务操作
- 调试日志：记录详细的处理过程
- 数据库日志：记录数据库操作
- 连接日志：记录连接池状态变化

## 性能优化

1. **异步处理**：所有操作都使用异步方式
2. **连接池**：使用数据库连接池提高性能
3. **懒加载**：数据库连接池按需初始化
4. **索引优化**：数据库表已添加必要的索引
5. **批量操作**：支持批量查询和更新
6. **缓存机制**：可以添加缓存来提高性能
7. **软删除**：使用软删除避免数据丢失，提高性能

## 安全考虑

1. **输入验证**：严格验证所有输入数据
2. **权限控制**：基于用户UUID进行数据隔离
3. **SQL注入防护**：使用参数化查询
4. **XSS防护**：对输出数据进行转义
5. **数据库安全**：使用环境变量管理敏感信息
6. **软删除**：防止数据意外丢失
7. **连接安全**：数据库连接使用SSL加密

## 部署说明

### 1. 环境准备

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接信息
```

### 2. 启动服务

```bash
python app/run.py
```

### 3. 测试功能

```bash
# 运行完整测试
python app/smart_time_client.py

# 运行连接测试
python app/test_connection.py
```

## 测试

### 1. 运行服务器测试
```bash
# 测试服务器连接和工具注册
python app/test_server.py
```

### 2. 运行客户端测试
```bash
python app/smart_time_client.py
```

### 3. 运行连接测试
```bash
python app/test_connection.py
```

### 4. 运行系统测试
```bash
# 运行完整的系统测试
python app/test_smarttime.py
```

### 5. 运行客户端示例
```bash
# 运行客户端使用示例
python app/smart_time_client_example.py
```

### 6. 运行示例代码
```bash
python -m app.plugins.smart.examples
```

### 7. 数据库连接测试
启动服务器时会自动测试数据库连接并创建必要的表结构。

## 故障排除

### 常见问题

1. **"Event loop is closed"错误**
   - 已通过懒加载机制解决
   - 确保数据库操作在正确的事件循环中执行

2. **"Future attached to a different loop"错误**
   - 已通过统一事件循环管理解决
   - 避免跨事件循环使用数据库连接

3. **"Object of type datetime is not JSON serializable"错误**
   - 已通过自定义序列化方法解决
   - datetime对象自动转换为ISO格式字符串

4. **数据库连接失败**
   - 检查环境变量配置
   - 确认数据库服务可用
   - 查看连接池日志

### 调试技巧

1. 使用 `test_connection.py` 进行连接测试
2. 查看服务器日志了解详细错误信息
3. 检查数据库连接池状态
4. 验证JSON数据格式

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 更新日志

### v1.1.0 (最新)
- ✅ 修复事件循环问题
- ✅ 解决JSON序列化错误
- ✅ 优化数据库连接管理
- ✅ 改进错误处理机制
- ✅ 添加连接测试脚本
- ✅ 更新文档和示例

### v1.0.0
- 🎉 初始版本发布
- 📋 基础任务管理功能
- 📅 基础计划管理功能
- 🤖 Agent集成支持

## 许可证

MIT License 