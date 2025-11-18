from string import ascii_letters
from random import choice

class cased(str):
    def __new__(cls, value):
        self = super().__new__(cls, value)
        return self

    # Other cases (9 cases)

    def mocking(self, foreach: bool = False):
        """Returns a MoCkInG cAsEd TeXt.
        
        Argument foreach:
        	if True, the mocking case will be applied for each letter, if not, mocking case will apply only to each word.
        	
        >>> cased("hello world").mocking() → 'HELLO world'
        >>> cased("hello world").mocking(foreach=True) → 'HeLlO WoRlD'
        """
        nt = ""
        if not foreach:
            for i, t in enumerate(self.split()):
                nt += (t.upper() if (i % 2 == 0) else t.lower()) + " "
        else:
            for i, t in enumerate(self):
                nt += t.upper() if (i % 2 == 0) else t.lower()
        return nt.strip()
        
     
    def camel(self, spaced: bool = False):
        """Return a camelCasedText.
        
        Argument spaced:
        	if True, the words will be spaced with a whitespace, if not, the words won't be spaced, defaulted to False.
        	
        >>> cased("hello world").camel() → 'helloWorld'
        >>> cased("hello world").camel(True) → 'hello World'
        """
        nt = ""
        for i, t in enumerate(self.split()):
            word = t.lower() if i == 0 else t.capitalize()
            nt += word + (" " if spaced else "")
        return nt.strip() if spaced else nt
        
     
     
    def Pascal(self, spaced: bool = True):
        """Returns a PascalCasedText.
        
        Argument spaced:
        	if True, the words will be spaced with a whitespace, if not, the words won't be spaced, defaulted to True.
        	
        >>> cased("hello world").Pascal() → 'Hello World'
        >>> cased("hello world").Pascal(False) → 'HelloWorld'
        """
        parts = (t.capitalize() for t in self.split())
        return " ".join(parts) if spaced else "".join(parts)
        
     
    def snake(self):
        """Returns a snake_cased_text."""
        return "_".join(self.split())
        
     
    def kebab(self):
        """Returns a kebab-cased-text."""
        return "-".join(self.split())
        
    
    def path(self):
        """Returns a path/cased/text."""
        return "/".join(self.split())
        
    def screaming_snake(self):
    	"""Returns an UPPER_SNAKE_CASED_TEXT."""
    	return "_".join(self.upper().split())
    
    def train(self):
    	"""Returns a Train-Cased-Text."""
    	return "-".join(self.title().split())
    	
    def dot(self):
    	"""Returns a dot.cased.text"""
    	return ".".join(self.split())
    
    # Methods & Properties
    def swapcase(self):
    	"""Returns a swapcased text, where every lowercase letter become upper case & vice versa.
    	>>> cased("Hello World").swapcase() → 'hELLO wORLD'
    	"""
    	text = ""
    	for i in self:
    		if i == i.lower():
    			text += i.upper()
    		else:
    			text += i.lower()
    	return text
    
    
    def reverse(self, foreach: bool = False):
        """Returns a reversed text
        Argument foreach:
        	if set to True, every letter in each word gets reversed, if not, each word becomes reversed, defaulted by False.
        >>> cased("hello world").reverse() → 'world hello'
        >>> cased("hello world").reverse(True) → 'dlrow olleh'
        """
        return self[::-1] if foreach else " ".join(self.split()[::-1])
    
    
    def to_ascii(self):
    	"""Removes any letters that don't exist in the ASCII letters
    	>>> cased("ɑpɸleʃ").to_ascii() → 'ple'
    	"""
    	text = ""
    	for i in self:
    		if i in ascii_letters or i == " ":
    			text += i
    	return text
    
    def rm_vowels(self):
    	"""Removes vowels from the text.
    	>>> cased("hello world").rm_vowels() → 'hll wrld'
    	"""
    	filtered: list = [i for i in self if not i in ["a", "e", "i", "o", "u", "y"]]
    	return "".join(filtered)
    	
    def repeat(self, n: int = 2):
    	"""Repeats a text for a given time.
    	Argument n:
    		the number of times repeating the text. Defaulted by 2.
    	>>> cased("Hi").repeat(3) → 'HiHiHi'
    	"""
    	return self * n
    
    def ct_constants(self):
    	"""Counts the constants in the text
    	>>> cased("python").ct_constants() → '4'
    	"""
    	count: tuple = 0
    	for i in self:
    		 if not i.lower() in ("a", "e", "i", "o", "u", "y", " "):
    		 	count += 1
    	return count
    
    def ct_vowels(self):
    	"""Counts the vowels in the text.
    	>>> cased("python").ct_vowels() → '2'
    	"""
    	count: int = 0
    	for i in self:
    		 if i.lower() in ("a", "e", "i", "o", "u", "y"):
    		 	count += 1
    	return count

    def contains(self, item: str | int | bool):
        """Checks if the text contains a specified item.
        >>> cased("Apple").contains("l") → True
        """
        return item.lower() in self.lower()
    	
    	
    # Aliases
    UpperCamel = Pascal
    slash = path
    upper_snake = screaming_snake
    capitalized_kebab = train

    
