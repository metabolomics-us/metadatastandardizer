import pandas as pd
import json
from pprint import pprint

class SexListParser():

    def __init__(self,input_file_path,output_file_path):
        self.input_file_path=input_file_path
        self.output_file_path=output_file_path

    def create_attribute_to_node_id(self):
        '''
        in the case of sexes, because we couldnt find a nice ontology we are just making our own list
        the node id, valid string, and main string will all be the same
        '''

        input_panda=pd.read_csv(self.input_file_path,sep='\t',header=None)

        self.total_feature_node_id_dict=dict()
        for index, series in input_panda.iterrows():
            
            
            self.total_feature_node_id_dict[series[0]]=dict()
            
            self.total_feature_node_id_dict[series[0]]['valid_strings']=[series[0]]
            self.total_feature_node_id_dict[series[0]]['main_string']=series[0]
            

        with open(self.output_file_path, 'w') as fp:
            json.dump(self.total_feature_node_id_dict, fp,indent=4) 


if __name__=="__main__":

    my_SexListParser=SexListParser(
        'resources/sexes_parker_created.txt',
        'results/individual_vocabulary_jsons/sex.json'
    )
    my_SexListParser.create_attribute_to_node_id()
