import networkx as nx
import obonet
import pickle


class NXParserEFO:

    def __init__(self,input_obo_address,output_address):
        self.input_address=input_obo_address
        self.output_address=output_address


    def read(self):
        self.efo_nx=obonet.read_obo(self.input_address)

    def reduce_by_rules(self):
        '''
        from jupyter notebook, found list of properties that we didnt care about
        'alt_id',
        'comment',
        'consider',
        'created_by',
        'creation_date',
        'def',
        'disjoint_from',
        'equivalent_to',
        'intersection_of',
        'is_a',
        'name',
        'namespace',
        'property_value',
        'relationship',
        'subset',
        'synonym',
        'union_of',
        'xref'

        '''
        
        properties_to_delete=[
            'alt_id',
            'comment',
            'consider',
            'created_by',
            'creation_date',
            'def',
            'disjoint_from',
            'equivalent_to',
            'intersection_of',
            'is_a',

            'namespace',
            'property_value',
            'relationship',
            'subset',

            'union_of',
            'xref'
        ]

        for temp_node in self.efo_nx.nodes:
            for temp_prop in properties_to_delete:
                try:
                    del self.efo_nx.nodes[temp_node][temp_prop]
                except:
                    continue
            


    def save(self):
        with open(self.output_address, 'wb') as f:
            pickle.dump(self.efo_nx, f)


if __name__=="__main__":

    my_NXParserCellLines=NXParserEFO(
        'resources/efo.obo',
        'results/individual_nxs/efo_nx.bin'
    )

    my_NXParserCellLines.read()
    my_NXParserCellLines.reduce_by_rules()
    my_NXParserCellLines.save()