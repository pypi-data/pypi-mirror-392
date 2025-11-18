# AA Timer Cog

A Discord bot extension for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) that adds the `/timer add` command to create structure timers directly from Discord.

## Features

- **Discord Slash Command**: Use `/timer add` to create structure timers
- **Autocomplete Support**: Smart autocomplete for solar systems, structure types, and timer types
- **Role-Based Permissions**: Configure which Discord roles can use the command
- **Channel Restrictions**: Optionally limit the command to specific channels
- **Full Integration**: Works seamlessly with [aa-structuretimers](https://gitlab.com/ErikKalkoken/aa-structuretimers)
- **Rich Embeds**: Beautiful Discord embeds for timer confirmation

## Requirements

- Alliance Auth >= 4.0.0
- [allianceauth-discordbot](https://github.com/Solar-Helix-Independent-Transport/allianceauth-discordbot) >= 3.0.0
- [aa-structuretimers](https://gitlab.com/ErikKalkoken/aa-structuretimers) >= 1.0.0
- py-cord >= 2.0.0

## Installation

### Step 1: Install the Package

**For manual installation (ZIP file):**

1. Extract the ZIP file to a temporary location
2. Navigate to the extracted directory
3. Activate your Alliance Auth virtual environment:
   ```bash
   source /home/allianceserver/venv/auth/bin/activate
   ```
4. Install the package:
   ```bash
   pip install .
   ```

**For future pip installation:**
```bash
pip install aa-timercog
```

### Step 2: Configure Alliance Auth

Add `'timercog'` to your `INSTALLED_APPS` in `local.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'timercog',
]
```

### Step 3: Configure Permissions (Optional but Recommended)

Add the following settings to your `local.py`:

```python
# Timer Cog Settings
# Discord Role IDs that can use the /timer add command
TIMERCOG_ALLOWED_ROLE_IDS = [
    123456789012345678,  # FC Role
    234567890123456789,  # Director Role
    # Add more role IDs as needed
]

# Discord Channel IDs where the command can be used (optional)
# If not set or empty, command works in all channels
TIMERCOG_ALLOWED_CHANNELS = [
    345678901234567890,  # timer-management channel
    # Add more channel IDs as needed
]
```

**How to get Discord IDs:**
1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on a role or channel and select "Copy ID"

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Restart Services

**For Docker:**
```bash
docker-compose restart allianceauth_discordbot
```

**For Supervisor (bare metal):**
```bash
supervisorctl restart myauth:authbot
```

## Usage

### Creating a Timer

Use the `/timer add` slash command in Discord with the following parameters:

**Required Parameters:**
- `system`: Solar system name (with autocomplete)
- `structure_type`: Type of structure (e.g., Astrahus, Fortizar, Keepstar) (with autocomplete)
- `owner`: Owner corporation or alliance name
- `timer_type`: Timer type (e.g., Armor, Hull, Final) (with autocomplete)

**Optional Parameters:**
- `days`: Days until timer expires (0-365)
- `hours`: Hours until timer expires (0-23)
- `minutes`: Minutes until timer expires (0-59)
- `structure_name`: Custom name for the structure
- `objective`: Friendly, Hostile, or Neutral (default: Hostile)
- `location_details`: Additional location info (e.g., "Planet VI, Moon 1")
- `notes`: Additional notes about the timer

### Example Commands

**Basic timer (1 hour):**
```
/timer add system:Jita structure_type:Astrahus owner:"Test Corp" timer_type:Hull hours:1
```

**Detailed timer (2 days, 3 hours, 30 minutes):**
```
/timer add system:Jita structure_type:Fortizar owner:"Test Alliance" timer_type:Final 
  days:2 hours:3 minutes:30 structure_name:"Death Star" 
  location_details:"Planet IV - Moon 4" objective:Hostile 
  notes:"Primary target, bring dreads"
```

## Permissions

Users must meet the following requirements to use the command:

1. **Discord Role**: Must have one of the roles specified in `TIMERCOG_ALLOWED_ROLE_IDS`
2. **Channel**: If `TIMERCOG_ALLOWED_CHANNELS` is set, command must be used in one of those channels
3. **Auth**: Must be authenticated with Alliance Auth

If permissions are denied, users will receive an ephemeral (private) error message.

## Troubleshooting

### Command not appearing in Discord

1. Make sure the bot has been restarted after installation
2. Verify that `'timercog'` is in `INSTALLED_APPS`
3. Check bot logs for any errors during startup

### "You don't have permission" error

1. Verify the user's Discord account is linked to Alliance Auth
2. Check that the user has the required role (if `TIMERCOG_ALLOWED_ROLE_IDS` is set)
3. Ensure the command is being used in an allowed channel (if `TIMERCOG_ALLOWED_CHANNELS` is set)

### Solar system or structure not found

1. Make sure `django-eveuniverse` data is loaded:
   ```bash
   python manage.py eveuniverse_load_types EveType --category_id 65
   python manage.py eveuniverse_load_types EveSolarSystem
   ```

### Check logs

Bot logs are typically at:
- Docker: `docker-compose logs allianceauth_discordbot`
- Supervisor: `/home/allianceserver/myauth/log/authbot.log`

## Development

### Project Structure

```
aa-timercog/
├── timercog/
│   ├── __init__.py
│   ├── apps.py
│   ├── auth_hooks.py
│   ├── cogs/
│   │   ├── __init__.py
│   │   └── timer_cog.py
│   └── migrations/
│       └── __init__.py
├── setup.py
├── README.md
└── LICENSE
```

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and feature requests, please:
- Open an issue on the GitHub repository
- Join the Alliance Auth Discord server

## License

This project is licensed under the MIT License.

## Credits

- Built for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
- Integrates with [aa-structuretimers](https://gitlab.com/ErikKalkoken/aa-structuretimers)
- Works with [allianceauth-discordbot](https://github.com/Solar-Helix-Independent-Transport/allianceauth-discordbot)
