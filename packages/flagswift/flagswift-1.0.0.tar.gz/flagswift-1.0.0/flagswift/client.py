"""
FlagSwift Client - Main SDK implementation
"""

import requests
from typing import Optional, List, Union, Dict
from dataclasses import dataclass, field
from .exceptions import FlagSwiftError, AuthenticationError, NetworkError


@dataclass
class FlagSwiftConfig:
    """Configuration for FlagSwift client"""
    api_key: str
    environment: str = 'production'
    base_url: str = 'https://flagswift.com'
    timeout: int = 5
    cache_timeout: int = 300  
    max_retries: int = 3
    failsafe_fallbacks: Dict[str, bool] = field(default_factory=dict)
    kill_switch_fallbacks: Dict[str, bool] = field(default_factory=dict)
    global_identifier: Optional[Union[str, List[str]]] = None


class FlagSwift:
    """
    FlagSwift Python Client
    
    Examples:
        Basic usage:
        >>> flags = FlagSwift(api_key='sk_live_your_key')
        >>> if flags.is_enabled('new-feature', user_id='user-123'):
        ...     # Use new feature
        ...     pass
        
        With configuration:
        >>> config = FlagSwiftConfig(
        ...     api_key='sk_live_your_key',
        ...     environment='staging',
        ...     failsafe_fallbacks={'new-feature': True}
        ... )
        >>> flags = FlagSwift.from_config(config)
    """
    
    def __init__(
        self,
        api_key: str,
        environment: str = 'production',
        base_url: str = 'https://flagswift.com',
        timeout: int = 5,
        cache_timeout: int = 300,
        max_retries: int = 3,
        failsafe_fallbacks: Optional[Dict[str, bool]] = None,
        kill_switch_fallbacks: Optional[Dict[str, bool]] = None,
        global_identifier: Optional[Union[str, List[str]]] = None
    ):
        """
        Initialize FlagSwift client
        
        Args:
            api_key: Your FlagSwift server API key (starts with sk_live_ or sk_test_)
            environment: Environment name (default: 'production')
            base_url: FlagSwift API base URL (default: 'https://flagswift.com')
            timeout: Request timeout in seconds (default: 5)
            cache_timeout: Cache validity in seconds (default: 300)
            max_retries: Maximum retry attempts (default: 3)
            failsafe_fallbacks: Default values when API is unavailable
            kill_switch_fallbacks: Values to use when kill switch is active
            global_identifier: Global user identifier for all flag checks
        """
        self.api_key = api_key
        self.environment = environment
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.cache_timeout = cache_timeout
        self.max_retries = max_retries
        self.failsafe_fallbacks = failsafe_fallbacks or {}
        self.kill_switch_fallbacks = kill_switch_fallbacks or {}
        self.global_identifier = global_identifier
        
        self._cache: Dict[str, dict] = {}
        self._cache_timestamp: Optional[float] = None
        self._is_initialized = False
        self._is_kill_switch_active = False
        
    @classmethod
    def from_config(cls, config: FlagSwiftConfig) -> 'FlagSwift':
        """Create client from configuration object"""
        return cls(
            api_key=config.api_key,
            environment=config.environment,
            base_url=config.base_url,
            timeout=config.timeout,
            cache_timeout=config.cache_timeout,
            max_retries=config.max_retries,
            failsafe_fallbacks=config.failsafe_fallbacks,
            kill_switch_fallbacks=config.kill_switch_fallbacks,
            global_identifier=config.global_identifier
        )
    
    def initialize(self) -> None:
        """
        Initialize the SDK by fetching flags
        
        Raises:
            FlagSwiftError: If initialization fails
        """
        self._fetch_flags()
        self._is_initialized = True
    
    def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[Union[str, List[str]]] = None
    ) -> bool:
        """
        Check if a feature flag is enabled
        
        Args:
            flag_name: Name of the flag to check
            user_id: Optional user ID(s) for targeting
        
        Returns:
            True if flag is enabled, False otherwise
        
        Examples:
            >>> flags.is_enabled('new-feature')
            True
            >>> flags.is_enabled('beta-feature', user_id='user-123')
            False
            >>> flags.is_enabled('test-flag', user_id=['user-1', 'user-2'])
            True
        """
        # Use global identifier if no user_id provided
        effective_user_id = user_id or self.global_identifier
        
        # Handle kill switch
        if self._is_kill_switch_active:
            return self.kill_switch_fallbacks.get(flag_name, False)
        
        # Fetch flags if cache is empty or expired
        if not self._is_cache_valid():
            try:
                self._fetch_flags(effective_user_id)
            except FlagSwiftError:
                # Use fallback if fetch fails
                return self.failsafe_fallbacks.get(flag_name, False)
        
        # Get flag from cache
        flag = self._cache.get(flag_name, {})
        
        if not flag:
            return self.failsafe_fallbacks.get(flag_name, False)
        
        # Check if flag is enabled
        if not flag.get('enabled', False):
            return False
        
        # Check user targeting
        targeting = flag.get('targeting')
        if targeting and targeting.get('enabled'):
            target_users = targeting.get('users', [])
            
            if target_users:
                if not effective_user_id:
                    return False
                
                # Handle both string and list user IDs
                user_ids = [effective_user_id] if isinstance(effective_user_id, str) else effective_user_id
                
                # Check if any user ID is in target list
                if not any(uid in target_users for uid in user_ids):
                    return False
        
        # Check rollout percentage
        rollout = flag.get('rolloutPercentage', 100)
        if rollout < 100 and effective_user_id:
            uid = effective_user_id[0] if isinstance(effective_user_id, list) else effective_user_id
            if not self._is_in_rollout(flag_name, uid, rollout):
                return False
        
        return True
    
    def get_all_flags(self) -> Dict[str, bool]:
        """
        Get all flags as a dictionary
        
        Returns:
            Dict mapping flag names to enabled status
        """
        if self._is_kill_switch_active:
            return {}
        
        if not self._is_cache_valid():
            self._fetch_flags()
        
        return {
            name: flag.get('enabled', False)
            for name, flag in self._cache.items()
        }
    
    def get_flag_config(self, flag_name: str) -> Optional[Dict]:
        """
        Get detailed flag configuration
        
        Args:
            flag_name: Name of the flag
        
        Returns:
            Flag configuration dict or None if not found
        """
        if self._is_kill_switch_active:
            return None
        
        if not self._is_cache_valid():
            self._fetch_flags()
        
        return self._cache.get(flag_name)
    
    def refresh(self, user_id: Optional[Union[str, List[str]]] = None) -> None:
        """
        Force refresh flags from server
        
        Args:
            user_id: Optional user ID(s) for targeting
        """
        self._cache = {}
        self._cache_timestamp = None
        self._fetch_flags(user_id)
    
    def activate_kill_switch(
        self,
        flags: Union[str, List[str]],
        environments: Optional[Union[str, List[str]]] = None
    ) -> Dict:
        """
        Activate kill switch to disable flags immediately
        
        Args:
            flags: Flag name(s) to disable
            environments: Environment(s) to affect (None for all)
        
        Returns:
            Response from server
        
        Raises:
            FlagSwiftError: If kill switch activation fails
        """
        flags_array = [flags] if isinstance(flags, str) else flags
        environments_array = None
        if environments:
            environments_array = [environments] if isinstance(environments, str) else environments
        
        self._is_kill_switch_active = True
        
        try:
            response = requests.post(
                f'{self.base_url}/api/flags/kill-switch',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'action': 'activate',
                    'flags': flags_array,
                    'environments': environments_array
                },
                timeout=self.timeout
            )
            
            if not response.ok:
                raise FlagSwiftError(f'Kill switch activation failed: {response.text}')
            
            # Refresh flags after kill switch
            self.refresh()
            
            return response.json()
        except requests.RequestException as e:
            raise NetworkError(f'Network error during kill switch activation: {str(e)}')
    
    def deactivate_kill_switch(
        self,
        flags: Union[str, List[str]],
        environments: Optional[Union[str, List[str]]] = None
    ) -> Dict:
        """
        Deactivate kill switch and restore flags
        
        Args:
            flags: Flag name(s) to restore
            environments: Environment(s) to affect (None for all)
        
        Returns:
            Response from server
        
        Raises:
            FlagSwiftError: If kill switch deactivation fails
        """
        flags_array = [flags] if isinstance(flags, str) else flags
        environments_array = None
        if environments:
            environments_array = [environments] if isinstance(environments, str) else environments
        
        try:
            response = requests.post(
                f'{self.base_url}/api/flags/kill-switch',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'action': 'deactivate',
                    'flags': flags_array,
                    'environments': environments_array
                },
                timeout=self.timeout
            )
            
            if not response.ok:
                raise FlagSwiftError(f'Kill switch deactivation failed: {response.text}')
            
            # Refresh flags after kill switch
            self.refresh()
            self._is_kill_switch_active = False
            
            return response.json()
        except requests.RequestException as e:
            raise NetworkError(f'Network error during kill switch deactivation: {str(e)}')
    
    def is_kill_switch_enabled(self) -> bool:
        """Check if kill switch is active"""
        return self._is_kill_switch_active
    
    def get_status(self) -> Dict:
        """
        Get SDK status information
        
        Returns:
            Dict with SDK status details
        """
        return {
            'initialized': self._is_initialized,
            'flag_count': len(self._cache),
            'environment': self.environment,
            'kill_switch_active': self._is_kill_switch_active,
            'cache_valid': self._is_cache_valid()
        }
    
    def _fetch_flags(self, user_id: Optional[Union[str, List[str]]] = None) -> None:
        """Internal method to fetch flags from FlagSwift API"""
        effective_user_id = user_id or self.global_identifier
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                url = f'{self.base_url}/api/flags/server'
                params = {'env': self.environment}
                
                # Add user identifiers if provided
                if effective_user_id:
                    user_ids = [effective_user_id] if isinstance(effective_user_id, str) else effective_user_id
                    for idx, uid in enumerate(user_ids):
                        params[f'user_identifier_{idx}'] = uid
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 401:
                    raise AuthenticationError('Invalid API key')
                
                response.raise_for_status()
                
                self._cache = response.json()
                import time
                self._cache_timestamp = time.time()
                return
                
            except requests.exceptions.Timeout:
                last_error = NetworkError(f'Request timeout (attempt {attempt + 1}/{self.max_retries})')
            except requests.exceptions.RequestException as e:
                last_error = NetworkError(f'Network error: {str(e)}')
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                import time
                time.sleep(2 ** attempt)
        
        # If all retries failed, raise the last error
        if last_error:
            raise last_error
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache or self._cache_timestamp is None:
            return False
        
        import time
        return (time.time() - self._cache_timestamp) < self.cache_timeout
    
    def _is_in_rollout(self, flag_name: str, user_id: str, percentage: int) -> bool:
        """Check if user is in rollout percentage using consistent hashing"""
        combined = f"{user_id}:{flag_name}:{self.environment}"
        hash_value = sum(ord(c) for c in combined)
        bucket = hash_value % 100
        return bucket < percentage