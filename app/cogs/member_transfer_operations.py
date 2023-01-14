from disnake.ext.commands import Cog

from app.services.GuildService import GuildService
from app.services.MemberService import MemberService


class MemberProfileCog(Cog, GuildService, MemberService):
    def __init__(self, bot: Bot):
        self.bot = bot