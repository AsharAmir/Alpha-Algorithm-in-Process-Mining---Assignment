import json
from collections import Counter, defaultdict
import pandas as pd
from tabulate import tabulate


def loadEventLog(filePath):
    with open(filePath, "r") as f:
        return json.load(f)


# Step 1: extracting unique traces from event logs 
def getUniqueTraces(eventLog):
    traces = [tuple(trace) for trace in eventLog]
    traceFreq = Counter(traces)
    return traceFreq


def displayUniqueTraces(traceFreq):
    df = pd.DataFrame(traceFreq.items(), columns=["Trace", "Frequency"])
    df["Trace"] = df["Trace"].apply(lambda x: " → ".join(x))
    print("\nUnique Traces and Frequencies:")
    print(tabulate(df, headers='keys', tablefmt='psql'))
    return df


# Step 2: extract unique events, initial events, and final events
def getUniqueEvents(eventLog):
    uniqueEvents = set()
    initialEvents = set()
    finalEvents = set()
    
    for trace in eventLog:
        if trace:
            uniqueEvents.update(trace)
            initialEvents.add(trace[0])
            finalEvents.add(trace[-1])
    
    return uniqueEvents, initialEvents, finalEvents


# Step 3: generating the footprint matrix
def buildFootprintMatrix(eventLog, uniqueEvents):
    follows = defaultdict(set)
    for trace in eventLog:
        for i in range(len(trace) - 1):
            follows[trace[i]].add(trace[i + 1])

    footprint = {}
    for a in uniqueEvents:
        for b in uniqueEvents:
            if b in follows[a] and a in follows[b]:
                footprint[(a, b)] = "#"
            elif b in follows[a]:
                footprint[(a, b)] = "→"
            elif a in follows[b]:
                footprint[(a, b)] = "←"
            else:
                footprint[(a, b)] = "||"
    return footprint


# Step 4: generating causal relationships, maximal pairs, place set, and flow relation
def extractRelationships(footprint, uniqueEvents):
    causalRelations = set((a, b) for (a, b), relation in footprint.items() if relation == "→")
    maximalPairs = set((a, b) for (a, b), relation in footprint.items() if relation == "||")
    
    placeSet = set()
    for a in uniqueEvents:
        for b in uniqueEvents:
            if (a, b) in causalRelations:
                placeSet.add((a, b))
    
    flowRelation = causalRelations.union({(b, a) for a, b in causalRelations})
    return causalRelations, maximalPairs, placeSet, flowRelation


# Step 5: building the Petri net model
def buildPetriNet(tl, ti, to, yl, pl, fl):
    petriNet = {
        "Places": list(pl),
        "Transitions": list(tl),
        "Initial Marking": list(ti),
        "Final Marking": list(to),
        "Flow Relation": list(fl)
    }
    return petriNet


if __name__ == "__main__":
    eventLog = loadEventLog("event_log.json")

    traceFreq = getUniqueTraces(eventLog)
    displayUniqueTraces(traceFreq)
    
    uniqueEvents, initialEvents, finalEvents = getUniqueEvents(eventLog)
    print("\nUnique Events (TL):", sorted(uniqueEvents))
    print("Initial Events (TI):", sorted(initialEvents))
    print("Final Events (TO):", sorted(finalEvents))
    
    footprint = buildFootprintMatrix(eventLog, uniqueEvents)
    print("\nFootprint Matrix:")
    footprintMatrix = pd.DataFrame(
        [[footprint[(a, b)] for b in sorted(uniqueEvents)] for a in sorted(uniqueEvents)],
        index=sorted(uniqueEvents),
        columns=sorted(uniqueEvents)
    )
    print(tabulate(footprintMatrix, headers='keys', tablefmt='psql'))
    
    causalRelations, maximalPairs, placeSet, flowRelation = extractRelationships(footprint, uniqueEvents)
    print("\nCausal Relationships (XL):", sorted(causalRelations))
    print("Maximal Pairs (YL):", sorted(maximalPairs))
    print("Place Set (PL):", sorted(placeSet))
    print("Flow Relation (FL):", sorted(flowRelation))
    
    petriNet = buildPetriNet(uniqueEvents, initialEvents, finalEvents, maximalPairs, placeSet, flowRelation)
    print("\nPetri Net Model:")
    print(json.dumps(petriNet, indent=4))
