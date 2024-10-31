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
    
    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

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
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > len(self.board) // 2 + len(self.board) % 2:
            self.board[y][x] = None
            return False
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False

        self.board[y][x] = None
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
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    if self.is_legal(x, y, num):
                        moves.append([str(x), str(y), str(num)])
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
        self.pattern_weights = {}

        try:
            with open(filename, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) != 3:
                        continue
                    try:
                        pattern, num, weight = parts[0], int(parts[1]), float(parts[2])
                        if num != 0 and num != 1:
                            #continue
                            self.pattern_weights[(pattern, num)] = weight
                    except ValueError:
                        continue
        except FileNotFoundError:
            return False
        except Exception as e:
            return False

        return True

    # new function to be implemented for assignment 3
    def policy_moves(self, args):
        try:
            moves = self.get_legal_moves()
            if not moves:
                return False

            # Use uniform distribution when no patterns loaded
            if not hasattr(self, 'pattern_weights') or not self.pattern_weights:
                prob = 1.0 / len(moves)
                moves.sort()  # Ensure consistent ordering
                # Pre-allocate output array for better performance
                #output = [''] * (len(moves) * 4)
                output = []
                #for i, move in enumerate(moves):
                    #base = i * 4
                    #output[base] = str(move[0])
                    #output[base+1] = str(move[1])
                    #output[base+2] = str(move[2])
                    #output[base+3] = "0.5" if prob == 0.5 else "0.25" if prob == 0.25 else f"{prob:.3f}"
                for move in moves:
                    output.extend([str(move[0]), str(move[1]), str(move[2]), f"{prob:.3f}".rstrip('0').rstrip('.')])
                print(" ".join(output))
                return True

            # Pre-calculate board info and sort moves
            board_size = len(self.board)
            moves.sort()
            base_weight = 0.00001  # Ultra-low base weight
            pattern_weights = self.pattern_weights  # Cache dictionary lookup
            pattern_buffer = bytearray(6)  # Single reusable pattern buffer

            # Pre-allocate arrays for maximum efficiency
            n_moves = len(moves)
            weights = [0.0] * n_moves  # Use list instead of array for better performance
            total_weight = 0.0

            # Calculate weights using optimized list operations
            for i, move in enumerate(moves):
                try:
                    pattern = self._fast_extract_pattern(move, pattern_buffer)
                    weight = pattern_weights.get((pattern, move[2]), base_weight)
                    if weight > base_weight:
                        weight *= 64  # Ultra-high pattern weight amplification
                    weights[i] = weight
                    total_weight += weight
                except Exception:
                    weights[i] = base_weight
                    total_weight += base_weight

            # Pre-allocate output array and calculate inverse total once
            #output = [''] * (n_moves * 4)
            output = []
            inv_total = 1.0 / total_weight if total_weight else 1.0

            # Generate output with minimal string operations and exact decimal matching
            #for i in range(n_moves):
                #base = i * 4
                #move = moves[i]
                #prob = weights[i] * inv_total
                # Format probability with exact decimal places and no trailing zeros
                #prob_str = "0.5" if abs(prob - 0.5) < 1e-6 else "0.25" if abs(prob - 0.25) < 1e-6 else f"{prob:.3f}".rstrip('0').rstrip('.')
                #output[base] = str(move[0])
                #output[base+1] = str(move[1])
                #output[base+2] = str(move[2])
                #output[base+3] = prob_str
            for i, move in enumerate(moves):
                prob = weights[i] * inv_total
                prob_str = f"{prob:.3f}".rstrip('0').rstrip('.')
                output.extend([str(move[0]), str(move[1]), str(move[2]), prob_str])

            print(" ".join(output))
            return True

        except Exception:
            # Catch any unexpected errors and return False
            return False

    def extract_pattern(self, move):
        # Wrapper for backward compatibility
        pattern_buffer = bytearray(6)
        return self._fast_extract_pattern(move, pattern_buffer)

    def _fast_extract_pattern(self, move, pattern_buffer):
        try:
            x, y, num = move
            board = self.board
            board_size = len(board)

            if not (0 <= x < board_size and 0 <= y < board_size):
                #raise ValueError("Invalid move coordinates")
                return "......"

            # Temporarily place the move
            original = board[y][x]
            board[y][x] = num

            try:
                # Direct array access for vertical pattern with bounds checking
                for i in range(3):
                    ny = y + i - 1
                    if 0 <= ny < board_size:
                        cell = board[ny][x]
                        pattern_buffer[i] = ord('0' + cell) if cell is not None else ord('.')
                    else:
                        pattern_buffer[i] = ord('#')

                # Direct array access for horizontal pattern with bounds checking
                for i in range(3):
                    nx = x + i - 1
                    if 0 <= nx < board_size:
                        cell = board[y][nx]
                        pattern_buffer[i+3] = ord('0' + cell) if cell is not None else ord('.')
                    else:
                        pattern_buffer[i+3] = ord('#')

                return pattern_buffer.decode('ascii')

            finally:
                # Ensure board is restored even if an error occurs
                board[y][x] = original

        except Exception:
            # Return a safe default pattern on error
            return "......"

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 3 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()