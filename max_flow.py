import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import collections
import random
from collections import Counter


def bfs(G, s, t):
    queue = collections.deque()
    visited = []
    visited.append(s)
    queue.append((s, [s]))
    while queue:
        u, path = queue.popleft()
        neighbors = G.neighbors(u)
        
        for v in neighbors:
            if v not in visited and G[u][v]['capacity']>0:
                visited.append(v)
                queue.append((v, path+[v]))
                if v == t:
                    return path+[v]
    return None
        
def fordFulkerson(G, s, t):
    addResidEdges(G)
    path = bfs(G, s, t)
    maxFlow = 0
    while(path):
        path.reverse()
        bottleneck = float("inf")
        for i in range(len(path)-1):
            a = path[i+1]
            b = path[i]
            bottleneck = min(bottleneck, G[a][b]['capacity'])
        maxFlow+=bottleneck
        
        
        for i in range(len(path)-1):
            a = path[i+1]
            b = path[i]
            G[a][b]['capacity'] -= bottleneck
            G[b][a]['capacity'] += bottleneck
        path = bfs(G, s, t)
    
    return maxFlow, G
        
def addResidEdges(G):
    l = list(G.edges)
    for edge in l:
        a, b = edge[0], edge[1]
        G.add_edge(b, a, capacity=0)

def createBiGraph(n, m):
    G = nx.DiGraph()
    S = 0
    T = len(n)+len(m) + 1
    for i in range(1, len(n)+1):
        G.add_edge(S, i, capacity=1)
    for i in range(len(n)+1, T):
        G.add_edge(i, T, capacity=1)
    for driver, riders in n.items():
        for rider in riders:
            riderID = rider+len(n)
            G.add_edge(driver, riderID, capacity=1)
    return G
def match(n, m):
    G = createBiGraph(n, m)
    origEdges = list(G.edges.data('capacity'))
    S = 0
    T = len(n)+len(m)+1
    maxFlow, Gnew = fordFulkerson(G, S, T)
    
    
    flowEdges = []
    for a, b, capacity in origEdges:
        if a != S and b != T:
            flow = capacity-Gnew[a][b]['capacity']
            if flow>0:
                flowEdges.append((a, b-len(n), flow))
    return maxFlow, flowEdges

from numpy import random

def decision(probability):
    return random.rand() < probability

def connected(n, p, j):
    mFlow = []
    # j number of iterations
    for it in range(j):
        drivers = {}
        riders = [i for i in range(1,n+1)]
        for i in range(1, n+1):
            drivers[i] = []
            for r in range(n+1):
                if (decision(p)):
                    drivers[i].append(r)
        maxflow, flowEdges = match(drivers,riders)
        mFlow.append(maxflow)
    return mFlow



