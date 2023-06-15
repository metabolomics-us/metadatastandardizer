import pandas as pd
from flask_restful import Resource 
from flask import request
import sqlalchemy
import json

engine=sqlalchemy.create_engine(f"sqlite:///../additional_files/sample_ingester_database.db")


class GenerateSubstringMatches(Resource):

    def read_files(self):
        ''':meta private:'''
        self.conglomerate_vocabulary_panda=pd.read_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')

    def coerce_db_into_conglomerate_panda(self):
        '''
        originally,we did not use a database, rather just a large panda.bin to hold the vocab info.
        we were motivated to switch to a .db in order ot make vocab additions very fast 
        everything was working if we started with the conglomerate panda
        so we just insert a step where we read the .db, coerce to conglomerate panda, then proceed as we already did
        without otuputting the small conglomerate files or unique vocab term files
        
        :meta private:
        '''

        fetch_vocab_string=f'''
        select *
        from vocab_table 
        where (header="{self.header}") and (valid_string like '%{self.substring}%') 
        '''

        # print(fetch_vocab_string)
        # engine=sqlalchemy.create_engine(f"sqlite:///{self.database_address}")
        # print('got here')
        connection=engine.connect()


        temp_cursor=connection.execute(
            fetch_vocab_string
        )
        # print('execution done')

        temp_result=json.dumps([dict(r) for r in temp_cursor])

        # print('have temp_result')
        # print(temp_result)
        connection.close()
        #https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql
        # engine.dispose()
        # print('closed connection')

        self.conglomerate_vocabulary_panda=pd.read_json(temp_result, orient="records")
        # print(self.conglomerate_vocabulary_panda)
        # self.vocabulary=self.conglomerate_vocabulary_panda['valid_string'].unique()
        # print(self.conglomerate_vocabulary_panda)


    def generate_substring_matches(self):
        '''
        :meta private:
        '''
        # print(self.conglomerate_vocabulary_panda.loc[
        #     self.conglomerate_vocabulary_panda['valid_string'].str.contains(self.substring.lower())
        # ])
        try:
            self.temp_values=self.conglomerate_vocabulary_panda.loc[
                self.conglomerate_vocabulary_panda['valid_string'].str.contains(self.substring.lower())
            ].drop_duplicates(subset=('main_string')).sort_values(['use_count','valid_string'],ascending=[False,True])[['valid_string','main_string']].agg(' AKA '.join, axis=1).tolist()
        except AttributeError:
            self.temp_values=[]
        

    def post(self):
        '''
        returns vocabulary terms for a header/substring pair

        Parameters
        ----------
        header : str
            which header
        substring : str
            portion of string to check
        
        Returns
        -------
        list
            a list of terms with matching strings

        Examples
        --------
        {
            "header":"species",
            "substring":"porcupi"
        }
        '''

        self.header=request.json['header']
        self.substring=request.json['substring']

        # self.read_files()
        self.coerce_db_into_conglomerate_panda()
        self.generate_substring_matches()

        # print(self.temp_values)

        return self.temp_values
