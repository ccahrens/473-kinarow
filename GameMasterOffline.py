'''GameMasterOffline.py based on GameMaster.py

 Updated Nov. 17, 2024.
 See the test function at the end for how to customize
 the runs: choice of games and agents.

(C) University of Washington and S. Tanimoto, 2024.

'''

from time import sleep
USE_HTML = True
if USE_HTML: import gameToHTML

from winTesterForK import winTesterForK

from game_types import TTT, FIAR, Cassini

TIME_PER_MOVE = 1.0 # In seconds
INITIAL_STATE = TTT.initial_state


# Establish global variables, with defaults for now.
K = None
N = None
M = None
TURN_LIMIT = None

# To be called from WebGameAgent if using the web:
def set_game(game_type):
    global K, GAME_TYPE, TURN_LIMIT, N, M, INITIAL_STATE
    K = game_type.k
    N = game_type.n
    M = game_type.m
    GAME_TYPE = game_type
    TURN_LIMIT = game_type.turn_limit
    INITIAL_STATE = game_type.initial_state

PLAYERX = None
PLAYERO = None
def set_players(px, po):
    global PLAYERX, PLAYERO
    PLAYERX = px
    PLAYERO = po
    
FINISHED = False
def runGame():
    currentState = INITIAL_STATE
    player1 = PLAYERX
    player2 = PLAYERO
    renderCommentary('The Gamemaster says, "Players, introduce yourselves."')
    renderCommentary('     (Playing X:) '+player1.introduce())
    renderCommentary('     (Playing O:) '+player2.introduce())

    if USE_HTML:
        gameToHTML.startHTML(player1.nickname, player2.nickname, GAME_TYPE.short_name, 1)
    try:
        p1comment = player1.prepare(GAME_TYPE, 'X', player2.nickname)
    except Exception as e:
        print("Failed to prepare perhaps because: ", e)
        report = 'Player 1 ('+player1.nickname+' failed to prepare, and loses by default.'
        renderCommentary(report)
        if USE_HTML: gameToHTML.reportResult(report)
        report = 'Congratulations to Player 2 ('+player2.nickname+')!'
        renderCommentary(report)
        if USE_HTML: gameToHTML.reportResult(report)
        if USE_HTML: gameToHTML.endHTML()
        return
    try:
        p2comment = player2.prepare(GAME_TYPE, 'O', player1.nickname)
    except Exception as e:
        print("Failed to prepare perhaps because: ", e)
        report = 'Player 2 ('+player2.nickname+' failed to prepare, and loses by default.'
        renderCommentary(report)
        if USE_HTML: gameToHTML.reportResult(report)
        report = 'Congratulations to Player 1 ('+player1.nickname+')!'
        renderCommentary(report)
        if USE_HTML: gameToHTML.reportResult(report)
        if USE_HTML: gameToHTML.endHTML()
        return
        return
    
    renderCommentary('The Gamemaster says: We\'re playing '+GAME_TYPE.long_name+'.')
    renderCommentary('The Gamemaster says: Let\'s Play!')
    renderCommentary('The initial state is...')

    currentRemark = "The game is starting."
    if USE_HTML: gameToHTML.stateToHTML(currentState)
    XsTurn = True
    name = None
    global FINISHED
    FINISHED = False
    turnCount = 0
    printState(currentState)
    while not FINISHED:
        who = currentState.whose_move
        if XsTurn:
            playerResult = player1.makeMove(currentState, currentRemark, TIME_PER_MOVE)
            name = player1.nickname
            XsTurn = False
        else:
            playerResult = player2.makeMove(currentState, currentRemark, TIME_PER_MOVE)
            name = player2.nickname
            XsTurn = True
        moveAndState, currentRemark = playerResult
        if moveAndState==None:
            FINISHED = True; continue
        move, currentState = moveAndState
        moveReport = "Move is by "+who+" to "+str(move)
        renderCommentary(moveReport)
        utteranceReport = name +' says: '+currentRemark
        renderCommentary(utteranceReport)
        if USE_HTML: gameToHTML.reportResult(moveReport)
        if USE_HTML: gameToHTML.reportResult(utteranceReport)
        possibleWin = winTesterForK(currentState, move, K)
        if possibleWin != "No win":
            FINISHED = True
            currentState.finished = True
            printState(currentState)
            if USE_HTML: gameToHTML.stateToHTML(currentState, finished=True)
            renderCommentary(possibleWin)
            if USE_HTML: gameToHTML.reportResult(possibleWin)
            if USE_HTML: gameToHTML.endHTML()
            if (XsTurn == False):
                return "X"
            return "O"
            return
        printState(currentState)
        if USE_HTML: gameToHTML.stateToHTML(currentState)
        turnCount += 1
        if turnCount == TURN_LIMIT: FINISHED=True
        else:
            sleep(WAIT_TIME_AFTER_MOVES) # NOT TOO FAST.
    printState(currentState)
    if USE_HTML: gameToHTML.stateToHTML(currentState)
    who = currentState.whose_move
    renderCommentary("Game over; it's a draw.")
    if USE_HTML: gameToHTML.reportResult("Game Over; it's a draw")
    if USE_HTML: gameToHTML.endHTML()

