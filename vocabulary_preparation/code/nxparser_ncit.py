import networkx as nx
import obonet
import pickle

class NXParserNCIT:

    def __init__(self,input_obo_address,output_address):
        self.input_address=input_obo_address
        self.output_address=output_address

    def read(self):
        self.ncit_nx=obonet.read_obo(self.input_address)

        self.ncit_nx=self.ncit_nx.reverse()


    def reduce_by_rules(self):
        '''
        could reduce by some subset of "subset" property or parse "comment" to do things like "eliminate 'Crustacean Cell Line'" or whatever
        '''
        #we just took these from the efo exploration
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

            'subset',

        ]

        for temp_node in self.ncit_nx.nodes:
            for temp_prop in properties_to_delete:
                try:
                    del self.ncit_nx.nodes[temp_node][temp_prop]
                except:
                    continue

    def save(self):
        with open(self.output_address, 'wb') as f:
            pickle.dump(self.ncit_nx, f)
            

if __name__=="__main__":

    my_NXParserCellLines=NXParserNCIT(
        'resources/ncit.obo',
        'results/individual_nxs/ncit_nx.bin'
    )

    my_NXParserCellLines.read()
    my_NXParserCellLines.reduce_by_rules()
    my_NXParserCellLines.save()