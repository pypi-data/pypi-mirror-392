# This code is an algorithm projected, architected and developed by Sapiens Technology®️ and aims to save indexed conversations from language models
# for later consultation through semantic comparison using the prompts as a key to return the respective responses.
# This avoids unnecessary processing when an instruction has already been made previously by the same user,
# thus returning the already existing response to the same instruction without the need to process it again in the model.
# The algorithm also has the ability to adapt responses when instructions are similar but not completely the same, readjusting terms and words in general.
class SemanticComparison:
    def __init__(self, display_error_point=True):
        try:
            self.__display_error_point = bool(display_error_point) if type(display_error_point) in (bool, int, float) else True
            from traceback import print_exc
            from os import path, mkdir
            from shutil import rmtree
            from base64 import b64encode, b64decode
            from unicodedata import normalize, combining
            from re import sub, escape, IGNORECASE
            from difflib import SequenceMatcher
            self.__print_exc = print_exc
            self.__path, self.__mkdir = path, mkdir
            self.__rmtree = rmtree
            self.__b64encode, self.__b64decode = b64encode, b64decode
            self.__normalize, self.__combining = normalize, combining
            self.__sub, self.__escape, self.__IGNORECASE = sub, escape, IGNORECASE
            self.__SequenceMatcher = SequenceMatcher
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.__init__: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
    def __getRootDirectory(self):
        try: return str(self.__path.dirname(self.__path.realpath(__file__)).replace('\\', '/')+'/').strip()
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.__getRootDirectory: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return './'
    def __autoRegressiveModel(self, training_prompt='', user_prompt='', answer=''):
        try:
            answer_transformed = answer
            def cleanText(text): return self.__sub(r'[^\w\s\+\-*/]', '', text)
            training_prompt_clean, user_prompt_clean = cleanText(training_prompt), cleanText(user_prompt)
            training_tokens, user_tokens = training_prompt_clean.split(), user_prompt_clean.split()
            matcher, substitutions = self.__SequenceMatcher(None, training_tokens, user_tokens), {}
            for tag, x1, x2, y1, y2 in matcher.get_opcodes():
                if tag != 'equal':
                    training_segment, user_segment = ' '.join(training_tokens[x1:x2]), ' '.join(user_tokens[y1:y2])
                    substitutions[training_segment] = user_segment
            for t_segment, u_segment in substitutions.items(): answer_transformed = self.__sub(r'\b'+self.__escape(t_segment)+r'\b', u_segment, answer_transformed, flags=self.__IGNORECASE)
            return answer_transformed
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.__autoRegressiveModel: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return answer
    def __semanticComparison(self, trainings=[], prompt='', precision=0.8, tokens_tolerance=0.5, length_tolerance=0.5):
        try:
            answer, found = '', False
            trainings = list(trainings) if type(trainings) in (tuple, list) else []
            if len(trainings) < 1: return ''
            def normalization(text): return self.__sub(r'[^A-Za-z0-9\s]', '', ''.join([char for char in self.__normalize('NFKD', str(text).lower()) if not self.__combining(char)]))
            tokens = normalization(text=prompt).split()
            for training in trainings:
                _prompt = str(training['prompt']).strip() if 'prompt' in training else ''
                _answer = str(training['answer']).strip() if 'answer' in training else ''
                if prompt == _prompt: answer, found = _answer, True
                elif prompt.lower() == _prompt.lower(): answer, found = _answer, True
                elif prompt.lower() in _prompt.lower(): answer, found = _answer, True
                elif _prompt.lower() in prompt.lower(): answer, found = _answer, True
                elif normalization(text=prompt) == normalization(text=_prompt): answer, found = _answer, True
                if found: break
                hits, total = 0, max((1, len(tokens)))
                for token in tokens:
                    if token in normalization(text=_prompt): hits += 1
                probability = hits/total
                if probability >= precision:
                    answer = self.__autoRegressiveModel(training_prompt=_prompt, user_prompt=prompt, answer=_answer) if probability < .9 else _answer
                    answer_tokens, _answer_tokens = answer.split(), _answer.split()
                    tokens_percentage = sum(1 for element in answer_tokens if element in _answer_tokens)/max((len(answer_tokens), len(_answer_tokens)))
                    answer_length, _answer_length = len(answer), len(_answer)
                    answer_percentage = 1-(abs(answer_length-_answer_length)/max((answer_length, _answer_length)))
                    if tokens_percentage < tokens_tolerance or answer_percentage < length_tolerance: answer = _answer
                    break
            return answer
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.__semanticComparison: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def train(self, training_id=0, prompt='', answer='', username=''):
        try:
            training_id, prompt, answer, username = str(training_id).strip(), str(prompt).strip(), str(answer).strip(), str(username).strip()
            root_directory, prompt_size, username_size = self.__getRootDirectory(), len(prompt.split()), len(username)
            training_directory = root_directory+training_id+'/'
            if not self.__path.exists(training_directory): self.__mkdir(training_directory)
            size_file = training_directory+str(prompt_size)+'.index'
            if username_size > 0 and username in prompt: prompt = prompt.replace(username, '<|username|>')
            if username_size > 0 and username in answer: answer = answer.replace(username, '<|username|>')
            prompt = self.__b64encode(prompt.encode('utf-8')).decode('utf-8')
            answer = self.__b64encode(answer.encode('utf-8')).decode('utf-8')
            context = prompt+'<|context|>'+answer
            if self.__path.exists(size_file):
                with open(size_file, 'r', encoding='utf-8') as file: context = file.read().strip()+'<|end|>'+context
            with open(size_file, 'w', encoding='utf-8') as file: file.write(context)
            return True
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.train: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return False
    def deleteTraining(self, training_id=0):
        try:
            training_id = str(training_id).strip()
            root_directory = self.__getRootDirectory()
            training_directory = root_directory+training_id+'/'
            if self.__path.exists(training_directory): self.__rmtree(training_directory)
            return not self.__path.exists(training_directory)
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.deleteTraining: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return False
    def predict(self, training_id=0, prompt='', username='', range_size=3, precision=0.8, tokens_tolerance=0.5, length_tolerance=0.5):
        try:
            answer = ''
            training_id, prompt, username = str(training_id).strip(), str(prompt).strip(), str(username).strip()
            range_size = max((0, int(range_size))) if type(range_size) in (bool, int, float) else 3
            precision = min((max((0, float(precision))), 1)) if type(precision) in (bool, int, float) else .8
            tokens_tolerance = min((max((0, float(tokens_tolerance))), 1)) if type(tokens_tolerance) in (bool, int, float) else .5
            length_tolerance = min((max((0, float(length_tolerance))), 1)) if type(length_tolerance) in (bool, int, float) else .5
            root_directory, prompt_size, username_size = self.__getRootDirectory(), len(prompt.split()), len(username)
            training_directory = root_directory+training_id+'/'
            if self.__path.exists(training_directory):
                adds, file_paths = [0], []
                for add in range(1, range_size+1): adds += [-add, add]
                for add in adds:
                    size_file = training_directory+str(prompt_size+add)+'.index'
                    if self.__path.exists(size_file): file_paths += [size_file]
                if len(file_paths) > 0:
                    full_context, trainings = '', []
                    for file_path in file_paths:
                        with open(file_path, 'r', encoding='utf-8') as file: full_context = file.read().strip()
                        contexts = full_context.split('<|end|>')
                        for context in contexts:
                            context = context.strip()
                            if len(context) > 0:
                                _input, _output = context.split('<|context|>')
                                _input = self.__b64decode(_input.encode('utf-8')).decode('utf-8')
                                _output = self.__b64decode(_output.encode('utf-8')).decode('utf-8')
                                trainings.append({'prompt': _input, 'answer': _output})
                    if len(trainings) > 0:
                        if username_size > 0 and username in prompt: prompt = prompt.replace(username, '<|username|>')
                        answer = self.__semanticComparison(trainings=trainings, prompt=prompt, precision=precision, tokens_tolerance=tokens_tolerance, length_tolerance=length_tolerance)
            if len(answer) > 0 and username_size > 0 and '<|username|>' in answer: answer = answer.replace('<|username|>', username)
            return answer.strip()
        except Exception as error:
            error_message = 'ERROR in SemanticComparison.predict: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
# This code is an algorithm projected, architected and developed by Sapiens Technology®️ and aims to save indexed conversations from language models
# for later consultation through semantic comparison using the prompts as a key to return the respective responses.
# This avoids unnecessary processing when an instruction has already been made previously by the same user,
# thus returning the already existing response to the same instruction without the need to process it again in the model.
# The algorithm also has the ability to adapt responses when instructions are similar but not completely the same, readjusting terms and words in general.
