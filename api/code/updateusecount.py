import pandas as pd
from flask_restful import Resource 
from flask import request
import sqlalchemy


engine=sqlalchemy.create_engine(f"sqlite:///../additional_files/sample_ingester_database.db")

class UpdateUseCountResource(Resource):

    def update_db(self):
        '''
        :meta private:
        '''

        update_usecount_string=f'''
        UPDATE vocab_table 
		set use_count=1
		where (header="{self.header}") and (main_string="{self.main_string}")
        '''

        print(update_usecount_string)
        print('')

        # print(fetch_vocab_string)
        # engine=sqlalchemy.create_engine(f"sqlite:///{self.database_address}")
        # print('got here')
        connection=engine.connect()


        connection.execute(
            update_usecount_string
        )
        # print('execution done')

        # temp_result=json.dumps([dict(r) for r in temp_cursor])

        # print('have temp_result')
        # print(temp_result)
        connection.close()

    # def read_files(self):
    #     self.conglomerate_vocabulary_panda=pd.read_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')

    def update_use_count(self):
        '''
        :meta private:
        '''
        #now, for each key in this dict, append to the corresponding panda in the conglomerate dict, then output it again
        self.conglomerate_vocabulary_panda['use_count']=self.conglomerate_vocabulary_panda['use_count'].where(
            (~self.conglomerate_vocabulary_panda.main_string.isin([self.main_string])),
            other=1
        )

    def write_file(self):
        '''
        :meta private:
        '''
        self.conglomerate_vocabulary_panda.to_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')


    def post(self):
        '''
        update the use_count column in the vocab table. change from 0 to 1 if used.

        Parameters
        ----------
        header : str
            which vocabulary to train
        main_string : str
            str of main_string to update. we update main_string to change all associated rows

        Returns
        -------
        str
            success status

        Examples
        --------
        {
            "header":"species",
            "main_string":"Bacteria"
        }
        '''

        self.header=request.json['header']
        self.main_string=request.json['main_string']

        self.update_db()
        # self.read_files()
        # self.update_use_count()
        # self.write_file()


        print(self.header+' '+self.main_string)
        return 'use_count update successful'