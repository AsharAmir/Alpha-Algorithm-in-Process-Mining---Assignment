import json
from collections import Counter, defaultdict
import pandas as pd
from tabulate import tabulate
from typing import Dict, Set, List, Tuple, Any
import logging
from datetime import datetime

class AlphaAlgorithm:
    """
    Implementation of the Alpha Algorithm for process mining.
    Discovers process models from event logs.
    """
    
    def __init__(self, log_path: str):
        """Initialize the Alpha Algorithm with an event log file path."""
        self.log_path = log_path
        self.event_log = None
        self.unique_traces = None
        self.trace_frequencies = None
        self.unique_events = None
        self.initial_events = None
        self.final_events = None
        self.footprint_matrix = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_event_log(self) -> None:
        """Load and validate the event log from the specified file."""
        try:
            with open(self.log_path, "r") as f:
                self.event_log = json.load(f)
                
            if not isinstance(self.event_log, list) or not self.event_log:
                raise ValueError("Event log must be a non-empty list of traces")
                
            # Extract just the task names from the event dictionaries
            self.event_log = [
                [event['task'] for event in trace]
                for trace in self.event_log
                if trace  # Skip empty traces
            ]
            
            self.logger.info(f"Successfully loaded {len(self.event_log)} traces")
        except Exception as e:
            self.logger.error(f"Error loading event log: {str(e)}")
            raise

    def extract_unique_traces(self) -> pd.DataFrame:
        """
        Extract unique traces and their frequencies from the event log.
        
        Returns:
            DataFrame containing unique traces and their frequencies
        """
        try:
            # Convert traces to tuples for counting
            traces = [tuple(trace) for trace in self.event_log]
            self.trace_frequencies = Counter(traces)
            
            # Create DataFrame for display
            df = pd.DataFrame(columns=["Trace", "Frequency", "Percentage"])
            total_traces = len(self.event_log)
            
            for trace, freq in self.trace_frequencies.items():
                percentage = (freq / total_traces) * 100
                df = pd.concat([df, pd.DataFrame({
                    "Trace": [" -> ".join(trace)],
                    "Frequency": [freq],
                    "Percentage": [f"{percentage:.2f}%"]
                })], ignore_index=True)
            
            df = df.sort_values("Frequency", ascending=False)
            self.unique_traces = df
            
            self.logger.info(f"Found {len(df)} unique traces")
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting unique traces: {str(e)}")
            raise

    def extract_event_sets(self) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Extract unique events (TL), initial events (TI), and final events (TO).
        
        Returns:
            Tuple of (unique_events, initial_events, final_events)
        """
        try:
            self.unique_events = set()
            self.initial_events = set()
            self.final_events = set()
            
            for trace in self.event_log:
                if trace:  # Skip empty traces
                    self.unique_events.update(trace)
                    self.initial_events.add(trace[0])
                    self.final_events.add(trace[-1])
            
            self.logger.info(
                f"Extracted {len(self.unique_events)} unique events, "
                f"{len(self.initial_events)} initial events, "
                f"{len(self.final_events)} final events"
            )
            
            return self.unique_events, self.initial_events, self.final_events
            
        except Exception as e:
            self.logger.error(f"Error extracting event sets: {str(e)}")
            raise

    def build_footprint_matrix(self) -> pd.DataFrame:
        """
        Construct the footprint matrix showing relationships between events.
        
        Returns:
            DataFrame containing the footprint matrix
        """
        try:
            # Build direct follow relationships
            follows = defaultdict(set)
            for trace in self.event_log:
                for i in range(len(trace) - 1):
                    follows[trace[i]].add(trace[i + 1])
            
            # Construct footprint matrix
            matrix_data = {}
            for a in sorted(self.unique_events):
                matrix_data[a] = {}
                for b in sorted(self.unique_events):
                    if b in follows[a] and a in follows[b]:
                        matrix_data[a][b] = "||"  # Parallel
                    elif b in follows[a]:
                        matrix_data[a][b] = "->"   # Causality
                    elif a in follows[b]:
                        matrix_data[a][b] = "<-"   # Reverse causality
                    else:
                        matrix_data[a][b] = "#"   # No relation
            
            self.footprint_matrix = pd.DataFrame(matrix_data)
            self.logger.info("Successfully built footprint matrix")
            return self.footprint_matrix
            
        except Exception as e:
            self.logger.error(f"Error building footprint matrix: {str(e)}")
            raise

    def extract_relationships(self) -> Dict[str, Set[Tuple[str, str]]]:
        """
        Extract causal relationships (XL), maximal pairs (YL), place set (PL), and flow relation (FL).
        
        Returns:
            Dictionary containing all relationship sets
        """
        try:
            relationships = {
                "causal": set(),
                "maximal": set(),
                "places": set(),
                "flow": set()
            }
            
            # Extract causal relationships (XL)
            for a in self.unique_events:
                for b in self.unique_events:
                    if self.footprint_matrix.loc[a, b] == "->":
                        relationships["causal"].add((a, b))
            
            # Extract maximal pairs (YL)
            for a in self.unique_events:
                for b in self.unique_events:
                    if self.footprint_matrix.loc[a, b] == "||":
                        relationships["maximal"].add((a, b))
            
            # Build place set (PL)
            for a, b in relationships["causal"]:
                relationships["places"].add((a, b))
            
            # Build flow relation (FL)
            relationships["flow"] = relationships["causal"].union(
                {(b, a) for a, b in relationships["causal"]}
            )
            
            self.relationships = relationships
            self.logger.info("Successfully extracted all relationships")
            return relationships
            
        except Exception as e:
            self.logger.error(f"Error extracting relationships: {str(e)}")
            raise

    def build_petri_net(self) -> Dict[str, Any]:
        """
        Build the Petri net model based on the extracted relationships.
        
        Returns:
            Dictionary containing the Petri net model components
        """
        try:
            petri_net = {
                "places": sorted(list(self.relationships["places"])),
                "transitions": sorted(list(self.unique_events)),
                "initial_marking": sorted(list(self.initial_events)),
                "final_marking": sorted(list(self.final_events)),
                "flow_relation": sorted(list(self.relationships["flow"]))
            }
            
            self.petri_net = petri_net
            self.logger.info("Successfully built Petri net model")
            return petri_net
            
        except Exception as e:
            self.logger.error(f"Error building Petri net: {str(e)}")
            raise

    def save_results(self, output_dir: str = "./") -> None:
        """Save all analysis results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            # Save unique traces
            self.unique_traces.to_csv(
                f"{output_dir}unique_traces_{timestamp}.csv",
                index=False
            )
            
            # Save footprint matrix
            self.footprint_matrix.to_csv(
                f"{output_dir}footprint_matrix_{timestamp}.csv"
            )
            
            # Save Petri net
            with open(f"{output_dir}petri_net_{timestamp}.json", "w") as f:
                json.dump(self.petri_net, f, indent=4)
            
            self.logger.info(f"All results saved to {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            raise

    def run_analysis(self) -> None:
        """Run the complete Alpha Algorithm analysis."""
        self.load_event_log()
        
        print("\n=== Unique Traces and Frequencies ===")
        df_traces = self.extract_unique_traces()
        print(tabulate(df_traces, headers='keys', tablefmt='psql'))
        
        print("\n=== Event Sets ===")
        unique, initial, final = self.extract_event_sets()
        print(f"Unique Events (TL): {sorted(unique)}")
        print(f"Initial Events (TI): {sorted(initial)}")
        print(f"Final Events (TO): {sorted(final)}")
        
        print("\n=== Footprint Matrix ===")
        matrix = self.build_footprint_matrix()
        print(tabulate(matrix, headers='keys', tablefmt='psql'))
        
        print("\n=== Relationships ===")
        relationships = self.extract_relationships()
        for name, rel_set in relationships.items():
            print(f"{name.title()}: {sorted(rel_set)}")
        
        print("\n=== Petri Net Model ===")
        petri_net = self.build_petri_net()
        print(json.dumps(petri_net, indent=2))
        
        # Save all results
        self.save_results()

if __name__ == "__main__":
    # Initialize and run the Alpha Algorithm
    alpha = AlphaAlgorithm("event_log.json")
    alpha.run_analysis()