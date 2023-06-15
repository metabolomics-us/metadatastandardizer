from flask_restful import Resource 
import pandas as pd
from flask import request
import sqlalchemy
import time
import json

import os


class AuthorID(Resource):

    def post(self):
        '''
        a starting point for exploring the study table. returns all authorIDs.

        Parameters
        ----------
        None
        
        Returns
        -------
        author_id : list
            a list of study author IDs

        Examples
        --------
        {}
        '''

        self.database_relative_address='./../additional_files/sample_ingester_database.db'

        engine=sqlalchemy.create_engine(f"sqlite:///{self.database_relative_address}")



        connection=engine.connect()
        temp_cursor=connection.execute(
            '''
            select distinct author_id from study_table
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