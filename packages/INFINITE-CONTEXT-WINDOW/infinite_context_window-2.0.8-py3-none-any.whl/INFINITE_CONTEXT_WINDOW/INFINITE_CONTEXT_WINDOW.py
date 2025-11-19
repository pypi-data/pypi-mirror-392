# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
class InfiniteContextWindow:
	def __init__(self, indexed_tokens=32768000, show_errors=True, display_error_point=False):
		try:
			self.__indexed_tokens = max(1, int(indexed_tokens)) if type(indexed_tokens) in (bool, int, float) else 32768000
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			self.__display_error_point = bool(display_error_point) if type(display_error_point) in (bool, int, float) else False
			self.__is_code = False
			from warnings import filterwarnings
			filterwarnings('ignore')
			from traceback import print_exc
			self.__print_exc = print_exc
		except Exception as error:
			try:
				if self.__show_errors:
					error_message = 'ERROR in InfiniteContextWindow.__init__: '+str(error)
					print(error_message)
					try: self.__print_exc() if self.__display_error_point else None
					except: pass
			except: pass
	def __model_selector(self, models_list=[], tokens_number=0):
		try:
			model_path_and_context_window = ('', 0)
			from utilities_nlp import UtilitiesNLP as SapiensUtilities
			sapiens_utilities = SapiensUtilities(120, self.__show_errors, self.__display_error_point)
			if models_list and tokens_number:
				models_list = sorted(models_list, key=lambda full_model_path: sapiens_utilities.getInputContextLimit(full_model_path))
				model_path_and_context_window = (models_list[-1], tokens_number)
				for model_path in models_list:
					n_context_window = sapiens_utilities.getInputContextLimit(model_path)
					if tokens_number <= n_context_window: return (model_path, n_context_window)
			return model_path_and_context_window
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in InfiniteContextWindow.__model_selector: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ('', 0)
	def __get_directory_interpretation(self, directory_path='', max_tokens=32768, main_page=None, language=None):
		try:
			directory_interpretation = ''
			from utilities_nlp import UtilitiesNLP as SapiensUtilities
			from perpetual_context_window import PerpetualContextWindow as SapiensPerpetualContextWindow
			from infinite_context import InfiniteContext as SapiensInfiniteContext
			sapiens_utilities = SapiensUtilities(120, self.__show_errors, self.__display_error_point)
			file_paths_from_directory = sapiens_utilities.getFilePathsFromDirectory(directory_path)
			sapiens_perpetual_context_window = SapiensPerpetualContextWindow(self.__indexed_tokens, self.__show_errors, self.__display_error_point)
			sapiens_infinite_context = SapiensInfiniteContext(self.__show_errors)
			context_for_code_interpretation, context_for_text_interpretation, len_file_paths_from_directory = sapiens_infinite_context.getSummaryCode, sapiens_infinite_context.getSummaryText, len(file_paths_from_directory)
			try: from .allowed_extensions import SapiensAllowedExtensions
			except: from allowed_extensions import SapiensAllowedExtensions
			get_allowed_extensions, get_programming_extensions = SapiensAllowedExtensions().get_allowed_extensions, SapiensAllowedExtensions().get_programming_extensions
			allowed_extensions, programming_extensions = get_allowed_extensions(), get_programming_extensions()
			max_tokens_1024, file_max_tokens = max_tokens*1024, max(1, max_tokens//max(1, len_file_paths_from_directory))
			for file_paths in file_paths_from_directory:
				file_extension = sapiens_utilities.getFileExtension(file_paths)
				if file_extension in allowed_extensions:
					file_name_with_extension = sapiens_utilities.getFileNameWithExtension(file_paths)
					if not file_name_with_extension.startswith('._'):
						file_interpreter = sapiens_perpetual_context_window.fileInterpreter(file_paths, max_tokens_1024, main_page, language)
						count_tokens, is_code = sapiens_infinite_context.countTokens(file_interpreter), file_extension in programming_extensions
						if file_extension in programming_extensions and count_tokens > max_tokens: file_interpreter, is_code = context_for_code_interpretation(file_interpreter, file_max_tokens-10), True
						elif count_tokens > max_tokens: file_interpreter = context_for_text_interpretation(file_interpreter, file_max_tokens)
						code_block_1, code_block_2 = ('```\n', '\n```') if is_code else ('', '')
						if file_extension: file_extension = str(file_extension[1:]).upper().strip()
						if is_code: file_interpreter = file_interpreter.replace(f'*TXT File*', '', 1).replace(f'*{file_extension} File*', '', 1).strip()
						directory_interpretation += f'# Contents of file "{file_name_with_extension}":\n{code_block_1}{file_interpreter}{code_block_2}\n\n'
			count_tokens = sapiens_infinite_context.countTokens(directory_interpretation)
			if count_tokens > max_tokens: directory_interpretation = context_for_text_interpretation(directory_interpretation, max_tokens)
			return directory_interpretation.strip()
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in InfiniteContextWindow.__get_directory_interpretation: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ''				
	def __get_prompt(self, messages=[], max_tokens=32768):
		try:
			user_prompt = ''
			if messages:
				last_message = messages[-1]
				if type(last_message) == dict:
					role = str(last_message.get('role', '')).lower().strip()
					if role == 'user': user_prompt = str(last_message.get('content', '')).strip()
			if user_prompt:
				from infinite_context import InfiniteContext as SapiensInfiniteContext
				from perpetual_context import PerpetualContext as SapiensPerpetualContext
				from utilities_nlp import UtilitiesNLP as SapiensUtilities
				sapiens_infinite_context = SapiensInfiniteContext(self.__show_errors)
				count_tokens = sapiens_infinite_context.countTokens(user_prompt)
				if count_tokens > max_tokens:
					is_programming_language_x = SapiensPerpetualContext(self.__show_errors)._PerpetualContext__itsCode(user_prompt)
					is_programming_language_y = SapiensUtilities(120, self.__show_errors, self.__display_error_point).isProgrammingLanguage(user_prompt)
					is_programming_language_z = is_programming_language_x and is_programming_language_y
					context_for_code_interpretation, context_for_text_interpretation = sapiens_infinite_context.getSummaryCode, sapiens_infinite_context.getSummaryText
					if is_programming_language_z: user_prompt, self.__is_code = context_for_code_interpretation(user_prompt, max_tokens), True
					else: user_prompt = context_for_text_interpretation(user_prompt, max_tokens)
			return user_prompt.strip()
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in InfiniteContextWindow.__get_prompt: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ''		
	def interpreter(self, file_path='', max_tokens=32768, main_page=None, language=None):
		try:
			interpretation_of_the_file, extraction_directory = '', ''
			file_path = str(file_path).strip()
			max_tokens = max(1, int(max_tokens)) if type(max_tokens) in (bool, int, float) else 32768
			if main_page is not None: main_page = max(1, int(main_page)) if type(main_page) in (bool, int, float) else None
			if language is not None: language = str(language).strip()
			from os import path as sapiens_path
			from utilities_nlp import UtilitiesNLP as SapiensUtilities
			sapiens_utilities = SapiensUtilities(120, self.__show_errors, self.__display_error_point)
			if not file_path.lower().startswith(('http://', 'https://')) and sapiens_path.isdir(file_path): interpretation_of_the_file = self.__get_directory_interpretation(file_path, max_tokens, main_page, language)
			elif file_path.lower().endswith(('.zip', '.tar.gz')):
				temporary_files_directory, hash_code = sapiens_utilities.getTemporaryFilesDirectory(), sapiens_utilities.getHashCode()
				extraction_directory = temporary_files_directory+hash_code
				zip_text, tar_gz_text = '**below is the content of the zip file**\n\n', '**below is the content of the tar.gz file**\n\n'
				n_zip_text, n_tar_gz_text = sapiens_utilities.countTokens(zip_text), sapiens_utilities.countTokens(tar_gz_text)
				if file_path.lower().endswith('.zip') and sapiens_utilities.extractZIPToFolder(file_path, extraction_directory): interpretation_of_the_file = zip_text+self.__get_directory_interpretation(extraction_directory, max_tokens-n_zip_text, main_page, language)
				elif file_path.lower().endswith('.tar.gz') and sapiens_utilities.extractTarGZToFolder(file_path, extraction_directory): interpretation_of_the_file = tar_gz_text+self.__get_directory_interpretation(extraction_directory, max_tokens-n_tar_gz_text, main_page, language)
			else:
				from perpetual_context_window import PerpetualContextWindow as SapiensPerpetualContextWindow
				interpretation_of_the_file = SapiensPerpetualContextWindow(self.__indexed_tokens, self.__show_errors, self.__display_error_point).fileInterpreter(file_path, max_tokens, main_page, language)
			if extraction_directory: sapiens_utilities.deleteDirectory(extraction_directory)
			count_tokens = sapiens_utilities.countTokens(interpretation_of_the_file)
			if count_tokens > max_tokens:
				context_for_text_interpretation = sapiens_utilities.getTokensSummary
				interpretation_of_the_file = context_for_text_interpretation(interpretation_of_the_file, max_tokens)
			return interpretation_of_the_file.strip()
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in InfiniteContextWindow.interpreter: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ''
	def getContext(self, messages=[], max_tokens=32768):
		try:
			context_result = {'messages': [], 'synthesis': []}
			messages = list(messages) if type(messages) in (tuple, dict, list) else []
			max_tokens = max(1, int(max_tokens)) if type(max_tokens) in (bool, int, float) else 32768
			context_result, self.__is_code = {'messages': messages, 'synthesis': messages}, False
			user_prompt = self.__get_prompt(messages=messages, max_tokens=max_tokens)
			if user_prompt: messages[-1]['content'] = user_prompt
			from perpetual_context_window import PerpetualContextWindow as SapiensPerpetualContextWindow
			context_result = SapiensPerpetualContextWindow(0 if self.__is_code else self.__indexed_tokens, self.__show_errors, self.__display_error_point).getContext(messages, max_tokens)
			return context_result
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in InfiniteContextWindow.getContext: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return {'messages': messages, 'synthesis': messages}
	def modelSelector(self, models_list=[], tokens_number=0):
		try:
			model_path_and_context_window = ('', 0)
			models_list = list(models_list) if type(models_list) in (tuple, dict, list) else []
			tokens_number = max(0, int(tokens_number)) if type(tokens_number) in (bool, int, float) else 0
			model_path_and_context_window = self.__model_selector(models_list=models_list, tokens_number=tokens_number)
			return model_path_and_context_window
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in InfiniteContextWindow.modelSelector: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ('', 0)
# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
