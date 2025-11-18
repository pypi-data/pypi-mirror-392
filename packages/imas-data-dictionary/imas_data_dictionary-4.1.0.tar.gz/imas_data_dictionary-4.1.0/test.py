import sys
with open('dd_data_dictionary_validation.txt') as f:
    assert not 'Error' in f.read(), "Found error in validation"
 

