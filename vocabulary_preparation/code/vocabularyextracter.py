import json
import pandas as pd


class VocabularyExtracter:

    def __init__(self,input_address,output_address):
        self.input_address=input_address
        self.output_address=output_address       

    def extract_vocabulary(self):
        '''
        takes the conglomerate json with valid strings as keys and outputs a list of 
        those strings.
        use pandas for convenience
        '''

        with open(self.input_address, 'r') as fp:
            conglomerate_json=json.load(fp)

        output_list=list(conglomerate_json.keys())

        output_panda=pd.DataFrame.from_dict({'valid_strings':output_list})

        output_panda.to_pickle(self.output_address)


if __name__=="__main__":
    my_VocabularyExtracter=VocabularyExtracter(
        'results/conglomerate_vocabulary_jsons/combined_valid_string_as_key.json',
        'results/training_set/valid_string_list_dataframe.bin'
    )
    my_VocabularyExtracter.extract_vocabulary()