import json
# Are you the one calculator
# dumb bitch graph theory

class Edge:
    def __init__(self, name1, name2, weight):
        self.name1 = name1
        self.name2 = name2
        self.weight = weight
    
    def __contains__(self, x):
        return x == name1 or x == name2

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return set([self.name1, self.name2]) == set([other.name1, other.name2])

    def __str__(self):
        return f"({self.name1}, {self.name2}, {self.weight})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash("".join(sorted([self.name1, self.name2])))
            
def read_events_json(file):
    with open(file) as f:
        data = json.load(f)
        required_keys = ["contestants", "no_matches", "perfect_matches", "beams"]
        for k in required_keys:
            if k not in data:
                raise Exception(f"Missing {key}")
        for beam_round in data["beams"]:
            arrangement = beam_round["arrangement"]
            testing = []
            for a in arrangement:
                testing = testing + a
            if set(testing) != set(data["contestants"]):
                raise Exception(f"invalid beam round {beam_round}")
        return data

game = read_events_json("season_8.json")

def create_initial_graph(game):
    graph = {}
    for contestant in game["contestants"]:
        graph[contestant] = []

    done = set([])
    
    for match in game["perfect_matches"]:
        name1, name2 = match
        graph[name1] = [Edge(name1, name2, 1)]
        graph[name2] = [Edge(name1, name2, 1)]
        done.add(name1)
        done.add(name2)

    def noMatch(name1, name2):
        for no_match in game["no_matches"]:
            no1, no2 = no_match
            if set([no1, no2]) == set([name1, name2]):
                return True
        return False
        

    for name1 in game["contestants"]:
        for name2 in game["contestants"]:
            if name1 == name2 or noMatch(name1, name2) or name1 in done or name2 in done:
                continue
            graph[name1] = graph.get(name1, []) + [Edge(name1, name2, 0)]
            graph[name2] = graph.get(name2, []) + [Edge(name1, name2, 0)]
    for k, v in graph.items():
        graph[k] = list(set(v))
    return graph

flatten = lambda l: [item for sublist in l for item in sublist]
def pgraph(graph):
    for k, v in graph.items():
        print(f"{k} : {max(v, key=lambda x: x.weight)}")
def calculate_odds(graph, game):
    def update_edge(name1, name2, w):
        for edge in graph[name1]:
            if edge.name2 == name2:
                edge.weight = 1 - (1 - edge.weight) * (1 - w)
                break
        for edge in graph[name2]:
            if edge.name1 == name1:
                edge.weight = 1 - (1 - edge.weight) * (1 - w)
                break
    def delete_edge(name1, name2):
        del_edge = Edge(name1, name2, -1)
        if del_edge in graph[name1]:
            graph[name1].remove(del_edge)
        if del_edge in graph[name2]:
            graph[name2].remove(del_edge)
    
    def noMatch(name1, name2):
        for no_match in game["no_matches"]:
            if set(no_match) == set([name1, name2]):
                delete_edge(name1, name2)
                return True
        for p_match in game["perfect_matches"]:
            if  name1 in p_match or name2 in p_match:
                return True
        return False

    for beam in game["beams"]:
        if beam["num"] == 0:
            for a in beam["arrangement"]:
                name1, name2 = a
                delete_edge(name1, name2)
                game["no_matches"].append([name1, name2])
    redo = False
    for beam in game["beams"]:
        arrangement = beam["arrangement"]
        num = beam["num"]
        # blackout
        if num == 0:
            continue
        possible_arrangements = []
        for a in arrangement:
            name1, name2 = a
            if not noMatch(name1, name2):
                possible_arrangements.append(a)
        print(possible_arrangements)
        right = 0
        for p_match in game["perfect_matches"]:
            for a in arrangement:
                if set(a) == set(p_match):
                    right += 1
        if len(possible_arrangements) == 0:
            continue
        prob = (num - right) / len(possible_arrangements)
        print(prob)
        for a in possible_arrangements:
            name1, name2 = a
            if prob == 0:
                delete_edge(name1, name2)
                game["no_matches"].append([name1, name2])
                redo = True
            update_edge(name1, name2, prob)
            
        for edgelists in graph.values():
            for edge in edgelists:
                if edge.weight >= 0.95 and (edge.name1 not in flatten(game["perfect_matches"]) or edge.name2 not in flatten(game["perfect_matches"])):
                    game["perfect_matches"].append([edge.name1, edge.name2])
                    redo = True
        pgraph(graph)
        if redo:
            print("REDO")
            break
    if redo:
        return game

def do(game):
    graph = create_initial_graph(game)
    while True:
        game = calculate_odds(graph,game)

        if game == None:
            break
        graph = create_initial_graph(game)
    # print(graph)

    pgraph(graph)
    print(graph)

do(game)