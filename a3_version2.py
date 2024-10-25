# CMPUT 455 Assignment 3 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a3.html

import sys
import random
import logging
import time
import threading
from functools import wraps, partial
import numpy as np

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='a3_debug.log', filemode='w')

# Add a stream handler to print logs to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def target():
                return func(*args, **kwargs)
            return threading.Timer(seconds, lambda: (_ for _ in ()).throw(TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds"))).start() or target()
        return wrapper
    return decorator

class CommandInterface:

    def __init__(self):
        logging.info("Initializing CommandInterface")
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner,
            "loadpatterns" : self.loadpatterns,
            "policy_moves" : self.policy_moves
        }
        self.patterns = []
        self.default_weight = 10
        self.board = [[None]]
        self.player = 1
        self.weight_cache = {}  # Initialize weight_cache as an instance variable
        logging.info("CommandInterface initialized")

    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        logging.debug(f"Processing command: {str}")
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            logging.warning(f"Unknown command: {command}")
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            result = self.command_dict[command](args)
            logging.debug(f"Command {command} executed with result: {result}")
            return result
        except Exception as e:
            logging.error(f"Command '{str}' failed with exception: {e}")
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False

    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        logging.info("Entering main loop")
        while True:
            try:
                str = input()
                logging.debug(f"Received input: {str}")
                if str.split(" ")[0] == "exit":
                    logging.info("Exiting main loop")
                    print("= 1\n")
                    return True
                if self.process_command(str):
                    print("= 1\n")
                else:
                    print("= -1\n")
            except EOFError:
                logging.info("Received EOFError, exiting main loop")
                return True
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                print(f"Error: {e}", file=sys.stderr)
                print("= -1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        logging.debug(f"Checking arguments: {args} against template: {template}")
        converted_args = []
        if len(args) < len(template.split(" ")):
            logging.warning(f"Not enough arguments. Expected: {template}, Received: {args}")
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                logging.warning(f"Invalid argument: {arg} cannot be interpreted as a number")
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        logging.debug("Argument check passed")
        return True

    # List available commands
    def help(self, args):
        logging.info("Executing help command")
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF PREDEFINED FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV START OF ASSIGNMENT 3 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
    #===============================================================================================

    def game(self, args):
        logging.info(f"Executing game command with args: {args}")
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            logging.warning(f"Invalid board size: {n}x{m}")
            print("Invalid board size:", n, m, file=sys.stderr)
            return False

        self.board = []
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        logging.info(f"Game initialized with board size {n}x{m}")

        # Load default patterns
        logging.info("Attempting to load default patterns from twopattern.txt")
        result = self.loadpatterns(["twopattern.txt"])
        logging.info(f"Default patterns loaded: {'success' if result else 'failed'}")
        return True

    def show(self, args):
        logging.info("Executing show command")
        logging.debug("Current board state:")
        for row in self.board:
            row_str = ""
            for x in row:
                if x is None:
                    row_str += "."
                    print(".", end="")
                else:
                    row_str += str(x)
                    print(x, end="")
            logging.debug(row_str)
            print()
        return True

    def is_legal_reason(self, x, y, num):
        logging.debug(f"Checking legality of move: x={x}, y={y}, num={num}")
        if self.board[y][x] is not None:
            logging.debug("Move is illegal: position is occupied")
            return False, "occupied"

        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    logging.debug("Move is illegal: three in a row")
                    return False, "three in a row"
            else:
                consecutive = 0
        too_many = count > len(self.board) // 2 + len(self.board) % 2

        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    logging.debug("Move is illegal: three in a row")
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            logging.debug(f"Move is illegal: too many {num}")
            return False, "too many " + str(num)

        self.board[y][x] = None
        logging.debug("Move is legal")
        return True, ""

    def is_legal(self, x, y, num):
        logging.debug(f"Checking if move is legal: x={x}, y={y}, num={num}")
        if self.board[y][x] is not None:
            logging.debug("Move is illegal: position is occupied")
            return False

        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    logging.debug("Move is illegal: three in a row")
                    return False
            else:
                consecutive = 0
        if count > len(self.board) // 2 + len(self.board) % 2:
            self.board[y][x] = None
            logging.debug(f"Move is illegal: too many {num} in column")
            return False

        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    logging.debug("Move is illegal: three in a row")
                    return False
            else:
                consecutive = 0
        if count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            logging.debug(f"Move is illegal: too many {num} in row")
            return False

        self.board[y][x] = None
        logging.debug("Move is legal")
        return True

    def valid_move(self, x, y, num):
        logging.debug(f"Checking if move is valid: x={x}, y={y}, num={num}")
        result = x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1) and\
                self.is_legal(x, y, num)
        logging.debug(f"Move validity: {result}")
        return result

    def play(self, args):
        logging.info(f"Executing play command with args: {args}")
        err = ""
        if len(args) != 3:
            logging.warning(f"Invalid number of arguments: {len(args)}")
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            logging.warning(f"Invalid coordinate: {args[0]}, {args[1]}")
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            logging.warning(f"Coordinate out of bounds: x={x}, y={y}")
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            logging.warning(f"Invalid number: {args[2]}")
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal_reason(x, y, num)
        if not legal:
            logging.warning(f"Illegal move: {reason}")
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        logging.info(f"Move played: x={x}, y={y}, num={num}")
        return True

    def legal(self, args):
        logging.info(f"Executing legal command with args: {args}")
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            logging.debug(f"Move is legal: x={x}, y={y}, num={num}")
            print("yes")
        else:
            logging.debug(f"Move is not legal: x={x}, y={y}, num={num}")
            print("no")
        return True

    def get_legal_moves(self):
        logging.debug("Getting legal moves")
        start_time = time.time()
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    if self.is_legal(x, y, num):
                        moves.append([str(x), str(y), str(num)])
        end_time = time.time()
        logging.debug(f"get_legal_moves execution time: {end_time - start_time:.6f} seconds")
        logging.debug(f"Legal moves: {moves}")
        return moves

    def genmove(self, args):
        logging.info("Executing genmove command")
        moves = self.get_legal_moves()
        if len(moves) == 0:
            logging.info("No legal moves available, resigning")
            print("resign")
        else:
            rand_move = moves[random.randint(0, len(moves)-1)]
            logging.info(f"Randomly selected move: {rand_move}")
            self.play(rand_move)
            print(" ".join(rand_move))
        return True

    def winner(self, args):
        logging.info("Executing winner command")
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                logging.info("Player 2 wins")
                print(2)
            else:
                logging.info("Player 1 wins")
                print(1)
        else:
            logging.info("Game is unfinished")
            print("unfinished")
        return True

    # new function to be implemented for assignment 3
    def loadpatterns(self, args):
        logging.info(f"Entering loadpatterns function with args: {args}")
        # Clear existing patterns
        self.patterns.clear()
        logging.debug("Cleared existing patterns")

        if len(args) != 1:
            logging.warning("Invalid number of arguments for loadpatterns")
            print("loadpatterns requires a filename argument.")
            return False

        filename = args[0]
        logging.debug(f"Attempting to load patterns from file: {filename}")
        try:
            with open(filename, 'r') as f:
                logging.info(f"Successfully opened file: {filename}")
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    logging.debug(f"Processing line {line_num}: {line}")
                    # Ignore comments
                    if line.startswith('#') or len(line) == 0:
                        logging.debug(f"Line {line_num}: Ignored (comment or empty)")
                        continue
                    # Each line is of the form: pattern move weight
                    parts = line.split()
                    if len(parts) != 3:
                        logging.error(f"Line {line_num}: Invalid pattern format: {line}")
                        print(f"Invalid pattern format: {line}")
                        return False
                    pattern, move, weight = parts
                    logging.debug(f"Line {line_num}: Parsed pattern: {pattern}, move: {move}, weight: {weight}")
                    try:
                        move = int(move)
                        weight = int(weight)
                        logging.debug(f"Line {line_num}: Converted move and weight to integers")
                    except ValueError:
                        logging.error(f"Line {line_num}: Invalid move or weight: {line}")
                        print(f"Invalid move or weight: {line}")
                        return False
                    self.patterns.append((pattern, move, weight))
                    logging.info(f"Line {line_num}: Successfully loaded pattern: {pattern}, move: {move}, weight: {weight}")
        except FileNotFoundError:
            logging.error(f"File not found: {filename}")
            print(f"File not found: {filename}")
            return False

        logging.info(f"Total patterns loaded: {len(self.patterns)}")
        logging.debug(f"Final state of patterns: {self.patterns}")
        return True

    def match_pattern(self, pattern, board_segment):
        """
        Check if the board segment matches the given pattern.
        A pattern is a 5-character string, and a board_segment is the 5x1 area of the board to check.
        The pattern can have '.', '0', '1', and 'X' (off-board).
        """
        logging.debug(f"Matching pattern: {pattern} against board segment: {board_segment}")
        match_result = all(p == '.' or (p == 'X' and b is None) or p == b for p, b in zip(pattern, board_segment))
        match_position = pattern.index('.') if '.' in pattern else -1
        relevance = 1 - abs(match_position - 2) / 2  # 2 is the center position
        return match_result, match_position, relevance

    def calculate_weight(self, x, y, num):
        start_time = time.time()
        logging.debug(f"Calculating weight for move: x={x}, y={y}, num={num}")

        # Check cache
        cache_key = (x, y, num)
        if cache_key in self.weight_cache:
            return self.weight_cache[cache_key]

        board_size = len(self.board) * len(self.board[0])
        base_weight = 1.0 / (board_size * 2)  # Ensures 0.005 probability for 10x10 board

        if not self.patterns or all(cell is None for row in self.board for cell in row):
            logging.debug("Empty board or no patterns loaded, returning base weight")
            return base_weight

        pattern_weights = []

        # Cache row and column segments
        row_segment = tuple(self.board[y][i] if 0 <= i < len(self.board[0]) else 'X' for i in range(x-2, x+3))
        col_segment = tuple(self.board[i][x] if 0 <= i < len(self.board) else 'X' for i in range(y-2, y+3))

        for pattern, move, weight in self.patterns:
            if move == num:
                row_match, row_pos, row_relevance = self.match_pattern(pattern, row_segment)
                col_match, col_pos, col_relevance = self.match_pattern(pattern, col_segment)
                if row_match or col_match:
                    relevance = max(row_relevance, col_relevance)
                    adjusted_weight = weight * relevance
                    pattern_weights.append(adjusted_weight)
                    logging.debug(f"Pattern {pattern} matched, adding adjusted weight {adjusted_weight}")

        if pattern_weights:
            pattern_weight = sum(pattern_weights)
            scaling_factor = 0.2  # Increased to have more impact
            final_weight = base_weight * (1 + scaling_factor * pattern_weight)  # Scaled pattern impact
        else:
            final_weight = base_weight

        logging.debug(f"Final weight calculated: {final_weight}")

        # Cache the result
        self.weight_cache[cache_key] = final_weight

        end_time = time.time()
        logging.debug(f"Time taken for calculate_weight: {end_time - start_time:.6f} seconds")
        return final_weight

    # new function to be implemented for assignment 3
    @timeout(0.9)
    def policy_moves(self, args):
        try:
            print("Starting policy_moves function")
            start_time = time.time()
            logging.info("Executing policy_moves command")

            # Convert board to numpy array
            np_board = np.array(self.board)
            logging.debug(f"Current board state:\n{np_board}")
            print(f"Current board state:\n{np_board}")

            logging.debug(f"Loaded patterns: {self.patterns}")
            print(f"Loaded patterns: {self.patterns}")

            # Get legal moves using numpy
            legal_moves = np.argwhere(np_board == None)
            print(f"Legal moves: {legal_moves}")
            logging.debug(f"Legal moves: {legal_moves}")

            if len(legal_moves) == 0:
                logging.warning("No legal moves available")
                print("No legal moves available")
                return True

            # Calculate weights for all legal moves
            board_size = np_board.size
            max_moves_to_calculate = min(5000, board_size)
            moves_calculated = 0
            move_weights = {}

            is_empty_board = np.all(np_board == None)

            for y, x in legal_moves:
                for num in range(2):
                    if is_empty_board:
                        weight = 1.0 / (board_size * 2)  # Ensures 0.005 probability for each move on 10x10 board
                    else:
                        weight = self.calculate_weight(x, y, num)
                    move_weights[(y, x, num)] = weight
                    moves_calculated += 1

                    if moves_calculated % 1000 == 0:
                        self._report_partial_results(move_weights)

                    if moves_calculated >= max_moves_to_calculate:
                        logging.warning(f"Reached maximum moves to calculate: {max_moves_to_calculate}")
                        break

                if moves_calculated >= max_moves_to_calculate:
                    break

            # Compute total weight and probabilities using numpy
            weights = np.array(list(move_weights.values()))
            total_weight = np.sum(weights)
            logging.debug(f"Total weight: {total_weight}")

            # Normalize probabilities
            probs = weights / total_weight

            # Ensure probabilities sum to 1.0
            probs /= np.sum(probs)
            logging.debug(f"Probability sum: {np.sum(probs)}")

            # Create a structured array for sorting
            moves = np.array(list(move_weights.keys()), dtype=[('y', int), ('x', int), ('num', int)])
            sorted_indices = np.lexsort((moves['num'], moves['x'], moves['y']))

            # Format results
            result = '\n'.join(f"{moves[i]['y']} {moves[i]['x']} {moves[i]['num']} {probs[i]:.3f}" for i in sorted_indices)
            print(result)
            logging.debug(f"Formatted result:\n{result}")

            total_time = time.time() - start_time
            logging.info(f"policy_moves execution time: {total_time:.4f}s")

            return True
        except TimeoutError:
            logging.error("policy_moves timed out")
            print("Error: policy_moves timed out")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in policy_moves: {e}")
            print(f"Error in policy_moves: {e}")
            return False

    def _report_partial_results(self, move_weights):
        total_weight = sum(move_weights.values())
        partial_probs = {move: weight / total_weight for move, weight in move_weights.items()}
        sorted_partial = sorted(partial_probs.items(), key=lambda x: (x[0][0], x[0][1], x[0][2]))
        partial_result = '\n'.join(f"{move[0]} {move[1]} {move[2]} {prob:.3f}" for move, prob in sorted_partial[:10])  # Show only top 10 moves
        print("Partial results (top 10 moves):")
        print(partial_result)
        logging.info("Partial results reported")



    policy_moves = timeout(0.9)(policy_moves)

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 3 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
