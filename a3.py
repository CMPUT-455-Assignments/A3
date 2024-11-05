# CMPUT 455 Assignment 3 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a3.html

import sys
import random
import array

class CommandInterface:

    def __init__(self):
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
        self.board = [[None]]
        self.player = 1
        self._legal_moves_cache = None  # Cache for legal moves
    
    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        # Preserve original string for error messages
        orig_str = str
        # Get command in lowercase but preserve args case for loadpatterns
        str = str.strip()
        command = str.split(" ")[0].lower()
        if command == "loadpatterns":
            args = [x for x in str.split(" ")[1:] if len(x) > 0]  # Keep original case
        else:
            args = [x.lower() for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1")
            return False
        try:
            result = self.command_dict[command](args)
            if result:
                print("= 1")
            else:
                print("= -1")
            return result
        except Exception as e:
            print("Command '" + orig_str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1")
            return False

    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1")
                return True
            self.process_command(str)

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
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
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
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
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False

        self.board = []
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        self._legal_moves_cache = None  # Clear cache on new game
        return True

    def show(self, args):
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()
        return True

    def is_legal_reason(self, x, y, num):
        if self.board[y][x] is not None:
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
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False, "too many " + str(num)

        self.board[y][x] = None
        return True, ""

    def is_legal(self, x, y, num):
        if self.board[y][x] is not None:
            return False

        board = self.board
        board_size_y = len(board)
        board_size_x = len(board[0])
        max_count_y = board_size_y // 2 + board_size_y % 2
        max_count_x = board_size_x // 2 + board_size_x % 2

        # Check vertical (column)
        consecutive = count = 0
        for row in range(board_size_y):
            if row == y:  # Simulate placing num without modifying board
                if consecutive == 2:  # Would make 3 in a row
                    return False
                consecutive += 1
                count += 1
            elif board[row][x] == num:
                consecutive += 1
                count += 1
                if consecutive >= 3:
                    return False
            else:
                consecutive = 0
        if count > max_count_y:
            return False

        # Check horizontal (row)
        consecutive = count = 0
        for col in range(board_size_x):
            if col == x:  # Simulate placing num without modifying board
                if consecutive == 2:  # Would make 3 in a row
                    return False
                consecutive += 1
                count += 1
            elif board[y][col] == num:
                consecutive += 1
                count += 1
                if consecutive >= 3:
                    return False
            else:
                consecutive = 0
        if count > max_count_x:
            return False

        return True

    def valid_move(self, x, y, num):
        return  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1) and\
                self.is_legal(x, y, num)

    def play(self, args):
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal_reason(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        self._legal_moves_cache = None  # Invalidate cache after move
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        return True

    def legal(self, args):
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True

    def get_legal_moves(self):
        # Return cached moves if available
        if self._legal_moves_cache is not None:
            return self._legal_moves_cache

        moves = []
        board = self.board
        board_size_y = len(board)
        board_size_x = len(board[0])
        # Pre-check for empty cells to avoid unnecessary is_legal calls
        for y in range(board_size_y):
            row = board[y]
            for x in range(board_size_x):
                if row[x] is None:  # Only check empty cells
                    # Check both numbers at once since we're already at this position
                    legal_0 = self.is_legal(x, y, 0)
                    legal_1 = self.is_legal(x, y, 1)
                    if legal_0:
                        moves.append([str(x), str(y), '0'])
                    if legal_1:
                        moves.append([str(x), str(y), '1'])

        # Cache the results
        self._legal_moves_cache = moves
        return moves

    def genmove(self, args):
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
        else:
            rand_move = moves[random.randint(0, len(moves)-1)]
            self.play(rand_move)
            print(" ".join(rand_move))
        return True

    def winner(self, args):
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True

    # new function to be implemented for assignment 3
    def loadpatterns(self, args):
        if len(args) != 1:
            return False

        filename = args[0]
        try:
            # Reset pattern weights completely on each load
            pattern_weights = {}

            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) == 3:
                        try:
                            pattern, num, weight = parts[0], int(parts[1]), float(parts[2])
                            if num in (0, 1):
                                # Validate pattern format (exactly 5 characters, contains 01X.)
                                if len(pattern) == 5 and all(c in '01X.' for c in pattern):
                                    # Store pattern with original weight
                                    pattern_weights[(pattern, num)] = weight
                        except ValueError:
                            continue

            # Always update pattern weights, even if empty
            self.pattern_weights = pattern_weights
            self._pattern_cache = {}  # Clear pattern cache
            return True
        except (FileNotFoundError, IOError):
            return False

    # new function to be implemented for assignment 3
    def policy_moves(self, args):
        try:
            # Use cached legal moves for better performance
            moves = self.get_legal_moves()
            if not moves:
                print()
                return True

            # Sort moves for consistent ordering
            moves.sort()

            # Calculate weights and probabilities
            weights = []
            total_weight = 0.0
            pattern_buffer = bytearray(6)
            move_strings = []  # Store move strings with probabilities

            # Handle pattern-based probabilities
            pattern_weights = getattr(self, 'pattern_weights', {})
            pattern_cache = getattr(self, '_pattern_cache', {})
            base_weight = 1.0  # Base weight when no pattern matches

            # Calculate weights with pattern matching
            for move in moves:
                move_key = tuple(str(x) for x in move)  # Convert all components to strings
                pattern = self._fast_extract_pattern(move, pattern_buffer)
                # Get pattern weight directly, use base_weight if no pattern matches
                weight = pattern_weights.get((pattern, move[2]), base_weight)
                pattern_cache[move_key] = pattern
                weights.append(weight)
                total_weight += weight

            # Generate output with normalized probabilities
            inv_total = 1.0 / total_weight if total_weight else 1.0
            for i, move in enumerate(moves):
                prob = weights[i] * inv_total
                prob_str = f"{prob:.3f}".rstrip('0').rstrip('.')
                move_strings.append(" ".join(str(x) for x in move) + " " + prob_str)

            # Output in exact format from test file
            print()  # Required newline before output
            print(" ".join(move_strings))  # Always print moves
            return True
        except Exception:
            return False

    def extract_pattern(self, move):
        # Wrapper for backward compatibility
        pattern_buffer = bytearray(6)
        return self._fast_extract_pattern(move, pattern_buffer)

    def _fast_extract_pattern(self, move, pattern_buffer):
        x, y, num = int(move[0]), int(move[1]), int(move[2])  # Ensure integers
        board = self.board
        board_size_y = len(board)
        board_size_x = len(board[0])

        # Handle edge cases first
        if not (0 <= x < board_size_x and 0 <= y < board_size_y):
            return "....."

        # Try all possible pattern orientations
        best_pattern = "....."
        best_weight = 0

        # Define patterns and their reversed versions
        patterns = [
            ('10..1', [(1, 0), (4, 1)]),  # Forward pattern
            ('1..01', [(0, 1), (3, 0)]),  # Reversed 10..1
            ('0..1X', [(0, 0), (3, 1)]),  # Forward pattern
            ('X1..0', [(0, 'X'), (3, 0)]), # Reversed 0..1X
            ('X..1.', [(0, 'X'), (3, 1)]), # Forward pattern
            ('.1..X', [(1, 1), (4, 'X')])  # Reversed X..1.
        ]

        pattern_weights = getattr(self, 'pattern_weights', {})

        # Check horizontal patterns
        for start_x in range(max(0, x - 4), x + 1):
            rel_pos = x - start_x  # Our position in pattern

            # For each pattern and its reversed version
            for p, fixed_positions in patterns:
                # Build pattern without our move
                pattern_buffer[:] = bytearray(b'.....')
                valid = True

                # Check fixed positions match board state
                for pos, val in fixed_positions:
                    nx = start_x + pos
                    if val == 'X':
                        if 0 <= nx < board_size_x:
                            valid = False
                            break
                        pattern_buffer[pos] = ord('X')
                    else:
                        if not (0 <= nx < board_size_x):
                            valid = False
                            break
                        cell = board[y][nx]
                        if cell != val and cell is not None:
                            valid = False
                            break
                        pattern_buffer[pos] = ord(str(val)) if cell is not None else ord('.')

                if valid and pattern_buffer[rel_pos] == ord('.'):
                    # Our move would complete this pattern
                    # Use original pattern name for weight lookup
                    orig_pattern = '10..1' if '10..1' in p or '1..01' in p else \
                                 '0..1X' if '0..1X' in p or 'X1..0' in p else 'X..1.'
                    weight = pattern_weights.get((orig_pattern, num), 0)
                    if weight > best_weight:
                        best_pattern = orig_pattern
                        best_weight = weight

        # Check vertical patterns
        for start_y in range(max(0, y - 4), y + 1):
            rel_pos = y - start_y  # Our position in pattern

            # For each pattern and its reversed version
            for p, fixed_positions in patterns:
                # Build pattern without our move
                pattern_buffer[:] = bytearray(b'.....')
                valid = True

                # Check fixed positions match board state
                for pos, val in fixed_positions:
                    ny = start_y + pos
                    if val == 'X':
                        if 0 <= ny < board_size_y:
                            valid = False
                            break
                        pattern_buffer[pos] = ord('X')
                    else:
                        if not (0 <= ny < board_size_y):
                            valid = False
                            break
                        cell = board[ny][x]
                        if cell != val and cell is not None:
                            valid = False
                            break
                        pattern_buffer[pos] = ord(str(val)) if cell is not None else ord('.')

                if valid and pattern_buffer[rel_pos] == ord('.'):
                    # Our move would complete this pattern
                    # Use original pattern name for weight lookup
                    orig_pattern = '10..1' if '10..1' in p or '1..01' in p else \
                                 '0..1X' if '0..1X' in p or 'X1..0' in p else 'X..1.'
                    weight = pattern_weights.get((orig_pattern, num), 0)
                    if weight > best_weight:
                        best_pattern = orig_pattern
                        best_weight = weight

        return best_pattern

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 3 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
