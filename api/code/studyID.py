from flask_restful import Resource 
import pandas as pd
from flask import request
import sqlalchemy
import time
import json

import os


class StudyID(Resource):

    def post(self):
        '''
        returns all studyIDs for a given author

        Parameters
        ----------
        author_id : str
            the author ID in question

        Returns
        -------
        errors:list
            list of relevant studyIDs

        Examples
        --------
        {
            "author_id":"parkerbremer"
        }
        '''
        self.provided_author_id=request.json['author_id']
        print(self.provided_author_id)

        self.database_relative_address='./../additional_files/sample_ingester_database.db'

        engine=sqlalchemy.create_engine(f"sqlite:///{self.database_relative_address}")



        connection=engine.connect()
        temp_cursor=connection.execute(
            f'''
            select distinct study_id from study_table where author_id="{self.provided_author_id}"
            '''
        )

        output=json.dumps([dict(r) for r in temp_cursor])
        


        if (len(output) <= 0):
            connection.close()
            #https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql
            engine.dispose()
            print('row count of final result cursor less than 1')
            return 'fail'
        else:
            
            connection.close()
            #https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql
            engine.dispose()
            #print(temp_result)
            return output