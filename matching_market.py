#!/usr/bin/env python
# coding: utf-8

# In[39]:


import max_flow


# In[2]:


import networkx as nx


# In[3]:


def createBiGraph(n, m, favorites):
    G = nx.DiGraph()
    S = 0
    T = len(n)+len(m) + 1
    for i in range(1, len(n)+1):
        G.add_edge(S, i, capacity=1)
    for i in range(len(n)+1, T):
        G.add_edge(i, T, capacity=1)
    for buyer, items in favorites.items():
        for item in items:
            itemID = item+len(n)
            G.add_edge(buyer, itemID, capacity=1)
    return G

def match(n, m, favorites):
    G = createBiGraph(n, m, favorites)
    origEdges = list(G.edges.data('capacity'))
    S = 0
    T = len(n)+len(m)+1
    maxFlow, Gnew = max_flow.fordFulkerson(G, S, T)
    
    
    flowEdges = []
    for a, b, capacity in origEdges:
        if a != S and b != T:
            flow = capacity-Gnew[a][b]['capacity']
            if flow>0:
                flowEdges.append((a, b-len(n), flow))
    return maxFlow, flowEdges


# # Recall the procedure constructed in Theorem 8.8 of the notes to find a market equilibrium in a matching market.

# ### The first step of this procedure involves either finding a perfect matching or a constricted set. Recall that this can be done using maximum flow. Now, using your maximum-flow implementation from assignment 2, implement an algorithm that finds either a perfect matching M or a constricted set S in a bipartite graph

# In[4]:


def findMatchorCSet(n, m, favorites):
    flow, edges = match(n, m, favorites)
    matching = list(map(lambda x: x[:2], edges))
    if flow == len(n):
        return True, matching
    else:
        buyers_with_matches = list(map(lambda x: x[0], matching))
        buyers_left_out = [x for x in n if x not in buyers_with_matches]
        constricted_set = set()
        for buyer in buyers_left_out:
            for fave in favorites[buyer]:
                constricted_set.add(fave)
        return False, constricted_set


# ### Now, given a bipartite matching frame with n players, n items, and values of each player for each item, implement the full procedure to find a market equilibrium.

# In[48]:


import collections

#Convert values to favorites
def get_faves(n, values):
    favorites = collections.defaultdict(list)
    for i in range(n):
        maxval = max(values[i])
        for j in range(n):
            if values[i][j] == maxval:
                favorites[i + 1].append(j + 1)
    return favorites


# In[270]:


#Find market equilibrium matching and prices
def findMktEq(n, values, prices):
    utilities = [[x - y for x,y in zip(buyer, prices)] for buyer in values]
    isMatch, res = findMatchorCSet(range(1, n+1), range(1, n+1), get_faves(n, utilities))
    if isMatch:
        return res, prices
    else:
        for x in res:
            prices[x-1] += 1
        minprice = min(prices)
        if minprice > 0:
            prices = list(map(lambda x: x - minprice, prices))
        findMktEq(n, values, prices)


# In[53]:


from random import randint


# In[282]:


def write_file():
    text_file = open("p7.txt", "w")
    for n in range(10,21,5):
        values = [[randint(0, n) for x in range(n)] for y in range(n)]
        prices = [0] * n
        findMktEq(n, values, prices)
        text_file.write("N: {}".format(n))
        text_file.write('\n')
        text_file.write("Values: {}".format(values))
        text_file.write('\n')
        text_file.write('Matching: {}'.format(findMktEq(n,values,prices)[0]))
        text_file.write('\n')
        text_file.write('Prices: {}'.format(findMktEq(n,values,prices)[1]))
        text_file.write('\n')
        text_file.write('\n')
    text_file.close()


# In[273]:


def get_matching(n, values, prices):
    findMktEq(n,values, prices)
    newprices = findMktEq(n,values, prices)[1]
    utilities = [[x - y for x,y in zip(buyer, newprices)] for buyer in values]
    return findMatchorCSet(range(1, n+1), range(1, n+1), get_faves(n, utilities))[1]


# In[247]:


def reshape(n, m, values):
    if n > m:
        for x in values:
            for i in range(n - m):
                x.append(0)
    elif n < m:
        for i in range(m - n):
            values.append([0] * m)
    return values


# In[92]:


from copy import deepcopy


# In[196]:


def get_prices(n, m, values, prices, matching):
    base_vals = deepcopy(values)
    newprices = []
    
    for i in range(1, len(matching) + 1):
        valwith = 0
        for buyer, item in matching:
            if buyer is not i:
                valwith += values[buyer - 1][item - 1]
        temp = deepcopy(base_vals)
        temp.pop(i - 1)
        temp = reshape(n - 1, m, temp)
        alt_matching = get_matching(len(temp), temp, prices)
        
        valwithout = 0
        for buyer, item in alt_matching:
            valwithout += temp[buyer - 1][item - 1]
            
        newprices.append(valwithout - valwith)
    return newprices


