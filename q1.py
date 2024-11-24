import random
import json
import datetime
import uuid
from typing import Dict, List, Set, Optional

class EventLogGenerator:
    def __init__(self, process_description: Dict):
        """
        Initialize the event log generator with process description.
        
        Args:
            process_description: Dictionary containing process details
        """
        self.process = process_description
        self.validate_process_description()
        
    def validate_process_description(self):
        """Validate that the process description contains all required elements."""
        required_keys = {'tasks', 'dependencies', 'task_details'}
        if not all(key in self.process for key in required_keys):
            raise ValueError(f"Process description must contain: {required_keys}")
            
    def generate_timestamp(self, previous_timestamp: Optional[datetime.datetime] = None) -> str:
        """Generate a realistic timestamp for an event."""
        if previous_timestamp is None:
            base = datetime.datetime.now()
        else:
            # Add random duration between 1 minute and 2 hours
            base = previous_timestamp + datetime.timedelta(
                minutes=random.randint(1, 120)
            )
        return base.strftime("%Y-%m-%d %H:%M:%S")
        
    def generate_event(self, task: str, case_id: str, timestamp: str) -> Dict:
        """Generate a single event with all required attributes."""
        task_details = self.process['task_details'].get(task, {})
        resources = task_details.get('resources', ['system'])
        
        return {
            'case_id': case_id,
            'task': task,
            'timestamp': timestamp,
            'resource': random.choice(resources),
            'lifecycle': 'complete',
            'cost': round(random.uniform(
                task_details.get('min_cost', 10),
                task_details.get('max_cost', 100)
            ), 2)
        }

    def generate_noise_event(self, case_id: str, timestamp: str) -> Dict:
        """Generate a noise event that doesn't belong to the actual process."""
        noise_tasks = [
            f"System_Check_{random.randint(1,100)}",
            f"Manual_Review_{random.randint(1,100)}",
            f"Data_Update_{random.randint(1,100)}"
        ]
        return self.generate_event(random.choice(noise_tasks), case_id, timestamp)

    def get_available_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """Get tasks whose dependencies have been satisfied."""
        available = []
        for task in self.process['tasks']:
            if task not in completed_tasks:
                dependencies = self.process['dependencies'].get(task, [])
                if all(dep in completed_tasks for dep in dependencies):
                    available.append(task)
        return available

    def generate_trace(self, 
                      use_uncommon_path: bool,
                      noise_level: float,
                      missing_event_prob: float) -> List[Dict]:
        """Generate a single trace (sequence of events)."""
        case_id = str(uuid.uuid4())
        trace = []
        timestamp = None
        completed_tasks = set()

        # Choose between normal and uncommon path
        if use_uncommon_path and 'uncommon_paths' in self.process:
            path = random.choice(self.process['uncommon_paths'])
        else:
            # Generate normal path considering dependencies and concurrency
            path = []
            while len(completed_tasks) < len(self.process['tasks']):
                available = self.get_available_tasks(completed_tasks)
                if not available:
                    break
                    
                # Handle concurrent tasks
                concurrent_tasks = [t for t in available 
                                 if t in self.process.get('concurrency', [])]
                if concurrent_tasks:
                    task = random.choice(concurrent_tasks)
                else:
                    task = random.choice(available)
                    
                path.append(task)
                completed_tasks.add(task)

        # Generate events for the path
        for task in path:
            # Check for missing events
            if random.random() < missing_event_prob:
                continue
                
            timestamp = self.generate_timestamp(
                previous_timestamp=timestamp and datetime.datetime.strptime(
                    timestamp, "%Y-%m-%d %H:%M:%S"
                )
            )
            trace.append(self.generate_event(task, case_id, timestamp))

        # Add noise events
        if noise_level > 0:
            num_noise = int(len(trace) * noise_level)
            for _ in range(num_noise):
                timestamp = self.generate_timestamp(
                    previous_timestamp=timestamp and datetime.datetime.strptime(
                        timestamp, "%Y-%m-%d %H:%M:%S"
                    )
                )
                noise_event = self.generate_noise_event(case_id, timestamp)
                insert_pos = random.randint(0, len(trace))
                trace.insert(insert_pos, noise_event)

        return trace

    def generate_log(self,
                    num_traces: int,
                    noise_level: float = 0.1,
                    uncommon_path_freq: float = 0.2,
                    missing_event_prob: float = 0.1) -> List[List[Dict]]:
        """Generate complete event log with specified parameters."""
        event_log = []
        
        for _ in range(num_traces):
            use_uncommon_path = random.random() < uncommon_path_freq
            trace = self.generate_trace(
                use_uncommon_path,
                noise_level,
                missing_event_prob
            )
            event_log.append(trace)
            
        return event_log

# Sample process description
sample_process = {
    "tasks": ["Register", "Review", "Validate", "Process", "Notify", "Archive"],
    "dependencies": {
        "Review": ["Register"],
        "Validate": ["Register"],
        "Process": ["Review", "Validate"],
        "Notify": ["Process"],
        "Archive": ["Notify"]
    },
    "concurrency": ["Review", "Validate"],
    "uncommon_paths": [
        ["Register", "Validate", "Review", "Process", "Notify", "Archive"],
        ["Register", "Review", "Validate", "Process", "Archive", "Notify"]
    ],
    "task_details": {
        "Register": {
            "resources": ["clerk", "system"],
            "min_cost": 10,
            "max_cost": 30
        },
        "Review": {
            "resources": ["senior_clerk", "supervisor"],
            "min_cost": 40,
            "max_cost": 80
        },
        "Validate": {
            "resources": ["system", "specialist"],
            "min_cost": 30,
            "max_cost": 60
        },
        "Process": {
            "resources": ["processor", "system"],
            "min_cost": 50,
            "max_cost": 100
        },
        "Notify": {
            "resources": ["system"],
            "min_cost": 5,
            "max_cost": 15
        },
        "Archive": {
            "resources": ["system", "clerk"],
            "min_cost": 20,
            "max_cost": 40
        }
    }
}

# Generate and save event log
if __name__ == "__main__":
    # Initialize generator
    generator = EventLogGenerator(sample_process)
    
    # Generate log with parameters
    event_log = generator.generate_log(
        num_traces=50,
        noise_level=0.1,  # 10% noise events
        uncommon_path_freq=0.2,  # 20% uncommon paths
        missing_event_prob=0.1  # 10% chance of missing events
    )
    
    # Save to JSON file
    output_file = "event_log.json"
    with open(output_file, "w") as f:
        json.dump(event_log, f, indent=2)
    
    print(f"Generated {len(event_log)} traces and saved to '{output_file}'")
    
    # Print sample trace for verification
    print("\nSample trace:")
    for event in event_log[0]:
        print(f"Task: {event['task']}, Time: {event['timestamp']}, Resource: {event['resource']}")