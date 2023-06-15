from flask_restful import Resource 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.exceptions import NotFittedError
import json
import pickle
import pandas as pd
from flask import request
from pprint import pprint
import sqlalchemy

engine=sqlalchemy.create_engine(f"sqlite:///../additional_files/sample_ingester_database.db")


class PredictVocabularyTermsResource(Resource):

    def coerce_db_into_conglomerate_panda(self):
        '''
        :meta private:
        '''

        fetch_vocab_string=f'''
        select rowid,* 
        from vocab_table 
        where header=\"{self.header}\"
        order by rowid
        '''

        # engine=sqlalchemy.create_engine(f"sqlite:///{self.database_address}")
        # print('got here')
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
        self.vocabulary=self.conglomerate_vocabulary_panda['valid_string'].unique()


    def read_files(self):
        '''
        :meta private:
        '''
        with open(f'../additional_files/NearestNeighbors_{self.header}.bin','rb') as f:
            self.nearest_neighbors=pickle.load(f)
        with open(f'../additional_files/tfidfVectorizer_{self.header}.bin','rb') as f:
            self.tfidf_vectorizer=pickle.load(f)
        
        
        # self.conglomerate_vocabulary_panda=pd.read_pickle(f'../additional_files/conglomerate_vocabulary_panda_{self.header}.bin')
        # self.vocabulary=pd.read_pickle(f'../additional_files/unique_valid_strings_{self.header}.bin')[0].values
        #we can get the fully vocab on the fly because if the nearest neighbors model is trained up to the nth term
        #then we can only map back up to the nth term
        #the n+ith new term will not be possible to reach
        #so, we can, on the fly, make a conglomerate vocabulary panda from the DB
        #and then make the unique directly from the conglomerate


        temp_translator=pd.read_csv(f'../assets/prediction_short_string_translations.tsv',sep='\t',na_filter=False)
        self.short_string_translator=dict(zip(temp_translator.short.tolist(),temp_translator.long.tolist()))



    def get_neighbors(self):
        '''
        :meta private:
        '''
        for written_string in self.written_strings:
            try:
                vectorized_string=self.tfidf_vectorizer.transform([str(written_string)])
            except NotFittedError:
                # print('not fitted')
                neighbors_df=pd.DataFrame.from_dict(
                    {
                        'guessed_valid_strings':[None],
                        'guessed_valid_string_distances':[None]
                    }
                )

                self.neighbors_panda_list.append(neighbors_df)
                continue

            #if there are fewer neighbors to retrieve than we want, set the neighbors to the max available
            if (self.nearest_neighbors.n_samples_fit_) < self.neighbors_to_retrieve:
                self.neighbors_to_retrieve=self.nearest_neighbors.n_samples_fit_

            #kn_ind is an array of indices of the nieghbors in the training matrix
            similarities,kn_ind=self.nearest_neighbors.kneighbors(
                vectorized_string,
                self.neighbors_to_retrieve
            )

            neighbors_df=pd.DataFrame.from_dict(
                {
                    'written_string':[written_string for similarity in similarities[0]],
                    'guessed_valid_strings':self.vocabulary[kn_ind[0]],
                    'guessed_valid_string_distances':similarities[0],
                    
                }
            )     
            # print(neighbors_df)  
            self.neighbors_panda_list.append(neighbors_df)

    def append_use_count_property(self):
        '''
        :meta private:
        '''
        #originally we had a for loop, but the problem with that was taht was that we were getting a result for each 
        #valid string that the written string mapped to. this meant that we coudl get the same main strin multiple times.
        for i in range(len(self.neighbors_panda_list)):
            self.neighbors_panda_list[i]=self.neighbors_panda_list[i].merge(
                self.conglomerate_vocabulary_panda,
                how='left',
                left_on='guessed_valid_strings',
                right_on='valid_string'
            ).drop_duplicates(subset=('main_string')).sort_values(by=['use_count','guessed_valid_string_distances'],ascending=[False,True])

            self.neighbors_panda_list[i].drop(
                ['guessed_valid_strings','node_id','ontology'],
                axis='columns',
                inplace=True
            )

    def post(self):
        '''
        takes a set of words and add them to a specific header's vocabulary

        Parameters
        ----------
        header : str
            which vocabulary
        writting_strings : list
            list of strings for which to provide nearest neighbors (NN prediction done on each)
        neighbors_to_retrieve: int
            how many neighbors to provide

        Returns
        -------
        list
            a list of records lists, where each record is the vocab term matched to, distance, etc

        Examples
        --------
        {
            "header":"species",
            "written_strings":["musk muskulus","homo"],
            "neighbors_to_retrieve":100
        }
        '''

        self.header=request.json['header']
        self.written_strings=request.json['written_strings']
        self.neighbors_to_retrieve=request.json['neighbors_to_retrieve']

        self.read_files()

        self.coerce_db_into_conglomerate_panda()


        #swap things like 'wt' that are too shrot for trigrams out with longer terms
        for i in range(len(self.written_strings)):
            if self.written_strings[i] in self.short_string_translator.keys():
                self.written_strings[i]=self.short_string_translator[self.written_strings[i]]


        self.neighbors_panda_list=list()
        self.get_neighbors()
        self.append_use_count_property()
        
        self.output_panda=pd.concat(
            self.neighbors_panda_list,
            axis='index',
            ignore_index=True
        )

        # print(self.output_panda)

        return json.dumps(self.output_panda.to_dict('records'))