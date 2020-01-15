"""
RandomBot -- A simple strategy: enumerates all legal moves, and picks one
uniformly at random.
"""

# Import the API objects
from api import State, util
import random, array
import numpy as np
class Node:
    def __init__(self):
        self.state = None
        self.q = 0
        self.n = 0
        self.parent = None
        self.children = []

DEBUG = False
previous_root = None
class Bot:
    root = None
    currentNode = None
    player = None
    def __init__(self):
        if previous_root is not None:
            self.root = previous_root

    def get_move(self, state):
        self.player = state.whose_turn()
        
        if state.get_opponents_played_card() is None:
            moves = state.moves()
            return random.choice(moves)

        if state.get_phase() == 1:
            try:
                state = state.make_assumption()
            except:
                pass
        #Expand the root state when the game first started
        if self.root is None:
            self.root = Node()
            self.root.state = state
            self.createChilds(state,self.root)
            self.currentNode = self.root
    
        return self.monteCarloTS(state) 

    def monteCarloTS(self,state = Node()):
        #printTree(self.currentNode)py
        for _ in range(0,100):
            search = True
            while search:
                self.currentNode = self.selection()
                #self.printTree(self.currentNode)
                if self.currentNode.n is 0:
                    #print("Simulate")
                    self.backpropagation(self.rollout(self.currentNode.state,self.player))
                    search = False
                else:
                    if len(self.currentNode.children) is 0:    
                        #print("Expand")
                        self.expand(self.currentNode.state,self.currentNode)
                        if DEBUG:
                            self.printTree(self.currentNode)
                        search = False
                    else:
                        #print("Select again")
                        search = True
        if DEBUG:
            print("\n\nFINAL RESULT: ")
            self.printTree(self.root)
        '''
        bestScore = 0
        bestIndex = 0
        i = 0
        for child in self.root.children:
            if child.n or child.q is 0:
                score = 0
            else:
                score = child.q / child.n 
            if score > bestScore:
                bestScore = score
                bestIndex = i
            i = i + 1
        '''
        previous_root = self.best_child(self.root,2)
        return self.root.state.moves()[self.bestChoice(self.root,2)]

    def createChilds(self,state,parent):
        for move in state.moves():
            st = state.clone()
            st.next(move)
            childNode = Node()
            childNode.state = st
            childNode.parent = parent
            parent.children.append(childNode)
        return


    def selection(self):
        return self.best_child(self.currentNode,2)

    def expand(self,state,node):
        self.createChilds(state,node)
        pass

    def rollout(self,state,player):
        st = state.clone()
        i = 0
        # Do some random moves
        while not st.finished():
            if st.get_points(1) >= 66 or st.get_points(2) >= 66:
                break
            i = i + 1
            st = st.next(random.choice(st.moves()))
        return self.evaluation(st)
    
    def best_child(self,init_node, c_param=2):
        i = 0
        for child in init_node.children:
            if child.n == 0:
                #print("Index of q=0 is ", i)
                return child
            i = i + 1
                
        choices_weights = [
            c.q + c_param * np.sqrt((np.log(self.root.n) / c.n))
            for c in init_node.children
        ]
        return init_node.children[np.argmax(choices_weights)]

    def bestChoice(self,init_node, c_param=2):
        i = 0
        for child in init_node.children:
            if child.n == 0:
                #print("Index of q=0 is ", i)
                return child
            i = i + 1
                
        choices_weights = [
            c.q + c_param * np.sqrt((np.log(self.root.n) / c.n))
            for c in init_node.children
        ]
        return np.argmax(choices_weights)
        

    def backpropagation(self,result):
        while True:
            self.currentNode.n = self.currentNode.n + 1
            self.currentNode.q = self.currentNode.q + result
            #print("Result: ",self.currentNode.q)
            if self.currentNode.parent is None:
                break
            self.currentNode = self.currentNode.parent

    def evaluation(self, state):
	    return util.ratio_points(state, self.player) 

    def printTree(self,root = Node()):
        i = 0
        for child in root.children:
            print("    ",i, end="    ")
            i = i + 1
        print()
        for child in root.children:
            print(" o N= ", child.n, end="  ")
        print()
        for child in root.children:    
            print(" o Q= ", child.q, end="  ")
        print()

    