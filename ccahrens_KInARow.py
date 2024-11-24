from agent_base import KAgent
from game_types import State, Game_Type
import game_types
from winTesterForK import winTesterForK
from openai import OpenAI
import random
import os
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
        self.my_past_utterances = []
        self.opponent_past_utterances = []
        self.repeat_count = 0
        self.utt_count = 0
        self.eval_calls = 0
        self.zobrist = []
        self.hashings = {}

    def introduce(self):
        # Ducky Wucky
        intro = '\nMy name is ' + self.long_name + ', also known as ' + self.nickname + ' and I\'m the great K In A Row Champion!\n'+\
            'CC Ahrens (ccahrens) and Cin Ahrens (ldahrens) claim to have made me,\n'+\
            'but I say I made them! Prepare to be ducked!\n'
        if self.twin:
            # Birdy Wordy, existential crisis
            intro = '\nMy name is ' + self.long_name + ', the Birdy K In A Row Champion!\n'+\
            'CC Ahrens (ccahrens) and Cin Ahrens (ldahrens) claim to have made me,\n'+\
            'but I say I made them!\nThey might be twins, but I\'m THE TWIN.\n'+\
            '*Sigh* What is the meaning of life?'
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
       if self.twin: self.utt_count = 5 # Offset the twin's utterances.
       self.zobrist = self.build_table(game_type.n, game_type.m)
       return "OK"
   
    # The core of your agent's ability should be implemented here:             
    def makeMove(self, currentState, currentRemark, timeLimit=10000):
        print("makeMove has been called")

        print("code to compute a good move should go here.")

        depth_limit = 3
        hash = self.hash(currentState)
        _, newMove, newState = self.minimax(currentState, depth_limit, alpha=float("-inf"), beta=float("inf"), pruning=False, zHashing=hash, x = self.who_i_play == 'X')

        other = self.other(currentState.whose_move)
        n_hash = self.rehash(self.who_i_play, hash, newMove[0], newMove[1])

        if n_hash not in self.hashings:
            self.hashings[n_hash] = (None, None)

        myUtterance = self.nextUtterance(currentState)
        return [[newMove, newState], myUtterance]

    # TODO: @cinahrens
    # 0's are mins, X's are maxes!
    # The main adversarial search function:
    def minimax(self,
            state,
            depthRemaining,
            pruning=False,
            alpha=None,
            beta=None,
            zHashing=None, x=True):
        
        if zHashing is None:
            zHashing = self.hash(state)

        if zHashing in self.hashings and depthRemaining in self.hashings[zHashing]:
            value, move = self.hashings[zHashing][depthRemaining]
            if move:
                next_state = self.do_move(state, move[0], move[1], self.other(state.whose_move))
            else:
                next_state = None
            return value, move, next_state
    
        states, moves = self.successors_and_moves(state)
    
        if(depthRemaining == 0 or state.finished or not states):
            value = self.staticEval(state)
            self.cache(zHashing, depthRemaining, value, None)
            return value, None, None
        
        move = None
        next_state = None
        length = len(states)
        v = float("inf")
        if x:
            v = -1 * v

        for i in range(length):
            successor = states[i]
            action = moves[i]
            new_hash = self.rehash(state.whose_move, zHashing, action[0], action[1])
            new_v, _, _ = self.minimax(successor, depthRemaining - 1, pruning, alpha, beta, new_hash, not x)
            if ((new_v > v and x) or (new_v < v and not x)):
                v = new_v
                next_state = successor
                move = action
            if pruning:
                alpha = max(alpha, v)
                beta = min(beta, v)
                if beta <= alpha:
                    break
        self.cache(zHashing, depthRemaining, v, move)
        return [v, move, next_state]


    def build_table(self, rows, columns):
        zobrist = {}
        for col in range(columns):
            for row in range(rows):
                for option in [' ','X','O']:
                    zobrist[(row, col, option)] = random.getrandbits(64)
        return zobrist
    
    def hash(self, state):
        rows = len(state.board)
        cols = len(state.board[0])
        hash = 0
        for row in range(rows):
            for col in range(cols):
                option = state.board[row][col]
                #if option is not "-":
                if option != "-":
                    hash ^= self.zobrist[(row, col, option)]  # XOR for each board cell
        return hash
    
    def rehash(self, player, hash, row, column):
        unplayed = self.zobrist[(row, column, ' ')]
        option = self.zobrist[(row, column, player)]
        return unplayed ^ option ^ hash
    
    def cache(self, hash, depth, value, move):
        if hash not in self.hashings:
            self.hashings[hash] = {}
        self.hashings[hash][depth] = (value, move)
    # TODO: @ccahrens
    # some things are better for different shapes,
    # figure out how to tell what shape you're playing
    def staticEval(self, state):
        #print('calling staticEval')
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
        for i in range (0, nRows):
            prevWasOpponent = False
            # get next row
            # row = state.board[i]
            for j in range (0, mCols):
                (sum_add, prevWasOpponent_new) = self.loopHelper(state.board[i][j], agent, prevWasOpponent, j, i)
                sum += sum_add
                prevWasOpponent = prevWasOpponent_new

        for j in range(0, mCols):
            prevWasOpponent = False
            for i in range (0, nRows):
                (sum_add, prevWasOpponent_new) = self.loopHelper(state.board[i][j], agent, prevWasOpponent, i, j)
                sum += sum_add
                prevWasOpponent = prevWasOpponent_new
        if (agent == "O"): return -sum
        return sum

    def loopHelper(self, check, agent, prevWasOpponent, i, j):
        if check == agent:
            return (1, False)
        if not prevWasOpponent:
            return (i, True)
        return (i + j, True)

    
    # TODO: @ccahrens
    # make this smarter based on who's winning
    # if self.twin = wordy
    # if !self.twin = wucky
    def nextUtterance(self, currentState):
        if (self.twin):
            #try:
            # completion = client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content":
            #             "You are a K-in a row champion known as Birdy Wordy. You are a silly bird who knows you're smart, but you're also in the middle of an existential crisis. Here are some statements you've been known to share in the past: {self.BIRDY_BANK}"},
            #         {
            #             "role": "user",
            #             "content": "Please create commentary based on the current game state: {currentState}. You're currently playing {self.playing}."
            #         }
            #     ]
            # )
            # return completion.choices[0].message
            # except:
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
    
    def other(self, p):
        if p=='X': return 'O'
        return 'X' 
    
    def successors_and_moves(self, state):
        b = state.board
        p = state.whose_move
        o = self.other(p)
        new_states = []
        moves = []
        mCols = len(b[0])
        nRows = len(b)

        for i in range(nRows):
            for j in range(mCols):
                if b[i][j] == ' ':
                    news = self.do_move(state, i, j, o)
                    new_states.append(news)
                    moves.append((i, j))
        return new_states, moves

    def do_move(self, state, i, j, o):
                news = game_types.State(old=state)
                news.board[i][j] = state.whose_move
                news.whose_move = o
                return news

    
