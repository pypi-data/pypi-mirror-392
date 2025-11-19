# Module specialized in reading and interpreting local or internet files, web pages, YouTube videos, zip packages, tar.gz packages, or local directories.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
class SapiensFileInterpreter:
	def __init__(self, show_errors=True, display_error_point=False, progress=True):
		try:
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			self.__display_error_point = bool(display_error_point) if type(display_error_point) in (bool, int, float) else False
			self.__progress = bool(progress) if type(progress) in (bool, int, float) else True
			from warnings import filterwarnings
			filterwarnings('ignore')
			from traceback import print_exc
			self.__print_exc = print_exc
		except Exception as error:
			try:
				if self.__show_errors:
					error_message = 'ERROR in SapiensFileInterpreter.__init__: '+str(error)
					print(error_message)
					try: self.__print_exc() if self.__display_error_point else None
					except: pass
			except: pass
	def __get_total_size_in_bytes(self, path_string=''):
		try:
			if not self.__progress: return 0
			from os import path, walk
			from os import stat
			if path.isfile(path_string): return stat(path_string).st_size
			total_size = 0
			for directory_path, directory_names, file_names in walk(path_string):
				for file_name in file_names:
					file_path = path.join(directory_path, file_name)
					total_size = total_size + stat(file_path).st_size
			return total_size
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in SapiensFileInterpreter.__get_total_size_in_bytes: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return 0
	def __display_progress_bar(self, value=0):
	    try:
	        if self.__progress:
	            from sys import stdout
	            from shutil import get_terminal_size
	            if not hasattr(self, 'progress_bar_value'): self.progress_bar_value = None
	            if value < 0: value = 0
	            if value > 100: value = 100
	            if value == 0: self.progress_bar_value = None
	            if self.progress_bar_value is None: self.progress_bar_value = 0
	            self.progress_bar_value = value
	            terminal_width = get_terminal_size().columns
	            prefix = 'Reading data '
	            suffix = ' ' + f'{value:.2f}' + '%'
	            usable_width = terminal_width - len(prefix) - len(suffix) - 2
	            if usable_width < 1: usable_width = 1
	            filled_characters = int(usable_width * value / 100)
	            empty_characters = usable_width - filled_characters
	            bar = '[' + '=' * filled_characters + ' ' * empty_characters + ']'
	            stdout.write('\r' + prefix + bar + suffix)
	            stdout.flush()
	            if value == 100: stdout.write('\n')
	    except Exception as error:
	        if self.__show_errors:
	            error_message = 'ERROR in SapiensFileInterpreter.__display_progress_bar: ' + str(error)
	            print(error_message)
	            try: self.__print_exc() if self.__display_error_point else None
	            except: pass
	def __start_progress_increment(self, start_value=11, stop_value=75, increment_value=1):
		try:
			if self.__progress:
				from threading import Thread
				from time import sleep
				if hasattr(self, 'progress_increment_active') and self.progress_increment_active: return
				self.progress_increment_active = True
				def run():
					current_value = start_value
					while self.progress_increment_active and current_value < stop_value:
						self.__display_progress_bar(value=current_value)
						current_value = current_value + 1
						sleep(increment_value)
				self.progress_thread = Thread(target=run)
				self.progress_thread.start()
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in SapiensFileInterpreter.__start_progress_increment: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
	def __stop_progress_increment(self):
		try:
			if self.__progress:
				if not hasattr(self, 'progress_increment_active'): return
				self.progress_increment_active = False
				if hasattr(self, 'progress_thread'):
					try: self.progress_thread.join()
					except: pass
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in SapiensFileInterpreter.__stop_progress_increment: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
	def readFiles(self, path='', language=None):
		try:
			self.__display_progress_bar(value=0)
			text_of_the_interpretation = ''
			path = str(path).strip()
			if language is not None: language = str(language).strip()
			self.__display_progress_bar(value=1)
			list_of_files = [path]
			from os import path as sapiens_path
			from utilities_nlp import UtilitiesNLP as SapiensUtilities
			sapiens_utilities = SapiensUtilities(120, self.__show_errors, self.__display_error_point)
			self.__display_progress_bar(value=2)
			if not path.lower().startswith(('http://', 'https://')) and sapiens_path.isdir(path):
				self.__display_progress_bar(value=5)
				list_of_files = sapiens_utilities.getFilePathsFromDirectory(path)
				self.__display_progress_bar(value=10)
			elif path.lower().endswith(('.zip', '.tar.gz')):
				self.__display_progress_bar(value=3)
				temporary_files_directory, hash_code = sapiens_utilities.getTemporaryFilesDirectory(), sapiens_utilities.getHashCode()
				extraction_directory = temporary_files_directory+hash_code
				self.__display_progress_bar(value=4)
				if path.lower().endswith('.zip') and sapiens_utilities.extractZIPToFolder(path, extraction_directory): list_of_files = sapiens_utilities.getFilePathsFromDirectory(extraction_directory)
				elif path.lower().endswith('.tar.gz') and sapiens_utilities.extractTarGZToFolder(path, extraction_directory): list_of_files = sapiens_utilities.getFilePathsFromDirectory(extraction_directory)
				self.__display_progress_bar(value=8)
				if extraction_directory: sapiens_utilities.deleteDirectory(extraction_directory)
				self.__display_progress_bar(value=10)
			from INFINITE_CONTEXT_WINDOW import InfiniteContextWindow
			infinite_context_window = InfiniteContextWindow(indexed_tokens=1000000000, show_errors=self.__show_errors, display_error_point=self.__display_error_point)
			self.__display_progress_bar(value=11)
			total_size_in_bytes = self.__get_total_size_in_bytes(path_string=path)+2
			increment_value = max(0.25, total_size_in_bytes/16601529)
			if increment_value > 1: increment_value += 0.75
			self.__start_progress_increment(start_value=11, stop_value=75, increment_value=increment_value)
			category = sapiens_utilities.getFileCategory(path)
			if category == 'IMAGE_FILE':
				try: text_of_the_interpretation = sapiens_utilities.imageInterpreter(path, max_tokens=1000000000, language=language)['answer']
				except: text_of_the_interpretation = infinite_context_window.interpreter(path, max_tokens=1000000000, language=language)				
			elif category == 'AUDIO_FILE':
				try: text_of_the_interpretation = sapiens_utilities.audioInterpreter(path, max_tokens=1000000000, language=language)['answer']
				except: text_of_the_interpretation = infinite_context_window.interpreter(path, max_tokens=1000000000, language=language)
			elif category == 'VIDEO_FILE':
				try: text_of_the_interpretation = sapiens_utilities.videoInterpreter(path, max_tokens=1000000000, language=language)['answer']
				except: text_of_the_interpretation = infinite_context_window.interpreter(path, max_tokens=1000000000, language=language)
			else: text_of_the_interpretation = infinite_context_window.interpreter(path, max_tokens=1000000000, language=language)
			self.__stop_progress_increment()
			self.__display_progress_bar(value=75)
			text_of_the_interpretation_lines = text_of_the_interpretation.split('\n')
			zip_text, tar_gz_text, progress_value = '**below is the content of the zip file**', '**below is the content of the tar.gz file**', 76
			self.__display_progress_bar(value=progress_value)
			for index_x, file_path in enumerate(list_of_files):
				if progress_value < 90:
					progress_value += 1
					self.__display_progress_bar(value=progress_value)
				file_name_with_extension = str(sapiens_utilities.getFileNameWithExtension(file_path)).lower().strip()
				for index_y, interpretation_lines in enumerate(text_of_the_interpretation_lines):
					if (file_name_with_extension in interpretation_lines.lower()) or (interpretation_lines.strip().startswith('*') and interpretation_lines.strip().endswith('*')) or (len(interpretation_lines.strip()) > 0 and interpretation_lines.strip()[-1].isdigit()): text_of_the_interpretation_lines[index_y] = ''
					if zip_text in interpretation_lines.lower() or tar_gz_text in interpretation_lines.lower(): text_of_the_interpretation_lines[index_y] = ''
					if 'audio file content:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('audio file content:')[-1].strip()
					if 'audio you hear:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('audio you hear:')[-1].strip()
					if 'Image content:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('Image content:')[-1].strip()
					if 'In the video you see:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('In the video you see:')[-1].strip()
					if 'In the video you hear:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('In the video you hear:')[-1].strip()
					if 'In the video you can see the following:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('In the video you can see the following:')[-1].strip()
					if 'In the vídeo you can hear the following:' in interpretation_lines: text_of_the_interpretation_lines[index_y] = interpretation_lines.split('In the vídeo you can hear the following:')[-1].strip()
					if 'The predominant colors in the video are' in interpretation_lines: text_of_the_interpretation_lines[index_y] = ''
					if interpretation_lines.startswith('rgb color names: '): text_of_the_interpretation_lines[index_y] = ''
					if interpretation_lines.startswith('texts: '): text_of_the_interpretation_lines[index_y] = interpretation_lines.replace('texts: ', '', 1).strip()
					if len(interpretation_lines.strip()) < 1: text_of_the_interpretation_lines[index_y] = ''
					if progress_value < 90:
						progress_value += 1
						self.__display_progress_bar(value=progress_value)
			self.__display_progress_bar(value=91)
			text_of_the_interpretation, progress_value = '\n'.join(text_of_the_interpretation_lines), 92
			self.__display_progress_bar(value=93)
			def _remove_excessive_line_breaks(text='', progress_value=81):
				result = ''
				consecutive_count = 0
				for character in text:
					if character == '\n':
						consecutive_count = consecutive_count + 1
						if consecutive_count <= 2: result = result + character
					else:
						consecutive_count = 0
						result = result + character
					if progress_value < 98:
						progress_value += 1
						self.__display_progress_bar(value=progress_value)
				return result
			self.__display_progress_bar(value=99)
			text_of_the_interpretation = _remove_excessive_line_breaks(text=text_of_the_interpretation, progress_value=progress_value)
			self.__display_progress_bar(value=100)
			return text_of_the_interpretation.strip()
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in SapiensFileInterpreter.readFiles: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ''
# Module specialized in reading and interpreting local or internet files, web pages, YouTube videos, zip packages, tar.gz packages, or local directories.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
