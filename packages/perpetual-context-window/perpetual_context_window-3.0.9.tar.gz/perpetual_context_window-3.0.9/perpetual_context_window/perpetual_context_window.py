# Module developed by Sapiens Technology® for building language model algorithms with a perpetual context window without complete forgetting of initial, intermediate, and final information.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
class PerpetualContextWindow:
	def __init__(self, indexed_tokens=20000000, show_errors=True, display_error_point=False):
		try:
			self.__indexed_tokens = max(1, int(indexed_tokens)) if type(indexed_tokens) in (bool, int, float) else 20000000
			self.__show_errors = bool(show_errors) if type(show_errors) in (bool, int, float) else True
			self.__display_error_point = bool(display_error_point) if type(display_error_point) in (bool, int, float) else False
			from traceback import print_exc
			self.__print_exc = print_exc
		except Exception as error:
			try:
				if self.__show_errors:
					error_message = 'ERROR in PerpetualContextWindow.__init__: '+str(error)
					print(error_message)
					try: self.__print_exc() if self.__display_error_point else None
					except: pass
			except: pass
	def __getWikipediaPage(self, url_path=''):
		try:
			result_text = ''
			url_path = str(url_path).strip()
			try:
				from os import environ
				from certifi import where
				environ['SSL_CERT_FILE'] = where()
				from logging import getLogger, ERROR
				getLogger('requests').setLevel(ERROR)
			except: pass
			from urllib.parse import unquote
			from urllib.request import Request, urlopen
			from urllib.parse import urlencode
			from json import loads
			from re import search, sub
			def _convert_encoded_url_to_readable_url(encoded_url):
				try: return unquote(encoded_url)
				except: return encoded_url
			url_path = _convert_encoded_url_to_readable_url(encoded_url=url_path)
			def _html_to_markdown(html):
				html = sub(r'<h2[^>]*><span[^>]*>(.*?)</span></h2>', r'## \1\n\n', html)
				html = sub(r'<h3[^>]*><span[^>]*>(.*?)</span></h3>', r'### \1\n\n', html)
				html = sub(r'<h4[^>]*><span[^>]*>(.*?)</span></h4>', r'#### \1\n\n', html)
				html = sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n\n', html)
				html = sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n\n', html)
				html = sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n\n', html)
				html = sub(r'<p>\s*(.*?)\s*</p>', r'\1\n\n', html)
				html = sub(r'<b>(.*?)</b>|<strong>(.*?)</strong>', lambda m: f'**{m.group(1) or m.group(2)}**', html)
				html = sub(r'<i>(.*?)</i>|<em>(.*?)</em>', lambda m: f'*{m.group(1) or m.group(2)}*', html)
				html = sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', html)
				html = sub(r'<[^>]+>', '', html)
				html = sub(r'={2,}\s*(.+?)\s*={2,}', lambda m: f'{"#" * (m.group(0).count("=") // 2)} {m.group(1).strip()}', html)
				html = sub(r'\n{3,}', '\n\n', html)
				html = sub(r'[ \t]+', ' ', html)
				html = sub(r'\n\s*\n', '\n\n', html)
				html = sub(r'^\s+|\s+$', '', html)
				return html.strip()
			def _get_wikipedia_markdown(url):
				title = url.split('/wiki/')[-1]
				match = search(r'https?://(\w+)\.wikipedia\.org', url)
				language = match.group(1) if match else 'en'
				api_url = f'https://{language}.wikipedia.org/w/api.php'
				params = {'action': 'query', 'format': 'json', 'titles': title, 'prop': 'extracts', 'exformat': 'html', 'explaintext': 'false'}
				query_string = urlencode(params)
				full_url = f'{api_url}?{query_string}'
				headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
				req = Request(full_url, headers=headers)
				with urlopen(req) as response: data = loads(response.read().decode('utf-8'))
				pages = data['query']['pages']
				page_id = list(pages.keys())[0]
				if page_id == '-1': return ''
				html = pages[page_id].get('extract', '')
				page_title = pages[page_id].get('title', '')
				markdown = _html_to_markdown(html)
				return f'# {page_title}\n\n{markdown}'
			get_wikipedia_markdown = _get_wikipedia_markdown(url=url_path).strip()
			result_text = f'## Contents of the WEB address: {url_path}\n\n{get_wikipedia_markdown}'
			return result_text.strip()
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in PerpetualContextWindow.__getWikipediaPage: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ''
	def fileInterpreter(self, file_path='', max_tokens=1000, main_page=None, language=None):
		try:
			interpretation_of_the_file = ''
			file_path = str(file_path).strip()
			if file_path.lower().startswith('https://') and '.wikipedia.org/' in file_path.lower(): interpretation_of_the_file = self.__getWikipediaPage(url_path=file_path)
			if not interpretation_of_the_file:
				from infinite_context import InfiniteContext
				infinite_context = InfiniteContext(display_error_point=self.__show_errors)
				if type(language) == str and '-' in language: language = str(language.split('-')[0]).lower().strip()
				interpretation_of_the_file = infinite_context.getSummaryFile(file_path=file_path, max_tokens=max_tokens, main_page=main_page, language=language, maximum_colors=5)
			return interpretation_of_the_file
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in PerpetualContextWindow.fileInterpreter: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return ''
	def getContext(self, messages=[], max_tokens=512):
		try:
			context_result, main_context = {'messages': [], 'synthesis': []}, []
			messages = list(messages) if type(messages) in (tuple, list) else []
			max_tokens = max(1, int(max_tokens)) if type(max_tokens) in (bool, int, float) else 512
			context_result = {'messages': messages, 'synthesis': messages}
			if not messages: return context_result
			system, original_prompt, prompt, answer = '', '', '', ''
			if str(messages[0].get('role', '')).lower().strip() == 'system': system = str(messages[0].get('content', '')).strip()
			if str(messages[-1].get('role', '')).lower().strip() == 'user': prompt = original_prompt = str(messages[-1].get('content', '')).strip()
			def get_messages():
				from sapiens_infinite_context_window import SapiensInfiniteContextWindow
				sapiens_infinite_context_window = SapiensInfiniteContextWindow()
				synthesized_messages = sapiens_infinite_context_window.synthesize_messages(prompt=prompt, messages=messages, maximum_tokens=max_tokens)
				return synthesized_messages['synthesis']
			from infinite_context import InfiniteContext
			infinite_context = InfiniteContext(display_error_point=self.__show_errors)
			count_tokens = infinite_context.countTokens(str(messages))
			if count_tokens > self.__indexed_tokens:
				try:
					user_id, dialog_id = infinite_context.getHashCode(), 0
					messages_length = len(messages)
					if messages_length >= 2:
						for message in messages[:-1] if original_prompt else messages:
							role = str(message.get('role', '')).lower().strip()
							content = str(message.get('content', '')).strip()
							if role == 'user': prompt = content
							elif role == 'assistant': answer = content
							if prompt and answer:
								save_context = infinite_context.saveContext(user_id=user_id, dialog_id=dialog_id, prompt=prompt, answer=answer)
								if save_context: prompt, answer = '', ''
					main_context = infinite_context.getContext(user_id=user_id, dialog_id=dialog_id, config={'system': system, 'prompt': original_prompt, 'max_tokens': max_tokens})
					if type(main_context) == str: main_context = [{'role': 'user', 'content': main_context}]
					new_main_context = []
					for context in main_context:
						if context not in new_main_context: new_main_context.append(context)
					if new_main_context: main_context = new_main_context
					if main_context:
						context_result['synthesis'] = main_context
						infinite_context.deleteContext(user_id=user_id, dialog_id=dialog_id)
						from perpetual_context import PerpetualContext
						perpetual_context = PerpetualContext(display_error_point=self.__show_errors)
						root_directory = perpetual_context._PerpetualContext__getRootDirectory()
						context_directory = f'{root_directory}context_directory/{user_id}'
						from os import path
						from shutil import rmtree
						if path.exists(context_directory):
							try: rmtree(context_directory)
							except: pass
				except Exception as error:
					if self.__show_errors:
						error_message = 'ERROR in PerpetualContextWindow.getContext (indexed_tokens): '+str(error)
						print(error_message)
						try: self.__print_exc() if self.__display_error_point else None
						except: pass
					context_result['synthesis'] = get_messages()
			else: context_result['synthesis'] = get_messages()
			return context_result
		except Exception as error:
			if self.__show_errors:
				error_message = 'ERROR in PerpetualContextWindow.getContext: '+str(error)
				print(error_message)
				try: self.__print_exc() if self.__display_error_point else None
				except: pass
			return {'messages': [], 'synthesis': []}
# Module developed by Sapiens Technology® for building language model algorithms with a perpetual context window without complete forgetting of initial, intermediate, and final information.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
