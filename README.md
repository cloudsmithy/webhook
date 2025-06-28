# 通用 Webhook 通知器

这是一个基于 Flask 的简单 Webhook 通知器，可以通过一个统一的接口向多种服务（如飞书、Slack、企业微信等）发送消息。

## 安装

1.  克隆或下载本仓库。
2.  安装依赖：

    ```bash
    pip install -r requirements.txt
    ```

## 运行

```bash
python app.py
```

服务将在 `http://127.0.0.1:5001` 上运行。

## 使用方法

通过向 `/notify` 端点发送 GET 请求来发送通知。请求需要包含三个 URL 参数：

*   `key`: 目标服务的标识符。
*   `url`: 目标服务的完整 Webhook URL。
*   `body`: 要发送的消息内容。

### 支持的 `key`

*   `lark`: [飞书](https://www.feishu.cn/hc/zh-CN/articles/360024984973)
*   `slack`: [Slack](https://api.slack.com/messaging/webhooks)
*   `chime`: [Amazon Chime](https://docs.aws.amazon.com/chime/latest/ag/webhooks.html)
*   `wechat`: [企业微信](https.open.work.weixin.qq.com/api/doc/90000/90136/91770)
*   `serverchan`: [Server酱](https://sct.ftqq.com/)
*   `discord`: [Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
*   `dingtalk`: [钉钉](https://open.dingtalk.com/document/robots/custom-robot-access)
*   `teams`: [Microsoft Teams](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
*   `email`: 发送邮件 (需要配置 SMTP 环境变量)

### 示例

假设你的飞书机器人 Webhook URL 是 `https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK_ID`。

你可以通过在浏览器中访问以下 URL 来发送一条 "Hello, World!" 的消息：

```
http://127.0.0.1:5001/notify?key=lark&url=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK_ID&body=Hello, World!
```

### Markdown 支持

现在，`body` 参数中的内容会被解析为 Markdown。你可以发送加粗、链接、列表等格式。

**Markdown 示例 Body:**

`### New Task\n**Task Name:** Deploy to production\n- **Assignee:** @JohnDoe\n- **Due Date:** 2025-07-01\n[Click here for details](http://example.com)`

（注意：在 URL 中使用时，换行符 `\n` 需要被正确编码。）

### 邮件发送配置 (SMTP)

当 `key` 设置为 `email` 时，应用会尝试通过 SMTP 发送邮件。为此，你必须在运行应用前设置以下环境变量：

*   `SMTP_SERVER`: 你的 SMTP 服务器地址 (例如: `smtp.example.com`)
*   `SMTP_PORT`: 你的 SMTP 服务器端口 (例如: `587`)
*   `SMTP_USER`: 你的邮箱用户名
*   `SMTP_PASSWORD`: 你的邮箱密码或应用专用密码

**在终端中设置环境变量 (示例):**

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT=587
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
python app.py
```

**使用邮件功能:**

*   **key**: `email`
*   **Recipient Email (原 Webhook URL 字段)**: `recipient@example.com`
*   **body**: 邮件的正文内容。

### 注意



*   请确保将 `YOUR_HOOK_ID` 替换为你的实际 Webhook ID。
*   对于 Server酱，`body` 参数将作为消息的 `desp`（描述），`title`（标题）会设为固定的“通知”。
*   本项目为简化示例，未对 URL 和 body 内容做严格的安全校验，在生产环境使用时请注意安全风险。
# webhook
