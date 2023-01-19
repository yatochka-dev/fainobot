from prisma.models import Guild

Guild.create_partial("GuildWithoutItems", exclude=["items"])

Guild.create_partial("GuildWithoutSettings", exclude=["settings"])

