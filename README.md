# bechdel_test

Assumptions made for the purpose of simplicity:

    - All the scripts begin with <pre> tag (ignore otherwise). 

    - Character names prior to their dialogues have a similar 
      indentation in the raw html script --> I figured out the 
      indentation values that pertain to the most names through 
      a constant denominated name_tolerance_ratio (i.e. if a 
      sufficiently large percentage of the words for a given 
      indentation are names (as per male.txt and female.txt), 
      we consider that indentation level to be exclusive for names.

PS: I made use of the tqdm library for the sake of not going mad while 
waiting for the scripts to be parsed and analysed. 
