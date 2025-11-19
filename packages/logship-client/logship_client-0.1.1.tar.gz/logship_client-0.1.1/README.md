# Logship – Python Logging Client for Elasticsearch

`Logship` 是一个轻量级、可扩展的 Python 日志上报客户端，用于将结构化日志批量、异步推送到 Elasticsearch。

## Features

- 异步发送
- 批量缓冲
- 自动重试
- 支持 Basic Auth
- 自动创建索引（可选）
- 最小依赖

## Installation

```bash
pip install logship-client
```

## Quick Start

```python
from logship import LogshipClient

client = LogshipClient(
    base_url="https://your-es-server.com",
    index_prefix="logship",
    username="elastic",
    password="your_password",
    app_name="order-service",
    env="prod",
)

client.info("用户登录成功", user_id=123)
```

## Advanced Usage

```python
client.debug("查询订单", order_id=9981, cost_ms=12)
client.error("订单支付失败", order_id=9981, code="PAY_TIMEOUT")
```

## Directory Structure

```
logship/
├── es_logger
│   ├── __init__.py
│   ├── config.py
│   ├── handler.py
│   └── setup.py
├── README.md
├── pyproject.toml
└── LICENSE
```

## License

MIT License
