import os
import json
from collections import defaultdict
import random


def load_event_log(file_path):
    """
    Load the event log from a JSON file.
    """
    with open(file_path, "r") as f:
        return json.load(f)


def preprocess_event_log(raw_event_log):
    """
    Extract the sequence of 'task' names from the raw event log.

    Args:
    - raw_event_log: List of traces, where each trace is a list of dictionaries.

    Returns:
    - List of traces, where each trace is a list of task names.
    """
    processed_event_log = []
    for trace in raw_event_log:
        processed_trace = [event["task"] for event in trace]  # Extract 'task' field
        processed_event_log.append(processed_trace)
    return processed_event_log


def fetch_latest_petri_net(directory="."):
    """
    Fetch the latest Petri net JSON file based on the timestamp in the filename.

    Args:
    - directory (str): Directory to search for Petri net files.

    Returns:
    - dict: Parsed JSON content of the latest Petri net file.
    """
    petri_net_files = [f for f in os.listdir(directory) if f.startswith("petri_net") and f.endswith(".json")]
    if not petri_net_files:
        raise FileNotFoundError("No Petri net JSON files found in the directory.")
    
    # Sort files by timestamp in the filename
    latest_file = max(petri_net_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    print(f"Using latest Petri net file: {latest_file}")
    
    # Load the latest Petri net JSON
    with open(os.path.join(directory, latest_file), "r") as f:
        petri_net = json.load(f)
    return petri_net


def calculate_fitness(petri_net, traces):
    """
    Calculate the fitness of the Petri net with respect to the given traces.
    """
    total_fitness = 0
    valid_traces = 0
    for trace in traces:
        if not trace:  # Skip empty traces
            continue
        marking = set(petri_net["initial_marking"])  # Use set for marking
        trace_fitness = 0
        for event in trace:
            if event in marking:
                trace_fitness += 1
                marking = set([place[1] for place in petri_net["flow_relation"] if place[0] == event])
            else:
                break
        total_fitness += trace_fitness / len(trace)
        valid_traces += 1
    return total_fitness / valid_traces if valid_traces > 0 else 0


def calculate_precision(petri_net, traces):
    """
    Calculate the precision of the Petri net with respect to the given traces.
    """
    allowed_behavior = defaultdict(set)
    observed_behavior = defaultdict(set)
    
    for trace in traces:
        for i in range(len(trace) - 1):
            observed_behavior[trace[i]].add(trace[i + 1])
    
    for source, target in petri_net["flow_relation"]:
        allowed_behavior[source].add(target)
    
    precision_sum = 0
    for event in allowed_behavior:
        if event in observed_behavior:
            precision_sum += len(observed_behavior[event]) / len(allowed_behavior[event])
    
    return precision_sum / len(allowed_behavior) if allowed_behavior else 0


def calculate_simplicity(petri_net):
    """
    Calculate the simplicity of the Petri net.
    """
    num_places = len(petri_net["places"])
    num_transitions = len(petri_net["transitions"])
    num_arcs = len(petri_net["flow_relation"])
    return 1 / (num_places + num_transitions + num_arcs)


def generate_test_traces(petri_net, num_traces, max_length=10, min_length=1):
    """
    Generate test traces based on the Petri net.
    """
    test_traces = []
    for _ in range(num_traces):
        trace = []
        marking = set(petri_net["initial_marking"])
        for _ in range(max_length):
            possible_events = [event for event in petri_net["transitions"] if event in marking]
            if not possible_events or (len(trace) >= min_length and random.random() < 0.1):  # 10% chance to end trace early, but ensure minimum length
                break
            event = random.choice(possible_events)
            trace.append(event)
            marking = set([place[1] for place in petri_net["flow_relation"] if place[0] == event])
        if trace:  # Only add non-empty traces
            test_traces.append(trace)
    return test_traces


if __name__ == "__main__":
    try:
        # Load the raw event log
        raw_event_log = load_event_log("event_log.json")
        
        # Preprocess the event log to extract task names
        event_log = preprocess_event_log(raw_event_log)
        
        # Fetch the latest Petri net model
        petri_net = fetch_latest_petri_net()
        
        # Generate additional test traces
        test_traces = generate_test_traces(petri_net, 20)
        
        # Calculate fitness, precision, and simplicity
        fitness = calculate_fitness(petri_net, event_log)
        precision = calculate_precision(petri_net, event_log)
        simplicity = calculate_simplicity(petri_net)
        test_fitness = calculate_fitness(petri_net, test_traces)
        test_precision = calculate_precision(petri_net, test_traces)
        
        # Display the results
        print(f"Model Fitness (Event Log): {fitness:.2f}")
        print(f"Model Precision (Event Log): {precision:.2f}")
        print(f"Model Simplicity: {simplicity:.2f}")
        print(f"Model Fitness (Test Traces): {test_fitness:.2f}")
        print(f"Model Precision (Test Traces): {test_precision:.2f}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
