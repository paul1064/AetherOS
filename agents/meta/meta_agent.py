#!/usr/bin/env python3
# MIT License

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

def discover_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "config" / "aether.yaml").exists():
            return candidate
    raise RuntimeError("Unable to determine AetherOS project root")


PROJECT_ROOT = discover_project_root()
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from aether_core import (
    emit_event,
    fetch_meta_jobs,
    init_event_bus,
    load_config,
    record_system_event,
    sleep_loop,
    update_meta_job,
    write_agent_state,
)

LOG_PATH = PROJECT_ROOT / "runtime" / "logs" / "meta-agent.log"


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def running_jobs() -> int:
    return len(fetch_meta_jobs("running", limit=100))


def max_parallel_jobs() -> int:
    return int(load_config().raw["meta_agent"]["max_parallel_jobs"])


def build_subagent_image() -> None:
    image_name = str(load_config().raw["meta_agent"]["default_image"])
    proc = subprocess.run(
        [
            "podman",
            "build",
            "-t",
            image_name,
            "-f",
            str(PROJECT_ROOT / "containers" / "subagent-base" / "Containerfile"),
            str(PROJECT_ROOT),
        ],
        text=True,
        capture_output=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stdout + "\n" + proc.stderr).strip() or "subagent image build failed")


def launch_job(job: dict) -> None:
    job_id = int(job["id"])
    container_name = f"aether-subagent-{job_id}"
    runs_dir = Path(load_config().raw["meta_agent"]["runs_dir"])
    runs_dir.mkdir(parents=True, exist_ok=True)
    output_path = runs_dir / f"job-{job_id}.json"

    payload = {
        "job_id": job_id,
        "name": job["name"],
        "role": job["role"],
        "prompt": job["prompt"],
    }
    prompt_file = runs_dir / f"job-{job_id}-prompt.json"
    prompt_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    image_name = job["image_name"] or str(load_config().raw["meta_agent"]["default_image"])
    update_meta_job(job_id, "running", container_name=container_name, output_path=str(output_path))

    proc = subprocess.run(
        [
            "podman",
            "run",
            "-d",
            "--name",
            container_name,
            "-v",
            f"{runs_dir}:/runs",
            image_name,
            "/app/run_subagent.sh",
            f"/runs/{prompt_file.name}",
            f"/runs/{output_path.name}",
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        update_meta_job(job_id, "failed", notes=(proc.stdout + "\n" + proc.stderr).strip())
        raise RuntimeError((proc.stdout + "\n" + proc.stderr).strip() or "subagent launch failed")

    emit_event(
        "meta.job.started",
        "meta-agent",
        {"job_id": job_id, "container_name": container_name, "output_path": str(output_path)},
    )
    log(f"job started id={job_id} container={container_name}")


def reconcile_running_jobs() -> None:
    for job in fetch_meta_jobs("running", limit=100):
        container_name = job["container_name"]
        output_path = Path(job["output_path"]) if job["output_path"] else None
        proc = subprocess.run(
            ["podman", "ps", "-a", "--format", "{{.Names}} {{.Status}}"],
            text=True,
            capture_output=True,
            timeout=30,
        )
        ps_text = proc.stdout
        if container_name and container_name in ps_text and "Exited" not in ps_text:
            continue

        if output_path and output_path.exists():
            update_meta_job(int(job["id"]), "completed")
            emit_event(
                "meta.job.completed",
                "meta-agent",
                {"job_id": int(job["id"]), "output_path": str(output_path)},
            )
            log(f"job completed id={int(job['id'])}")
        else:
            update_meta_job(int(job["id"]), "failed", notes="container exited without output")
            emit_event("meta.job.failed", "meta-agent", {"job_id": int(job["id"])})
            log(f"job failed id={int(job['id'])}")


def main() -> None:
    init_event_bus()
    write_agent_state("meta-agent", "running", "running")
    log("meta_agent_started")
    try:
        build_subagent_image()
    except Exception as exc:
        record_system_event("meta-agent", "error", f"image_build_failed: {exc}")
        write_agent_state("meta-agent", "running", "degraded")

    while True:
        try:
            reconcile_running_jobs()
            if bool(load_config().raw["meta_agent"]["auto_start_queued_jobs"]):
                available_slots = max_parallel_jobs() - running_jobs()
                if available_slots > 0:
                    for job in fetch_meta_jobs("queued", limit=available_slots):
                        launch_job(dict(job))
            write_agent_state("meta-agent", "running", "running")
        except Exception as exc:
            message = f"meta_agent_cycle_failed: {exc}"
            log(message)
            record_system_event("meta-agent", "error", message)
            write_agent_state("meta-agent", "running", "degraded")
        sleep_loop(5)


if __name__ == "__main__":
    main()