def printState(s):
    global FINISHED
    board = s.board
    who = s.whose_move
    horizontalBorder = "+"+3*M*"-"+"+"
    renderCommentary(horizontalBorder)
    for row in board:
        line = "|"
        for item in row:
            line += " "+item+" "
        line += "|"
        renderCommentary(line)
    renderCommentary(horizontalBorder)
    if not FINISHED:
      renderCommentary("It is "+who+"'s turn to move.\n")

# Temporary function.  Remove when other channels are working.
def renderCommentary(stuff):
    print(stuff)
      
def render_move_and_state(move, state):
   # NOTE: THIS DEFN WILL BE OVERWRITTEN WHEN USED ON THE WEB.
   print(move, state)

def render_utterance(who, utterance):
   # NOTE: THIS DEFN WILL BE OVERWRITTEN WHEN USED ON THE WEB.
   print(who+' says: '+utterance)

# Not used in offline version:
#def async_runGame():
#    fut = ensure_future(runGame())

WAIT_TIME_AFTER_MOVES = 0.01
def set_wait_time(t):
    global WAIT_TIME_AFTER_MOVES
    WAIT_TIME_AFTER_MOVES = float(t)
     
def test():
    # Stand-alone test
    print("Starting stand-alone test of GameMaster.py")
    # Edit this to change what version of K-in-a-Row is used.
    set_game(FIAR) # default is Tic-Tac-Toe
    #set_game(FIAR) # Five in a Row
    # Import 1 or 2 agent files here.
    # If using only 1, create 2 instances of it, one of
    # which is a "twin".

    import ccahrens_KInARow as h
    #import ccahrens_KInARow as m
    import tony_KInARow as m
    #import RandomPlayer as m
    px = h.OurAgent()
    # po = h.OurAgent(twin=True)
    po = m.OurAgent()
    set_players(px, po)
    print("Players are set.")
    print("Now let's run the game.")
    runGame()
    print("X accesses: ", px.eval_calls)
    print("O accesses: ", po.eval_calls)

