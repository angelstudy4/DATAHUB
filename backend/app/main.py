from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from uuid import uuid4
from typing import Optional
from .repository import Work, WorkRepository
from .policy import evaluate

app=FastAPI(title="DATAHUB",version="16.0-rc1")
repo=WorkRepository()
AUDIT=[]
OUTBOX=[]

class WorkCreate(BaseModel):
    title:str
    priority:str="medium"

def principal(
    x_user_id:Optional[str]=Header(default=None),
    x_tenant_id:Optional[str]=Header(default=None),
    x_permissions:Optional[str]=Header(default=None)
):
    if not x_user_id or not x_tenant_id:
        raise HTTPException(401,"AUTHENTICATION_REQUIRED")
    return {"id":x_user_id,"tenant_id":x_tenant_id,
            "permissions":x_permissions.split(",") if x_permissions else []}

def record(p, action, resource, decision, reason):
    e={"id":str(uuid4()),"tenant_id":p["tenant_id"],"actor_id":p["id"],
       "action":action,"resource_id":resource,"decision":decision,"reason":reason}
    AUDIT.append(e)
    OUTBOX.append({"type":"audit.recorded","payload":e})
    return e

@app.get("/health")
def health(): return {"status":"ok","release":"16.0-rc1"}

@app.post("/v1/work")
def create_work(payload:WorkCreate,p=Depends(principal)):
    result=evaluate("work:create",p["permissions"])
    if result.decision!="allow":
        record(p,"work.create","new",result.decision,result.reason)
        raise HTTPException(403,"POLICY_DENIED")
    wid=str(uuid4())
    w=repo.create(Work(wid,p["tenant_id"],payload.title,payload.priority))
    record(p,"work.create",wid,"allow","policy_satisfied")
    OUTBOX.append({"type":"work.created","payload":{"id":wid,"tenant_id":p["tenant_id"]}})
    return w.__dict__

@app.post("/v1/work/{wid}/execute")
def execute(wid:str,p=Depends(principal)):
    w=repo.get(wid)
    if not w: raise HTTPException(404,"WORK_NOT_FOUND")
    if w.tenant_id!=p["tenant_id"]: raise HTTPException(403,"TENANT_BOUNDARY_VIOLATION")
    result=evaluate("work:execute",p["permissions"],"normal")
    if result.decision!="allow":
        record(p,"work.execute",wid,result.decision,result.reason)
        raise HTTPException(403,"POLICY_DENIED")
    w.status="completed"; repo.update(w)
    record(p,"work.execute",wid,"allow","policy_satisfied")
    record(p,"work.verify",wid,"allow","execution_verified")
    OUTBOX.append({"type":"work.completed","payload":{"id":wid}})
    return w.__dict__

@app.get("/v1/audit")
def audit(p=Depends(principal)):
    result=evaluate("audit:read",p["permissions"])
    if result.decision!="allow": raise HTTPException(403,"POLICY_DENIED")
    return [x for x in AUDIT if x["tenant_id"]==p["tenant_id"]]

@app.get("/v1/events")
def events(p=Depends(principal)):
    result=evaluate("audit:read",p["permissions"])
    if result.decision!="allow": raise HTTPException(403,"POLICY_DENIED")
    return [x for x in OUTBOX if x["payload"].get("tenant_id")==p["tenant_id"] or
            x["payload"].get("id") in {a["resource_id"] for a in AUDIT if a["tenant_id"]==p["tenant_id"]}]
