from parser import IMDBParser
from tqdm import tqdm

class BechdelAnalyser():
    def __init__(self, num_scripts=10):
        self.parser = IMDBParser(num_scripts=num_scripts)
        self.script_dialogues = self.parser.scripts

        self.female_names = self.parser.female_names
        self.male_tags = self.parser.male_tags 
        self.female_tags = self.parser.female_tags 

        self.num_fail_one = 0
        self.num_fail_two = 0
        self.num_fail_three = 0
        self.num_pass_test = 0

        self.num_scripts = len(self.script_dialogues)
    
    def passes_first_criteria(self, character, prev_character):
        """Check if two female characters are speaking with each other."""
        if character != prev_character and self.prev_female:
            return True
        return False

    def passes_second_criteria(self, text, prev_text):
        """Checks if two women are talking to each other about 
        something other than a man."""
        if prev_text is not None:
            for male_tag in self.male_tags:
                if male_tag in text or male_tag in prev_text:
                    return False
        return True

    def passes_third_criteria(self, character, prev_character):
        """Checks if two women are named."""
        if (character in self.female_names 
            and prev_character in self.female_names):
            return True 
        return False
    
    def _passes_test(self, character, prev_character, text, prev_text):
        if (self.passes_first_criteria(character, prev_character)
            and self.passes_third_criteria(character, prev_character)
            and self.passes_second_criteria(text, prev_text)):
            return True
        return False
    
    def _passes_one(self, character, prev_character, text, prev_text):
        if ((self.passes_first_criteria(character, prev_character)
            and not self.passes_third_criteria(character, prev_character)
            and not self.passes_second_criteria(text, prev_text))

            or (self.passes_first_criteria(character, prev_character)
            and not self.passes_second_criteria(text, prev_text)
            and not self.passes_third_criteria(character, prev_character))

            or (self.passes_second_criteria(text, prev_text)
            and not self.passes_third_criteria(character, prev_character))
            and not self.passes_first_criteria(character, prev_character)):
            return True
    
    def _passes_two(self, character, prev_character, text, prev_text):
        if ((self.passes_first_criteria(character, prev_character)
            and self.passes_third_criteria(character, prev_character)
            and not self.passes_second_criteria(text, prev_text))

            or (self.passes_first_criteria(character, prev_character)
            and self.passes_second_criteria(text, prev_text)
            and not self.passes_third_criteria(character, prev_character))

            or (self.passes_second_criteria(text, prev_text)
            and self.passes_third_criteria(character, prev_character))
            and not self.passes_first_criteria(character, prev_character)):
            return True

    def perform_bechdel_test(self, script):
        passes_one = False
        passes_two = False
        passes_test = False

        prev_character = None
        prev_text = None
        self.prev_female = False

        for character, text in script:
            if character in self.female_tags:
                if not passes_one:
                    if self._passes_one(character, prev_character, text, prev_text):
                        passes_one = True

                if not passes_two: #if passes only two 
                    if self._passes_two(character, prev_character, text, prev_text):
                        passes_two = True

                #check if passes full test
                if self._passes_test(character, prev_character, text, prev_text):
                    passes_test = True
                    break

                prev_text = text
                prev_character = character
                self.prev_female = True
            
            else: 
                prev_character = None
                prev_text = None
                self.prev_female = False
        
        if passes_one:
            if passes_two:
                if passes_test:
                    self.num_pass_test += 1
                else:
                    self.num_fail_one += 1
            else: 
                self.num_fail_two += 1
        else: 
            self.num_fail_three += 1
    
    def get_bechdel_analysis(self):
        for script in tqdm(self.script_dialogues.values(), desc="Analysing scripts..."):
            self.perform_bechdel_test(script)
        
        statistics = {'Pass': self.num_pass_test/self.num_scripts, 
                      'Fail 1': self.num_fail_one/self.num_scripts, 
                      'Fail 2': self.num_fail_two/self.num_scripts, 
                      'Fail 3': self.num_fail_three/self.num_scripts}

        print(statistics)

if __name__ == '__main__':
    analyser = BechdelAnalyser(num_scripts = 50)
    analyser.get_bechdel_analysis()


