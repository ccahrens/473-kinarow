'''
<yourUWNetID>_KInARow.py
Authors: <your name(s) here, lastname first and partners separated by ";">
  Example:  
    Authors: Smith, Jane; Lee, Laura

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 473, University of Washington

THIS IS A TEMPLATE WITH STUBS FOR THE REQUIRED FUNCTIONS.
YOU CAN ADD WHATEVER ADDITIONAL FUNCTIONS YOU NEED IN ORDER
TO PROVIDE A GOOD STRUCTURE FOR YOUR IMPLEMENTATION.

'''

from agent_base import KAgent
from game_types import State, Game_Type
import game_types
from winTesterForK import winTesterForK

AUTHORS = 'CC Ahrens and Cin Ahrens' 

import time # You'll probably need this to avoid losing a
 # game due to exceeding a time limit.

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'Ducky Wucky'
        if twin: self.nickname = 'Birdy Wordy'
        self.long_name = 'Duckilisious Wuckington'
        if twin: self.long_name = 'Birdy Wordy the Wise'
        self.persona = 'bland'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".

    def introduce(self):
        intro = '\nMy name is ' + self.nickname + ', the great K In A Row Champion!\n'+\
            'CC Ahrens (ccahrens) and Cin Ahrens (ldahrens) claim to have made me,\n'+\
            'but I say I made them! Prepare to be ducked!\n'
        if self.twin:
            intro = '\nMy name is ' + self.long_name + ', the Birdy K In A Row Champion!\n'+\
            'CC Ahrens (ccahrens) and Cin Ahrens (ldahrens) claim to have made me,\n'+\
            'but I say I made them! Prepare to be ducked!\n'
        #if self.twin: intro += "By the way, I'm the TWIN.\n"
        return intro

    # Receive and acknowledge information about the game from
    # the game master:
    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move = 0.1, # Time limits can be
                                      # changed mid-game by the game master.
        utterances_matter=True):      # If False, just return 'OK' for each utterance.

       # Write code to save the relevant information in variables
       # local to this instance of the agent.
       # Game-type info can be in global variables.
       #print("Change this to return 'OK' when ready to test the method.")
       self.who_i_play = what_side_to_play
       self.opponent_nickname = opponent_nickname
       self.time_limit = expected_time_per_move
       global GAME_TYPE
       GAME_TYPE = game_type
       print("Oh, I love playing Duck Duck ", game_type.long_name)
       self.my_past_utterances = []
       self.opponent_past_utterances = []
       self.repeat_count = 0
       self.utt_count = 0
       self.eval_calls = 0
       if self.twin: self.utt_count = 5 # Offset the twin's utterances.
       return "OK"
   
    # The core of your agent's ability should be implemented here:             
    def makeMove(self, currentState, currentRemark, timeLimit=10000):
        print("makeMove has been called")

        print("code to compute a good move should go here.")
        value, newMove, newState = self.minimax(currentState, timeLimit, pruning=False)
        # possibleMoves = successors_and_moves(currentState)
        # print(currentState.whose_move)
        # myMove = self.chooseMove(possibleMoves, currentState.whose_move, timeLimit)
        myUtterance = self.nextUtterance()
        #newState, newMove = myMove
        return [[newMove, newState], myUtterance]
        # # Here's a placeholder:
        # a_default_move = [0, 0] # This might be legal ONCE in a game,
        # # if the square is not forbidden or already occupied.
    
        # newState = currentState # This is not allowed, and even if
        # # it were allowed, the newState should be a deep COPY of the old.
        # print("CURRENT STATE", currentState)
    
        # newRemark = "I need to think of something appropriate.\n" +\
        # "Well, I guess I can say that this move is probably illegal."

        # print("Returning from makeMove")
        # return [[a_default_move, newState], newRemark]

    # TODO: @cinahrens
    # 0's are mins, X's are maxes!
    # The main adversarial search function:
    def minimax(self,
            state,
            depthRemaining,
            pruning=False,
            alpha=None,
            beta=None,
            zHashing=None):
        print("Calling minimax. We need to implement its body.")

        #default_score = 0 # Value of the passed-in state. Needs to be computed.
        next_moves = successors_and_moves(state)
        #print(next_moves)

        if (state.whose_move == 'X'):
            v = -float("inf")
            move = None
            state = None
            len = next_moves[0].__len__()
            for i in range(len):
                successor = next_moves[0][i]
                action = next_moves[1][i]
                new_val = self.min_value(successor, depthRemaining, alpha=float("-inf"), beta=float("inf"), pruning=pruning)
                if(new_val > v):
                    v = new_val
                    move = action
                    state = successor
            
            return [v, move, state]
        else:
            v = float("inf")
            move = None
            state = None
            len = next_moves[0].__len__()
            for i in range(len):
                successor = next_moves[0][i]
                action = next_moves[1][i]
                new_val = self.max_value(successor, depthRemaining, alpha=float("-inf"), beta=float("inf"), pruning=pruning)
                if(new_val < v):
                    v = new_val
                    move = action
                    state = successor
            
            return [v, move, state]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
    def max_value(self, gameState, depthRemaining, alpha=None, beta=None, pruning=False):

        depthRemaining-=1

        v = -float("inf")
        # actions = gameState.getLegalActions(index)
        next_moves = successors_and_moves(gameState)
        
        len = next_moves[0].__len__()
        for i in range(len):
            successor = next_moves[0][i]
            action = next_moves[1][i]
            if(depthRemaining == 0 or winTesterForK(gameState, action, GAME_TYPE.k) != 'No Win'):
                    return self.staticEval(gameState)
            v = max(v, self.min_value(successor, depthRemaining, alpha, beta))
            if pruning:
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
        return v

    def min_value(self, gameState, depthRemaining, alpha = None, beta = None, pruning = False):
        depthRemaining-=1

        v = float("inf")
        next_moves = successors_and_moves(gameState)
        
        len = next_moves[0].__len__()
        for i in range(len):
            successor = next_moves[0][i]
            action = next_moves[1][i]
            if(depthRemaining == 0 or winTesterForK(gameState, action, GAME_TYPE.k) != 'No Win'):
                    return self.staticEval(gameState)
            v = min(v, self.max_value(successor, depthRemaining, alpha, beta))
            if pruning:
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return v

    # TODO: @ccahrens
    # some things are better for different shapes,
    # figure out how to tell what shape you're playing
    def staticEval(self, state):
        print('calling staticEval')
        # NOTE FROM CIN:
        # This is for my testing functions, please leave it as is!
        self.eval_calls += 1
        # Values should be higher when the states are better for X,
        # lower when better for O.

        nRows: int = len(state.board)
        mCols: int = len(state.board[0])
        return self.staticEvalHelper(state, "X", nRows, mCols) + self.staticEvalHelper(state, "O", nRows, mCols)
        return 0


    # dumb helper that for now just counts number of positions for each
    def staticEvalHelper(self, state, agent, nRows, mCols):
        sum: int = 0
        #unblockedRow: bool = True
        for i in range (0, nRows):
            prevWasOpponent = False
            # get next row
            row = state.board[i]
            for j in range (0, mCols):
                if row[j] == agent:
                    sum += 1
                    prevWasOpponent = False
                else:
                    sum -= j
                    if (prevWasOpponent):
                        sum -= j
                    prevWasOpponent = True

        for j in range (0, mCols):
            for i in range (0, nRows):
                if state.board[i][j] == agent:
                    sum += 1
                    prevWasOpponent = False
                else:
                    sum -= i
                    if (prevWasOpponent):
                        sum -= j
                    prevWasOpponent = True
        if (agent == "O"): return -sum
        return sum

    
    # TODO: @ccahrens
    # make this smarter based on who's winning
    # if self.twin = wordy
    # if !self.twin = wucky
    def nextUtterance(self):
        if (self.twin):
            if self.repeat_count > 1: return "I am randomed out now."
            n = len(BIRDY_BANK)
            if self.utt_count == n:
                self.utt_count = 0
                self.repeat_count += 1
            this_utterance = BIRDY_BANK[self.utt_count]
            self.utt_count += 1
            return this_utterance
        if self.repeat_count > 1: return "I am randomed out now."
        n = len(DUCKY_BANK)
        if self.utt_count == n:
            self.utt_count = 0
            self.repeat_count += 1
        this_utterance = DUCKY_BANK[self.utt_count]
        self.utt_count += 1
        return this_utterance
    
    def chooseMove(self, statesAndMoves, whosemove, timeLimit):
        states, moves = statesAndMoves
        if states==[]: return None
        i = 0
        curr = -float("inf")
        best_i = i
        for state in states:
            new = self.staticEval(state)
            if (new > curr):
                curr = new
                best_i = i
            i += 1
        my_choice = [states[best_i], moves[best_i]]
        return my_choice
    
