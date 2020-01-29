# Import the API objects
from api import State, util, Deck
from datetime import datetime 
import random, array
import numpy as np

class Node:
    def __init__(self):
        # DEBUG ONLY
        self.card = None

        self.state = None
        self.v = 0.0        
        self.n = 0
        self.parent = None
        self.children = []


bestRoot = None


class Bot:
    root = None
    player = None
    N = 1000
    debug = False


    def __init__(self):
        pass

    def get_move(self, state):
        self.player = state.whose_turn()

        try: state = state.make_assumption()
        except: pass
        
        if bestRoot is None:
            self.root = Node()
            self.root.state = state
        else:
            self.root = bestRoot
        
        return self.root.state.moves()[self.MCTS(state)]
        
    def MCTS(self, state):
        currentNode = self.root
        t1 = datetime.now()

        while (datetime.now()-t1).seconds <= 2:
            if len(currentNode.children) > 0:
                currentNode = self.selection(currentNode)
            else:
                if self.expansion(currentNode) is True:
                    for child in currentNode.children:
                        simResult = self.rollout(child)
                        self.backPropogation(simResult,child)
        
        #self.printTree(self.root)
        
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
        return bestIndex

    def selection(self, currentNode=Node(), C=1.0):
        def playerNode():
            t = self.root.n
            index = bestIndex = 0 
            bestSi = 0.0

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
        
        return playerNode() #if currentNode.state.whose_turn() is self.player else opponentNode()

    def expansion(self, currentNode=Node()):
        state = currentNode.state
        if state.finished() is True:
            return False
        for move in state.moves():
            # Play the card and set the state acording to the result
            st = state.clone()
            childNode = Node()

            st = st.next(move)
            childNode.state = st
            childNode.parent = currentNode
            currentNode.children.append(childNode)
        return True

    def rollout(self, currentNode=Node()):
        score = 0
        for _ in range(0, self.N):
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
        return score/float(self.N)

    def backPropogation(self, result, currentNode):
        while True:
            currentNode.n = currentNode.n + self.N
            currentNode.v = currentNode.v + result

            if currentNode.parent is None:
                break
            currentNode = currentNode.parent
        return

    def heuristics(self, state, player, phase, phaseEnterence):
        Bonus = 0.0
        if util.difference_points(state,self.player) >= 40:
            if state.winner()[1] == 3:   Bonus += 3
            elif state.winner()[1] == 2: Bonus += 1
            elif state.winner()[1] == 1: Bonus += 0
        else:
            if state.winner()[1] == 3:   Bonus += 0
            elif state.winner()[1] == 2: Bonus += 1
            elif state.winner()[1] == 1: Bonus += 3
        
        if phase == 2: # If game enters to the phase 2 at some point more trump cards means more points
            for card in phaseEnterence.moves():
                if card[0] != None and util.get_suit(card[0]) == state.get_trump_suit():
                    Bonus += 3

        for card in state.moves(): # And this is for ending the game with almost zero trumps in either case
            if card[0] != None and util.get_suit(card[0]) != state.get_trump_suit():
                Bonus += 3

        return 1 + Bonus if state.winner()[0] == self.player else -2
    
    def printTree(self,rt = Node()):
        i = 0
        
        for child in rt.children:
            print("     ",i, end="      ")
            i = i + 1
        print()
        for child in rt.children:
            print("  o N= ", child.n, end="   ")
        print()
        for child in rt.children:    
            print("  o V= ",  round(child.v,3), end="   ")
        print()
        for child in rt.children:    
            if  child.n is 0:
                print("  o x̄= ", "inf", end="   ")
            else:
             print("  o x̄= ", round(child.v / child.n,3), end="   ")
        print()
