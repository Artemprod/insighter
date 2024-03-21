import asyncio

import openai
import tiktoken
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.document import Document
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_openai import ChatOpenAI

from DB.Mongo.mongo_enteties import Assistant
from logging_module.log_config import insighter_logger


class GPTAAssistant:
    def __init__(self, api_key, name, instructions):
        self.assistant = self._create_assistant(name, instructions)
        openai.api_key = api_key

    @staticmethod
    def _load_file(path):
        with open(path, "rb") as file:
            return openai.files.create(file=file, purpose="assistants")

    @staticmethod
    def _create_assistant(name, instructions):
        return openai.beta.assistants.create(
            name=name,
            instructions=instructions,
            model="gpt-4",
        )

    @staticmethod
    async def create_thread():
        return openai.beta.threads.create()

    @staticmethod
    async def delete_thread(thread_id):
        openai.beta.threads.delete(thread_id=thread_id)

    @staticmethod
    def add_user_message(thread_id, message_text):
        return openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_text,
        )

    async def unify_prompt_text(self, prompt: str, text: str):
        return prompt + "\n" + "вот траснкрибация разговора:" + "\n" + text

    async def generate_answer(self, thread_id, prompt, user_message, max_retries=3):
        message = await self.unify_prompt_text(prompt=prompt, text=user_message)
        self.add_user_message(thread_id=thread_id, message_text=message)
        attempts = 0
        while attempts < max_retries:
            run = openai.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id,
            )
            while run.status not in ["completed", "failed"]:
                insighter_logger.info(run.status)
                await asyncio.sleep(5)
                run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            if run.status == "completed":
                # Вывод сообщений и шагов выполнения
                insighter_logger.info("Run выполнен успешно.")
                # здесь можно обработать результаты run'а
                break
            elif run.status == "failed":
                error_message = run.last_error.message if run.last_error else "Неизвестная ошибка"
                insighter_logger.info(f"Run завершился с ошибкой: {error_message}")
                attempts += 1
                insighter_logger.info(f"Попытка {attempts} из {max_retries}... Перезапуск...")
                await asyncio.sleep(5)  # небольшая задержка перед следующей попыткой
        else:
            insighter_logger.info("Все попытки выполнить Run завершились неудачно. Останавливаемся.")

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        raw_data = messages.dict()["data"][0]["content"][0]["text"]["value"]
        return raw_data


class GPTAPIrequest:
    MODEL_3 = "gpt-3.5-turbo-1106"
    MODEL_4 = "gpt-4"
    MODEL_4_8K = "gpt-4-0613"
    MODEL_3_16 = "gpt-3.5-turbo-16k"
    MODEL_GPT_4_LIMIT = 8192
    MODEL_GPT_3_LIMIT = 16385

    def __init__(self, api_key, chunk_size=5000, chunk_overlap=800):
        openai.api_key = api_key
        self._system_assistant = None
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    @property
    def system_assistant(self):
        return self._system_assistant

    @system_assistant.setter
    def system_assistant(self, assistant: Assistant):
        if not isinstance(assistant, Assistant):
            raise ValueError("Не тот асистент")
        self._system_assistant = assistant

    @staticmethod
    async def send_request_to_chatgpt(messages, max_tokens):
        insighter_logger.info(messages)
        response = openai.chat.completions.create(
            model=GPTAPIrequest.MODEL_3,
            timeout=6000,
            messages=messages,
            n=1,
            stop=None,
            temperature=0.5,
            frequency_penalty=0,
            top_p=0.8,
            presence_penalty=-0,
            max_tokens=max_tokens,
        )
        response_message = response.dict()["choices"][0]["message"]["content"].strip()
        insighter_logger.info("ответ от чата: " + response_message)
        return response_message

    async def conversation(self, user_message, max_tokens_response=1000):
        tokens_in_text = await self.num_tokens_from_string(string=user_message, encoding_name="cl100k_base")
        insighter_logger.info(tokens_in_text)
        if tokens_in_text > GPTAPIrequest.MODEL_GPT_4_LIMIT - max_tokens_response:
            result = await self.make_long_text(
                string=user_message,
            )
            return result

        prompt_text = [
            {
                "role": "system",
                "content": self.system_assistant.assistant_prompt,
            },
            {
                "role": "user",
                "content": f'{self.system_assistant.user_prompt} + "\n", {user_message}',
            },
        ]
        response = await self.send_request_to_chatgpt(messages=prompt_text, max_tokens=max_tokens_response)
        return response

    async def split_text_into_parts(self, string, max_tokens):
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(string)
        token_parts = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]
        parts = [encoding.decode(i) for i in token_parts]

        return parts

    @staticmethod
    async def combine_responses(responses):
        # Объединяет ответы в один текст
        return " ".join(responses)

    async def make_long_text(self, string):
        # dotenv.load_dotenv()
        llm = ChatOpenAI(temperature=0, model_name="gpt-4")
        # Map
        map_template = f"""{self.system_assistant.assistant_prompt}
        {self.system_assistant.user_prompt_for_chunks}
        {'{docs}'}
        ответ на русском :"""
        map_prompt = PromptTemplate.from_template(map_template)
        map_chain = LLMChain(llm=llm, prompt=map_prompt)
        # Reduce
        reduce_template = f"""{self.system_assistant.assistant_prompt}
        {self.system_assistant.user_prompt}
        {'{docs}'}
        ответ на русском:"""
        reduce_prompt = PromptTemplate.from_template(reduce_template)
        # Run chain
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
        # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
        combine_documents_chain = StuffDocumentsChain(llm_chain=reduce_chain, document_variable_name="docs")
        # Combines and iteravely reduces the mapped documents
        reduce_documents_chain = ReduceDocumentsChain(
            # This is final chain that is called.
            combine_documents_chain=combine_documents_chain,
            # If documents exceed context for `StuffDocumentsChain`
            collapse_documents_chain=combine_documents_chain,
            # The maximum number of tokens to group documents into.
            token_max=GPTAPIrequest.MODEL_GPT_4_LIMIT,
        )

        # Combining documents by mapping a chain over them, then combining results
        map_reduce_chain = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="docs",
            # Return the results of the map steps in the output
            return_intermediate_steps=False,
        )

        split_docs = self.text_splitter.split_documents(await self.get_text_chunks_langchain(string))
        return map_reduce_chain.run(split_docs)

    @staticmethod
    async def get_text_chunks_langchain(text):
        text_splitter = CharacterTextSplitter(chunk_size=5000, chunk_overlap=800)
        docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
        return docs

    @staticmethod
    async def num_tokens_from_string(string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    async def num_tokens_from_messages(self, messages, model="gpt-4-0314"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            insighter_logger.info("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            insighter_logger.info("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            insighter_logger.info("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}.
                 See https://github.com/openai/openai-python/blob/main/chatml.md 
                 for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

