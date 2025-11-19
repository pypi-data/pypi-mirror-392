from .config import ESConfig
from typing import Optional
import logging
from .handler import ElasticsearchHandler

def setup_es_logging(
    config: ESConfig,
    level: int = logging.INFO,
    console: bool = True,
    root_logger_name: Optional[str] = None,
) -> logging.Logger:
    """
    对外提供的统一入口。
    其他项目只需要调用这个方法，就能把日志统一打进 ES。

    :param config: ESConfig 配置
    :param level: 日志级别
    :param console: 是否同时输出到控制台
    :param root_logger_name: 如果为 None，则配置 root logger
    :return: 已配置好的 logger
    """
    logger = logging.getLogger(root_logger_name)
    logger.setLevel(level)
    logger.propagate = False  # 避免重复日志

    # 先清掉旧 handler，避免重复添加
    logger.handlers.clear()

    # ES handler
    es_handler = ElasticsearchHandler(config=config)
    es_handler.setLevel(level)

    # 控制台 handler（可选）
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.addHandler(es_handler)

    return logger
