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

AUTHORS = 'Jane Smith and Laura Lee' 

import time # You'll probably need this to avoid losing a
 # game due to exceeding a time limit.

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'Nic'
        if twin: self.nickname += '2'
        self.long_name = 'Templatus Skeletus'
        if twin: self.long_name += ' II'
        self.persona = 'bland'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".

    def introduce(self):
        intro = '\nMy name is Templatus Skeletus.\n'+\
            '"An instructor" made me.\n'+\
            'Somebody please turn me into a real game-playing agent!\n'
        if self.twin: intro += "By the way, I'm the TWIN.\n"
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
       print("Change this to return 'OK' when ready to test the method.")
       return "Not-OK"
   
    # The core of your agent's ability should be implemented here:             
    def makeMove(self, currentState, currentRemark, timeLimit=10000):
        print("makeMove has been called")

        print("code to compute a good move should go here.")
        # Here's a placeholder:
        a_default_move = [0, 0] # This might be legal ONCE in a game,
        # if the square is not forbidden or already occupied.
    
        newState = currentState # This is not allowed, and even if
        # it were allowed, the newState should be a deep COPY of the old.
    
        newRemark = "I need to think of something appropriate.\n" +\
        "Well, I guess I can say that this move is probably illegal."

        print("Returning from makeMove")
        return [[a_default_move, newState], newRemark]

    # The main adversarial search function:
    def minimax(self,
            state,
            depthRemaining,
            pruning=False,
            alpha=None,
            beta=None,
            zHashing=None):
        print("Calling minimax. We need to implement its body.")

        default_score = 0 # Value of the passed-in state. Needs to be computed.
    
        return [default_score, "my own optional stuff", "more of my stuff"]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
 
    def staticEval(self, state):
        print('calling staticEval. Its value needs to be computed!')
        # Values should be higher when the states are better for X,
        # lower when better for O.
        return 0
 
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

