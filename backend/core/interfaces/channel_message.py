from pydantic import BaseModel


class ChannelMessageSchema(BaseModel):
    message_id: int
    unique_id: str
    channel_name: str | None = None
