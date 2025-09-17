# Production Guide - User Profiles

## Quick Start

### 1. Environment Setup
```bash
# Set profile via environment variable
export HEROES_PROFILE=ik    # or lisa

# Or let system auto-detect based on USER
# (ilyakrasinsky -> ik, lisa -> lisa)
```

### 2. Keychain Setup

#### For ik profile (ilyakrasinsky):
```bash
# Store keys as labels
security add-generic-password -l "ik_tg_api_id" -w "YOUR_API_ID"
security add-generic-password -l "ik_tg_api_hash" -w "YOUR_API_HASH"
security add-generic-password -l "ik_tg_session" -w "YOUR_SESSION"
security add-generic-password -l "ik_tg_phone" -w "YOUR_PHONE"
```

#### For lisa profile:
```bash
# Store keys as services with account
security add-generic-password -s "lisa_tg_api_key" -a "lisa" -w "YOUR_API_ID"
security add-generic-password -s "lisa_tg_app_hash" -a "lisa" -w "YOUR_API_HASH"
security add-generic-password -s "lisa_tg_session" -a "lisa" -w "YOUR_SESSION"
security add-generic-password -s "lisa_tg_phone" -a "lisa" -w "YOUR_PHONE"
```

### 3. Usage in Code
```python
from credentials_manager import credentials_manager

# Auto-detect profile
print(f"Current profile: {credentials_manager.get_current_profile()}")

# Get credentials
api_id = credentials_manager.get_credential('telegram_api_id')
api_hash = credentials_manager.get_credential('telegram_api_hash')

# Switch profile if needed
credentials_manager.set_profile('lisa')
```

## Troubleshooting

### Profile Not Detected
1. Check environment variables:
   ```bash
   echo $HEROES_PROFILE
   echo $USER
   ```

2. Check keychain access:
   ```bash
   # For ik profile
   security find-generic-password -l "ik_tg_api_id" -w
   
   # For lisa profile
   security find-generic-password -s "lisa_tg_api_key" -a "lisa" -w
   ```

### Permission Errors
1. Grant keychain access to your IDE/terminal
2. Check keychain item permissions
3. Verify account names match exactly

### Wrong Keys Retrieved
1. Verify profile is set correctly
2. Check key naming convention
3. Ensure correct keychain storage format

## Adding New Profile

1. **Add profile detection logic** in `_detect_current_profile()`
2. **Add key mapping** in `_setup_default_configs()`
3. **Add keychain access logic** in `_get_from_keychain()`
4. **Update documentation** and tests

## Monitoring

### Logs to Watch
- Profile detection: `Detected [profile] profile`
- Profile switching: `Switched to profile: [profile]`
- Keychain access errors: `Error getting from keychain`

### Health Checks
```python
# Check profile system health
def health_check():
    manager = CredentialsManager()
    
    # Test current profile
    profile = manager.get_current_profile()
    assert profile in ['ik', 'lisa']
    
    # Test credential access
    result = manager.get_credential('telegram_api_id')
    assert result.success, f"Failed to get API ID: {result.error}"
    
    return True
```
