import os
import base64
import pathlib
import requests

def upload_to_workspace(local_file_path, workspace_dir_env="WORKSPACE_TARGET_DIR"):
    host = os.environ["DATABRICKS_HOST"].split("?")[0].rstrip("/")
    token = os.environ["DATABRICKS_TOKEN"]
    target_dir = os.getenv(workspace_dir_env, "/Workspace/Users/juanes.pelaez18@gmail.com").rstrip("/")

    filename = pathlib.Path(local_file_path).name
    workspace_path = f"{target_dir}/{filename}"

    with open(local_file_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    url = f"{host}/api/2.0/workspace/import"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "path": workspace_path,
        "format": "AUTO",
        "content": content_b64,
        "overwrite": True,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"Workspace upload failed ({r.status_code}): {r.text}")

    return workspace_path

def run_databricks_job():
    host = os.environ["DATABRICKS_HOST"].split("?")[0].rstrip("/")
    token = os.environ["DATABRICKS_TOKEN"]
    job_id = int(os.environ["DATABRICKS_JOB_ID"])

    url = f"{host}/api/2.1/jobs/run-now"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"job_id": job_id}

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"Run job failed ({r.status_code}): {r.text}")

    run_id = r.json().get("run_id")
    print(f"Databricks job triggered. run_id={run_id}")
    return run_id