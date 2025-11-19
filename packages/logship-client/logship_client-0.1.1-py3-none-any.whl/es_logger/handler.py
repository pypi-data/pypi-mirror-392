import logging
import threading
import queue
import json
import traceback
from datetime import datetime
from typing import  Dict, Any, List
from .config import ESConfig

import requests


class ElasticsearchHandler(logging.Handler):
    """
    把日志写到 Elasticsearch 的 Handler。
    内部使用异步队列 + 后台线程，避免阻塞业务线程。
    """

    def __init__(self, config: ESConfig):
        super().__init__()
        self.config = config
        self._queue: "queue.Queue[logging.LogRecord]" = queue.Queue(maxsize=10000)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._session = requests.Session()

        if self.config.username and self.config.password:
            self._session.auth = (self.config.username, self.config.password)

        self._session.verify = self.config.verify_ssl
        self._thread.start()

    # 核心：logging 调用 emit -> 我们只是把 record 丢进队列，真正请求在后台线程
    def emit(self, record: logging.LogRecord) -> None:
        try:
            # 不要在这里做 heavy 操作
            self._queue.put_nowait(record)
        except queue.Full:
            # 队列满了时可以做降级策略：丢弃 / 打印到 stderr
            # 这里选择丢弃并输出简单告警
            try:
                print("[ElasticsearchHandler] queue is full, dropping log.")
            except Exception:
                pass

    def close(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=2)
        self._session.close()
        super().close()

    # 后台线程负责不断从队列取日志写 ES
    def _worker(self):
        buffer: List[Dict[str, Any]] = []

        while not self._stop_event.is_set():
            try:
                record = self._queue.get(timeout=0.5)
            except queue.Empty:
                # 如果启用 bulk，把攒的日志刷掉
                if self.config.bulk and buffer:
                    self._flush_bulk(buffer)
                    buffer.clear()
                continue

            doc = self._format_record(record)
            if self.config.bulk:
                buffer.append(doc)
                if len(buffer) >= self.config.bulk_max_actions:
                    self._flush_bulk(buffer)
                    buffer.clear()
            else:
                self._send_single(doc)

            self._queue.task_done()

        # 退出前把剩余的刷掉
        if self.config.bulk and buffer:
            self._flush_bulk(buffer)

    def _get_index_name(self) -> str:
        date_str = datetime.utcnow().strftime("%Y.%m.%d")
        return f"{self.config.index_prefix}-{date_str}"

    def _format_record(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        把 LogRecord 转为 JSON 文档。你可以根据自己习惯扩展字段。
        """
        # 基本字段
        doc: Dict[str, Any] = {
            "@timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app": self.config.app_name,
            "env": self.config.env,
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "process": record.process,
            "thread": record.thread,
        }

        # extra 字段：logging 调用时 logger.info("msg", extra={"user_id": 1})
        for key, value in record.__dict__.items():
            if key in (
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process"
            ):
                continue
            # 把 extra 下来的字段塞到 doc["extra"]
            doc.setdefault("extra", {})[key] = value

        # 异常信息
        if record.exc_info:
            try:
                doc["exception"] = "".join(
                    traceback.format_exception(*record.exc_info)
                )
            except Exception:
                # 最兜底，避免因为格式化异常再崩一次
                doc["exception"] = "Failed to format exception"

        return doc

    def _send_single(self, doc: Dict[str, Any]):
        index = self._get_index_name()
        url = f"{self.config.base_url}/{index}/_doc"

        try:
            resp = self._session.post(
                url,
                data=json.dumps(doc),
                headers={"Content-Type": "application/json"},
                timeout=self.config.timeout,
            )
            if resp.status_code >= 300:
                # 失败时，不抛异常避免死循环，用 print 简单输出
                print(f"[ElasticsearchHandler] failed to send log: {resp.status_code} {resp.text}")
        except Exception as e:
            # 为了避免循环日志，尽量不要再用 logging 打这类错误
            print(f"[ElasticsearchHandler] error sending log: {e}")

    def _flush_bulk(self, docs: List[Dict[str, Any]]):
        if not docs:
            return

        index = self._get_index_name()
        url = f"{self.config.base_url}/{index}/_bulk"
        # bulk 协议： action\nsource\naction\nsource\n...
        lines = []
        for d in docs:
            lines.append(json.dumps({"index": {}}))
            lines.append(json.dumps(d))
        body = "\n".join(lines) + "\n"

        try:
            resp = self._session.post(
                url,
                data=body,
                headers={"Content-Type": "application/x-ndjson"},
                timeout=self.config.timeout,
            )
            if resp.status_code >= 300:
                print(f"[ElasticsearchHandler] bulk failed: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"[ElasticsearchHandler] error bulk sending logs: {e}")


