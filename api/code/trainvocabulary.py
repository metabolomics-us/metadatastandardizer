from flask_restful import Resource #Api, Resource, reqparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.exceptions import NotFittedError
import json
import pickle
import pandas as pd
from flask import request
import sqlalchemy

engine=sqlalchemy.create_engine(f"sqlite:///../additional_files/sample_ingester_database.db")



class TrainVocabularyResource(Resource):


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
        select rowid,* 
        from vocab_table 
        where header=\"{self.header}\"
        order by rowid
        '''

        # engine=sqlalchemy.create_engine(f"sqlite:///{self.database_address}")
        print('got here')
        connection=engine.connect()


        temp_cursor=connection.execute(
            fetch_vocab_string
        )

        temp_result=json.dumps([dict(r) for r in temp_cursor])

        # print(temp_result)
        connection.close()
        #https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql
        # engine.dispose()

        self.conglomerate_vocabulary_panda=pd.read_json(temp_result, orient="records")
        # print(self.conglomerate_vocabulary_panda)
        # self.vocabulary=self.conglomerate_vocabulary_panda['valid_string'].unique()



    def post(self):
        '''
        trains the TF-IDF vectorizer and nearest neighbors model for current vocab

        Parameters
        ----------
        header : str
            which vocabulary to train

        Returns
        -------
        errors:list
            True/False on error list

        Examples
        --------
        {
            "header":"organ"
        }
        '''
        self.header=request.json['header']
        self.read_files()
        self.coerce_db_into_conglomerate_panda()

        self.train_models()
        self.write_models()
        
        # print('')
        # print('trained a model')
        # print('')

        return {'errors':False}



    def read_files(self):
        '''
        :meta private:
        '''
        # self.conglomerate_vocabulary_panda=pd.read_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')

        with open('../additional_files/ngram_limits_per_heading.json', 'r') as fp:
            self.ngram_limits_per_heading_json=json.load(fp)


    def train_models(self):
        '''
        blah

        :meta private:
        '''
        #for temp_key in new_vocab_dict.keys():
        self.model_vocabulary=self.conglomerate_vocabulary_panda['valid_string'].unique()
        self.TfidfVectorizer=TfidfVectorizer(
            analyzer='char',
            ngram_range=self.ngram_limits_per_heading_json[self.header],
            use_idf=False,
            norm=None
        )
        self.tfidf_matrix=self.TfidfVectorizer.fit_transform(self.model_vocabulary)

        self.NN_model=NearestNeighbors(
            n_neighbors=50,
            n_jobs=5,
            metric='cosine'
        )
        self.NN_model.fit(self.tfidf_matrix)


    def write_models(self):
        '''
        :meta private:
        '''

        with open(f'../additional_files/tfidfVectorizer_{self.header}.bin','wb') as fp:
            pickle.dump(self.TfidfVectorizer,fp)

        with open(f'../additional_files/NearestNeighbors_{self.header}.bin','wb') as fp:
            pickle.dump(self.NN_model,fp)

        output_vocab_panda=pd.DataFrame.from_dict(
            self.model_vocabulary
        )

        # output_vocab_panda.to_pickle(f'../additional_files/unique_valid_strings_{self.header}.bin')