import json
import networkx as nx
from collections.abc import Iterable
import sys
import pickle
import re

class NodeIDDictParser:

    def __init__(self,file_path,attributes,main_attribute):
        # self.input_nx=nx.read_gpickle(file_path)
        with open(file_path,'rb') as temp_file:
            self.input_nx=pickle.load(temp_file)
        self.attributes_to_record=attributes
        self.main_attribute=main_attribute


    def reduce_ncbi_taxonomy(self):
        '''
        the logic for this came from exploring the ncbi taxonomy a little in 
        "propose_ncbi_removals.ipynb"
        the eventual conclusion was that the safest thing to do was to remove
        those subgraphs where the parent node contained the string "unclassified" or "environmental"
        as in "environmental samples"
        these seemed to contain the largest dumps, and reduced the total number of nodes from 2344973
        to 942320
        there are still many "overly specific" nodes, imo, but we dont have the manpower to deeply explore
        hundreds of thousands of nodes

        in our second perusal of the 942320 nodes that were leftover, we decided to also do the following
        remove all nodes with rank 'no rank' that contained at least one '/' as these were basically tens
        of thousands of flu virus strains

        remove all 'strain' rank - we will get a decent, realistic strain set from EFO (experimental factor ontology)

        remove all nodes with rank 'species' that contain a number 

        remove all nodes with rank 'species' that contain 'vector'
        '''


        #####first removal approach also removes their children
        unclassified_or_environmental_nodes=set()
        for temp_node in self.input_nx.nodes:
            if ('unclassified' in self.input_nx.nodes[temp_node]['scientific_name']) or ('environmental' in self.input_nx.nodes[temp_node]['scientific_name']):
                unclassified_or_environmental_nodes.add(temp_node)
            
        unclassified_or_environmental_nodes_and_children=set()
        unclassified_or_environmental_nodes_and_children.update(
            unclassified_or_environmental_nodes
        )
    
        for temp_node in unclassified_or_environmental_nodes:
            
            unclassified_or_environmental_nodes_and_children.update(
                nx.descendants(self.input_nx,temp_node)
            )

        self.input_nx.remove_nodes_from(
            unclassified_or_environmental_nodes_and_children
        )
        ##########################################################

        #second removal approach will simply remove nodes and connect children and parents#

        nodes_to_remove=set()
        for temp_node in self.input_nx.nodes:
            if (self.input_nx.nodes[temp_node]['rank']=='no rank' and ('/' in self.input_nx.nodes[temp_node]['scientific_name'])):
                nodes_to_remove.add(temp_node)
            elif (self.input_nx.nodes[temp_node]['rank']=='species' and ('vector' in self.input_nx.nodes[temp_node]['scientific_name'])):
                nodes_to_remove.add(temp_node)
            elif (self.input_nx.nodes[temp_node]['rank']=='strain'):
                nodes_to_remove.add(temp_node)
            elif (self.input_nx.nodes[temp_node]['rank']=='species' and any([temp_char.isdigit() for temp_char in self.input_nx.nodes[temp_node]['scientific_name']])):
                nodes_to_remove.add(temp_node)


        for temp_node in nodes_to_remove:
            temp_parents=list(self.input_nx.predecessors(temp_node))
            temp_children=list(self.input_nx.successors(temp_node))

            self.input_nx.remove_node(temp_node)

            for temp_parent in temp_parents:
                for temp_child in temp_children:
                    self.input_nx.add_edge(temp_parent,temp_child)




        ####################################################################################


    def parse_synonyms(self,temp_node):
        
        pattern = r'"(.*?)"'
        synonym_list=list()
        for temp_syn in self.input_nx.nodes[temp_node]['synonym']:
            try:
                synonym_list.append(re.findall(pattern, temp_syn)[0])
                
            except:
                continue
                
         
        return synonym_list


    def reduce_efo_taxonomy(self):
        '''
        '''
        for temp_node in self.input_nx.nodes:
            if 'synonym' in self.input_nx.nodes[temp_node].keys():
                self.input_nx.nodes[temp_node]['synonym']=self.parse_synonyms(temp_node)

    def reduce_ncit_taxonomy(self):
        '''
        '''
        '''
        when making the strain property, we observed that we wanted children of node "organism", but not those nodes that were in the ncbi taxonomy
        we also wanted to avoid nodes that were also children of the node gene
        '''


        #descendants of organism
        nodes_scan=nx.descendants(self.input_nx,'NCIT:C14250')
        #want to remove if it also in ncbi taxonomy or if it is a child of gene
        children_of_gene_node=set(nx.descendants(self.input_nx,'NCIT:C16612'))
        nodes_to_remove=set()



        for temp_node in nodes_scan:
            if temp_node in children_of_gene_node:
                nodes_to_remove.add(temp_node)
                continue
            
            for temp_prop in self.input_nx.nodes[temp_node]['property_value']:
                if 'NCIT:P331' in temp_prop:
                    nodes_to_remove.add(temp_node)
                    break

        for temp_node in nodes_to_remove:
            temp_parents=list(self.input_nx.predecessors(temp_node))
            temp_children=list(self.input_nx.successors(temp_node))

            self.input_nx.remove_node(temp_node)

            for temp_parent in temp_parents:
                for temp_child in temp_children:
                    self.input_nx.add_edge(temp_parent,temp_child)


        for temp_node in self.input_nx.nodes:
            if 'synonym' in self.input_nx.nodes[temp_node].keys():
                self.input_nx.nodes[temp_node]['synonym']=self.parse_synonyms(temp_node)



    def reduce_mesh_taxonomy(self):
        '''
        '''
        pass

    def reduce_unit_taxonomy(self):
        '''
        not so much a reduction as a cleaning
        the synonym attributes are very poorly arranged
        '''

        for temp_node in self.input_nx.nodes:
            if 'synonym' in self.input_nx.nodes[temp_node]:
                new_synonym_list=list()
                for temp_syn in self.input_nx.nodes[temp_node]['synonym']:
                    if '\"' in temp_syn:
                        new_synonym_list.append(
                            temp_syn.split('\"')[1]
                        )
                    else:
                        new_synonym_list.append(temp_syn)

                self.input_nx.nodes[temp_node]['synonym']=new_synonym_list

    def clean_and_reduce_cellline_taxonomy(self):
        '''
        noticed two things: one, redundant synonyms. some nodeID X might have synonym Y repeated n times
        two, noticed that the obo parser was not parsing synonyms correctly. "293/IL-1RI" RELATED []
        was being picked up directly, wehn we just want what i sin the quotes
        '''
        for temp_node in self.input_nx.nodes:
            if 'synonym' in self.input_nx.nodes[temp_node]:
                new_synonym_set=set()
                for temp_syn in self.input_nx.nodes[temp_node]['synonym']:
                    if 'RELATED' in temp_syn:
                        term_of_interest=temp_syn.split('\"')[1]
                        new_synonym_set.add(term_of_interest)
                    else:
                        new_synonym_set.add(temp_syn)
                self.input_nx.nodes[temp_node]['synonym']=list(new_synonym_set)


    def replace_node_id_with_ancestor_path(self):
        '''
        when we went to add vocabularies for geography, ethnicity, strain, etc
        we planned to use the defninitions in 'subset_headings_per_json', where basically
        the headnode of certain "subtrees" were used to define what is included.
        it was the case that often times it was simply enough to define the ontology,
        like in the ncbi taxonomy, to get what we wanted, which was everything. 
        however, in the case of the mesh, we coudl define subtrees conveniently because
        the node names were the paths from the root node.

        in order to take advantage of that for trees that do not have that property,
        we change the names of the node to have that property.

        the general procedure to od this is
        for each node, get all ancestors
        for each ancestor, get distance from this node
        for largest distance, get path explicitly
        set path to name of this node
        '''
        relabel_dict=dict()

        for temp_node in self.input_nx.nodes:

            temp_ancestors=nx.ancestors(self.input_nx,temp_node)

            temp_shortest_path_length=0
            furthest_ancestor=None

            for temp_ancestor in temp_ancestors:

                temp_length=nx.shortest_path_length(self.input_nx,temp_ancestor,temp_node)

                if temp_length>temp_shortest_path_length:
                    temp_shortest_path_length=temp_length
                    furthest_ancestor=temp_ancestor
            
            if furthest_ancestor is not None:
                furthest_ancestor_path=nx.shortest_path(self.input_nx,source=furthest_ancestor,target=temp_node)
                relabel_dict[temp_node]='|'.join(furthest_ancestor_path)
            

        nx.relabel_nodes(self.input_nx,mapping=relabel_dict,copy=False)


    def create_all_attribute_to_node_id_dict(self):
        '''
        we basically assume that there isnt some crazy nested situaion with respect ot the freature nodes
        the above commented code was an attempt to overengineer some foolpreoof solution for a case that didnt exist
        for each node in the tree
        
        the output is in the form of 
        {
            'node id':[strings that map to node id]
        }
        '''

        self.node_id_to_strings_dict=dict()
        for temp_node in self.input_nx.nodes:
            
            if self.main_attribute not in self.input_nx.nodes[temp_node].keys():
                continue

            self.node_id_to_strings_dict[temp_node]=dict()

            self.node_id_to_strings_dict[temp_node]['valid_strings']=set()

            for temp_attribute in self.attributes_to_record:
                
                #if there is no attribute for this node id
                if temp_attribute not in self.input_nx.nodes[temp_node].keys():
                    continue
                
                if isinstance(self.input_nx.nodes[temp_node][temp_attribute],list)==True:
                    for element in self.input_nx.nodes[temp_node][temp_attribute]:
                        if isinstance(element,list)==True:
                            #print('found a nested list')
                            raise Exception('found a nested list')
                        self.node_id_to_strings_dict[temp_node]['valid_strings'].add(element)
                else:
                    self.node_id_to_strings_dict[temp_node]['valid_strings'].add(
                        self.input_nx.nodes[temp_node][temp_attribute]
                    )

            #set not json serializable
            self.node_id_to_strings_dict[temp_node]['valid_strings']=list(self.node_id_to_strings_dict[temp_node]['valid_strings'])
            self.node_id_to_strings_dict[temp_node]['main_string']=self.input_nx.nodes[temp_node][self.main_attribute]

                

