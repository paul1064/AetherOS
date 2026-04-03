#!/home/miqua/Desktop/pcfAI/.venv/bin/python
# MIT License

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aether_core import (
    approve_proposal,
    create_meta_job,
    emit_event,
    fetch_agent_states,
    fetch_model,
    fetch_meta_job,
    fetch_meta_jobs,
    fetch_proposal,
    list_entities,
    list_governance_profiles,
    list_models,
    latest_plan,
    latest_proposal,
    latest_resource_sample,
    load_memory_graph,
    load_config,
    recent_audit,
    recent_long_term_memories,
    recent_events,
    recent_remediations,
    recent_system_events,
    reject_proposal,
    search_long_term_memory,
    update_governance_profile,
)

PROJECT_ROOT = Path("/home/miqua/Desktop/pcfAI")
app = FastAPI(title="AetherOS Local Control API", version="0.4.0")


class SubmitPromptRequest(BaseModel):
    text: str


class NoteRequest(BaseModel):
    note: str = ""


class SpeechRequest(BaseModel):
    audio_path: str


class MetaJobRequest(BaseModel):
    name: str = "subagent-job"
    role: str = "general"
    prompt: str
    image_name: str = ""
    notes: str = ""


class MemorySearchRequest(BaseModel):
    query: str


class GovernanceProfileRequest(BaseModel):
    source_name: str
    capability_profile: str


class ModelPullRequest(BaseModel):
    model_name: str


def row_to_dict(row: Any) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/status")
def status() -> dict[str, Any]:
    return {
        "agents": [dict(row) for row in fetch_agent_states()],
        "latest_plan": latest_plan(),
        "latest_proposal": row_to_dict(latest_proposal()),
        "latest_resource_sample": row_to_dict(latest_resource_sample()),
        "recent_remediations": [dict(row) for row in recent_remediations()],
        "recent_system_events": [dict(row) for row in recent_system_events()],
        "recent_events": [dict(row) for row in recent_events(10)],
    }


@app.post("/shell/submit")
def shell_submit(request: SubmitPromptRequest) -> dict[str, str]:
    emit_event("user.prompt.received", "aether-api", {"text": request.text})
    return {"status": "queued", "text": request.text}


@app.get("/plans/latest")
def plans_latest() -> dict[str, Any]:
    plan = latest_plan()
    if not plan:
        raise HTTPException(status_code=404, detail="No plan available")
    return plan


@app.get("/proposals/latest")
def proposals_latest() -> dict[str, Any]:
    proposal = latest_proposal()
    if proposal is None:
        raise HTTPException(status_code=404, detail="No proposal available")
    return dict(proposal)


@app.get("/proposals/{proposal_id}")
def proposal_get(proposal_id: int) -> dict[str, Any]:
    proposal = fetch_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return dict(proposal)


@app.post("/proposals/{proposal_id}/approve")
def proposal_approve(proposal_id: int, request: NoteRequest) -> dict[str, Any]:
    if not approve_proposal(proposal_id, request.note):
        raise HTTPException(status_code=404, detail="Proposal not found")
    emit_event("proposal.approved", "aether-api", {"proposal_id": proposal_id, "note": request.note})
    return {"status": "approved", "proposal_id": proposal_id}


@app.post("/proposals/{proposal_id}/reject")
def proposal_reject(proposal_id: int, request: NoteRequest) -> dict[str, Any]:
    if not reject_proposal(proposal_id, request.note):
        raise HTTPException(status_code=404, detail="Proposal not found")
    emit_event("proposal.rejected", "aether-api", {"proposal_id": proposal_id, "note": request.note})
    return {"status": "rejected", "proposal_id": proposal_id}


@app.post("/multimodal/screenshot")
def multimodal_screenshot() -> dict[str, Any]:
    result = subprocess.run(
        [str(PROJECT_ROOT / "bin" / "aether-screenshot")],
        text=True,
        capture_output=True,
        timeout=120,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=output or "screenshot failed")
    return {"status": "ok", "output": output}


