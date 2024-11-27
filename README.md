import requests
from datetime import datetime, timedelta

# Astronomer API Configuration
ASTRONOMER_API_URL = "https://<your-astronomer-instance>/api/v1"  # Replace with your Astronomer API URL
API_TOKEN = "your_api_token"  # Replace with your API token

# Headers for Authentication
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_active_dags():
    """
    Fetch all active DAGs using the Astronomer API.
    """
    endpoint = f"{ASTRONOMER_API_URL}/dags"
    response = requests.get(endpoint, headers=HEADERS)
    if response.status_code == 200:
        return [dag for dag in response.json().get("dags", []) if dag.get("is_paused") == False]
    else:
        print(f"Failed to fetch DAGs. Status Code: {response.status_code}")
        print(response.text)
        return None

def fetch_dag_runs(dag_id):
    """
    Fetch all DAG runs for a given DAG ID.
    """
    endpoint = f"{ASTRONOMER_API_URL}/dags/{dag_id}/dagRuns"
    response = requests.get(endpoint, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("dag_runs", [])
    else:
        print(f"Failed to fetch DAG runs for {dag_id}. Status Code: {response.status_code}")
        print(response.text)
        return None

def fetch_task_instances(dag_id, dag_run_id):
    """
    Fetch task instances for a specific DAG run.
    """
    endpoint = f"{ASTRONOMER_API_URL}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances"
    response = requests.get(endpoint, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("task_instances", [])
    else:
        print(f"Failed to fetch task instances for DAG Run {dag_run_id}. Status Code: {response.status_code}")
        print(response.text)
        return None

def check_long_running_tasks():
    """
    Check all active DAGs for tasks named 'success_task' running for more than 1 day.
    """
    dags = fetch_active_dags()
    if not dags:
        return

    current_time = datetime.utcnow()
    long_running_tasks = []

    for dag in dags:
        dag_id = dag["dag_id"]
        print(f"Checking DAG: {dag_id}")

        dag_runs = fetch_dag_runs(dag_id)
        if not dag_runs:
            continue

        for run in dag_runs:
            dag_run_id = run.get("run_id")
            if not dag_run_id:
                continue

            task_instances = fetch_task_instances(dag_id, dag_run_id)
            if not task_instances:
                continue

            for task in task_instances:
                if task["task_id"] == "success_task" and task["state"] == "running":
                    start_time = datetime.strptime(task["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    duration = current_time - start_time
                    if duration > timedelta(days=1):
                        long_running_tasks.append(
                            {
                                "dag_id": dag_id,
                                "run_id": dag_run_id,
                                "task_id": task["task_id"],
                                "start_time": task["start_date"],
                                "duration": str(duration),
                            }
                        )

    # Print the long-running tasks
    if long_running_tasks:
        print("\nTasks running for more than 1 day:")
        for task in long_running_tasks:
            print(
                f"DAG ID: {task['dag_id']}, Task ID: {task['task_id']}, "
                f"Run ID: {task['run_id']}, Start Time: {task['start_time']}, Duration: {task['duration']}"
            )
    else:
        print("\nNo tasks running for more than 1 day.")

# Main Execution
if __name__ == "__main__":
    check_long_running_tasks()