import os
from bs4 import BeautifulSoup
import string
import random
from tqdm import tqdm


alphabet_upper = list(string.ascii_uppercase)

#just some that i noticed could be used as a reference to a man or a woman 
#in a mobvie script
additional_female_tags = ['woman', 'women', 'girl', 'she'
                          'her', 'grandmother', 'grandma'
                          'mother', 'daughter', 'girlfriend'
                          'niece']

additional_male_tags = ['man', 'men', 'boy', 'he', 'him'
                        'grandfather', 'grandpa', 'father',
                        'son', 'nephew', 'boyfriend']

def get_names_list(filename):
    names_list = []
    with open(filename) as file:
        for line in file:
            if line[0] in alphabet_upper:
                names_list.append(line.strip().lower()) #strip name and
    return names_list

class IMDBParser():
    """Class to parse IMDB scripts provided."""
    def __init__(self, num_scripts=30, name_tolerance_ratio=0.6):
        self.scripts_dir = 'scripts_html'
        self.num_scripts = num_scripts

        #person tags
        self.male_names = get_names_list('male.txt')
        self.male_tags = self.male_names + additional_male_tags
        self.female_names = get_names_list('female.txt')
        self.female_tags = self.female_names + additional_female_tags
        self.person_tags = self.male_tags + self.female_tags

        self.name_tolerance_ratio = name_tolerance_ratio
        self.scripts = self.get_scripts_data()

    def get_html_data(self, filename):
        """Get data from .html file."""
        with open(f'{self.scripts_dir}/{filename}') as obj:
            #parse html
            data = BeautifulSoup(obj, "html.parser")
        return data
    
    def get_btag_indentations(self, b_tags):
        
        #get btags with same indentation
        indentations = {}
        for b_tag in b_tags:
            btag_text = b_tag.get_text()
            indent = len(btag_text) - len(btag_text.lstrip())

            if indent not in indentations.keys():
                indentations[indent] = []

            indentations[indent].append(btag_text.strip().lower())

        return indentations
    
    def identify_name_indents(self, indentations: dict):
        #initialise dictionary of name occurences and name ratios
        names_occurences = {}

        for (ind, line_texts) in indentations.items():
            num_names = 0
            total_words = 0
            names_list = []
            for text in line_texts:
                if ' ' in text:
                    #split occurences with a space to account for (cont'd) cases 
                    text_words = text.split(' ')
                    #remove punctuation from words
                    text_words = [word.translate(str.maketrans('', '', string.punctuation)) 
                                  for word in text_words]
                    for word in text_words:
                        if word in self.person_tags:
                            num_names += 1
                            names_list.append(word)
                        total_words += 1
                else: 
                    #remove punctuation if any
                    text = text.translate(str.maketrans('', '', string.punctuation)) 
                    if text in self.person_tags:
                        num_names += 1
                        names_list.append(text)
                    
                    total_words += 1

            name_ratio = num_names / total_words

            if name_ratio >= self.name_tolerance_ratio:
                names_occurences[ind] = names_list
        
        indents = list(names_occurences.keys()) #get relevant indent values

        return indents, names_occurences
    

    def get_dialogue_script(self, raw_script, name_indents):
        dialogue_script = []
        prev_line = ''
        dialogue = ''
        curr_name = ''
        dialogue_text = False

        #parse through script and identify dialogue text
        for i, line in enumerate(raw_script):
            if i == 0:
                prev_line = line
                continue

            #check if previous line corresponds to a name
            if len(prev_line) - len(prev_line.lstrip()) in name_indents and dialogue_text == False:
                if ' ' in prev_line:
                    #split occurences with a space to account for (cont'd) cases 
                    text_words = prev_line.split(' ')
                    #remove punctuation from words
                    text_words = [word.translate(str.maketrans('', '', string.punctuation)).strip().lower() 
                                    for word in text_words]
                    for word in text_words:
                        if word in self.person_tags:
                            curr_name = word 
                else: 
                    curr_name = prev_line.strip().lower()

                dialogue_text = True
            
            #condition for text ending is that indentation of
            #current line while dialogue_text == True is that the 
            #line is empty
            if dialogue_text == True:
                if line == '':
                    dialogue_text = False
                else: 
                    dialogue += ' ' + line.strip()
                
            if (dialogue_text == False and curr_name != '' 
                and dialogue != ''):
                dialogue_script.append((curr_name, dialogue))
                curr_name = ''
                dialogue = ''

            prev_line = line

        return dialogue_script

    def get_scripts_data(self):
        """Return a dictionary containing a list of
        tuples of the form (name, text). 
        """
        scripts = {}
        files = os.listdir(self.scripts_dir)
        parsed_files = 0

        #parse self.num_scripts files with acceptable format
        while parsed_files < self.num_scripts:
            filename = random.choice(files) #choose random file
            files.remove(filename) #remove chosen file from list
            #parse raw script data
            try:
                data = self.get_html_data(filename)
                btags =  data.find_all('b')
                script_title = btags[0].get_text().lstrip().strip('\n')
                raw_script = data.find('pre').get_text().split('\n')
            except Exception: #in some cases script may not be able to be parsed like this --> ignore them
                continue

            #get all indentations that pertain to names
            indentations = self.get_btag_indentations(btags)
            indents, name_occurences = self.identify_name_indents(indentations)

            #get dialogue between characters
            dialogue_script = self.get_dialogue_script(raw_script, indents)
            if len(dialogue_script) > 50: #minimum number of interactions between characters
                scripts[script_title] = dialogue_script
                parsed_files += 1

            print(f"Parsed files = {parsed_files}/{self.num_scripts}", end='\r')

        return scripts

if __name__ == '__main__':
    parser = IMDBParser()

    