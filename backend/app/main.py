from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base, engine, get_db
from app.models import AuditLog, Department, Workflow, WorkflowRun
from app.schemas import DepartmentOut, WorkflowCreate, WorkflowOut, RunOut

DEPARTMENTS = [
    ("MAX_ENERGY", "MAX Energy"),
    ("CONSTRUCTION", "MAX Myanmar Construction"),
    ("FINANCE", "Finance & Accounting"),
    ("LOGISTICS", "MAX Logistics"),
    ("GROUP_WIDE", "Group-wide RPA"),
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        for code, name in DEPARTMENTS:
            if not db.scalar(select(Department).where(Department.code == code)):
                db.add(Department(code=code, name=name))
        db.commit()
    yield

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])

@app.get("/", tags=["system"])
def root():
    return {"service": settings.app_name, "status": "running", "environment": settings.app_env, "api": settings.api_prefix}

@app.get("/health", tags=["system"])
def health():
    return {"status": "healthy", "database": "configured", "environment": settings.app_env}

@app.get(f"{settings.api_prefix}/departments", response_model=list[DepartmentOut], tags=["departments"])
def list_departments(db: Session = Depends(get_db)):
    return list(db.scalars(select(Department).order_by(Department.id)))

@app.get(f"{settings.api_prefix}/workflows", response_model=list[WorkflowOut], tags=["workflows"])
def list_workflows(db: Session = Depends(get_db)):
    return list(db.scalars(select(Workflow).order_by(Workflow.id.desc())))

@app.post(f"{settings.api_prefix}/workflows", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED, tags=["workflows"])
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)):
    if not db.get(Department, payload.department_id):
        raise HTTPException(status_code=404, detail="Department not found")
    workflow = Workflow(**payload.model_dump(), status="draft")
    db.add(workflow)
    db.flush()
    db.add(AuditLog(actor="bootstrap-user", action="workflow.created", resource_type="workflow", resource_id=str(workflow.id), details={"name": workflow.name}))
    db.commit()
    db.refresh(workflow)
    return workflow

@app.post(f"{settings.api_prefix}/workflows/{{workflow_id}}/test-run", response_model=RunOut, status_code=status.HTTP_201_CREATED, tags=["workflow-runs"])
def create_test_run(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.status != "active":
        raise HTTPException(status_code=409, detail="Only active workflows can be test-run")
    # Safe placeholder: no external systems or business data are touched in this starter.
    run = WorkflowRun(workflow_id=workflow.id, status="queued", message="Queued for a worker; execution adapter is not enabled.", result={"mode": "safe-placeholder", "external_actions": False})
    db.add(run)
    db.flush()
    db.add(AuditLog(actor="bootstrap-user", action="workflow.test_run.queued", resource_type="workflow_run", resource_id=str(run.id), details={"workflow_id": workflow.id}))
    db.commit()
    db.refresh(run)
    return run
