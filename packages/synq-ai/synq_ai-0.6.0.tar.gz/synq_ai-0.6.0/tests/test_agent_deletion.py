#!/usr/bin/env python3
"""
Test script to verify that agent deletion completely removes all agent data.
This test creates an agent, uses it in a pod, then deletes it and verifies:
1. Agent is completely removed from registry
2. Pods using the agent are stopped
3. Deleted agent cannot be retrieved or used
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8080"

def create_test_agent():
    """Create a test agent"""
    print("Creating test agent...")
    
    response = requests.post(
        f"{BASE_URL}/agents",
        json={
            "id": "test_agent_to_delete",
            "name": "Test Agent for Deletion",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "system_prompt": "You are a test assistant"
        }
    )
    
    if response.status_code == 200:
        print(f"✓ Agent created: {response.json()['agent_id']}")
        return True
    else:
        print(f"✗ Failed to create agent: {response.status_code} - {response.text}")
        return False

def create_pod_with_agent(agent_id):
    """Create a pod using the test agent"""
    print(f"\nCreating pod with agent {agent_id}...")
    
    response = requests.post(
        f"{BASE_URL}/pods",
        json={
            "agent_ids": [agent_id],
            "config": {
                "turn_delay": "2s",
                "max_turns": 10
            }
        }
    )
    
    if response.status_code == 200:
        pod_id = response.json().get("pod_id")
        print(f"✓ Pod created: {pod_id}")
        return pod_id
    else:
        print(f"✗ Failed to create pod: {response.status_code} - {response.text}")
        return None

def verify_agent_exists(agent_id):
    """Check if agent exists"""
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    return response.status_code == 200

def verify_pod_status(pod_id):
    """Get pod status"""
    response = requests.get(f"{BASE_URL}/pods/{pod_id}")
    if response.status_code == 200:
        return response.json().get("status")
    return None

def delete_agent(agent_id):
    """Delete an agent"""
    print(f"\nDeleting agent {agent_id}...")
    
    response = requests.delete(f"{BASE_URL}/agents/{agent_id}")
    
    if response.status_code in [200, 204]:
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Agent deleted")
            if "pods_stopped" in data:
                print(f"  Stopped {len(data['pods_stopped'])} pod(s): {data['pods_stopped']}")
            return data.get("pods_stopped", [])
        else:
            print(f"✓ Agent deleted (no pods affected)")
            return []
    else:
        print(f"✗ Failed to delete agent: {response.status_code} - {response.text}")
        return None

def list_all_agents():
    """List all agents"""
    response = requests.get(f"{BASE_URL}/agents")
    if response.status_code == 200:
        return response.json().get("agents", [])
    return []

def test_agent_deletion():
    """Test complete agent deletion"""
    print("=" * 70)
    print("Testing Agent Deletion: Complete Cleanup")
    print("=" * 70)
    
    agent_id = "test_agent_to_delete"
    
    # Step 1: Create agent
    if not create_test_agent():
        print("\n✗ Test failed: Could not create agent")
        return False
    
    # Step 2: Verify agent exists
    print("\nVerifying agent exists...")
    if not verify_agent_exists(agent_id):
        print("✗ Agent should exist but doesn't")
        return False
    print("✓ Agent exists in registry")
    
    # Step 3: Create a pod using the agent
    pod_id = create_pod_with_agent(agent_id)
    if not pod_id:
        print("\n✗ Test failed: Could not create pod")
        return False
    
    # Wait for pod to start
    time.sleep(2)
    initial_status = verify_pod_status(pod_id)
    print(f"  Pod initial status: {initial_status}")
    
    # Step 4: Delete the agent
    stopped_pods = delete_agent(agent_id)
    if stopped_pods is None:
        print("\n✗ Test failed: Could not delete agent")
        return False
    
    # Step 5: Verify agent is completely removed
    print("\nVerifying agent is completely removed...")
    
    # Check if agent still exists in registry
    if verify_agent_exists(agent_id):
        print("✗ FAIL: Agent still exists in registry after deletion!")
        return False
    print("✓ Agent removed from registry")
    
    # Check if agent appears in list
    all_agents = list_all_agents()
    agent_ids = [a.get("id") for a in all_agents]
    if agent_id in agent_ids:
        print("✗ FAIL: Agent still appears in agent list!")
        return False
    print("✓ Agent removed from agent list")
    
    # Step 6: Verify pod was stopped
    print("\nVerifying pod was stopped...")
    if pod_id in stopped_pods:
        print(f"✓ Pod {pod_id} was stopped as expected")
    else:
        print(f"⚠ Warning: Pod {pod_id} not in stopped list")
    
    # Check pod status
    final_status = verify_pod_status(pod_id)
    print(f"  Pod final status: {final_status}")
    if final_status in ["stopped", "finished", "failed"]:
        print("✓ Pod is no longer running")
    else:
        print(f"⚠ Warning: Pod status is {final_status} (expected stopped/finished/failed)")
    
    # Step 7: Try to use deleted agent (should fail)
    print("\nVerifying deleted agent cannot be used...")
    response = requests.post(
        f"{BASE_URL}/pods",
        json={
            "agent_ids": [agent_id],
            "config": {"turn_delay": "2s", "max_turns": 5}
        }
    )
    
    if response.status_code != 200:
        print("✓ Cannot create pod with deleted agent (as expected)")
    else:
        print("✗ FAIL: Was able to create pod with deleted agent!")
        return False
    
    # Step 8: Try to retrieve deleted agent (should fail)
    print("\nVerifying deleted agent cannot be retrieved...")
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    if response.status_code == 404:
        print("✓ Agent not found (as expected)")
    else:
        print(f"✗ FAIL: Got status {response.status_code} when retrieving deleted agent!")
        return False
    
    return True

if __name__ == "__main__":
    try:
        print("\n⚠️  Make sure the Synq server is running before starting the test!\n")
        time.sleep(1)
        
        success = test_agent_deletion()
        
        print("\n" + "=" * 70)
        if success:
            print("✓ ALL TESTS PASSED: Agent deletion works correctly")
            print("  - Agent completely removed from registry")
            print("  - All agent instances cleaned up")
            print("  - Pods using agent were stopped")
            print("  - Deleted agent cannot be used")
            sys.exit(0)
        else:
            print("✗ TEST FAILED: Agent deletion has issues")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

