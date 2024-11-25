from agent_base import KAgent
from game_types import State, Game_Type
import game_types
from winTesterForK import winTesterForK
import random
import google.generativeai as genai
import os

AUTHORS = 'CC Ahrens and Cin Ahrens' 

import time # You'll probably need this to avoid losing a
 # game due to exceeding a time limit.

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        if self.twin:
            self.nickname = 'Birdy Wordy'
            self.long_name = 'Birdy Wordy the Wise'
            self.persona = 'existential philosopher'
        else:
            self.nickname = 'Ducky Wucky'
            self.long_name = 'Duckilisious Wuckington'
            self.persona = 'self confident duckaroo'
        
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".
        self.my_past_utterances = []
        self.opponent_past_utterances = []
        self.repeat_count = 0
        self.utt_count = 0
        self.eval_calls = 0
        self.zobrist = []
        self.hashings = {}
        genai.configure(api_key="AIzaSyDWhKiqG2rO8vZhW7cCD8LluN4Q_Of8pck")
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def introduce(self):
        # Ducky Wucky
        if not self.twin:
            intro = '\nMy name is ' + self.long_name + ', also known as ' + self.nickname + '.\n'+\
                'I\'m the greatest K In A Row Champion of all time!\n'+\
                'CC Ahrens (ccahrens) and Cin Ahrens (ldahrens) claim to have made me,\n'+\
                'but I say I made them! Prepare to be ducked!\n'
        if self.twin:
            # Birdy Wordy, existential crisis
            intro = '\nMy name is ' + self.long_name + ', and I\'m not really sure what I\'m doing here.\n'+\
            'I think I was made by CC Ahrens (ccahrens) and Cin Ahrens (ldahrens)... or at least, that\'s what I\'m told.\n'+\
            '*Sigh* What is the meaning of life?'
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
        if self.twin:
            prompt = "You are a bird named " + self.long_name + " but you go by " + self.nickname + "."
            prompt += " You are in the middle of an existential crisis, and you're playing a game of"
            prompt += " K in a Row, and you'll be placing" + what_side_to_play + " to score points."
            prompt += " In past games, you have been known to say things such as those contained in "
            prompt += "the following list: " + ', '.join(BIRDY_BANK) + "."
            self.chat = self.model.start_chat(
                    history=[
                        {"role": "user", "parts": prompt},
                    ]
                )
        else:
            prompt = "You are a duck named " + self.long_name + " and you go by " + self.nickname + ". "
            prompt += "You are incredibly self-confident and love to make duck jokes. "
            prompt += "You're currently in the middle of a game of K in a Row, and you'll be placing "
            prompt += what_side_to_play + " to score points. In past games, you have said things such as: "
            prompt += ', '.join(DUCKY_BANK) + "."
            self.chat = self.model.start_chat(
                history=[
                    {"role": "user", "parts": prompt},
                ]
            )
        self.prompt = prompt
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

    
    def nextUtterance(self, currentState):
        # this method uses try/except since part way through the game, gemini stops responding as well and
        # frequently throws errors, so when this happens, we default to our deterministic responses

        # base prompt that is the same for both personas
        prompt = "The current game state is" + currentState.__str__() + "."
        prompt += "Please provide a one sentence response without mentioning your next move."
        prompt += "Take inspiration from previous statements you've made!"

        if (self.twin):
            prompt += "Get creative, and don't forget your existentialist and philosophical roots!"
        else:
            prompt += "Get creative, arogant, and don't forget your stellar duckiliciousness!"
        
        try:
            response = self.chat.send_message(prompt)
            return response.text

        except:
            # restart model for the next time
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.chat = self.model.start_chat(
                    history=[
                        {"role": "user", "parts": self.prompt},
                    ]
                )
            if (self.twin):   
                if self.repeat_count > 1: return "I am randomed out now."
                n = len(BIRDY_BANK)
                if self.utt_count == n:
                    self.utt_count = 0
                    self.repeat_count += 1
                this_utterance = BIRDY_BANK[self.utt_count]
                self.utt_count += 1
                return this_utterance
            else:
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
                  "Remember folks: flap smarter, not harder!",
                  "Eenie Meenie Miney Mo. I hope I'm getting K in a row.",
                  "I'm the smartest duck you'll ever meet.",
                  "I've really got it all. I'm fluffy, I've got some oats, and I'm gonna get K in a Row!",
                  "Read 'em and weap! Oh wait, this isn't a card game?",
                  "Teeheehee *quack* teeheehee.",
                  "I've got bigger fish to fry than you.",
                  "Quack quack, you fell into my trap!",
                  "I'm going to win this so well they'll write movies about me!",
                  "I think they should write a musical about me. I think Lin Manuel-Miranda would be cast to play me.",
                  "Roses are red. Violets are blue. You're so through!"]
BIRDY_BANK = ["The baddest Birdy in the game!",
                  "Trick or tweet! Birdy Wordy is here to eat... your game!",
                  "Better start picking up my crumbs.",
                  "I meant to do that.",
                  "If birds aren't real, does that mean I'm fake?",
                  "How do I know if I'm even real?",
                  "I wish I'd stayed at home to read about philosophy...",
                  "Pardon me, it's time for my mid-game existential crisis.",
                  "OH NO A CAT. Wait, is it my turn?",
                  "Neeeeeeeeer, Birdy Wordy coming in hot!",
                  "Omg, you're so cooked! Actually, I appologize. That was rude.",
                  "I, I, I, I stayin' alive, stayin' alive! Ooops, my turn, huh?",
                  "If I win, can I have your sandwich?",
                  "If I don't think, therefore I aren't? What?",
                  "I'm so confused",
                  "Should I become a philosofeather? Darn, it's my turn again, isn't it?"]
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

