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


class Game:
    def __init__(self, json_file):
        with open(json_file) as f:
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
            self.game_data = data

    def no_match(self, name1, name2):
        for no_match in self.game_data["no_matches"]:
            no1, no2 = no_match
            if set([no1, no2]) == set([name1, name2]):
                return True
        return False

    def add_no_match(self, name1, name2):
        self.game_data["no_matches"].append([name1, name2])

    def in_perfect_match(self, name):
        for p_match in self.game_data["perfect_matches"]:
            if  name in p_match:
                return True

    def perfect_match(self, name1, name2):
        for p_match in self.game_data["perfect_matches"]:
            if  name1 in p_match and name2 in p_match:
                return True
        return False

    def get_contestants(self):
        return self.game_data["contestants"]

    def get_perfect_matches(self):
        return self.game_data["perfect_matches"]

    def add_perfect_match(self, name1, name2):
        return self.game_data["perfect_matches"].append([name1, name2])

    def get_beams(self):
        return self.game_data["beams"]

    def num_correct_arrangement(self, arrangement):
        correct_beams = 0
        for p_match in self.get_perfect_matches():
            for a in arrangement:
                if set(a) == set(p_match):
                    correct_beams += 1
        return correct_beams

class GameGraph:
    def __init__(self, game):
        self.graph = {}
        for contestant in game.get_contestants():
            self.graph[contestant] = []
        
        for match in game.get_perfect_matches():
            name1, name2 = match
            self.graph[name1] = [Edge(name1, name2, 1)]
            self.graph[name2] = [Edge(name1, name2, 1)]
            

        for name1 in game.get_contestants():
            for name2 in game.get_contestants():
                if name1 == name2 or game.no_match(name1, name2) or game.in_perfect_match(name1) or game.in_perfect_match(name2):
                    continue
                self.graph[name1] = self.graph.get(name1, []) + [Edge(name1, name2, 0)]
                self.graph[name2] = self.graph.get(name2, []) + [Edge(name1, name2, 0)]
        for k, v in self.graph.items():
            self.graph[k] = list(set(v))

    def update_edge(self, name1, name2, w):
        for edge in self.graph[name1]:
            if edge.name2 == name2:
                edge.weight = 1 - (1 - edge.weight) * (1 - w)
                break
        for edge in self.graph[name2]:
            if edge.name1 == name1:
                edge.weight = 1 - (1 - edge.weight) * (1 - w)
                break

    def delete_edge(self, name1, name2):
        del_edge = Edge(name1, name2, -1)
        if del_edge in self.graph[name1]:
            self.graph[name1].remove(del_edge)
        if del_edge in self.graph[name2]:
            self.graph[name2].remove(del_edge)

    def edges(self):
        return self.graph.values()

    def __str__(self):
        return "\n".join([f"{k} : {max(v, key=lambda x: x.weight)}" for k, v in self.graph.items()])

    def __repr__(self):
        return self.__str__()      

game = Game("season_8.json")

def calculate_odds(graph: GameGraph, game: Game):

    def noMatch(name1, name2):
        if game.no_match(name1, name2):
            graph.delete_edge(name1, name2)
            return True
        if game.in_perfect_match(name1) or game.in_perfect_match(name2):
            return True
        return False

    for beam in game.get_beams():
        if beam["num"] == 0:
            for a in beam["arrangement"]:
                name1, name2 = a
                graph.delete_edge(name1, name2)
                game.add_no_match(name1,name2)
    redo = False
    for beam in game.get_beams():
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

        if len(possible_arrangements) == 0:
            continue
        prob = (num - game.num_correct_arrangement(arrangement)) / len(possible_arrangements)
        print(prob)
        for a in possible_arrangements:
            name1, name2 = a
            if prob == 0:
                graph.delete_edge(name1, name2)
                game.add_no_match(name1,name2)
                redo = True
            graph.update_edge(name1, name2, prob)
            
        for edgelists in graph.edges():
            for edge in edgelists:
                if edge.weight >= 0.95 and (not game.perfect_match(edge.name1, edge.name2)):
                    game.add_perfect_match(edge.name1, edge.name2)
                    redo = True
        print(graph)
        if redo:
            print("REDO")
            break
    return redo

def do(game):
    graph = GameGraph(game)
    while True:
        if not calculate_odds(graph,game):
            break
        graph = GameGraph(game)

do(game)