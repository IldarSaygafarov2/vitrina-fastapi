from dataclasses import dataclass

from environs import Env


# @dataclass
# class WebhookConfig:
#     web_server_host: str
#     web_server_port: int
#     base_webhook_url: str
#     main_bot_path: str

#     @property
#     def main_webhook_url(self):
#         return f"{self.base_webhook_url}{self.main_bot_path}"

#     @staticmethod
#     def from_env(env: Env) -> "WebhookConfig":
#         return WebhookConfig(
#             web_server_host=env.str("WEB_SERVER_HOST"),
#             web_server_port=env.int("WEB_SERVER_PORT"),
#             base_webhook_url=env.str("BASE_WEBHOOK_URL"),
#             main_bot_path=env.str("MAIN_BOT_PATH"),
#         )
