import json
from typing import Any, Literal
from doc_store.interface import Task, TaskInput
from .doc_store import DocStore as DocStoreMongo, TaskEntity
from .redis_stream import RedisStreamProducer, RedisStreamConsumer
from .config import config

class DocStoreRedis(DocStoreMongo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = RedisStreamProducer()
        self.consumer_group = config.redis.consumer_group
        self.consumer_pool = {}

    def _get_or_create_consumer(self, stream: str) -> RedisStreamConsumer:
        key = f"{stream}:{self.consumer_group}"
        if key not in self.consumer_pool:
            self.consumer_pool[key] = RedisStreamConsumer(None, stream, self.consumer_group, create_group=True)
        return self.consumer_pool[key]
    
    def impersonate(self, username: str) -> "DocStoreRedis":
        """Impersonate another user for this DocStore instance."""
        # use __new__ to bypass __init__
        new_store = DocStoreRedis.__new__(DocStoreRedis)
        new_store.coll_docs = self.coll_docs
        new_store.coll_pages = self.coll_pages
        new_store.coll_layouts = self.coll_layouts
        new_store.coll_blocks = self.coll_blocks
        new_store.coll_contents = self.coll_contents
        new_store.coll_values = self.coll_values
        new_store.coll_tasks = self.coll_tasks
        new_store.coll_users = self.coll_users
        new_store.coll_known_names = self.coll_known_names
        new_store.coll_task_shortcuts = self.coll_task_shortcuts
        new_store.locker = self.locker
        new_store.counters = self.counters
        new_store.measure_time = self.measure_time
        new_store.times = {}
        new_store._event_sink = self._event_sink
        new_store.username = username
        new_store.writable = username in self.all_users
        new_store.producer = self.producer
        new_store.consumer_group = self.consumer_group
        new_store.consumer_pool = self.consumer_pool
        return new_store

    # TODO: priority
    def insert_task(self, target_id: str, task_input: TaskInput) -> Task:
        """Insert a new task into the database."""
        self._check_writable()
        if not target_id:
            raise ValueError("target_id must be provided.")
        if not isinstance(task_input, TaskInput):
            raise ValueError("task_input must be a TaskInput instance.")
        command = task_input.command
        if not command:
            raise ValueError("command must be a non-empty string.")
        args = task_input.args or {}
        if any(not isinstance(k, str) for k in args.keys()):
            raise ValueError("All keys in args must be strings.")

        if command.startswith("ddp."):
            # command is a handler path.
            command, args["path"] = "handler", command

        task_entity = {
            "target": target_id,
            "command": command,
            "args": json.dumps(args),
            "create_user": self.username,
        }

        result = self.producer.add(command, fields=task_entity)
        return Task(
                id=result,
                rid=0,
                status="new",
                target=task_entity["target"],
                command=task_entity["command"],
                args=args,
                create_user=task_entity["create_user"],
            )

    def grab_new_tasks(self, command: str, args: dict[str, Any] = {}, create_user: str | None = None, num=500, hold_sec=3600) -> list[Task]:
        consumer = self._get_or_create_consumer(command)
        messages = consumer.read_or_claim(num, min_idle_ms=hold_sec * 1000)

        tasks = []
        for message in messages:
            task_entity = message.fields
            task = Task(
                id=message.id,
                rid=0,
                status="new",
                target=task_entity["target"],
                command=task_entity["command"],
                args=json.loads(task_entity["args"]),
                create_user=task_entity["create_user"],
                grab_time=int(__import__("time").time() * 1000),  # 确保非 0，便于 update 校验
            )
            tasks.append(task)
        return tasks

    
    def update_task(
        self,
        task_id: str,
        grab_time: int,
        command: str,
        status: Literal["done", "error", "skipped"],
        error_message: str | None = None,
    ):
        """Update a task after processing."""
        self._check_writable()
        if not command:
            raise ValueError("command must be provided.")
        if not task_id:
            raise ValueError("task ID must be provided.")
        if not grab_time:
            raise ValueError("grab_time must be provided.")
        if status not in ("done", "error", "skipped"):
            raise ValueError("status must be one of 'done', 'error', or 'skipped'.")
        if status == "error" and not error_message:
            raise ValueError("error_message must be provided if status is 'error'.")

        consumer = self._get_or_create_consumer(command)
        consumer.ack([task_id])
        # TODO: persist task status