def ccTestMany(runs=10, ai=False):
    # Stand-alone test
    print("Starting ccTestMany()")
    # Edit this to change what version of K-in-a-Row is used.
    set_game(TTT) # default is Tic-Tac-Toe
    #set_game(FIAR) # Five in a Row
    # Import 1 or 2 agent files here.
    # If using only 1, create 2 instances of it, one of
    # which is a "twin".

    # set up to play tic tac toe
    opponent_wins_ttt = 0
    we_win_ttt = 0
    import ccahrens_KInARow as h
    import RandomPlayer as m

    static_eval_accesses = 0
    ttt_evals_x = 0
    ttt_evals_o = 0
    fiar_evals_x = 0
    fiar_evals_o = 0
    cassini_evals_x = 0
    cassini_evals_o = 0

    # run games with our agent as x
    for i in range (0, runs):
        px = h.OurAgent(ai=ai)
        po = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "X":
                we_win_ttt += 1
            else:
                opponent_wins_ttt += 1
        ttt_evals_x += px.eval_calls
        static_eval_accesses += px.eval_calls
    # run games with our agent as O
    for i in range (0, runs):
        po = h.OurAgent(ai=ai)
        px = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "O":
                we_win_ttt += 1
            else:
                opponent_wins_ttt += 1
        ttt_evals_o += po.eval_calls
        static_eval_accesses += po.eval_calls

    # set up for FIAR
    set_game(FIAR)
    opponent_wins_fiar = 0
    we_win_fiar = 0
    # run games with our agent as X
    for i in range (0, runs):
        px = h.OurAgent(ai=ai)
        po = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "X":
                we_win_fiar += 1
            else:
                opponent_wins_fiar += 1
        fiar_evals_x += px.eval_calls
        static_eval_accesses += px.eval_calls

    # run games with our agent as O
    for i in range (0, runs):
        po = h.OurAgent(ai=ai)
        px = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "O":
                we_win_fiar += 1
            else:
                opponent_wins_fiar += 1
        fiar_evals_o += po.eval_calls
        static_eval_accesses += po.eval_calls

    # set up for cassini
    set_game(Cassini)
    opponent_wins_cassini = 0
    we_win_cassini = 0
    # run games with our agent as X
    for i in range (0, runs):
        px = h.OurAgent(ai=ai)
        po = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "X":
                we_win_cassini += 1
            else:
                opponent_wins_cassini += 1
        cassini_evals_x += px.eval_calls
        static_eval_accesses += px.eval_calls
    # run games with our agent as O
    for i in range (0, runs):
        po = h.OurAgent(ai=ai)
        px = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "O":
                we_win_cassini += 1
            else:
                opponent_wins_cassini += 1
        cassini_evals_o += po.eval_calls
        static_eval_accesses += po.eval_calls

    # display results
    showResults("TTT", opponent_wins_ttt, we_win_ttt, runs*2)
    showResults("FIAR", opponent_wins_fiar, we_win_fiar, runs*2)
    showResults("CASSINI", opponent_wins_cassini, we_win_cassini, runs*2)

    print()
    print("***STATIC EVAL ACCESSES***")
    print(f"static eval accesses: {static_eval_accesses}")
    print(f"static evals ttt x: {ttt_evals_x}")
    print(f"static evals ttt o: {ttt_evals_o}")
    print(f"static evals fiar x: {fiar_evals_x}")
    print(f"static evals fiar o: {fiar_evals_o}")
    print(f"static evals cassini x: {cassini_evals_x}")
    print(f"static evals cassini o: {cassini_evals_o}")
    

def showResults(game: str, opponent_wins: int, our_wins: int, runs: int):
    print()
    print(f"***{game} RESULTS***")
    print(f"opponent wins: {opponent_wins}")
    print(f"our wins: {our_wins}")
    print(f"our win rate (excludes ties from total): {100*our_wins/(opponent_wins + our_wins)}")
    print(f"our win rate (counts ties as losses): {100*our_wins/runs}")

