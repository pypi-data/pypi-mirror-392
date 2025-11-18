from biz_agent_hub.supportbot_elite import SupportbotElite


class BizAgentHub:
    user_id: str
    api_key: str
    supportbot_elite: SupportbotElite
    def __init__(self, user_id: str, api_key: str) -> None:
        self.user_id = user_id
        self.api_key = api_key
        self.supportbot_elite = SupportbotElite(user_id, api_key)

