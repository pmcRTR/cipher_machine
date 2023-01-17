import random, numbers, sys

# import this code with: from CipherMachine import CipherMachine
# create a cipher with: en = CipherMachine(number)
# then cipher text with: cipher_text = en.cipher("clear text")
# to decipher, create another cipher machine with the same start number (you can get the original start number from the existing cipher machine by calling en.start_position)
# then pass the cipher_text through and the original unciphered text will come back again: de = CipherMachine(en.start_position), clear_text = de.cipher(cipher_text)

# this is a software implementation of an Enigma machine but with 10 rotors (9 scramblers, 1 reflector) instead of 4 rotors (3 scramblers, 1 reflector)
# this software version also fixes the "a character can never be enciphered to itself" issue of the original (see reflector comments below)

class CipherMachine:

    # initialise the cipher machine components based on the start_position request
    # as long as the same start_position is used clear_text will be turned into cipher_text and cipher_text will be turned back into the original clear_text
    def __init__(self, start_position):
        self.start_position = start_position
        if isinstance(self.start_position, numbers.Number):
            random.seed(self.start_position)
        else:
            raise TypeError("The start position of the cipher machine must be expressed as a number.")
            sys.exit(1)
        # build master wheel alphabet (which is comprised of all printable ASCII characters)
        self.all_chars = [chr(char + 32) for char in range(0,95)]
        # build 9 scrambler wheel alphabets
        self.scrambled_1 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_2 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_3 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_4 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_5 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_6 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_7 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_8 = [chr(char + 32) for char in range(0,95)]
        self.scrambled_9 = [chr(char + 32) for char in range(0,95)]
        # and randomise them in a repeatable way with the seeded random (needs to be repeatable so deciphering from the same seed works)
        random.shuffle(self.scrambled_1)
        random.shuffle(self.scrambled_2)
        random.shuffle(self.scrambled_3)
        random.shuffle(self.scrambled_4)
        random.shuffle(self.scrambled_5)
        random.shuffle(self.scrambled_6)
        random.shuffle(self.scrambled_7)
        random.shuffle(self.scrambled_8)
        random.shuffle(self.scrambled_9)
        # combining the master wheel alphabet with a scrambled wheel alphabet you get the two halves of a scrambler wheel, for example:
        #  !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ <= entry side
        # gO7if0d>x,1#NDvZ5~T?AVp3^E9 FjUuwyMLGbc2@CWon};+]6*!{(hQ|YIma<JP"$lz.Ksq\:-_S48)=Hk`[&%rte/RBX' <= exit side
        # each character in the top row (entry side of the wheel) maps to the character directly below it in the bottom row (exit side of the wheel)
        # in the example wheel above, if I ciphered an uppercase E it would come out as a lowercase b
        #
        # the reflector wheel is different...
        reflector_base = [chr(char + 32) for char in range(0,95)]
        random.shuffle(reflector_base)
        # //2 to force integer division
        half_length = len(reflector_base) // 2
        top, bottom = reflector_base[:half_length], reflector_base[half_length:]
        # there are an odd number of printable ASCII characters which means the number of characters in the reflector is not neatly divisible by 2
        # when the reflector is constructed the result of the split between the two halves of the reflector not being even is that there is always one
        # character that reflects *to itself* - the nice thing about that is it neatly fixes a problem with the original Enigma: that it could never encipher a character into that same character...
        # this software cipher machine can  :)
        self.reflector = [chr(char + 32) for char in range(0,95)]
        # in the reflector wheel, pairs of characters always map to each other
        # ie. if A in the entry side of the wheel is mapped to e in the exit side of the wheel then e in the entry side of the wheel is mapped to A in the exit side of the wheel, for example:
        #  !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ <= entry side
        # -7vqm<lf?0s/V 9+)MTznyK!^.pF%H\(Ze|YrQ;o=cP6j1`iJEXk2a,_RC@t>{8WNUgIhA'bdOLS&$4G:#D*[u"}~53]Bwx <= exit side
        # note that, in the example reflector, the character lowercase u reflects to itself (see not neatly divisible by 2 comment above)
        for i in range(0,half_length):
            self.reflector[self.all_chars.index(top[i])] = bottom[i]
            self.reflector[self.all_chars.index(bottom[i])] = top[i]
        self.wheel_1 = [0, 0, self.all_chars, self.scrambled_1]
        self.wheel_2 = [0, 0, self.all_chars, self.scrambled_2]
        self.wheel_3 = [0, 0, self.all_chars, self.scrambled_3]
        self.wheel_4 = [0, 0, self.all_chars, self.scrambled_4]
        self.wheel_5 = [0, 0, self.all_chars, self.scrambled_5]
        self.wheel_6 = [0, 0, self.all_chars, self.scrambled_6]
        self.wheel_7 = [0, 0, self.all_chars, self.scrambled_7]
        self.wheel_8 = [0, 0, self.all_chars, self.scrambled_8]
        self.wheel_9 = [0, 0, self.all_chars, self.scrambled_9]
        # the reflector has a step of -1 which, in this case, means never step
        self.wheel_10 = [-1, -1, self.all_chars, self.reflector]
        self.out_wheels = [self.wheel_1, self.wheel_2, self.wheel_3, self.wheel_4, self.wheel_5, self.wheel_6, self.wheel_7, self.wheel_8, self.wheel_9, self.wheel_10]
        self.in_wheels = list(reversed(self.out_wheels))
        self.in_wheels = self.in_wheels[1:]
        # as well as a character being modified as it passes through each wheel, at various intervals, the scrambled sides of those wheels also rotate (step)
        # this means that a character entering a wheel won't always exit as the same character if, in the meantime, the wheel has rotated
        # this is further randomised by each wheel having a different step interval
        # all step numbers are actual step number minus one ie. a step number of 1 is defined as 0
        # steps are defined as primes so that wheels don't step together (except for whichever wheel that has a step interval of 0 which steps every time)
        step_intervals = [0, 1, 2, 4, 6, 10, 12, 16, 18]
        wheel_numbers = range(0, 9)
        random.shuffle(step_intervals)
        wheel_intervals = zip(wheel_numbers, step_intervals)
        # increase the randomness by randomly assigning the step intervals to the various wheels
        for wheel, step in wheel_intervals:
            self.in_wheels[wheel][0] = step
            self.in_wheels[wheel][1] = step

    # every time a character passes through the ciper all the wheels are checked to see if they need to step.  If not, their step interval is decremented
    # a wheel steps whenever its step interval reaches 0
    # when that happens it's scrambled side is stepped and its step interval is reset
    # a wheel step is just rotation of the scrambled side of the wheel by one character, eg. a wheel of ['a', 'b', 'c' ,'d'] would be ['b', 'c', 'd', 'a'] after it steps
    def step_wheels(self):
        for wheel in self.out_wheels:
            if wheel[0] < 0:
                wheel[0] = wheel[0]
            elif wheel[0] == 0:
                wheel[3] = wheel[3][1:] + wheel[3][0:1]
                wheel[0] = wheel[1]
            else:
                wheel[0] = wheel[0] - 1

    # the cipher machine does an outward and an inward pass for each character.  Each character passes through the machine like this:
    # wheel_1, wheel_2, wheel_3, wheel_4, wheel_5, wheel_6, wheel_7, wheel_8, wheel_9, wheel_10 (the reflector), wheel_9, wheel_8, wheel_7, wheel_6, wheel_5, wheel_4, wheel_3, wheel_2, wheel_1
    # in other words, a character is swapped 19 times between entering and exiting the cipher machine
    # adding in the wheel steps that happen at various intervals, as long as the start_position number is kept secret, the cipher is for all practical purposes, unbreakable
    def outward_pass(self, character):
        for wheel in self.out_wheels:
            character = wheel[3][wheel[2].index(character)]
        return character

    def inward_pass(self, character):
        for wheel in self.in_wheels:
            character = wheel[2][wheel[3].index(character)]
        return character

    def cipher(self, input_text):
        input_chars = [char for char in input_text]
        output_chars = []
        for char in input_chars:
            self.step_wheels()
            if char not in self.all_chars:
                in_char = char
            else:
                out_char = self.outward_pass(char)
                in_char = self.inward_pass(out_char)
                output_chars += in_char
        output_text = ''.join(output_chars)
        return output_text