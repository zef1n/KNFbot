import time
from collections import defaultdict

from aiogram import BaseMiddleware


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0, cleanup_interval: float = 60.0):
        self.limit = limit
        self.cleanup_interval = cleanup_interval
        self.users: dict[int, float] = defaultdict(float)
        self._last_cleanup = time.time()

    def _cleanup(self, now: float) -> None:
        if now - self._last_cleanup < self.cleanup_interval:
            return
        cutoff = now - self.cleanup_interval
        for uid in [uid for uid, ts in self.users.items() if ts < cutoff]:
            del self.users[uid]
        self._last_cleanup = now

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)

        now = time.time()
        self._cleanup(now)

        if now - self.users[user.id] < self.limit:
            return

        self.users[user.id] = now
        return await handler(event, data)