# In[400]:


def vcg(n, m, values):
    values = reshape(n, m, values)
    prices = [0] * n
    matching = get_matching(len(values), values, prices)
    return matching, get_prices(n, m, values, prices, matching)


# In[401]:


def write_file2():
    text_file = open("p8.txt", "w")
    
    #Values in 8.3
    n = 3
    values = [[4,12,5],[7,10,9],[7,7,10]]
    text_file.write("N: {}".format(n))
    text_file.write('\n')
    text_file.write("Values: {}".format(values))
    text_file.write('\n')
    text_file.write('Prices: {}'.format(vcg(n, n, values))[1])
    text_file.write('\n')
    text_file.write('\n')
        
    for n in range(10,21,5):
        values = [[randint(0, n) for x in range(n)] for y in range(n)]
        text_file.write("N: {}".format(n))
        text_file.write('\n')
        text_file.write("Values: {}".format(values))
        text_file.write('\n')
        text_file.write('Prices: {}'.format(vcg(n, n, values))[1])
        text_file.write('\n')
        text_file.write('\n')
    text_file.close()


# In[415]:


def simulateVCG():
    values = [[0]*20 for x in range(20)]
    seeds = {}
    for i in range(20):
        seed = randint(1,50)
        seeds[i + 1] = seed
        for j in range(20):
            values[i][j] = seed * j
    matching, prices = vcg(20, 20, values)
    return seeds, matching, prices


# In[418]:


def write_file3():
    text_file = open('p9.txt','w')
    
    seeds, matching, prices = simulateVCG()
    text_file.write('Random seeds: {}'.format(seeds))
    text_file.write('\n')
    text_file.write('Matching: {}'.format(matching))
    text_file.write('\n')
    text_file.write('Prices: {}'.format(prices))
    
    text_file.close()


# In[225]:


def manhattanDist(a,b):
    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]
    return abs(x2-x1) + abs(y2-y1)


# In[257]:


def edgeval(rider, driver):
    return rider['val'] - manhattanDist(driver, rider['curr']) - manhattanDist(rider['dest'], rider['curr'])

def createValues(riders, drivers):
    values = []
    for i in range(len(riders)):
        temp = []
        for j in range(len(drivers)):
            temp.append(edgeval(riders[i], drivers[j]))
        values.append(temp)
    values = reshape(len(riders), len(drivers), values)
    return values


# In[333]:


def valproftups(riders, drivers):
    values = createValues(riders, drivers)
    n = len(values)
    prices = [0] * n
    findMktEq(n, values, prices)
    matching, prices = findMktEq(n, values, prices)
    res = []
    for i in range(len(matching)):
        rider = matching[i][0] - 1
        driver = matching[i][1] - 1
        res.append((values[rider][driver] - prices[driver], prices[driver]))
    return res


# In[433]:


def test_case():
    riders = []
    n1 = randint(5,10)
    for x in range(n1):
        x1, x2, y1, y2 = randint(0, 15), randint(0, 15), randint(0, 15), randint(0, 15)
        c = (x1, y1)
        d = (x2, y2)
        riders.append({'curr' : c, 'dest' : d, 'val' : 25})
        
    drivers = []
    n2 = randint(5,10)
    for x in range(n2):
        x1, x2 = randint(0, 15), randint(0, 15)
        c = (x1, y1)
        drivers.append(c)
    
    values = createValues(riders, drivers)
    n = len(values)
    prices = [0] * n
    findMktEq(n, values, prices)
    matching, profits = findMktEq(n, values, prices)
    valprofs = valproftups(riders, drivers)
    return n1, n2, matching, profits, valprofs


# In[367]:


def genMarket(n1, n2):
    riders = []
    for i in range(n1):
        x1, x2, y1, y2 = randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100)
        c = (x1, y1)
        d = (x2, y2)
        riders.append({'curr' : c, 'dest' : d, 'val' : 300})
        
    drivers = []
    for i in range(n2):
        x1, x2 = randint(0, 100), randint(0, 100)
        c = (x1, y1)
        drivers.append(c)
    return riders, drivers


# In[378]:


def simulateUber(n1, n2):
    totalval = 0
    totalprof = 0
    for x in range(100):
        riders, drivers = genMarket(n1, n2)
        valprofs = valproftups(riders, drivers)
        totalval += sum(list(map(lambda x: x[0], valprofs))) / len(riders)
        totalprof += sum(list(map(lambda x: x[1], valprofs))) / len(drivers)
    print('For %d riders and %d drivers:' %(n1, n2))
    print('The average utility for riders is {}'.format(totalval / 100))
    print('The average profit for drivers is {}'.format(totalprof / 100))


# In[380]:


simulateUber(10, 10)


# In[381]:


simulateUber(5, 20)


# In[382]:


simulateUber(20, 5)

