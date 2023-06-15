import networkx as nx
import obonet
import pickle


class NXParserCellLines:

    def __init__(self,input_obo_address,output_address):
        self.input_address=input_obo_address
        self.output_address=output_address


    def read(self):
        self.units_nx=obonet.read_obo(self.input_address)
        #from looking at the ontologies
        #we want to remove the prefixes and some strange nodes that have no properties but names looke like PATOsomething
        #remove prefixes


    def reduce_by_rules(self):
        '''
        could reduce by some subset of "subset" property or parse "comment" to do things like "eliminate 'Crustacean Cell Line'" or whatever
        '''
        pass

    def save(self):
        with open(self.output_address, 'wb') as f:
            pickle.dump(self.units_nx, f)



if __name__=="__main__":

    my_NXParserCellLines=NXParserCellLines(
        'resources/cellosaurus.obo',
        'results/individual_nxs/celllines_nx.bin'
    )

    my_NXParserCellLines.read()
    my_NXParserCellLines.reduce_by_rules()
    my_NXParserCellLines.save()