@app.post("/multimodal/stt")
def multimodal_stt(request: SpeechRequest) -> dict[str, Any]:
    result = subprocess.run(
        [str(PROJECT_ROOT / "bin" / "aether-stt"), request.audio_path],
        text=True,
        capture_output=True,
        timeout=300,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=output or "stt failed")
    return {"status": "ok", "output": output}


@app.get("/config")
def config() -> dict[str, Any]:
    return load_config().raw


@app.post("/meta/jobs")
def meta_job_create(request: MetaJobRequest) -> dict[str, Any]:
    job_id = create_meta_job(
        name=request.name,
        role=request.role,
        prompt=request.prompt,
        image_name=request.image_name,
        notes=request.notes,
    )
    emit_event("meta.job.queued", "aether-api", {"job_id": job_id, "name": request.name, "role": request.role})
    return {"status": "queued", "job_id": job_id}


@app.get("/meta/jobs")
def meta_job_list(status: str | None = None) -> list[dict[str, Any]]:
    return [dict(row) for row in fetch_meta_jobs(status=status, limit=50)]


@app.get("/meta/jobs/{job_id}")
def meta_job_get(job_id: int) -> dict[str, Any]:
    row = fetch_meta_job(job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Meta job not found")
    return dict(row)


@app.get("/memory/recent")
def memory_recent(limit: int = 20) -> list[dict[str, Any]]:
    return [dict(row) for row in recent_long_term_memories(limit=limit)]


@app.post("/memory/search")
def memory_search(request: MemorySearchRequest) -> list[dict[str, Any]]:
    return [dict(row) for row in search_long_term_memory(request.query, limit=20)]


@app.get("/memory/entities")
def memory_entities(limit: int = 30) -> list[dict[str, Any]]:
    return [dict(row) for row in list_entities(limit=limit)]


@app.get("/memory/graph")
def memory_graph() -> dict[str, Any]:
    return load_memory_graph()


@app.get("/governance/profiles")
def governance_profiles() -> list[dict[str, Any]]:
    return [dict(row) for row in list_governance_profiles()]


@app.post("/governance/profiles")
def governance_profile_update(request: GovernanceProfileRequest) -> dict[str, Any]:
    update_governance_profile(request.source_name, request.capability_profile)
    emit_event(
        "governance.profile.updated",
        "aether-api",
        {"source_name": request.source_name, "capability_profile": request.capability_profile},
    )
    return {"status": "updated", "source_name": request.source_name, "capability_profile": request.capability_profile}


@app.get("/governance/audit")
def governance_audit(limit: int = 30) -> list[dict[str, Any]]:
    return [dict(row) for row in recent_audit(limit=limit)]


@app.get("/models")
def models_list() -> list[dict[str, Any]]:
    return [dict(row) for row in list_models()]


@app.get("/models/{model_name}")
def model_get(model_name: str) -> dict[str, Any]:
    row = fetch_model(model_name)
    if row is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return dict(row)


@app.post("/models/pull")
def models_pull(request: ModelPullRequest) -> dict[str, Any]:
    result = subprocess.run(
        [str(PROJECT_ROOT / "bin" / "aether-models"), "--pull", request.model_name],
        text=True,
        capture_output=True,
        timeout=7200,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=output or "model pull failed")
    return {"status": "ok", "model_name": request.model_name, "output": output}


@app.get("/verify")
def verify() -> dict[str, Any]:
    result = subprocess.run(
        [str(PROJECT_ROOT / "bin" / "aether-verify"), "--json"],
        text=True,
        capture_output=True,
        timeout=180,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=output or "verification failed")
    return json.loads(output)


@app.post("/reports/export")
def reports_export() -> dict[str, Any]:
    result = subprocess.run(
        [str(PROJECT_ROOT / "bin" / "aether-report")],
        text=True,
        capture_output=True,
        timeout=300,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=output or "report export failed")
    return {"status": "ok", "path": output}


@app.get("/release/manifest")
def release_manifest() -> dict[str, Any]:
    manifest_path = PROJECT_ROOT / "RELEASE_MANIFEST.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="release manifest not found")
    return json.loads(manifest_path.read_text(encoding="utf-8"))
