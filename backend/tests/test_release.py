from fastapi.testclient import TestClient
import sys
sys.path.insert(0,"backend")
from app.main import app
c=TestClient(app)
H={"X-User-Id":"u1","X-Tenant-Id":"t1","X-Permissions":"work:create,work:execute,audit:read"}

def test_release_health():
    assert c.get("/health").json()["release"]=="16.0-rc1"

def test_governed_end_to_end():
    r=c.post("/v1/work",headers=H,json={"title":"RC workflow"})
    assert r.status_code==200
    wid=r.json()["id"]
    assert c.post(f"/v1/work/{wid}/execute",headers=H).status_code==200
    assert len(c.get("/v1/audit",headers=H).json())>=3

def test_cross_tenant_block():
    r=c.post("/v1/work",headers=H,json={"title":"Private"})
    wid=r.json()["id"]
    other={"X-User-Id":"u2","X-Tenant-Id":"t2","X-Permissions":"work:execute,audit:read"}
    assert c.post(f"/v1/work/{wid}/execute",headers=other).status_code==403

def test_policy_block():
    h={"X-User-Id":"u3","X-Tenant-Id":"t1","X-Permissions":""}
    assert c.post("/v1/work",headers=h,json={"title":"Blocked"}).status_code==403
