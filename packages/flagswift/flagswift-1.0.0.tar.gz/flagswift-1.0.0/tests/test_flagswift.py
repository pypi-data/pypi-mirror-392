"""
Test script for FlagSwift Python SDK
Run this to verify your installation
"""

from flagswift import FlagSwift

def test_basic():
    """Basic test with your API key"""
    
    # Replace with your actual API key
    API_KEY = 'sk_live_your_api_key_here'
    
    # Initialize client
    print("🚀 Initializing FlagSwift...")
    flags = FlagSwift(
        api_key=API_KEY,
        environment='staging'  # or 'production'
    )
    
    # Get status
    status = flags.get_status()
    print(f"📊 Status: {status}")
    
    # Check a flag
    print("\n🔍 Checking flag 'show-cta'...")
    
    # Without user
    is_enabled = flags.is_enabled('show-cta')
    print(f"   Without user: {is_enabled}")
    
    # With user
    is_enabled_user = flags.is_enabled('show-cta', user_id='user-mane')
    print(f"   With user-mane: {is_enabled_user}")
    
    # With different user
    is_enabled_other = flags.is_enabled('show-cta', user_id='random-user')
    print(f"   With random-user: {is_enabled_other}")
    
    # Get all flags
    print("\n📋 All flags:")
    all_flags = flags.get_all_flags()
    for flag_name, enabled in all_flags.items():
        print(f"   {flag_name}: {enabled}")
    
    # Get detailed config
    print("\n⚙️  Detailed config for 'show-cta':")
    config = flags.get_flag_config('show-cta')
    print(f"   {config}")
    
    print("\n✅ Test complete!")


def test_kill_switch():
    """Test kill switch functionality"""
    
    API_KEY = 'sk_live_your_api_key_here'
    
    flags = FlagSwift(
        api_key=API_KEY,
        environment='staging'
    )
    
    print("\n🚨 Testing Kill Switch...")
    
    # Check current state
    print("1. Current state:")
    print(f"   show-cta enabled: {flags.is_enabled('show-cta', user_id='user-mane')}")
    
    # Activate kill switch
    print("\n2. Activating kill switch...")
    try:
        response = flags.activate_kill_switch(
            flags=['show-cta'],
            environments=['staging']
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check after activation
    print("\n3. After kill switch activation:")
    print(f"   show-cta enabled: {flags.is_enabled('show-cta', user_id='user-mane')}")
    print(f"   Kill switch active: {flags.is_kill_switch_enabled()}")
    
    # Deactivate kill switch
    print("\n4. Deactivating kill switch...")
    try:
        response = flags.deactivate_kill_switch(
            flags=['show-cta'],
            environments=['staging']
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check after deactivation
    print("\n5. After kill switch deactivation:")
    print(f"   show-cta enabled: {flags.is_enabled('show-cta', user_id='user-mane')}")
    print(f"   Kill switch active: {flags.is_kill_switch_enabled()}")
    
    print("\n✅ Kill switch test complete!")


if __name__ == '__main__':
    print("=" * 60)
    print("FlagSwift Python SDK Test")
    print("=" * 60)
    
    # Run basic test
    test_basic()
    
    # Uncomment to test kill switch
    # test_kill_switch()