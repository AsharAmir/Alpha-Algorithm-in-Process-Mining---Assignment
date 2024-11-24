import random
import json

def generate_event_log(process_description, num_traces, noise_level, uncommon_path_frequency, missing_event_probability):
    """
    Generate an event log based on the given process description and parameters.
    
    Args:
    - process_description (dict): Description of the process (tasks, order, dependencies, concurrency).
    - num_traces (int): Number of traces to generate.
    - noise_level (float): Probability of adding random noise.
    - uncommon_path_frequency (float): Probability of generating uncommon paths.
    - missing_event_probability (float): Probability of missing events in traces.
    
    Returns:
    - list: A list of generated traces (event log).
    """
    tasks = process_description["tasks"]
    dependencies = process_description["dependencies"]
    concurrency = process_description.get("concurrency", [])
    uncommon_paths = process_description.get("uncommon_paths", [])
    
    event_log = []
    
    for _ in range(num_traces):
        trace = []
        
        # Determine if this trace will use an uncommon path
        use_uncommon_path = random.random() < uncommon_path_frequency
        
        if use_uncommon_path and uncommon_paths:
            # Choose a random uncommon path
            trace = random.choice(uncommon_paths)
        else:
            # Generate a normal path based on dependencies and concurrency
            remaining_tasks = set(tasks)
            while remaining_tasks:
                available_tasks = [
                    task for task in remaining_tasks
                    if all(dep in trace for dep in dependencies.get(task, []))
                ]
                if concurrency:
                    concurrent_tasks = [
                        task for task in available_tasks if task in concurrency
                    ]
                    if concurrent_tasks:
                        selected_task = random.choice(concurrent_tasks)
                    else:
                        selected_task = random.choice(available_tasks)
                else:
                    selected_task = random.choice(available_tasks)
                
                trace.append(selected_task)
                remaining_tasks.remove(selected_task)
        
        # Simulate missing events
        trace = [
            task for task in trace
            if random.random() > missing_event_probability
        ]
        
        # Add noise
        if noise_level > 0:
            num_noisy_events = int(len(trace) * noise_level)
            for _ in range(num_noisy_events):
                noise_event = f"noise_{random.randint(1, 100)}"
                position = random.randint(0, len(trace))
                trace.insert(position, noise_event)
        
        event_log.append(trace)
    
    return event_log


# Example process description
process_description = {
    "tasks": ["A", "B", "C", "D", "E"],
    "dependencies": {"B": ["A"], "C": ["A"], "D": ["B", "C"], "E": ["D"]},
    "concurrency": ["B", "C"],
    "uncommon_paths": [["A", "C", "B", "D", "E"]]
}

# Parameters
num_traces = 50
noise_level = 0.1  # 10% of events are noise
uncommon_path_frequency = 0.2  # 20% of traces are uncommon paths
missing_event_probability = 0.1  # 10% chance of missing events in a trace

# Generate event log
event_log = generate_event_log(
    process_description, num_traces, noise_level, uncommon_path_frequency, missing_event_probability
)

# Save to JSON file
with open("event_log.json", "w") as f:
    json.dump(event_log, f, indent=4)

print("Event log generated and saved to 'event_log.json'.")