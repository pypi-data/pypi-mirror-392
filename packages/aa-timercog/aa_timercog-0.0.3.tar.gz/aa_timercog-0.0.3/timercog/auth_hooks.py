"""
Auth hooks for Timer Cog
"""

from allianceauth import hooks


class TimerCogHooks:
    """Hooks for Timer Cog"""

    @staticmethod
    @hooks.register("discord_cogs_hook")
    def register_cogs():
        """Register Timer Cog with aa-discordbot"""
        return ["timercog.cogs.timer_cog"]


hooks_module = TimerCogHooks
