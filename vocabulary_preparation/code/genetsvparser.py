import pandas as pd
import json

class GeneTSVParser:
    
    def __init__(self,file_path):
        self.gene_panda=pd.read_csv(file_path,sep='\t')


    def create_attribute_to_node_id_from_panda(self):
        '''
        we assume that 'Symbol' and 'Description' are what we need to complete this
        '''

        self.total_feature_node_id_dict=dict()
        for index, series in self.gene_panda.iterrows():
            
            self.total_feature_node_id_dict[series['NCBI GeneID']]=dict()
            
            self.total_feature_node_id_dict[series['NCBI GeneID']]['main_string']=series['Description']

            self.total_feature_node_id_dict[series['NCBI GeneID']]['valid_strings']=[
                series['Symbol'],
                series['Description']
            ]


if __name__=="__main__":
    my_GeneTSVParser=GeneTSVParser('resources/ncbi_genes_human.tsv')
    my_GeneTSVParser.create_attribute_to_node_id_from_panda()
    with open('results/individual_vocabulary_jsons/genesHuman.json', 'w') as fp:
        json.dump(my_GeneTSVParser.total_feature_node_id_dict, fp,indent=4) 
