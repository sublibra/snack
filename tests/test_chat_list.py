import asyncio
import pytest

from chat_tui.components.chat_list import ChatList


class DummyAPI:
    def __init__(self, chats):
        self._chats = chats

    async def get_current_user(self):
        return {"user_id": 1, "username": "tester"}

    async def get_chats(self):
        return self._chats


@pytest.mark.asyncio
async def test_load_chats_populates_list(event_loop):
    # Prepare dummy chat data
    chats = [
        {"chat_id": 10, "created_at": "2025-10-11T12:00:00Z", "members": [{"user_id":1, "username":"tester"}, {"user_id":2, "username":"alice"}]},
        {"chat_id": 11, "created_at": "2025-10-11T13:00:00Z", "members": [{"user_id":1, "username":"tester"}, {"user_id":3, "username":"bob"}]},
    ]

    api = DummyAPI(chats)

    chat_list = ChatList()

    # Ensure chat list is visible by default
    assert chat_list.display is True

    # Load chats
    await chat_list.load_chats(api)

    # After loading, chats reactive should be set and contain our data
    assert isinstance(chat_list.chats, list)
    assert len(chat_list.chats) == 2

    # Verify that get_chat_by_id works
    c = chat_list.get_chat_by_id(10)
    assert c is not None
    assert c.get("chat_id") == 10
