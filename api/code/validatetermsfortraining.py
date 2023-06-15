from flask_restful import Resource 
from flask import request


from newvocabularyuploadchecker import NewVocabularyUploadChecker

class ValidateTermsForTrainingResource(Resource):

    def validate_training_request(self):
        '''
        :meta private:
        '''
        self.NewVocabularyUploadChecker=NewVocabularyUploadChecker(self.new_vocabulary)
        self.NewVocabularyUploadChecker.check_char_length()
        self.NewVocabularyUploadChecker.verify_string_absence()

    def post(self):
        '''
        used in the frontend to validate input. things like number of characters, etc.

        Parameters
        ----------
        new_vocabulary : list
            strings that will get added to a vocabulary, at all
        
        Returns
        -------
        errors: list
            errors if any, otherwise length of zero

        Examples
        --------
        {
            "new_vocabulary":["Bacteria","Azorhizobium"]
        }
        '''

        
        self.new_vocabulary=request.json['new_vocabulary']

        if self.new_vocabulary==None:
            return {'errors':[]}


        self.validate_training_request()

        return {'errors':self.NewVocabularyUploadChecker.error_list}
