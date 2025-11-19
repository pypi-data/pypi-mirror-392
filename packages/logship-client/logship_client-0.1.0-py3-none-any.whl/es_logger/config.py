from dataclasses import dataclass
from typing import Optional

@dataclass
class ESConfig:
    """
    Elasticsearch 配置
    """
    base_url: str            # ES 地址，例如: http://localhost:9200
    index_prefix: str = "app-logs"  # 索引前缀，最终索引: {index_prefix}-YYYY.MM.DD
    username: Optional[str] = None
    password: Optional[str] = None
    app_name: str = "default-app"   # 应用名，用于区分不同项目
    env: str = "dev"                # 环境，如 dev / test / prod
    timeout: float = 5.0            # 请求超时秒数
    verify_ssl: bool = True         # 是否验证 SSL 证书
    bulk: bool = False              # 是否使用 _bulk 写入（简单实现，默认关）
    bulk_max_actions: int = 1000    # bulk 模式下攒多少条一起发