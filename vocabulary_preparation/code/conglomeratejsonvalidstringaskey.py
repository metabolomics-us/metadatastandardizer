import json


class ConglomerateJSONMakerValidStringAsKey:

    def __init__(self,input_address,output_address):
        self.input_address=input_address
        self.output_address=output_address       

    def reshape_json(self):
        '''
        takes the conglomerate json and reshapes it into something with the form
        {
            valid_string:[
                {
                    'node_id':
                    'main_string'
                },
                {
                    'node_id':
                    'main_string'            
                }
            ],
            valid_string:[
                {
                    'node_id':
                    'main_string'
                },
            ],    
        }
        '''

        with open(self.input_address, 'r') as fp:
            conglomerate_json=json.load(fp)

        output_dict=dict()

        for temp_node_id in conglomerate_json.keys():
            for temp_string in conglomerate_json[temp_node_id]['valid_strings']:
                output_dict[temp_string]=list()
                
        for temp_node_id in conglomerate_json.keys():
            for temp_string in conglomerate_json[temp_node_id]['valid_strings']:
                output_dict[temp_string].append(
                    {
                        'node_id':temp_node_id,
                        'main_string':conglomerate_json[temp_node_id]['main_string']
                    }
                )  

        with open(self.output_address, 'w') as fp:
            json.dump(output_dict, fp,indent=4)         
        
if __name__=="__main__":

    my_ConglomerateJSONMakerValidStringAsKey=ConglomerateJSONMakerValidStringAsKey(
        'results/conglomerate_vocabulary_jsons/combined_ontologies.json',
        'results/conglomerate_vocabulary_jsons/combined_valid_string_as_key.json'
    )
    my_ConglomerateJSONMakerValidStringAsKey.reshape_json()