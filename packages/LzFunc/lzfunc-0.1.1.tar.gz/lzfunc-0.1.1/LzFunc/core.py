"""
The Lazy Functions Module (LFM) - minimalist utilities for clean code.

A collection of shortcuts for routine tasks: quick outputs, pauses, 
decorative elements, and other "lazy" solutions to reduce boilerplate.

Key Features:
    - nl(lines=1)          - line break (1 by default).
    - pause(seconds)       - animated delay.
    - input_yesno(prompt)  - yes/no question with auto-conversion to bool.

Quickstart:
    >>> from lfm import nl, pause
    >>> print("Start")
    >>> nl(2)
    >>> pause(3)  # 3-second countdown
    >>> print("Done!")

Note:
    The code is intentionally simple - feel free to fork and adapt.
    Author: Pozitive_Guy
    Version: 1.1
"""

import time

class All:
    """All variable type for some functions, don't really mind it."""
    def __init__(self):
        self._allowed_to_print = False
        self._secret_key = None
    
    def __call__(self, key=None):
        if key is None:
            raise NonSpecificError("Can't call non-specified order from All")
        
        self._allowed_to_print = True
        self._secret_key = key
        return self
    
    def __str__(self):
        if not self._allowed_to_print:
            raise NonSpecificError("Can't call non-specified order from All")
        
        self._allowed_to_print = False
        return str(self._secret_key)
        
    def __invert__(self):
        return None
    
    def __repr__(self):
        return "All"

class NonSpecificError(Exception):
    pass

All = All()

def nl(lines=1):
    """Skips a line. 
    
    Example:
        
        print("Hello")
        nl(2)
        print("World")
    
    Result:
    
        Hello
    
    
        World
        """
    print((lines - 1) * "\n")
   
def pause(seconds=1):
    """Waits an interval with a fancy three-dot animation
    
    Example:
        
        print("Wait a second", end="")
        pause(3)
        print("Hello, World!!!")
        
    Result:
        
        No result :(
        
    About:
        
        Default interval is set to 1 second, animation works proportionally to the interval, so if you set the function to 3 seconds, each dot will take 1 second to appear. Boom. Cool, isn't it?
    """
    interval = seconds / 3
    for i in range(3):
        print(".", end="", flush=True)
        time.sleep(interval)
    print("\n") # No way I didn't use nl() here. Boilerplate rules the world.

def input_yesno(message):
    """Makes simple "Yes or No" question, that returns complete boolean answer to the variable. (Has different yes or no answers: yes, y, ofc, of course, duh, yeah, yea, no, n, nah, naw, nuh uh)
    
    Example:
        
        answer = input_yesno("Do you like dancing? ")
        if answer == True:
            print("I like trains.") 
        if answer == False:
            print("I like singing!")
    
    Result:
       
        Do you like dancing? Yes
        I like trains.
       """
    while True:
        question = input(message).lower()
        if question in ["yes", "y", "ofc", "of course", "duh", "yeah", "yea"]:
            return True
        if question in ["no", "n", "nah", "naw", "nuh uh"]:
            return False
           
def input_default(prompt, default):
    """Returns Default value on [ENTER]. 
    
    Example:
        
        name = input_default("What is your name? (Anonym by Default) ", "Anonym")
        print(name)
        
     Result:
         
         What is your name? (Anonym by Default) [ENTER]
         Anonym
          """
    answer = input(prompt)
    return answer if answer else default

def invert(var):
    """Simple switch to invert the variable
    
    Example:
    
        switchstate = True
        
        if switchstate == True:
            turn = input_yesno("Turn off the switch? ")
        if turn == False:
            None
        if turn == True:
            switchstate = invert(switchstate)
            
        print("Current switch state:", switchstate)"""
    if isinstance(var, bool):
        return not var
    elif isinstance(var, int):
        return -var
    elif isinstance(var, str):
        text = list(var)
        rev = text[::-1]
        inv = "".join(rev)
        return inv
    elif isinstance(var, list):
        return var[::-1]
    elif var == None or var == All:
        try:
            var = ~var
        except Exception:
            var = All
        return var
    else:
        print("This variable type is not supported :(")
        return var
        
if __name__ == "__main__":
    None # Well done! You've got nothing!
