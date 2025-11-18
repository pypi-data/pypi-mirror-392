"""
Timer Cog - Discord bot command for creating structure timers
Fixed version with improved error handling and authentication
"""

import logging
import re
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Optional

import discord
from discord import AutocompleteContext, Option, SlashCommandGroup
from discord.ext import commands
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from eveuniverse.models import EveSolarSystem, EveType
from structuretimers.models import Timer

logger = logging.getLogger(__name__)


# Configuration settings - to be added to local.py
def get_allowed_discord_roles():
    """Get allowed Discord role IDs from settings"""
    return getattr(settings, "TIMERCOG_ALLOWED_ROLE_IDS", [])


def get_timer_channels():
    """Get allowed timer command channel IDs from settings"""
    return getattr(settings, "TIMERCOG_ALLOWED_CHANNELS", [])


def get_guild_ids():
    """Get guild IDs for instant command registration (optional)"""
    return getattr(settings, "TIMERCOG_GUILD_IDS", None)


class TimerCog(commands.Cog):
    """
    Discord Cog for creating structure timers
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Timer Cog loaded")

    timer = SlashCommandGroup("timer", "Structure timer commands", guild_ids=get_guild_ids())

    async def solar_system_autocomplete(self, ctx: AutocompleteContext):
        """Autocomplete for solar systems"""
        try:
            query = ctx.value.lower() if ctx.value else ""
            systems = EveSolarSystem.objects.filter(name__icontains=query)[:25]
            return [system.name for system in systems]
        except Exception as e:
            logger.error(f"Error in solar system autocomplete: {e}")
            return []

    async def structure_type_autocomplete(self, ctx: AutocompleteContext):
        """Autocomplete for structure types"""
        try:
            query = ctx.value.lower() if ctx.value else ""
            structure_types = EveType.objects.filter(
                eve_group__eve_category_id=65,  # Structure category
                name__icontains=query,
                published=True,
            )[:25]
            return [stype.name for stype in structure_types]
        except Exception as e:
            logger.error(f"Error in structure type autocomplete: {e}")
            return []

    async def timer_type_autocomplete(self, ctx: AutocompleteContext):
        """Autocomplete for timer types"""
        try:
            query = ctx.value.lower() if ctx.value else ""

            # Check if Timer model has Type choices
            if hasattr(Timer, "Type") and hasattr(Timer.Type, "choices"):
                choices = [str(choice[1]) for choice in Timer.Type.choices]
                return [choice for choice in choices if query in choice.lower()][:25]

            # Check if timer_type field exists and has choices
            try:
                timer_type_field = Timer._meta.get_field("timer_type")
                if hasattr(timer_type_field, "choices") and timer_type_field.choices:
                    choices = [str(choice[1]) for choice in timer_type_field.choices]
                    return [choice for choice in choices if query in choice.lower()][:25]
            except:
                pass

            # Fallback to common EVE Online timer types
            common_types = [
                "Armor",
                "Hull",
                "Final",
                "Anchoring",
                "Unanchoring",
                "Shield",
                "Repair",
            ]
            return [t for t in common_types if query in t.lower()]

        except Exception as e:
            logger.error(f"Error in timer type autocomplete: {e}")
            return ["Armor", "Hull", "Final"]

    async def objective_autocomplete(self, ctx: AutocompleteContext):
        """Autocomplete for objectives"""
        try:
            query = ctx.value.lower() if ctx.value else ""

            # Check if Timer has Objective choices
            if hasattr(Timer, "Objective") and hasattr(Timer.Objective, "choices"):
                choices = [str(choice[1]) for choice in Timer.Objective.choices]
                return [choice for choice in choices if query in choice.lower()]

            # Fallback to common objectives
            objectives = ["Friendly", "Hostile", "Neutral"]
            return [obj for obj in objectives if query in obj.lower()]

        except Exception as e:
            logger.error(f"Error in objective autocomplete: {e}")
            return ["Friendly", "Hostile", "Neutral"]

    async def check_permissions(self, ctx) -> bool:
        """Check if user has permission to use timer commands (role and channel restrictions)"""
        try:
            # Check if command is used in allowed channels
            allowed_channels = get_timer_channels()
            if allowed_channels and ctx.channel.id not in allowed_channels:
                logger.debug(f"Permission denied: Channel {ctx.channel.id} not in allowed list")
                return False

            # Check if user has allowed role
            allowed_roles = get_allowed_discord_roles()
            if allowed_roles:
                user_role_ids = [role.id for role in ctx.author.roles]
                if not any(role_id in allowed_roles for role_id in user_role_ids):
                    logger.debug(f"Permission denied: User {ctx.author} doesn't have required role")
                    return False

            # Note: Authentication is checked separately when getting the user
            return True

        except Exception as e:
            logger.error(f"Error in permission check: {e}", exc_info=True)
            # On error, deny permission for safety
            return False

    @timer.command(name="add", description="Add a new structure timer")
    async def add_timer(
        self,
        ctx,
        system: Option(
            str,
            description="Solar system where the structure is located",
            required=True,
            autocomplete=solar_system_autocomplete,
        ),
        structure_type: Option(
            str,
            description="Type of structure (e.g., Astrahus, Fortizar, Keepstar)",
            required=True,
            autocomplete=structure_type_autocomplete,
        ),
        owner: Option(str, description="Owner corporation or alliance name", required=True),
        timer_type: Option(
            str,
            description="Timer type (e.g., Armor, Hull, Final)",
            required=True,
            autocomplete=timer_type_autocomplete,
        ),
        days: Option(
            int,
            description="Days until timer expires",
            required=False,
            default=0,
            min_value=0,
            max_value=365,
        ),
        hours: Option(
            int,
            description="Hours until timer expires",
            required=False,
            default=0,
            min_value=0,
            max_value=23,
        ),
        minutes: Option(
            int,
            description="Minutes until timer expires",
            required=False,
            default=0,
            min_value=0,
            max_value=59,
        ),
        structure_name: Option(
            str, description="Custom name for the structure (optional)", required=False, default=""
        ),
        objective: Option(
            str,
            description="Objective: Friendly, Hostile, or Neutral",
            required=False,
            default="Hostile",
            autocomplete=objective_autocomplete,
        ),
        location_details: Option(
            str,
            description="Additional location information (e.g., Planet, Moon)",
            required=False,
            default="",
        ),
        notes: Option(
            str, description="Additional notes about the timer", required=False, default=""
        ),
    ):
        """
        Add a new structure timer to the system
        """
        await ctx.defer()

        # Check permissions
        try:
            has_permission = await self.check_permissions(ctx)
            if not has_permission:
                allowed_channels = get_timer_channels()
                channel_mention = ""
                if allowed_channels:
                    channel_mention = f" in the designated timer channels"

                await ctx.respond(
                    "❌ You don't have permission to use this command." + channel_mention,
                    ephemeral=True,
                )
                return
        except Exception as e:
            logger.error(f"Error checking permissions: {e}", exc_info=True)
            await ctx.respond(
                "❌ An error occurred while checking permissions. "
                "Please contact an administrator.",
                ephemeral=True,
            )
            return

        try:
            # Get the authenticated user directly from database
            # We don't use aadiscordbot's get_auth_user because it requires bot-level authentication
            # that this cog doesn't have. We just need the linked user from the database.
            auth_user = None
            DiscordUser = None

            try:
                # Try to import DiscordUser model
                try:
                    from allianceauth.services.modules.discord.models import DiscordUser
                except ImportError:
                    # Fallback for different AllianceAuth versions
                    try:
                        from discord.models import DiscordUser
                    except ImportError as ie:
                        logger.error(f"Could not import DiscordUser model: {ie}")
                        await ctx.respond(
                            "❌ Discord integration not available. "
                            "Please contact your administrator.",
                            ephemeral=True,
                        )
                        return

                logger.info(
                    f"Looking up auth user for Discord ID: " f"{ctx.author.id} ({ctx.author.name})"
                )

                # Get the Discord user from database
                discord_user = DiscordUser.objects.select_related("user").get(uid=ctx.author.id)
                auth_user = discord_user.user

                logger.info(
                    f"Successfully found auth user: " f"{auth_user.username} (ID: {auth_user.id})"
                )

            except Exception as e:
                # Check if it's a DoesNotExist error
                if DiscordUser and e.__class__.__name__ == "DoesNotExist":
                    logger.warning(
                        f"No Discord link found for user "
                        f"{ctx.author.name} (ID: {ctx.author.id})"
                    )
                    await ctx.respond(
                        "❌ **Your Discord account is not linked to AllianceAuth.**\n\n"
                        "**To fix this:**\n"
                        "1. Visit your AllianceAuth website\n"
                        "2. Go to **Services**\n"
                        "3. Find **Discord** and click **Activate**\n"
                        "4. Complete the authorization\n"
                        "5. Try this command again\n\n"
                        f"Your Discord ID: `{ctx.author.id}`",
                        ephemeral=True,
                    )
                    return
                else:
                    logger.error(
                        f"Unexpected error looking up auth user for " f"{ctx.author.id}: {e}",
                        exc_info=True,
                    )
                    await ctx.respond(
                        "❌ An error occurred while looking up your account. "
                        "Please contact an administrator.",
                        ephemeral=True,
                    )
                    return

            if not auth_user:
                logger.error(
                    f"Discord user found but no auth user linked for "
                    f"{ctx.author.name} (ID: {ctx.author.id})"
                )
                await ctx.respond(
                    "❌ Your Discord is linked but there's no associated user account. "
                    "Please contact an administrator.",
                    ephemeral=True,
                )
                return

            # Validate and get solar system
            try:
                solar_system = EveSolarSystem.objects.get(name__iexact=system)
            except EveSolarSystem.DoesNotExist:
                await ctx.respond(
                    f"❌ Solar system '{system}' not found. "
                    "Please use the autocomplete suggestions.",
                    ephemeral=True,
                )
                return

            # Validate and get structure type
            try:
                structure_type_obj = EveType.objects.get(
                    name__iexact=structure_type, published=True
                )
            except EveType.DoesNotExist:
                await ctx.respond(
                    f"❌ Structure type '{structure_type}' not found. "
                    "Please use the autocomplete suggestions.",
                    ephemeral=True,
                )
                return

            # Calculate timer expiration date
            total_time = timedelta(days=days, hours=hours, minutes=minutes)

            if total_time.total_seconds() == 0:
                await ctx.respond("❌ Timer duration must be greater than 0.", ephemeral=True)
                return

            date = timezone.now() + total_time

            # Determine objective value
            if hasattr(Timer, "Objective"):
                objective_map = {}
                for choice in Timer.Objective.choices:
                    objective_map[choice[1].lower()] = choice[0]
                objective_value = objective_map.get(
                    objective.lower(),
                    Timer.Objective.HOSTILE if hasattr(Timer.Objective, "HOSTILE") else 2,
                )
            else:
                objective_map = {"friendly": 1, "hostile": 2, "neutral": 3}
                objective_value = objective_map.get(objective.lower(), 2)

            # Determine timer type value
            if hasattr(Timer, "Type"):
                type_map = {}
                for choice in Timer.Type.choices:
                    type_map[choice[1].lower()] = choice[0]
                timer_type_value = type_map.get(
                    timer_type.lower(), list(type_map.values())[0] if type_map else 1
                )
            else:
                # Use the string directly
                timer_type_value = timer_type

            # Build timer creation kwargs
            timer_kwargs = {
                "eve_solar_system": solar_system,
                "structure_type": structure_type_obj,
                "structure_name": structure_name or structure_type_obj.name,
                "owner_name": owner,
                "date": date,
                "location_details": location_details,
                "objective": objective_value,
                "details_notes": notes,
                "user": auth_user,
            }

            # Add timer_type if the field exists
            try:
                Timer._meta.get_field("timer_type")
                timer_kwargs["timer_type"] = timer_type_value
            except:
                # Field doesn't exist, skip it
                logger.debug("timer_type field doesn't exist in Timer model")
                pass

            # Create the timer
            timer = Timer.objects.create(**timer_kwargs)

            # Create success embed
            embed = discord.Embed(
                title="✅ Timer Created Successfully",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(name="System", value=solar_system.name, inline=True)
            embed.add_field(name="Structure", value=structure_type_obj.name, inline=True)
            embed.add_field(name="Type", value=timer_type, inline=True)
            embed.add_field(name="Owner", value=owner, inline=True)
            embed.add_field(name="Objective", value=objective.capitalize(), inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(date.timestamp())}:R>", inline=True)

            if structure_name:
                embed.add_field(name="Structure Name", value=structure_name, inline=False)

            if location_details:
                embed.add_field(name="Location Details", value=location_details, inline=False)

            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)

            embed.set_footer(text=f"Created by {ctx.author.display_name}")

            await ctx.respond(embed=embed)

            logger.info(
                f"Timer created by {ctx.author} ({auth_user.username}): "
                f"{system} - {structure_type} - {timer_type}"
            )

        except Exception as e:
            logger.error(f"Error creating timer: {e}", exc_info=True)
            await ctx.respond(
                f"❌ An error occurred while creating the timer: {str(e)}", ephemeral=True
            )

    @timer.command(name="list", description="List structure timers for a specific date")
    async def list_timers(
        self,
        ctx,
        date: Option(
            str,
            description=(
                "Date to show timers for (YYYY-MM-DD or YYYY.MM.DD format). "
                "Leave empty for today."
            ),
            required=False,
            default="",
        ),
    ):
        """
        List all timers for a specific date (defaults to today)
        """
        await ctx.defer()

        # Check permissions
        try:
            has_permission = await self.check_permissions(ctx)
            if not has_permission:
                allowed_channels = get_timer_channels()
                channel_mention = ""
                if allowed_channels:
                    channel_mention = f" in the designated timer channels"

                await ctx.respond(
                    "❌ You don't have permission to use this command." + channel_mention,
                    ephemeral=True,
                )
                return
        except Exception as e:
            logger.error(f"Error checking permissions: {e}", exc_info=True)
            await ctx.respond(
                "❌ An error occurred while checking permissions. "
                "Please contact an administrator.",
                ephemeral=True,
            )
            return

        try:
            # Parse the date parameter
            target_date = None
            if date:
                # Try to parse the date in various formats
                date_str = date.strip()
                for date_format in ["%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"]:
                    try:
                        parsed = datetime.strptime(date_str, date_format)
                        target_date = timezone.make_aware(parsed, timezone.get_current_timezone())
                        break
                    except ValueError:
                        continue

                if not target_date:
                    await ctx.respond(
                        "❌ Invalid date format. Please use YYYY-MM-DD or YYYY.MM.DD "
                        "format (e.g., 2025-11-14 or 2025.11.14)",
                        ephemeral=True,
                    )
                    return
            else:
                # Use today's date
                target_date = timezone.now()

            # Get start and end of the target day
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Query timers for this date range (exclude friendly timers)
            timers = (
                Timer.objects.filter(date__gte=start_of_day, date__lte=end_of_day)
                .select_related("eve_solar_system", "structure_type")
                .order_by("date")
            )

            # Filter out friendly timers (objective = 1)
            # Check if the Timer model has an Objective enum
            if hasattr(Timer, "Objective") and hasattr(Timer.Objective, "FRIENDLY"):
                timers = timers.exclude(objective=Timer.Objective.FRIENDLY)
            else:
                # Fallback: assume friendly = 1
                timers = timers.exclude(objective=1)

            if not timers.exists():
                date_display = start_of_day.strftime("%Y.%m.%d")
                await ctx.respond(
                    f"No timers found for **{date_display}**",
                    ephemeral=True,
                )
                return

            # Format the output
            date_display = start_of_day.strftime("%Y.%m.%d")
            output_lines = [f"**Current timers for {date_display}:**\n"]

            for timer in timers:
                # Get structure type name
                structure_name = timer.structure_type.name if timer.structure_type else "Unknown"

                # Get timer type if available
                timer_type_display = ""
                if hasattr(timer, "timer_type") and timer.timer_type:
                    if hasattr(Timer, "Type"):
                        # Get the display value from choices
                        try:
                            choice_value = dict(Timer.Type.choices).get(
                                timer.timer_type, str(timer.timer_type)
                            )
                            timer_type_display = f" - {choice_value}"
                        except:
                            timer_type_display = f" - {timer.timer_type}"
                    else:
                        timer_type_display = f" - {timer.timer_type}"

                # Build the owner/location info
                location_info = timer.owner_name if timer.owner_name else ""
                if timer.location_details:
                    location_info += f" - {timer.location_details}"

                # Format: Structure: System - Owner - Location -> Date Time or in X hours
                # Convert to UTC (EVE Time) for display
                timer_utc = (
                    timer.date.astimezone(dt_timezone.utc) if timer.date.tzinfo else timer.date
                )
                eve_time_str = timer_utc.strftime("%Y.%m.%d %H:%M:%S")

                # Discord relative timestamp (shows in user's local timezone automatically)
                timestamp_rel = f"<t:{int(timer.date.timestamp())}:R>"

                output_lines.append(
                    f"**{structure_name}**: {timer.eve_solar_system.name}"
                    f"{timer_type_display} -> {eve_time_str} ET or {timestamp_rel}"
                )

                if location_info:
                    output_lines.append(f"  _{location_info}_")

            # Split into multiple messages if too long
            full_message = "\n".join(output_lines)

            if len(full_message) <= 2000:
                await ctx.respond(full_message)
            else:
                # Split into chunks
                chunks = []
                current_chunk = output_lines[0] + "\n"

                for line in output_lines[1:]:
                    if len(current_chunk) + len(line) + 1 <= 2000:
                        current_chunk += line + "\n"
                    else:
                        chunks.append(current_chunk)
                        current_chunk = line + "\n"

                if current_chunk:
                    chunks.append(current_chunk)

                # Send first chunk as response
                await ctx.respond(chunks[0])

                # Send remaining chunks as follow-ups
                for chunk in chunks[1:]:
                    await ctx.send(chunk)

            logger.info(f"Timer list requested by {ctx.author} for date: {date_display}")

        except Exception as e:
            logger.error(f"Error listing timers: {e}", exc_info=True)
            await ctx.respond(
                f"❌ An error occurred while listing timers: {str(e)}", ephemeral=True
            )

    @timer.command(name="parse", description="Quick add timer from EVE Online reinforcement text")
    async def parse_timer(
        self,
        ctx,
        eve_text: Option(
            str,
            description="Paste EVE reinforcement text from target window",
            required=True,
        ),
        structure_type: Option(
            str,
            description="Type of structure (e.g., Astrahus, Fortizar, Keepstar)",
            required=True,
            autocomplete=structure_type_autocomplete,
        ),
        owner: Option(str, description="Owner corporation or alliance name", required=True),
        timer_type: Option(
            str,
            description="Timer type (e.g., Armor, Hull, Final)",
            required=True,
            autocomplete=timer_type_autocomplete,
        ),
        objective: Option(
            str,
            description="Objective: Friendly, Hostile, or Neutral",
            required=False,
            default="Hostile",
            autocomplete=objective_autocomplete,
        ),
        notes: Option(
            str, description="Additional notes about the timer", required=False, default=""
        ),
    ):
        """
        Parse EVE Online reinforcement text and create a timer
        """
        await ctx.defer()

        # Check permissions
        try:
            has_permission = await self.check_permissions(ctx)
            if not has_permission:
                allowed_channels = get_timer_channels()
                channel_mention = ""
                if allowed_channels:
                    channel_mention = " in the designated timer channels"

                await ctx.respond(
                    "❌ You don't have permission to use this command." + channel_mention,
                    ephemeral=True,
                )
                return
        except Exception as e:
            logger.error(f"Error checking permissions: {e}", exc_info=True)
            await ctx.respond(
                "❌ An error occurred while checking permissions. "
                "Please contact an administrator.",
                ephemeral=True,
            )
            return

        try:
            # Get authenticated user
            auth_user = None
            DiscordUser = None

            try:
                # Try to import DiscordUser model
                try:
                    from allianceauth.services.modules.discord.models import DiscordUser
                except ImportError:
                    # Fallback for different AllianceAuth versions
                    try:
                        from discord.models import DiscordUser
                    except ImportError as ie:
                        logger.error(f"Could not import DiscordUser model: {ie}")
                        await ctx.respond(
                            "❌ Discord integration not available. "
                            "Please contact your administrator.",
                            ephemeral=True,
                        )
                        return

                logger.info(
                    f"Looking up auth user for Discord ID: {ctx.author.id} ({ctx.author.name})"
                )

                # Get the Discord user from database
                discord_user = DiscordUser.objects.select_related("user").get(uid=ctx.author.id)
                auth_user = discord_user.user

                logger.info(
                    f"Successfully found auth user: {auth_user.username} (ID: {auth_user.id})"
                )

            except Exception as e:
                # Check if it's a DoesNotExist error
                if DiscordUser and e.__class__.__name__ == "DoesNotExist":
                    logger.warning(
                        f"No Discord link found for user {ctx.author.name} (ID: {ctx.author.id})"
                    )
                    await ctx.respond(
                        "❌ **Your Discord account is not linked to AllianceAuth.**\n\n"
                        "**To fix this:**\n"
                        "1. Visit your AllianceAuth website\n"
                        "2. Go to **Services**\n"
                        "3. Find **Discord** and click **Activate**\n"
                        "4. Complete the authorization\n"
                        "5. Try this command again\n\n"
                        f"Your Discord ID: `{ctx.author.id}`",
                        ephemeral=True,
                    )
                    return
                else:
                    logger.error(
                        f"Unexpected error looking up auth user for {ctx.author.id}: {e}",
                        exc_info=True,
                    )
                    await ctx.respond(
                        "❌ An error occurred while looking up your account. "
                        "Please contact an administrator.",
                        ephemeral=True,
                    )
                    return

            if not auth_user:
                logger.error(
                    f"Discord user found but no auth user linked for "
                    f"{ctx.author.name} (ID: {ctx.author.id})"
                )
                await ctx.respond(
                    "❌ Your Discord is linked but there's no associated user account. "
                    "Please contact an administrator.",
                    ephemeral=True,
                )
                return

            # Parse the EVE text
            # Extract first line which contains: "SYSTEM - ... - Structure Name"
            lines = eve_text.strip().split("\n")
            first_line = lines[0].strip() if lines else ""

            if not first_line:
                await ctx.respond(
                    "❌ Empty EVE text provided. Please paste the reinforcement text.",
                    ephemeral=True,
                )
                return

            # Extract system name from the first part (before " - " separator)
            # Example: "6U-MFQ - NF - Fort Enterprise" -> system: "6U-MFQ", rest: "NF - Fort Enterprise"
            # Example: "M-NP5O - VIII - 3 - For Sale" -> system: "M-NP5O", rest: "VIII - 3 - For Sale"
            # Split by " - " (space-dash-space) to preserve system names with dashes like "6U-MFQ"
            parts = first_line.split(" - ", 1)
            extracted_system = parts[0].strip() if parts else first_line

            # Use the extracted system name
            system_to_use = extracted_system

            # Validate the solar system against the database
            solar_system = None
            try:
                solar_system = EveSolarSystem.objects.get(name__iexact=system_to_use)
            except EveSolarSystem.DoesNotExist:
                # Try fuzzy match
                systems = EveSolarSystem.objects.filter(name__icontains=system_to_use)[:5]
                if systems.exists():
                    system_list = ", ".join([s.name for s in systems])
                    await ctx.respond(
                        f"❌ Solar system '{system_to_use}' not found. "
                        f"Did you mean: {system_list}?\n\n"
                        f"Extracted from text: `{extracted_system}`",
                        ephemeral=True,
                    )
                else:
                    await ctx.respond(
                        f"❌ Solar system '{system_to_use}' not found. "
                        "Please check the system name.\n\n"
                        f"Extracted from text: `{extracted_system}`",
                        ephemeral=True,
                    )
                return

            # Remove system name from structure name
            # If we found the system, remove it from the beginning of the first line
            structure_name = first_line
            if parts and len(parts) > 1 and solar_system.name.upper() == parts[0].strip().upper():
                # Remove the system name and the dash from the structure name
                structure_name = parts[1].strip()

            # Extract date/time from "Reinforced until YYYY.MM.DD HH:MM:SS" pattern
            # Pattern supports both dots and dashes in date
            date_pattern = (
                r"Reinforced until (\d{4})[.\-](\d{2})[.\-](\d{2})\s+(\d{2}):(\d{2}):(\d{2})"
            )
            date_match = re.search(date_pattern, eve_text, re.IGNORECASE)

            if not date_match:
                await ctx.respond(
                    "❌ Could not parse reinforcement date/time from the text.\n"
                    'Expected format: "Reinforced until YYYY.MM.DD HH:MM:SS"\n'
                    "Example: `Reinforced until 2025.11.16 03:50:50`",
                    ephemeral=True,
                )
                return

            # Extract date components
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            day = int(date_match.group(3))
            hour = int(date_match.group(4))
            minute = int(date_match.group(5))
            second = int(date_match.group(6))

            # Create datetime object (EVE time is UTC)
            try:
                date = datetime(year, month, day, hour, minute, second, tzinfo=dt_timezone.utc)
            except ValueError as ve:
                await ctx.respond(
                    f"❌ Invalid date/time values: {ve}\n"
                    f"Parsed: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}",
                    ephemeral=True,
                )
                return

            # Check if date is in the past
            if date < datetime.now(dt_timezone.utc):
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")
                await ctx.respond(
                    f"⚠️ Warning: The parsed date ({date_str} UTC) is in the past!",
                    ephemeral=True,
                )
                return

            # Validate and get structure type
            try:
                structure_type_obj = EveType.objects.get(
                    name__iexact=structure_type, published=True
                )
            except EveType.DoesNotExist:
                await ctx.respond(
                    f"❌ Structure type '{structure_type}' not found. "
                    "Please use the autocomplete suggestions.",
                    ephemeral=True,
                )
                return

            # Determine objective value
            if hasattr(Timer, "Objective"):
                objective_map = {}
                for choice in Timer.Objective.choices:
                    objective_map[choice[1].lower()] = choice[0]
                objective_value = objective_map.get(
                    objective.lower(),
                    (Timer.Objective.HOSTILE if hasattr(Timer.Objective, "HOSTILE") else 2),
                )
            else:
                objective_map = {"friendly": 1, "hostile": 2, "neutral": 3}
                objective_value = objective_map.get(objective.lower(), 2)

            # Determine timer type value
            if hasattr(Timer, "Type"):
                type_map = {}
                for choice in Timer.Type.choices:
                    type_map[choice[1].lower()] = choice[0]
                timer_type_value = type_map.get(
                    timer_type.lower(), list(type_map.values())[0] if type_map else 1
                )
            else:
                # Use the string directly
                timer_type_value = timer_type

            # Build timer creation kwargs
            timer_kwargs = {
                "eve_solar_system": solar_system,
                "structure_type": structure_type_obj,
                "structure_name": structure_name or structure_type_obj.name,
                "owner_name": owner,
                "date": date,
                "location_details": "",
                "objective": objective_value,
                "details_notes": notes,
                "user": auth_user,
            }

            # Add timer_type if the field exists
            try:
                Timer._meta.get_field("timer_type")
                timer_kwargs["timer_type"] = timer_type_value
            except:
                # Field doesn't exist, skip it
                logger.debug("timer_type field doesn't exist in Timer model")
                pass

            # Create the timer
            timer = Timer.objects.create(**timer_kwargs)

            # Create success embed
            embed = discord.Embed(
                title="✅ Timer Created from EVE Text",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(name="System", value=solar_system.name, inline=True)
            embed.add_field(name="Structure", value=structure_type_obj.name, inline=True)
            embed.add_field(name="Type", value=timer_type, inline=True)
            embed.add_field(name="Structure Name", value=structure_name, inline=False)
            embed.add_field(name="Owner", value=owner, inline=True)
            embed.add_field(name="Objective", value=objective.capitalize(), inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(date.timestamp())}:R>", inline=True)

            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)

            embed.set_footer(text=f"Created by {ctx.author.display_name}")

            await ctx.respond(embed=embed)

            logger.info(
                f"Timer parsed and created by {ctx.author} ({auth_user.username}): "
                f"{solar_system.name} - {structure_name} - {timer_type}"
            )

        except Exception as e:
            logger.error(f"Error parsing timer: {e}", exc_info=True)
            await ctx.respond(
                f"❌ An error occurred while parsing the timer: {str(e)}", ephemeral=True
            )


def setup(bot):
    """Setup function called by discord.py"""
    bot.add_cog(TimerCog(bot))
