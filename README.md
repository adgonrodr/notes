def kill_task(dag_id, dag_run_id, task_id):
    """
    Kill (clear) a specific task in a DAG run.
    """
    endpoint = f"{ASTRONOMER_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/clear"
    payload = {
        "only_failed": False,  # Clear task regardless of its state
        "reset_dag_runs": False  # Only reset this task, not the entire DAG run
    }

    response = requests.post(endpoint, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Successfully killed task {task_id} in DAG {dag_id} (Run ID: {dag_run_id})")
    else:
        print(f"Failed to kill task. Status Code: {response.status_code}")
        print(response.text)