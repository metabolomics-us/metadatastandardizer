import pandas as pd
from flask_restful import Resource 
from flask import request
import sqlalchemy
import json


engine=sqlalchemy.create_engine(f"sqlite:///../additional_files/sample_ingester_database.db")

class RetrieveVocabRowsResource(Resource):

    def select_rows(self):
        '''
        :meta private:
        '''

        select_vocab_string=f'''
        SELECT *
        from vocab_table
		where (header="{self.header}") and (valid_string="{self.valid_string}")
        '''


        # print(fetch_vocab_string)
        # engine=sqlalchemy.create_engine(f"sqlite:///{self.database_address}")
        # print('got here')
        connection=engine.connect()
        temp_cursor=connection.execute(
            select_vocab_string
        )

        temp_result=json.dumps([dict(r) for r in temp_cursor])

        # print(temp_result)
        connection.close()
        #https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql
        # engine.dispose()

        self.returned_rows=pd.read_json(temp_result, orient="records")



    def post(self):
        '''
        takes a valid string and a header and allows you to see the complete row

        Parameters
        ----------
        header : str
            which vocabulary
        valid_strings : list
            a string that exists as a representation of a main_string

        Returns
        -------
        list
            the complete row for that string in that vocabulary

        Examples
        --------
        {
            "header":"organ",
            "valid_string":"kidney"
        }
        '''

        self.header=request.json['header']
        self.valid_string=request.json['valid_string']

        self.select_rows()
        # self.read_files()
        # self.update_use_count()
        # self.write_file()


        return json.dumps(self.returned_rows.to_dict('records'))