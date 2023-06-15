from pprint import pprint
from flask import Flask,request
from flask_restful import Api, Resource, reqparse
import json


from predictvocabularyterms import PredictVocabularyTermsResource
from updateusecount import UpdateUseCountResource
from validatetermsfortraining import ValidateTermsForTrainingResource
from generatesubstringmatches import GenerateSubstringMatches
from addtermstovocab import AddTermsToVocabularyResource
from trainvocabulary import TrainVocabularyResource

from addstudytodatabase import AddStudyToDatabase

from authorID import AuthorID
from studyID import StudyID
from samples import Samples

from retrievevocabrows import RetrieveVocabRowsResource

app=Flask(__name__)
api=Api(app)


api.add_resource(PredictVocabularyTermsResource,'/predictvocabularytermsresource/')
api.add_resource(UpdateUseCountResource,'/updateusecountresource/')
api.add_resource(ValidateTermsForTrainingResource,'/validatetermsfortrainingresource/')
api.add_resource(GenerateSubstringMatches,'/generatesubstringmatchesresource/')
api.add_resource(AddTermsToVocabularyResource,'/addtermstovocabularyresource/')
api.add_resource(TrainVocabularyResource,'/trainvocabularyresource/')
api.add_resource(RetrieveVocabRowsResource,'/retrievevocabrowsresource/')


api.add_resource(AddStudyToDatabase,'/addstudytodatabase/')
api.add_resource(AuthorID,'/authorid/')
api.add_resource(StudyID,'/studyid/')
api.add_resource(Samples,'/samples/')





if __name__ == '__main__':
    app.run(debug=True,port=4999,host='0.0.0.0')
