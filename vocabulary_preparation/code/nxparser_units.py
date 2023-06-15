import networkx as nx
import obonet
import pickle

class NXParserUnits:

    def __init__(self,input_obo_address,output_address):
        self.input_address=input_obo_address
        self.output_address=output_address


    def read_and_save(self):
        self.units_nx=obonet.read_obo(self.input_address)
        self.units_nx=self.units_nx.reverse()
        #from looking at the ontologies
        #we want to remove the prefixes and some strange nodes that have no properties but names looke like PATOsomething
        #remove prefixes

        nodes_to_remove=set()
        for temp_node in self.units_nx.nodes:
            if 'subset' in self.units_nx.nodes[temp_node]:
                if 'prefix_slim' in self.units_nx.nodes[temp_node]['subset']:    
                    nodes_to_remove.add(temp_node)
        for element in nodes_to_remove:
            self.units_nx.remove_node(element)

        nodes_to_remove=set()
        for temp_node in self.units_nx.nodes:
            if 'PATO' in temp_node:
                #if 'prefix_slim' in self.units_nx.nodes[temp_node]['subset']:    
                nodes_to_remove.add(temp_node)
        for element in nodes_to_remove:
            self.units_nx.remove_node(element)  

        with open(self.output_address, 'wb') as f:
            pickle.dump(self.units_nx, f)




if __name__=="__main__":

    my_NXParserUnits=NXParserUnits(
        'resources/unit.obo',
        'results/individual_nxs/unit_nx.bin'
    )

    my_NXParserUnits.read_and_save()