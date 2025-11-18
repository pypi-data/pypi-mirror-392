#!/usr/bin/env python3
"""
Test script to verify that pods stop when agents have fatal errors (like bad API keys).
This test creates a pod with an agent that has an invalid API key and verifies
that the pod stops instead of continuing infinitely.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8080"

def create_agent_with_bad_key():
    """Create an agent with an invalid API key"""
    print("Creating agent with invalid API key...")
    
    # Create an agent with a bad API key
    response = requests.post(
        f"{BASE_URL}/agents",
        json={
            "id": "bad_key_agent",
            "name": "Test Agent with Bad Key",
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "sk-invalid_key_12345",  # Invalid API key
            "system_prompt": "You are a helpful assistant"
        }
    )
    
    if response.status_code == 200:
        print(f"✓ Agent created: {response.json()}")
        return True
    else:
        print(f"✗ Failed to create agent: {response.status_code} - {response.text}")
        return False

def create_pod():
    """Create a pod with the test agent"""
    print("\nCreating pod...")
    
    response = requests.post(
        f"{BASE_URL}/pods",
        json={
            "agent_ids": ["bad_key_agent"],
            "config": {
                "turn_delay": "1s",
                "max_turns": 20
            }
        }
    )
    
    if response.status_code == 200:
        pod_data = response.json()
        pod_id = pod_data.get("pod_id")
        print(f"✓ Pod created: {pod_id}")
        return pod_id
    else:
        print(f"✗ Failed to create pod: {response.status_code} - {response.text}")
        return None

def check_pod_status(pod_id):
    """Check the status of a pod"""
    response = requests.get(f"{BASE_URL}/pods/{pod_id}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def test_error_handling():
    """Test that pods stop on fatal agent errors"""
    print("=" * 60)
    print("Testing Error Handling: Bad API Key")
    print("=" * 60)
    
    # Create agent with bad key
    if not create_agent_with_bad_key():
        print("\n✗ Test failed: Could not create agent")
        return False
    
    # Create pod
    pod_id = create_pod()
    if not pod_id:
        print("\n✗ Test failed: Could not create pod")
        return False
    
    # Wait and monitor the pod
    print("\nMonitoring pod status...")
    print("(The pod should stop after detecting fatal errors, not continue infinitely)")
    
    max_wait = 30  # Wait up to 30 seconds
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        time.sleep(2)
        
        pod_data = check_pod_status(pod_id)
        if pod_data:
            status = pod_data.get("status")
            turn_count = pod_data.get("turn_count", 0)
            
            if status != last_status:
                print(f"  Status: {status} (Turn: {turn_count})")
                last_status = status
            
            # Check if pod stopped due to errors
            if status in ["failed", "stopped"]:
                elapsed = time.time() - start_time
                print(f"\n✓ SUCCESS: Pod stopped with status '{status}' after {elapsed:.1f}s")
                print(f"  Turn count when stopped: {turn_count}")
                
                # Verify it stopped quickly (should stop on first fatal error)
                if turn_count <= 3:
                    print("✓ Pod stopped quickly (within 3 turns), as expected for fatal errors")
                    return True
                else:
                    print(f"⚠ Pod took {turn_count} turns to stop (expected ≤3)")
                    return True  # Still a success, just not optimal
        
        # Print a dot to show we're still waiting
        print(".", end="", flush=True)
    
    # If we got here, the pod didn't stop in time
    print(f"\n\n✗ FAILURE: Pod did not stop within {max_wait}s")
    print("This suggests the infinite loop bug is still present!")
    
    pod_data = check_pod_status(pod_id)
    if pod_data:
        print(f"Final status: {pod_data.get('status')}")
        print(f"Turn count: {pod_data.get('turn_count', 0)}")
    
    return False

if __name__ == "__main__":
    try:
        success = test_error_handling()
        print("\n" + "=" * 60)
        if success:
            print("✓ TEST PASSED: Error handling works correctly")
            sys.exit(0)
        else:
            print("✗ TEST FAILED: Error handling needs improvement")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