def other(p):
    if p=='X': return 'O'
    return 'X'


def successors_and_moves(state):
    b = state.board
    p = state.whose_move
    o = other(p)
    new_states = []
    moves = []
    mCols = len(b[0])
    nRows = len(b)

    for i in range(nRows):
        for j in range(mCols):
            if b[i][j] != ' ': continue
            news = do_move(state, i, j, o)
            new_states.append(news)
            moves.append([i, j])
    return [new_states, moves]

def do_move(state, i, j, o):
            news = game_types.State(old=state)
            news.board[i][j] = state.whose_move
            news.whose_move = o
            return news
    

# TODO: @ccahrens
# Write better commentary for each
# list of lists
# formalize which indices are for what type of commentary
DUCKY_BANK = ["How's that for random?",
                  "Flip!",
                  "Spin!",
                  "I hope this is my lucky day!",
                  "How's this move for high noise to signal ratio?",
                  "Uniformly distributed. That's me.",
                  "Maybe I'll look into Bayes' Nets in the future.",
                  "Eenie Meenie Miney Mo.  I hope I'm getting K in a row.",
                  "Your choice is probably more informed than mine.",
                  "If I only had a brain.",
                  "I'd while away the hours, playing K in a Row.",
                  "So much fun.",
                  "Roll the dice!",
                  "Yes, I am on a roll -- of my virtual dice.",
                  "randint is my cousin.",
                  "I like to spread my influence around on the board."]
BIRDY_BANK = ["How's that for random?",
                  "Flip!",
                  "Spin!",
                  "I hope this is my lucky day!",
                  "How's this move for high noise to signal ratio?",
                  "Uniformly distributed. That's me.",
                  "Maybe I'll look into Bayes' Nets in the future.",
                  "Eenie Meenie Miney Mo.  I hope I'm getting K in a row.",
                  "Your choice is probably more informed than mine.",
                  "If I only had a brain.",
                  "I'd while away the hours, playing K in a Row.",
                  "So much fun.",
                  "Roll the dice!",
                  "Yes, I am on a roll -- of my virtual dice.",
                  "randint is my cousin.",
                  "I like to spread my influence around on the board."]
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

