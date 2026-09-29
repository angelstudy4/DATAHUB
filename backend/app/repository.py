from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Work:
    id: str
    tenant_id: str
    title: str
    priority: str
    status: str = "queued"

class WorkRepository:
    """Repository boundary. Replace InMemoryRepository with PostgreSQL adapter."""
    def __init__(self):
        self.items: Dict[str, Work] = {}

    def create(self, work: Work) -> Work:
        self.items[work.id] = work
        return work

    def get(self, work_id: str) -> Work | None:
        return self.items.get(work_id)

    def update(self, work: Work) -> Work:
        self.items[work.id] = work
        return work

    def list_tenant(self, tenant_id: str) -> List[Work]:
        return [w for w in self.items.values() if w.tenant_id == tenant_id]
