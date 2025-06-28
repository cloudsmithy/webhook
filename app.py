
from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown2

app = Flask(__name__)

def send_notification(url, payload):
    """通用发送函数"""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 如果请求失败则抛出异常
        return True, response.json()
    except requests.exceptions.RequestException as e:
        # 尝试解析e.response获取更详细的错误信息
        error_details = str(e)
        if e.response is not None:
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = e.response.text
        return False, error_details

def send_email(recipient, subject, body):
    """发送邮件函数，支持Markdown转HTML"""
    try:
        # 从环境变量获取SMTP配置
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 587)) # 默认587 for TLS
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')

        if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
            return False, "SMTP environment variables not configured."

        # 创建一个MIMEMultipart消息对象
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = recipient

        # 创建邮件的纯文本和HTML版本
        plain_text_body = body # 保留原始文本
        html_body = markdown2.markdown(body) # 转换Markdown为HTML

        # 将两个版本都附加到MIMEMultipart消息中
        # 邮件客户端会优先显示HTML版本
        msg.attach(MIMEText(plain_text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # 启用安全传输模式
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True, {"status": "Email sent successfully"}
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notify', methods=['GET'])
def notify():
    key = request.args.get('key')
    url = request.args.get('url')
    body = request.args.get('body')
    subject = request.args.get('subject', 'Notification from Universal Webhook') # 新增 subject 参数

    if not all([key, url, body]):
        return jsonify({"error": "Missing key, url, or body parameter"}), 400

    # 如果是邮件，特殊处理
    if key == 'email':
        recipient = url # url 参数作为收件人地址
        success, message = send_email(recipient, subject, body)
        if success:
            return jsonify({"status": "success", "response": message})
        else:
            return jsonify({"status": "error", "message": message}), 500

    payload = {}

    # 根据 key 构建不同的 payload
    # 对于支持Markdown的服务，我们优先使用Markdown格式
    if key == 'lark': # 飞书 (使用post消息支持Markdown)
        # 将 body 按换行符分割，生成飞书 post 格式
        content_list = []
        for line in body.split('\n'):
            content_list.append([{"tag": "text", "text": line}])

        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": subject, # 使用 subject
                        "content": content_list
                    }
                }
            }
        }
    elif key == 'slack': # Slack (原生支持mrkdwn)
        payload = {'text': body}
    elif key == 'chime': # Chime (原生支持Markdown)
        payload = {'Content': body}
    elif key == 'wechat': # 企业微信 (使用markdown类型)
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": body
            }
        }
    elif key == 'serverchan': # Server酱 (desp字段支持Markdown)
        payload = {'title': '通知', 'desp': body}
    elif key == 'discord': # Discord (原生支持Markdown)
        payload = {'content': body}
    elif key == 'dingtalk': # 钉钉 (使用markdown类型)
        payload = {
            'msgtype': 'markdown',
            'markdown': {
                'title': '通知',
                'text': body
            }
        }
    elif key == 'teams': # Microsoft Teams (原生支持Markdown)
        payload = {'text': body}
    else:
        return jsonify({"error": "Unsupported key"}), 400

    success, message = send_notification(url, payload)

    if success:
        return jsonify({"status": "success", "response": message})
    else:
        return jsonify({"status": "error", "message": message}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