# TODO: @ccahrens
# Write better commentary for each
# list of lists
# formalize which indices are for what type of commentary
DUCKY_BANK = ["Do I get oats???",
                  "I want oats!",
                  "Oooh! Quack Quack!",
                  "When I finish this move, I'm going to much on some yummy grass!",
                  "Get quacked, loser!",
                  "Ducky Wucky for the win!",
                  "Remember folks: flap smarter, not harder.",
                  "Eenie Meenie Miney Mo.  I hope I'm getting K in a row.",
                  "I'm the smartest duck you'll ever meet.",
                  "I've really got it all. I'm fluffy, I've got some oats, and I'm gonna get K in a Row!",
                  "Read 'em and weap! Oh wait, this isn't a card game?",
                  "Teeheehee *quack* teeheehee.",
                  "I've got bigger fish to fry than you.",
                  "Oh yeah, I'm a big bird now!",
                  "Quack quack, you fell into my trap!",
                  "Roses are red. Violets are blue. You're so through!"]
BIRDY_BANK = ["The baddest Birdy in the game!",
                  "Trick or tweet! Birdy Wordy is here to eat... your game!",
                  "Better start picking up my crumbs.",
                  "I meant to do that.",
                  "If birds aren't real, does that mean I'm fake?",
                  "Pardon me, it's time for my mid-game existential crisis.",
                  "OH NO A CAT. Wait, is it my turn?",
                  "Neeeeeeeeer, Birdy Wordy coming in hot!",
                  "I'm going to win this so well they'll write movies about me!",
                  "I think they should write a musical about me. I think Lin Manuel-Miranda would be cast to play me.",
                  "I, I, I, I stayin' alive, stayin' alive! Ooops, my turn, huh?",
                  "If I win, can I have your sandwich?",
                  "If I don't think, therefore I aren't? What?",
                  "Oh yeah, I'm a big bird now!",
                  "I'm so confused",
                  "Should I become a philosofeather? Darn, it's my turn again, isn't it?"]
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

