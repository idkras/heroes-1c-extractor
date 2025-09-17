# User Profiles System

## Overview

The credentials manager supports multiple user profiles to handle different Telegram accounts and API keys.

## Supported Profiles

### `ik` Profile (Default)
- **User**: ilyakrasinsky
- **Keys**: `ik_tg_*` (stored as labels in keychain)
- **Access Method**: `security find-generic-password -l "ik_tg_*" -w`

### `lisa` Profile
- **User**: lisa
- **Keys**: `lisa_tg_*` (stored as services in keychain)
- **Access Method**: `security find-generic-password -s "lisa_tg_*" -a "lisa" -w`

## Profile Detection Logic

The system automatically detects the active profile using this priority:

1. **Environment Variable**: `HEROES_PROFILE` (highest priority)
2. **Current User**: Based on `USER` environment variable
3. **Keychain Check**: Tests which keys are available
4. **Default**: Falls back to `ik` profile

## Usage Examples

### Automatic Detection
```python
from credentials_manager import credentials_manager

# System automatically detects profile
print(f"Current profile: {credentials_manager.get_current_profile()}")
```

### Manual Profile Switching
```python
# Switch to lisa profile
credentials_manager.set_profile('lisa')

# Switch back to ik profile
credentials_manager.set_profile('ik')
```

### Environment Variable Override
```bash
# Force lisa profile
export HEROES_PROFILE=lisa

# Force ik profile
export HEROES_PROFILE=ik
```

## Key Mapping

| Credential | ik Profile Key | lisa Profile Key |
|------------|----------------|------------------|
| telegram_api_id | ik_tg_api_id | lisa_tg_api_key |
| telegram_api_hash | ik_tg_api_hash | lisa_tg_app_hash |
| telegram_session | ik_tg_session | lisa_tg_session |
| telegram_phone | ik_tg_phone | lisa_tg_phone |

## Keychain Storage Differences

### ik Profile Keys
- Stored as **labels** in keychain
- Accessed with `-l` flag
- No account specified

### lisa Profile Keys
- Stored as **services** in keychain
- Accessed with `-s` flag and `-a lisa`
- Account field set to "lisa"

## Testing

```python
# Test current profile
result = credentials_manager.get_credential('telegram_api_id')
print(f"API ID: {result.value}")

# Test profile switching
credentials_manager.set_profile('lisa')
result = credentials_manager.get_credential('telegram_api_id')
print(f"Lisa API ID: {result.value}")
```

## Troubleshooting

### Profile Not Detected
- Check if keys exist in keychain
- Verify environment variables
- Check key naming convention

### Wrong Keys Retrieved
- Verify profile is set correctly
- Check keychain permissions
- Ensure correct key names are used

### Permission Errors
- Grant keychain access to terminal/IDE
- Check keychain item permissions
- Verify account names match
