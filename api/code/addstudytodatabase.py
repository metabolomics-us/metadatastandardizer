from flask_restful import Resource 
import pandas as pd
from flask import request
import sqlalchemy
import time

import os


class AddStudyToDatabase(Resource):

    def make_author_id(self):
        '''
        :meta private:
        '''

        self.author_id=''.join(
            [temp_char.lower() for temp_char in self.provided_author_name if(temp_char.isalpha()==True)]
        )

    def make_list_of_dataframes_for_upload(self):
        '''
        :meta private:
        '''

        self.study_id=time.time()

        highest_parallel_degree=0
        for temp_col in self.sample_metadata_curated_panda.columns:
            if int(temp_col.split('.')[1])>highest_parallel_degree:
                highest_parallel_degree=int(temp_col.split('.')[1])
        print('highest parallel')
        print(highest_parallel_degree)
        print('')


        self.pandas_for_db=list()
        for temp_degree in range(highest_parallel_degree+1):
            temp_column_list=[temp_col for temp_col in self.sample_metadata_curated_panda if int(temp_col.split('.')[1])==temp_degree]
            self.pandas_for_db.append(
                self.sample_metadata_curated_panda[temp_column_list].copy()
            )
            print(self.pandas_for_db[temp_degree])
            
            #always use the same function....
            temp_column_rename_function=lambda x: x.split('.')[0]
            #conveniently, degrees are the same as the indices in the panda_upload list
            self.pandas_for_db[temp_degree].rename(
                mapper=temp_column_rename_function,
                axis='columns',
                inplace=True
            )

        for i,temp_df in enumerate(self.pandas_for_db):
            temp_df['author_id']=self.author_id
            temp_df['study_id']=self.study_id
            temp_df['sample_id']=temp_df.index
            temp_df['metadata_parallel_id']=[i for element in temp_df.index]

       


    def upload_to_database(self):
        '''
        :meta private:
        '''
        
        engine=sqlalchemy.create_engine(f"sqlite:///{self.database_relative_address}")
        print(engine)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++==')

        for temp_df in self.pandas_for_db:
            print(temp_df)

            temp_df.to_sql(
                'study_table',
                con=engine,
                if_exists='append',
                index=False
            )
        


    def post(self):
        '''
        takes a post-curation study and adds it to database for downstream retrieval
        
        Parameters
        ----------
        provided_author_name : str
            provided author name. will be coerced to authorID
        sample_metadata_sheet_panda : json
            records representation of study metadata
        
        Returns
        -------
        author_id : str
            provided_author_name without spaces and lowercased
        study_id : float
            millisecond time of submission using time.time()

        Examples
        --------
        {
            "provided_author_name": "Parker Bremer",
            "sample_metadata_sheet_panda":[{"species.0": "Homo sapiens", "organ.0": "Kidney", "cellLine.0": "not available", "cellCount.0": "not available", "mass.0": "5.0", "massUnit.0": "milligram", "drugName.0": "control", "drugDoseMagnitude.0": "not available", "drugDoseUnit.0": "not available"}, {"species.0": "Homo sapiens", "organ.0": "Kidney", "cellLine.0": "not available", "cellCount.0": "not available", "mass.0": "5.0", "massUnit.0": "milligram", "drugName.0": "control", "drugDoseMagnitude.0": "not available", "drugDoseUnit.0": "not available"}, {"species.0": "Homo sapiens", "organ.0": "Kidney", "cellLine.0": "not available", "cellCount.0": "not available", "mass.0": "5.0", "massUnit.0": "milligram", "drugName.0": "control", "drugDoseMagnitude.0": "not available", "drugDoseUnit.0": "not available"}, {"species.0": "Homo sapiens", "organ.0": "Kidney", "cellLine.0": "not available", "cellCount.0": "not available", "mass.0": "5.0", "massUnit.0": "milligram", "drugName.0": "KERENDIA", "drugDoseMagnitude.0": "20.0", "drugDoseUnit.0": "milligram"}, {"species.0": "Homo sapiens", "organ.0": "Kidney", "cellLine.0": "not available", "cellCount.0": "not available", "mass.0": "5.0", "massUnit.0": "milligram", "drugName.0": "KERENDIA", "drugDoseMagnitude.0": "20.0", "drugDoseUnit.0": "milligram"}, {"species.0": "Homo sapiens", "organ.0": "Kidney", "cellLine.0": "not available", "cellCount.0": "not available", "mass.0": "5.0", "massUnit.0": "milligram", "drugName.0": "KERENDIA", "drugDoseMagnitude.0": "20.0", "drugDoseUnit.0": "milligram"}, {"species.0": "Homo sapiens", "organ.0": "not available", "cellLine.0": "HEK293", "cellCount.0": "1000000.0", "mass.0": "not available", "massUnit.0": "not available", "drugName.0": "control", "drugDoseMagnitude.0": "not available", "drugDoseUnit.0": "not available"}, {"species.0": "Homo sapiens", "organ.0": "not available", "cellLine.0": "HEK293", "cellCount.0": "1000000.0", "mass.0": "not available", "massUnit.0": "not available", "drugName.0": "control", "drugDoseMagnitude.0": "not available", "drugDoseUnit.0": "not available"}, {"species.0": "Homo sapiens", "organ.0": "not available", "cellLine.0": "HEK293", "cellCount.0": "1000000.0", "mass.0": "not available", "massUnit.0": "not available", "drugName.0": "control", "drugDoseMagnitude.0": "not available", "drugDoseUnit.0": "not available"}, {"species.0": "Homo sapiens", "organ.0": "not available", "cellLine.0": "HEK293", "cellCount.0": "1000000.0", "mass.0": "not available", "massUnit.0": "not available", "drugName.0": "KERENDIA", "drugDoseMagnitude.0": "20.0", "drugDoseUnit.0": "milligram"}, {"species.0": "Homo sapiens", "organ.0": "not available", "cellLine.0": "HEK293", "cellCount.0": "1000000.0", "mass.0": "not available", "massUnit.0": "not available", "drugName.0": "KERENDIA", "drugDoseMagnitude.0": "20.0", "drugDoseUnit.0": "milligram"}, {"species.0": "Homo sapiens", "organ.0": "not available", "cellLine.0": "HEK293", "cellCount.0": "1000000.0", "mass.0": "not available", "massUnit.0": "not available", "drugName.0": "KERENDIA", "drugDoseMagnitude.0": "20.0", "drugDoseUnit.0": "milligram"}]
        }
        '''

        self.database_relative_address='./../additional_files/sample_ingester_database.db'

        print(os.listdir('./../additional_files/'))
        print('8'*100)

        self.provided_author_name=request.json['provided_author_name']
        self.sample_metadata_curated_panda=pd.DataFrame.from_records(request.json['sample_metadata_sheet_panda'])

        print(self.provided_author_name)
        self.make_author_id()

        print(self.sample_metadata_curated_panda)

        self.make_list_of_dataframes_for_upload()


        self.upload_to_database()

        return {
            'author_id':self.author_id,
            'study_id':self.study_id
        }
