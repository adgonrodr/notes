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

# Function to fetch running tasks
def fetch_running_tasks():
    """
    Fetch all running tasks using the Astronomer API.
    """
    endpoint = f"{ASTRONOMER_API_URL}/dags"
    response = requests.get(endpoint, headers=HEADERS)

    if response.status_code == 200:
        return response.json()  # Return the response as JSON
    else:
        print(f"Failed to fetch DAGs. Status Code: {response.status_code}")
        print(response.text)
        return None

# Function to check for tasks running more than a day
def check_long_running_tasks():
    """
    Check for tasks with the name 'success_task' running for more than 1 day.
    """
    tasks = fetch_running_tasks()
    if not tasks:
        return

    # Get the current timestamp
    current_time = datetime.utcnow()

    long_running_tasks = []

    for dag in tasks.get("dags", []):
        dag_id = dag["dag_id"]
        task_endpoint = f"{ASTRONOMER_API_URL}/dags/{dag_id}/dagRuns"
        task_response = requests.get(task_endpoint, headers=HEADERS)

        if task_response.status_code == 200:
            dag_runs = task_response.json()

            for run in dag_runs:
                for task in run.get("task_instances", []):
                    if (
                        task["task_id"] == "success_task"  # Check for task name
                        and task["state"] == "running"  # Ensure it's running
                    ):
                        start_time = datetime.strptime(task["start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        duration = current_time - start_time

                        if duration > timedelta(days=1):
                            long_running_tasks.append(
                                {
                                    "dag_id": dag_id,
                                    "run_id": run["run_id"],
                                    "task_id": task["task_id"],
                                    "start_time": task["start_date"],
                                    "duration": str(duration),
                                }
                            )

    # Print long-running tasks
    if long_running_tasks:
        print("Tasks running more than 1 day:")
        for task in long_running_tasks:
            print(f"DAG ID: {task['dag_id']}, Task ID: {task['task_id']}, "
                  f"Run ID: {task['run_id']}, Start Time: {task['start_time']}, Duration: {task['duration']}")
    else:
        print("No tasks running for more than 1 day.")

# Run the script
if __name__ == "__main__":
    check_long_running_tasks()