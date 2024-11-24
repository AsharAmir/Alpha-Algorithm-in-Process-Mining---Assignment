# Task 2: Alpha Algorithm Implementation

## **Overview**

This task involves implementing the Alpha Algorithm to discover a process model from an event log. The event log generated in Task 1 was used as input to extract process insights and construct a Petri net model. Below is the detailed explanation of the preprocessing steps, design choices, and model evaluation.

---

## **Preprocessing Steps**

1. **Event Log Loading**  
   The event log (`event_log.json`) was loaded into a Python list. Each trace in the log represented a sequence of events for a process instance.

2. **Unique Traces and Frequencies**  
   The traces were processed to identify unique event sequences and their frequencies. This step reduced redundancy, focusing on distinct process patterns and their occurrence rates.

3. **Extraction of Unique Events**
   - `TL`: Set of all unique events in the log.
   - `TI`: Set of all initial events (starting events of traces).
   - `TO`: Set of all final events (ending events of traces).  
     These sets defined the building blocks for constructing the process model.

---

## **Design Choices**

1. **Footprint Matrix**  
   A matrix was constructed to represent relationships between events using the following notations:

   - `→`: Event A directly follows event B.
   - `←`: Event B directly follows event A.
   - `||`: Event A and B occur concurrently.
   - `#`: No direct relation exists between A and B.

2. **Causal Relationships (`XL`)**  
   Causal relationships were extracted from the footprint matrix to identify sequences of events that determine the order of execution.

3. **Maximal Pairs (`YL`)**  
   Pairs of events occurring concurrently were identified to reflect parallelism in the process.

4. **Place Sets (`PL`) and Flow Relations (`FL`)**

   - Place sets linked causal relationships to define dependencies between events.
   - Flow relations connected transitions and places to define the flow of the process.

5. **Petri Net Construction**  
   The Petri net (`α(L)`) was built using the following components:
   - `TL`: Transitions (unique events).
   - `TI`: Initial marking (start places).
   - `TO`: Final marking (end places).
   - `YL`, `PL`, and `FL`: Relationships defining the structure and flow of the net.

---

## **Evaluation**

1. **Trace Representation**  
   Unique traces and their frequencies were displayed in a tabular format, ensuring accurate representation of the process instances in the log.

2. **Relationship Validation**  
   The causal relationships and footprint matrix were validated to confirm that they accurately captured dependencies, parallelism, and independence among events.

3. **Petri Net Model**  
   The final Petri net was evaluated for:
   - Correctness in representing the process flow from initial to final states.
   - Parallelism and concurrency in the process.
   - Adherence to the original event log structure.

The Alpha Algorithm successfully discovered a process model that captured the behavior and structure of the event log, providing an accurate and interpretable representation of the workflow.

---

## **Outputs**

- **Unique Traces and Frequencies**: Tabular representation of unique traces in the event log.
- **Footprint Matrix**: A clear representation of event relationships.
- **Causal and Maximal Relationships**: Sets describing dependencies and concurrency.
- **Petri Net Model**: A visual and functional model constructed from the discovered relationships.
