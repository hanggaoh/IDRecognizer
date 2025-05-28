def example_task(x, y):
    print(f"Running example_task with {x} and {y}")

TASK_REGISTRY = {
    "example_task": example_task,
    # Add more tasks here
}