import pandas as pd
import json
import sqlalchemy

import os


class DatabaseCreator:


    def __init__(self,db_address,subset_json_address,no_vocab_header_address,conglomerate_pandas_directory):
        self.db_address=db_address
        self.subset_json_address=subset_json_address
        self.no_vocab_header_address=no_vocab_header_address
        self.conglomerate_pandas_directory=conglomerate_pandas_directory
        
    def make_header_list(self):
        with open(self.subset_json_address, 'r') as fp:
            subset_per_heading_json=json.load(fp)
        no_vocab_header_panda=pd.read_csv(self.no_vocab_header_address)
        self.metadata_categories=set(subset_per_heading_json.keys()).union(
            set(
                no_vocab_header_panda['headers_without_vocabs'].tolist()
            )
        )
        
    def create_connection(self):
        ## sqlite://<nohostname>/<path>
        engine=sqlalchemy.create_engine(f"sqlite:///{self.db_address}")
        print('got here')
        self.connection=engine.connect()
    
    def build_study_table_string(self):
        metadata_category_string=(' TEXT, '.join(self.metadata_categories))+' TEXT'
        #sqlite implicitly makes rowid primary key
        self.study_table_string='''
        CREATE TABLE study_table(
        author_id TEXT,
        study_id TEXT,
        sample_id TEXT, 
        metadata_parallel_id TEXT,
        '''+metadata_category_string+' )'
        
    def create_study_table(self):
        self.connection.execute(
            self.study_table_string
        )

    def create_index_study(self):


        query=f'''
        create index study_id
        on study_table (study_id)
        '''

        temp_cursor=self.connection.execute(
            query
        )


        query=f'''
        create index author_id
        on study_table (author_id)
        '''

        temp_cursor=self.connection.execute(
            query
        )


        return









    def build_vocab_table_string(self):
        # metadata_category_string=(' TEXT, '.join(self.metadata_categories))+' TEXT'
        self.vocab_table_string='''
        CREATE TABLE vocab_table(
        main_string TEXT,
        valid_string TEXT,
        node_id TEXT, 
        ontology TEXT,
        header TEXT,
        use_count INTEGER,
        UNIQUE (main_string,valid_string,header)
        )
        '''

    def create_vocab_table(self):
        self.connection.execute(
            self.vocab_table_string
        )

    def upload_conglomerate_to_db(self):
        for temp_file in os.listdir(self.conglomerate_pandas_directory):
            if 'conglomerate_vocabulary_panda' in temp_file:
                temp_conglomerate_panda=pd.read_pickle(self.conglomerate_pandas_directory+temp_file)
                temp_conglomerate_panda['header']=temp_file.split('_')[-1].split('.')[0]
        
        
                temp_conglomerate_panda.to_sql(
                    'vocab_table',
                    self.connection,
                    if_exists='append',
                    index=False
                )

    def create_index_vocab(self):

        '''
        '''


        query=f'''
        create index vocab_main_and_valid_string_and_header
        on vocab_table (main_string, valid_string, header)
        '''

        temp_cursor=self.connection.execute(
            query
        )

        query=f'''
        create index vocab_valid_string_header
        on vocab_table (valid_string, header)
        '''

        temp_cursor=self.connection.execute(
            query
        )

        query=f'''
        create index vocab_header
        on vocab_table (header)
        '''

        temp_cursor=self.connection.execute(
            query
        )


        return















        
if __name__=="__main__":
    my_DatabaseCreator=DatabaseCreator(
        'results/database/sample_ingester_database.db',
        'resources/parameter_files/subset_per_heading.json',
        'resources/parameter_files/headers_without_vocabs.tsv',  
        'results/models/'
        
    )
    my_DatabaseCreator.make_header_list()
    # print(my_DatabaseCreator.metadata_categories)
    # print(my_DatabaseCreator.build_study_table_string())
    my_DatabaseCreator.create_connection()
    my_DatabaseCreator.build_study_table_string()
    my_DatabaseCreator.create_study_table()
    my_DatabaseCreator.create_index_study()








    my_DatabaseCreator.build_vocab_table_string()
    my_DatabaseCreator.create_vocab_table()
    my_DatabaseCreator.upload_conglomerate_to_db()
    my_DatabaseCreator.create_index_vocab()
    # my_PandaFromConglomerate.create_constraint_vocab()