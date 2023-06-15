class NewVocabularyUploadChecker:
    '''
    for all of these, if they return true, there is a problem
    '''

    def __init__(self,vocabulary_list):
        ''':meta private:'''
        self.vocabulary_list=vocabulary_list
        self.error_list=list()
        
    def check_char_length(self):
        '''
        '''
        for new_vocab_term in self.vocabulary_list:
            if new_vocab_term is None:
                continue
            if len(new_vocab_term)<3:
                self.error_list.append(
                    f'{new_vocab_term} must contain at least 3 characters'
                )

    def verify_string_absence(self):
        '''
        '''
        forbidden_string_list=[
            ' AKA '
        ]
        for new_vocab_term in self.vocabulary_list:
            if new_vocab_term is None:
                continue
            for forbidden_string in forbidden_string_list:
                if forbidden_string in new_vocab_term:
                    self.error_list.append(
                        f'{new_vocab_term} cannot contain \"{forbidden_string}\"'
                    )
 