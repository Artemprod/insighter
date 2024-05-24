from analitics.mixpanel_system.mixpanel_tracker import MixpanelAnalyticsSystem
from api.progress_bar.command import ProgressBarClient
from config.bot_configs import Config, load_bot_config
from DB.Mongo.mongo_db import (
    MongoAssistantRepositoryORM,
    MongoORMConnection,
    MongoUserRepoORM,
    TariffRepoORM,
    TransactionRepoORM,
    UserBalanceRepoORM,
    UserDocsRepoORM,
)
from main_process.ChatGPT.gpt_dispatcher import (
    BigDataGPTWorker,
    GPTDispatcher,
    GPTDispatcherOnlyLonghain,
    OneRequestGPTWorker,
    TextTokenizer,
)
from main_process.ChatGPT.gpt_models_information import GPTModelManager
from main_process.file_format_manager import TelegramServerFileFormatDefiner
from main_process.file_manager import TelegramMediaFileManager
from main_process.media_file_manager import MediaFileManager
from main_process.post_ptocessing import PostProcessor
from main_process.text_invoke import (
    FORMATS,
    AudioFileHandler,
    PdfFileHandler,
    TextInvokeFactory,
    TxtFileHandler,
    VideoFileHandler, AssemblyInvoke,
)
from main_process.Whisper.openai_whisper_complain import WhisperClient
from main_process.Whisper.whisper_dispatcher import (
    LongMediaFilesTranscriber,
    MediaRecognitionFactory,
    ShortMediaFilesTranscriber,
)
from main_process.Whisper.whisper_information import WhisperModelManager

# ______LOGGING____________________________________________

# ______FORMATS____________________________________________
formats = FORMATS()
# ______CONFIGS____________________________________________
config_data: Config = load_bot_config(".env")
# ______DATABASE ____________________________________________

mongo_connection = MongoORMConnection(config_data.data_base, system_type=config_data.system.system_type)
assistant_repository = MongoAssistantRepositoryORM()
user_repository = MongoUserRepoORM()
document_repository = UserDocsRepoORM()
user_balance_repo = UserBalanceRepoORM()
transaction_repository = TransactionRepoORM()
tariff_repository = TariffRepoORM()

# ______PROGRESSBAR____________________________________________
progress_bar = ProgressBarClient()

# ______TOKENIZER____________________________________________
tokenizer = TextTokenizer()

# ______PREPROCESSOR____________________________________________
# default russian language (ru)
# text_preprocessor = TextPreprocessorAggregator("ru")

# ______POST-PROCESSOR____________________________________________
whisper_post_processor = PostProcessor()
# ______FILE_MANAGERS____________________________________________
file_format_manager = TelegramServerFileFormatDefiner()
server_file_manager = TelegramMediaFileManager()
media_file_manager = MediaFileManager(file_format_manager=file_format_manager)

# ______WHISPER_OBJECTS____________________________________________
whisper_model_manager = WhisperModelManager()
whisper_client = WhisperClient(whisper_manager=whisper_model_manager)

# ______TRANSCRIPTION_OBJECTS____________________________________________
short_media_file_transcriber = ShortMediaFilesTranscriber(whisper_client=whisper_client)
long_media_file_transcriber = LongMediaFilesTranscriber(
    whisper_client=whisper_client, media_file_manager=media_file_manager
)

# ______GPT_LLM_OBJECTS____________________________________________
gpt_model_manager = GPTModelManager()

# ______SUMMARY_OBJECTS____________________________________________
one_request_gpt = OneRequestGPTWorker(
    assistant_repositorysitory=assistant_repository,
    model_manager=gpt_model_manager,
)
long_request_gpt = BigDataGPTWorker(
    assistant_repositorysitory=assistant_repository,
    model_manager=gpt_model_manager,
    tokenizer=tokenizer,
)

# ______FACTORIES____________________________________________
recognition_factory = MediaRecognitionFactory(
    media_file_manager=media_file_manager,
    short_media_transcriber=short_media_file_transcriber,
    long_media_transcriber=long_media_file_transcriber,
)

gpt_dispatcher = GPTDispatcher(
    token_sizer=tokenizer,
    model_manager=gpt_model_manager,
    one_request_gpt=one_request_gpt,
    long_request_gpt=long_request_gpt,
)
gpt_dispatcher_only_longcahin = GPTDispatcherOnlyLonghain(
    long_request_gpt=long_request_gpt,
)

# ______TEXT_INVOKERS_OBJECTS____________________________________________

pdf_handler = PdfFileHandler()
txt_handler = TxtFileHandler()
video_handler = AssemblyInvoke(api_key=config_data.assembly)
audio_handler = AudioFileHandler(ai_transcriber=recognition_factory)

text_invoker = TextInvokeFactory(
    format_definer=file_format_manager,
    pdf_handler=pdf_handler,
    txt_handler=txt_handler,
    video_handler=video_handler,
    audio_handler=audio_handler,
    formats=formats,
)
# ____ANALITIC INSTRUMENT____________________________________________
mixpanel_tracker = MixpanelAnalyticsSystem(mixpanel_token=config_data.analytical_system_token)


# ______PROCESS_PIPELINE____________________________________________


# ____SERVER_CONNECTION____________________________________________
# server_file_worker = ServerFileManager()

