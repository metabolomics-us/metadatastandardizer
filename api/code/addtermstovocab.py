from flask_restful import Resource 
import pandas as pd
from flask import request
import sqlalchemy

from newvocabularyuploadchecker import NewVocabularyUploadChecker



engine=sqlalchemy.create_engine(f"sqlite:///../additional_files/sample_ingester_database.db")


class AddTermsToVocabularyResource(Resource):


    def post(self):
        '''
        takes a set of words and add them to a specific header's vocabulary

        Parameters
        ----------
        header : str
            which vocabulary the terms will be added to. 
        new_vocabulary : list
            list of strings where each string is a new term
        
        Returns
        -------
        errors : list
            a list of errors associated with terms. empty if success.

        Examples
        --------
        {
            "header":"species",
            "new_vocabulary":["new species 1","new species 2"]
        }
        '''
        self.header=request.json['header']
        self.written_strings=request.json['new_vocabulary']
        

        self.validate_vocabulary_request()

        if len(self.NewVocabularyUploadChecker.error_list)>0:
            return {'errors':self.NewVocabularyUploadChecker.error_list}

        # one of the major points of switching to db was to avoid these three steps
        # self.read_files()
        # self.append_to_conglomerate_panda()
        # self.write_files()
        self.append_new_vocab_to_table()
        
        print(f'added {self.written_strings} to {self.header}')

        return {'errors':self.NewVocabularyUploadChecker.error_list}


    def read_files(self):
        ''':meta private:'''
        self.conglomerate_vocabulary_panda=pd.read_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')

    def validate_vocabulary_request(self):
        ''':meta private:'''
        self.NewVocabularyUploadChecker=NewVocabularyUploadChecker(self.written_strings)
        self.NewVocabularyUploadChecker.check_char_length()
        self.NewVocabularyUploadChecker.verify_string_absence()


    def append_to_conglomerate_panda(self):
        ''':meta private:'''
    #now, for each key in this dict, append to the corresponding panda in the conglomerate dict, then output it again
        appending_dict={
            'valid_string':[],
            'node_id':[],
            'main_string':[],
            'ontology':[],
            'use_count':[]
        }
        for temp_addition in self.written_strings:
            appending_dict['valid_string'].append(temp_addition)
            appending_dict['node_id'].append(temp_addition)
            appending_dict['main_string'].append(temp_addition)
            appending_dict['ontology'].append('userAdded')
            appending_dict['use_count'].append(1)
        appending_panda=pd.DataFrame.from_dict(appending_dict)

        self.conglomerate_vocabulary_panda=pd.concat(
            [self.conglomerate_vocabulary_panda,appending_panda],
            axis='index',
            ignore_index=True,
        )
        #the pattern for new suggestions is that the given string becomes the valid_string, main_string, and node_id (something like that)
        #to make sure that a user doesnt put someonething that already exists
        self.conglomerate_vocabulary_panda.drop_duplicates(subset=('valid_string','main_string'),ignore_index=True,inplace=True)


    def write_files(self):
        ''':meta private:'''
        self.conglomerate_vocabulary_panda.to_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')

    def append_new_vocab_to_table(self):
        ''':meta private:'''

        appending_dict={
            'valid_string':[],
            'node_id':[],
            'main_string':[],
            'ontology':[],
            'use_count':[],
            'header':[]
        }
        for temp_addition in self.written_strings:
            appending_dict['valid_string'].append(temp_addition)
            appending_dict['node_id'].append(temp_addition)
            appending_dict['main_string'].append(temp_addition)
            appending_dict['ontology'].append('userAdded')
            appending_dict['use_count'].append(1)
            appending_dict['header'].append(self.header)
        appending_panda=pd.DataFrame.from_dict(appending_dict)

        # self.conglomerate_vocabulary_panda=pd.concat(
        #     [self.conglomerate_vocabulary_panda,appending_panda],
        #     axis='index',
        #     ignore_index=True,
        # )

        connection=engine.connect()

        # print(appending_panda)


        # for index,series in appending_panda.iterrows():

            # try:
        appending_panda.to_sql(
            'vocab_table',
            connection,
            if_exists='append',
            index=False
        )
            # except:
                # continue

        connection.close()