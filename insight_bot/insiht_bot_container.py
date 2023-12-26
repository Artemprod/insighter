from DB.Mongo.mongo_db import MongoORMConnection, MongoAssistantRepositoryORM, MongoUserRepoORM, UserDocsRepoORM
from api.progress_bar.command import ProgressBarClient
from config.bot_configs import load_bot_config, Config

config_data: Config = load_bot_config('.env')
MongoORMConnection(config_data.data_base)
assistant_repo = MongoAssistantRepositoryORM()
user_repo = MongoUserRepoORM()
doc_repo = UserDocsRepoORM()
progress_bar = ProgressBarClient()