def cinTestMany():
    # Stand-alone test
    print("Starting stand-alone test of GameMaster.py")
    # Edit this to change what version of K-in-a-Row is used.
    set_game(TTT) # default is Tic-Tac-Toe
    #set_game(FIAR) # Five in a Row
    # Import 1 or 2 agent files here.
    # If using only 1, create 2 instances of it, one of
    # which is a "twin".

    # set up to play tic tac toe
    opponent_wins_ttt = 0
    we_win_ttt = 0
    static_eval_accesses = 0
    import ccahrens_KInARow as h
    import RandomPlayer as m
    num_matched = 10

    # run games with our agent as x
    print("Starting TTT X games...")
    for i in range (0, num_matched):
        print(f"...running game {i + 1}")
        px = h.OurAgent()
        po = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "X":
                we_win_ttt += 1
            else:
                opponent_wins_ttt += 1
            static_eval_accesses += px.eval_calls
    # run games with our agent as O
    print("Starting TTT O games...")
    for i in range (0, num_matched):
        print(f"...running game {i + 1}")
        po = h.OurAgent()
        px = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "O":
                we_win_ttt += 1
            else:
                opponent_wins_ttt += 1
            static_eval_accesses += po.eval_calls

    # set up for FIAR
    set_game(FIAR)
    opponent_wins_fiar = 0
    we_win_fiar = 0
    # run games with our agent as X
    print("Starting FIAR X games...")
    for i in range (0, num_matched):
        print(f"...running game {i + 1}")
        px = h.OurAgent()
        po = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "X":
                we_win_fiar += 1
            else:
                opponent_wins_fiar += 1
            static_eval_accesses += px.eval_calls
    # run games with our agent as O
    print("Starting FIAR O games...")
    for i in range (0, num_matched):
        print(f"...running game {i + 1}")
        po = h.OurAgent()
        px = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "O":
                we_win_fiar += 1
            else:
                opponent_wins_fiar += 1
            static_eval_accesses += po.eval_calls

    # set up for cassini
    set_game(Cassini)
    opponent_wins_cassini = 0
    we_win_cassini = 0
    # run games with our agent as X
    print("Starting CASSINI X games...")
    for i in range (0, num_matched):
        print(f"...running game {i + 1}")
        px = h.OurAgent()
        po = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "X":
                we_win_cassini += 1
            else:
                opponent_wins_cassini += 1
            static_eval_accesses += px.eval_calls
    # run games with our agent as O
    print("Starting CASSINI O games...")
    for i in range (0, num_matched):
        print(f"...running game {i + 1}")
        po = h.OurAgent()
        px = m.OurAgent()
        set_players(px, po)
        res = runGame()
        if res is not None:
            if res == "O":
                we_win_cassini += 1
            else:
                opponent_wins_cassini += 1
            static_eval_accesses += po.eval_calls
    

    # display results
    print()
    print("***TTT RESULTS***")
    print(f"opponent wins: {opponent_wins_ttt}")
    print(f"our wins: {we_win_ttt}")
    print(f"our win rate: {100* we_win_ttt/(opponent_wins_ttt + we_win_ttt)}%")

    print()
    print("***FIAR RESULTS***")
    print(f"opponent wins: {opponent_wins_fiar}")
    print(f"our wins: {we_win_fiar}")
    print(f"our win rate: {100* we_win_fiar/(opponent_wins_fiar + we_win_fiar)}%")

    print()
    print("***CASSINI RESULTS***")
    print(f"opponent wins: {opponent_wins_cassini}")
    print(f"our wins: {we_win_cassini}")
    print(f"our win rate: {100*we_win_cassini/(opponent_wins_cassini + we_win_cassini)}%")

    print()
    print("***STATIC EVAL ACCESSES***")
    print(f"static eval accesses: {static_eval_accesses}")

    # Depth limit: 3
    # Pruning: True
    # Total games: 60

    #***TTT RESULTS***
    # opponent wins: 16
    # our wins: 3
    # our win rate: 15.789473684210526%

    # ***FIAR RESULTS***
    # opponent wins: 6
    # our wins: 13
    # our win rate: 68.42105263157895%

    # ***CASSINI RESULTS***
    # opponent wins: 9
    # our wins: 8
    # our win rate: 47.05882352941177%

    # ***STATIC EVAL ACCESSES***
    # static eval accesses: 21277103

def testDialogue(game=FIAR, ai=True):
    import ccahrens_KInARow as h
    print("Starting testDialogue()")
    set_game(game)
    px = h.OurAgent(ai=ai)
    po = h.OurAgent(twin=True, ai=ai)
    set_players(px, po)
    print("Players are set.")
    print("Now let's run the game.")
    runGame()
    print("X accesses: ", px.eval_calls)
    print("O accesses: ", po.eval_calls)

import sys
if __name__ == '__main__':
    runs: int = 10
    if sys.argv[1:] is not None and sys.argv[1].isdigit():
        runs = int(sys.argv[1])
    ccTestMany(runs=runs, ai=False)
    # test()
    