if __name__ == "__main__":

    ontology=sys.argv[1]
    drop_nodes=sys.argv[2]
    
    if ontology=='ncbi':
        my_NodeIDDictParser=NodeIDDictParser(
            'results/individual_nxs/ncbi_nx.bin',
            {'common_name','genbank_common_name','scientific_name'},
            'scientific_name'
        )
        if drop_nodes=='True':
            my_NodeIDDictParser.reduce_ncbi_taxonomy()
        my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
        with open('results/individual_vocabulary_jsons/ncbi.json', 'w') as fp:
            json.dump(my_NodeIDDictParser.node_id_to_strings_dict, fp,indent=4)        

    elif ontology=='mesh':
        my_NodeIDDictParser=NodeIDDictParser(
            'results/individual_nxs/mesh_nx.bin',
            {'mesh_label','common_name'},
            'mesh_label'
        )
        # if drop_nodes==True:
        #     my_NodeIDDictParser.reduce_ncbi_taxonomy()
        my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
        with open('results/individual_vocabulary_jsons/mesh.json', 'w') as fp:
            json.dump(my_NodeIDDictParser.node_id_to_strings_dict, fp,indent=4)       

    elif ontology=='unit':
        my_NodeIDDictParser=NodeIDDictParser(
            'results/individual_nxs/unit_nx.bin',
            {'name','synonym'},
            'name'
        )


        if drop_nodes=='True':
            my_NodeIDDictParser.reduce_unit_taxonomy()
        my_NodeIDDictParser.replace_node_id_with_ancestor_path()
        my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
        with open('results/individual_vocabulary_jsons/unit.json', 'w') as fp:
            json.dump(my_NodeIDDictParser.node_id_to_strings_dict, fp,indent=4)    

    elif ontology=='celllines':
        my_NodeIDDictParser=NodeIDDictParser(
            'results/individual_nxs/celllines_nx.bin',
            {'name','synonym'},
            'name'
        )

        if drop_nodes=='True':
            my_NodeIDDictParser.clean_and_reduce_cellline_taxonomy()
        my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
        with open('results/individual_vocabulary_jsons/celllines.json', 'w') as fp:
            json.dump(my_NodeIDDictParser.node_id_to_strings_dict, fp,indent=4)    

    elif ontology=='ncit':
        my_NodeIDDictParser=NodeIDDictParser(
            'results/individual_nxs/ncit_nx.bin',
            {'name','synonym'},
            'name'
        )

        if drop_nodes=='True':
            my_NodeIDDictParser.reduce_ncit_taxonomy()
        my_NodeIDDictParser.replace_node_id_with_ancestor_path()
        my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
        with open('results/individual_vocabulary_jsons/ncit.json', 'w') as fp:
            json.dump(my_NodeIDDictParser.node_id_to_strings_dict, fp,indent=4)   


    elif ontology=='efo':
        my_NodeIDDictParser=NodeIDDictParser(
            'results/individual_nxs/efo_nx.bin',
            {'name','synonym'},
            'name'
        )

        if drop_nodes=='True':
            my_NodeIDDictParser.reduce_efo_taxonomy()
        my_NodeIDDictParser.replace_node_id_with_ancestor_path()
        my_NodeIDDictParser.create_all_attribute_to_node_id_dict()
        with open('results/individual_vocabulary_jsons/efo.json', 'w') as fp:
            json.dump(my_NodeIDDictParser.node_id_to_strings_dict, fp,indent=4)   