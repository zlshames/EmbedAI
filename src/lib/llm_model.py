import os
import requests
import atexit

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import GPT4All

from .flask import app


class LLMModel:
    _llm = None
    model_path = None
    model_n_ctx = None
    model_filename = None
    models_folder = None

    def __init__(self, **kwargs):
        self.load_config(**kwargs)

    @property
    def llm(self):
        if not self._llm:
            self.load_model()

        return self._llm
    
    @property
    def models_path(self):
        return f'{self.models_folder}/{self.model_filename}'

    def load_config(self, **kwargs):
        app.logger.debug('Loading LLM Model Configuration...')

        self.model_filename = (
            kwargs.get('model_filename') or
            os.environ.get('MODEL_FILENAME') or
            'ggml-gpt4all-j-v1.3-groovy.bin'
        )
        self.model_path = kwargs.get('model_path') or os.environ.get('MODEL_PATH') or f'models/{this.model_filename}'
        self.model_n_ctx = kwargs.get('model_n_ctx') or os.environ.get('MODEL_N_CTX') or 1000
        self.models_folder = kwargs.get('models_folder') or os.environ.get('MODELS_FOLDER') or 'models'

    def remove_model(self):
        if os.path.exists(self.models_path):
            os.remove(self.models_path)

    def download_model(self, force=False):
        # If the model is already downloaded, don't re-download it
        if not force and os.path.exists(self.models_path):
            raise Exception(f'Model already exists at {self.models_path}')

        app.logger.info('Downloading model...')
        url = f'https://gpt4all.io/models/{self.model_filename}'

        # Ensure the parent models dir exists
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
        
        print(self.models_folder)

        # Remove the model if it already exists
        self.remove_model()

        # Add a callback to remove the model on exit
        atexit.register(self.remove_model)

        try:
            # Stream the model download
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            progress = 0
            with open(self.models_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=4096):
                    file.write(chunk)
                    bytes_downloaded += len(chunk)
                    new_progress = round((bytes_downloaded / total_size) * 100, 2)

                    if new_progress != progress:
                        app.logger.info(f'Download Progress: {new_progress}%')
                        progress = new_progress

            atexit.unregister(self.remove_model)
        except Exception as ex:
            app.logger.error(f'Error downloading model: {ex}')
            self.remove_model()
            raise ex

    def load_model(self):
        if not os.path.exists(self.models_path):
            return

        callbacks = [StreamingStdOutCallbackHandler()]
        self._llm = GPT4All(model=self.model_path, n_ctx=self.model_n_ctx, backend='gptj', callbacks=callbacks, verbose=False)