# ZSXQ MCP Server

知识星球 MCP 服务器 - 通过 Model Context Protocol 自动发布内容到知识星球。

## 🔥 核心功能

- ✅ 发布文字主题
- ✅ 上传并发布带图片的主题
- ✅ 从本地文件读取内容发布
- ✅ 灵活的环境变量配置
- ✅ Cookie 身份验证
- ✅ 定时发布主题
- ✅ 定时任务管理

## 📦 安装与配置

### 1. 安装 uv 工具（首次使用）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Claude Desktop 配置

直接在配置文件中使用 uvx 运行：

```json
{
  "mcpServers": {
    "zsxq": {
      "command": "uvx",
      "args": ["zsxq-mcp", "server"],
      "env": {
        "ZSXQ_COOKIE": "your_cookie_here",
        "ZSXQ_GROUP_ID": "your_group_id_here"
      }
    }
  }
}
```

重启 Claude Desktop 即可使用。

### 配置说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `ZSXQ_COOKIE` | 知识星球浏览器 Cookie | ✅ |
| `ZSXQ_GROUP_ID` | 星球 ID（URL 中获取） | 🔹 |

> Cookie 获取方法：浏览器登录知识星球 → F12 开发者工具 → Network → 任意 API 请求 → 请求头 `Cookie` 字段

## 🚀 使用示例

### 在 Claude 中使用

```
帮我发布一条动态到知识星球："今天学习了 MCP 的使用方法！"
```

```
把这个文件的内容发布到知识星球：/path/to/article.txt
```

```
帮我发布一条带图片的动态，内容是"分享今天的成果"，图片路径：/path/to/screenshot.png
```

```
帮我定时发布一条动态，5分钟后发布，内容是"定时测试"
```

```
帮我查看所有定时发布的任务
```

### MCP 工具列表

| 工具 | 功能 |
|------|------|
| `publish_topic` | 发布文字主题 |
| `publish_topic_from_file` | 从文件发布内容 |
| `publish_topic_with_images` | 发布带图片的主题 |
| `upload_image` | 单独上传图片 |
| `get_group_info` | 获取星球信息 |
| `schedule_topic` | 定时发布主题 |
| `get_scheduled_jobs` | 获取定时任务列表 |

## 📌 注意事项

- 🔒 Cookie 包含登录凭证，请勿泄露
- ⏰ Cookie 可能过期，需定期更新
- 💡 未指定 `ZSXQ_GROUP_ID` 时，每次调用需手动指定

## 📁 开发相关

### 本地开发

```bash
git clone https://github.com/your-repo/zsxq-mcp.git
cd zsxq-mcp
pip install -e .
```

### 调试工具

```bash
# 使用 MCP Inspector 调试（uvx 方式）
npx @modelcontextprotocol/inspector uvx zsxq-mcp server

# 或本地开发调试
uvx zsxq-mcp server
```

## 📄 许可证

MIT License
