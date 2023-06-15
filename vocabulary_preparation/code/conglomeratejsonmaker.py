import os
import json


class ConglomerateJSONMaker:

    def __init__(self,json_directory_address,output_directory_address):
        self.json_directory_address=json_directory_address
        self.output_directory_address=output_directory_address

    def generate_conglomerate_json(self):
        file_list=os.listdir(self.json_directory_address)
        conglomerate_dict=dict()

        for temp_file in file_list:
            current_json_type=temp_file[:-5]
            with open(self.json_directory_address+temp_file, 'r') as fp:
                current_json=json.load(fp)
            for temp_key in current_json.keys():
                conglomerate_dict[current_json_type+'_'+temp_key]=current_json[temp_key]

        with open(self.output_directory_address+'combined_ontologies.json', 'w') as fp:
            json.dump(conglomerate_dict, fp,indent=4)          

if __name__=="__main__":

    my_ConglomerateJSONMaker=ConglomerateJSONMaker(
        'results/individual_vocabulary_jsons/',
        'results/conglomerate_vocabulary_jsons/'
    )
    my_ConglomerateJSONMaker.generate_conglomerate_json()