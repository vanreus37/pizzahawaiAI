# Import the API objects
from api import State, util, Deck
import random, array
import numpy as np

class Node:
    def __init__(self):
        # DEBUG ONLY
        self.card = None

        self.state = None
        self.v = 0
        self.n = 0
        self.parent = None
        self.children = []


bestRoot = None


class Bot:
    root = None
    player = None
    N = 100
    DL = 100
    debug = False


    def __init__(self):
        pass

    def get_move(self, state):
        self.player = state.whose_turn()

        if state.get_phase() == 1:
            try:
                state = state.make_assumption()
            except:
                pass

        if bestRoot is None:
            self.root = Node()
            self.root.state = state

            if self.debug:
                if self.root.state.get_opponents_played_card() is not None:
                    self.root.card = util.get_card_name(self.root.state.get_opponents_played_card())
                    print(self.root.card[0], self.root.card[1])
                else:
                    print("Started With An Empty Deck")
                    print("Trump suit is: ", self.root.state.get_trump_suit())
                    print("Start...\n")

            self.expansion(self.root)
        else:
            if self.root.state.get_opponents_played_card() is not None:
                self.root = bestRoot
            else:
                for nodes in bestRoot.children:
                    if state == nodes.state:
                        self.root = nodes.state
                        break

        return self.root.state.moves()[self.MCTS(state)]

    def MCTS(self, state):
        for iteration in range(0, self.DL):
            # For iteration 0 we go slct->sim->bck instead of slct->exp->sim->bck
            if iteration == 0: 
                selectedNode = self.selection(self.root)
                simulationResult = self.rollout(selectedNode)
                self.backPropogation(simulationResult,selectedNode)
            else:
                currentNode = self.root # Slct
                while len(currentNode.children) != 0 and currentNode.state.finished() is False:
                    currentNode = self.selection(currentNode) # Slct

                if currentNode.n is 0: # If this done is never visited before
                    self.expansion(currentNode) # Exp
                simulationResult = self.rollout(currentNode) # Sim
                self.backPropogation(simulationResult,currentNode)
                

        bestScore = 0.0 
        bestIndex = i = 0
        for child in self.root.children:
            if not child.n or not child.v:
                score = 0.0
            else:
                score = child.v / child.n
            if score > bestScore:
                bestScore = score
                bestIndex = i
            i += 1

        bestRoot = self.root.children[bestIndex]
        if self.debug:
            print("Chosed Index= ", bestIndex)
        # Return a random choice
        return bestIndex

    def selection(self, currentNode=Node(), C=0.5):
        t = self.root.n

        index = bestIndex = bestSi = 0

        for child in currentNode.children:
            if child.n is 0:
                bestIndex = index
                break

            Xi = child.v / child.n
            Ni = child.n
            Si = Xi + C * np.sqrt(np.log(t) / Ni)

            if Si > bestSi:
                bestSi = Si
                bestIndex = index

            index += 1
        return currentNode.children[bestIndex]

    def expansion(self, currentNode=Node()):
        state = currentNode.state
        if state.finished() is True:
            return False
        for move in state.moves():
            # Play the card and set the state acording to the result
            st = state.clone()

            childNode = Node()

            if st.finished() is True:
                return False

            st = st.next(move)
            childNode.state = st
            childNode.parent = currentNode
            currentNode.children.append(childNode)

            # DEBUG ONLY
            if move[0] is not None:
                childNode.card = util.get_card_name(move[0])

        return True

    def rollout(self, currentNode=Node()):
        score = 0
        for ooo in range(0, self.N):
            st = currentNode.state.clone()
            i = 0
            # Do some random moves
            maxPhase = 0
            phaseEnterence = Node()
            while not st.finished():
                st = st.next(random.choice(st.moves()))
                phase = st.get_phase()
                if phase > maxPhase: 
                    maxPhase = phase
                    phaseEnterence = st
                i += 1
            score += self.heuristics(st,currentNode.state.whose_turn(),maxPhase,phaseEnterence)
        return score


    def backPropogation(self, result, currentNode):
        while True:
            currentNode.n = currentNode.n + self.N
            currentNode.v = currentNode.v + result

            if currentNode.parent is None:
                break
            currentNode = currentNode.parent
        return

    def heuristics(self, state, player, phase, phaseEnterence):
        def playerHeuristic():
            Bonus = 0
            if state.winner()[1] == 3:
                Bonus += 3
            elif state.winner()[1] == 2:
                Bonus += 1
            elif state.winner()[1] == 1:
                Bonus += 0

            if phase == 2: # If game enters to the phase 2 at some point more trump cards means more points
                for card in phaseEnterence.moves():
                    if card[0] != None and util.get_suit(card[0]) == state.get_trump_suit():
                        Bonus += 3

            for card in state.moves(): # And this is for ending the game with almost zero trumps in either case
                if card[0] != None and util.get_suit(card[0]) != state.get_trump_suit():
                    Bonus += 3

            return 1 + Bonus if state.winner()[0] == self.player else 0
        
        def opponentHeuristic(): # NOT SURE ABOUT THIS I STILL NEED TO READ ABOUT HOW TO REACT FOR THE OPPONENTS TURNS
            return 3 if state.winner()[0] != self.player else 0
        
        return playerHeuristic() #if player == self.player else opponentHeuristic() # ADD THIS WHEN YOU ARE SURE
    
    def printTree(self,rt = Node()):
        i = 0
        for child in rt.children:
            print("     ",i, end="      ")
            i = i + 1
        print()
        for child in rt.children:
            print("",child.card, end="  ")
            i = i + 1
        print()
        for child in rt.children:
            print("  o N= ", child.n, end="   ")
        print()
        for child in rt.children:    
            print("  o V= ", child.v, end="   ")
        print()
        for child in rt.children:    
            if  child.n is 0:
                print("  o x̄= ", "inf", end="  ")
            else:
             print("  o x̄= ", round(child.v / child.n,2), end="  ")
        print()