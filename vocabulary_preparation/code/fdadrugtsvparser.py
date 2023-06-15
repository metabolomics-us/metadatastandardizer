import pandas as pd
import json


class FDADrugTSVParser:

    def __init__(self,input_file_path,output_file_path):
        self.input_file_path=input_file_path
        self.output_file_path=output_file_path

    def create_attribute_to_node_id_from_panda(self):
        '''
        
        '''

        input_panda=pd.read_csv(self.input_file_path,sep='\t')
        input_panda.drop_duplicates(inplace=True)
        input_panda.drop_duplicates(
            subset=['DrugName'],
            inplace=True
        )
        input_panda.reset_index(drop=True,inplace=True)


        self.total_feature_node_id_dict=dict()
        for index, series in input_panda.iterrows():
            
            self.total_feature_node_id_dict[index]=dict()
            
            self.total_feature_node_id_dict[index]['main_string']=series['ActiveIngredient']

            self.total_feature_node_id_dict[index]['valid_strings']=[
                series['DrugName'],
                series['ActiveIngredient']
            ]

        with open(self.output_file_path, 'w') as fp:
            json.dump(my_FDADrugTSVParser.total_feature_node_id_dict, fp,indent=4) 


if __name__=="__main__":

    my_FDADrugTSVParser=FDADrugTSVParser(
        'resources/fda_drugs_simplified.tsv',
        'results/individual_vocabulary_jsons/drugs.json'
    )
    my_FDADrugTSVParser.create_attribute_to_node_id_from_panda()

