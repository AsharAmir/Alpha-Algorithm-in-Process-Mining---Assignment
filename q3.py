import json
import os
from graphviz import Digraph
from typing import Dict, Any
import glob
from datetime import datetime

class PetriNetVisualizer:
    """
    Visualizes Petri nets using Graphviz with enhanced visual features
    and automatic latest file detection.
    """
    
    def __init__(self):
        """Initialize the PetriNet visualizer with default styles."""
        self.styles = {
            'transition': {
                'shape': 'rectangle',
                'style': 'filled',
                'fillcolor': 'lightgreen',
                'height': '0.6',
                'width': '1.2',
                'fontname': 'Arial'
            },
            'place': {
                'shape': 'circle',
                'style': 'filled',
                'fillcolor': 'lightblue',
                'height': '0.6',
                'width': '0.6',
                'fontname': 'Arial'
            },
            'initial_place': {
                'shape': 'circle',
                'style': 'filled',
                'fillcolor': 'lightgray',
                'height': '0.6',
                'width': '0.6',
                'peripheries': '2',
                'fontname': 'Arial'
            },
            'final_place': {
                'shape': 'circle',
                'style': 'filled',
                'fillcolor': 'lightpink',
                'height': '0.6',
                'width': '0.6',
                'peripheries': '2',
                'fontname': 'Arial'
            }
        }
        
    def find_latest_petri_net(self, directory: str = "./") -> str:
        """Find the most recent Petri net file in the specified directory."""
        # Look for both .txt and .json files
        files = glob.glob(os.path.join(directory, "petri_net_*.json"))
        files.extend(glob.glob(os.path.join(directory, "petri_net.txt")))
        
        if not files:
            raise FileNotFoundError("No Petri net files found in the specified directory")
            
        # Get the most recent file
        latest_file = max(files, key=os.path.getmtime)
        print(f"Using latest Petri net file: {latest_file}")
        return latest_file

    def load_petri_net(self, file_path: str = None) -> Dict[str, Any]:
        """Load the Petri net model from the specified file or find the latest one."""
        try:
            if file_path is None:
                file_path = self.find_latest_petri_net()
                
            with open(file_path, "r") as f:
                petri_net = json.load(f)
                
            # Convert keys to lowercase for consistency
            return {k.lower(): v for k, v in petri_net.items()}
            
        except Exception as e:
            raise Exception(f"Error loading Petri net: {str(e)}")

    def create_visualization(self, petri_net: Dict[str, Any]) -> Digraph:
        """Create a Graphviz visualization of the Petri net."""
        dot = Digraph(comment='Petri Net Visualization')
        dot.attr(rankdir='LR')  # Left to Right layout
        dot.attr('node', fontsize='12')
        dot.attr('edge', fontsize='10')
        
        # Add initial place
        dot.node('start', '', **self.styles['initial_place'])
        
        # Add final place
        dot.node('end', '', **self.styles['final_place'])
        
        # Add transitions
        for t in petri_net['transitions']:
            dot.node(f"T_{t}", t, **self.styles['transition'])
            
        # Add places for each flow relation
        seen_places = set()
        for source, target in petri_net['flow_relation']:
            place_id = f"P_{source}_{target}"
            if place_id not in seen_places:
                dot.node(place_id, '', **self.styles['place'])
                seen_places.add(place_id)
        
        # Add edges for initial transitions
        for t in petri_net['initial_marking']:
            dot.edge('start', f"T_{t}")
            
        # Add edges for final transitions
        for t in petri_net['final_marking']:
            dot.edge(f"T_{t}", 'end')
            
        # Add edges for flow relations
        for source, target in petri_net['flow_relation']:
            place_id = f"P_{source}_{target}"
            dot.edge(f"T_{source}", place_id)
            dot.edge(place_id, f"T_{target}")
            
        return dot

    def generate_legend(self) -> Digraph:
        """Create a legend subgraph explaining the symbols."""
        legend = Digraph('cluster_legend')
        legend.attr(label='Legend', labeljust='l')
        
        # Add legend items
        legend.node('L_trans', 'Activity', **self.styles['transition'])
        legend.node('L_place', 'Place', **self.styles['place'])
        legend.node('L_init', 'Start', **self.styles['initial_place'])
        legend.node('L_final', 'End', **self.styles['final_place'])
        
        # Arrange legend items vertically
        legend.attr(rankdir='TB')
        
        return legend

    def visualize(self, output_path: str = "petri_net_visualization") -> None:
        """
        Create and save the complete Petri net visualization.
        
        Args:
            output_path: Base path for the output files (without extension)
        """
        try:
            # Load the Petri net
            petri_net = self.load_petri_net()
            
            # Create main graph
            main_graph = self.create_visualization(petri_net)
            
            # Create legend
            legend = self.generate_legend()
            
            # Combine main graph and legend
            combined = Digraph()
            combined.attr(rankdir='LR')
            
            with combined.subgraph(name='cluster_main') as main:
                main.attr(label='Process Model')
                for line in main_graph.body:
                    main.body.append(line)
                    
            with combined.subgraph(name='cluster_legend') as leg:
                for line in legend.body:
                    leg.body.append(line)
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{output_path}_{timestamp}"
            
            # Render in multiple formats
            combined.render(output_filename, format='png', cleanup=True)
            combined.render(output_filename, format='pdf', cleanup=True)
            
            print(f"Visualization saved as '{output_filename}.png' and '{output_filename}.pdf'")
            
        except Exception as e:
            print(f"Error during visualization: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        visualizer = PetriNetVisualizer()
        visualizer.visualize()
    except Exception as e:
        print(f"An error occurred: {str(e)}")