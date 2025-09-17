#!/usr/bin/env python3
"""
Test script for Potpie integration with Heroes Platform
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add heroes_platform to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class PotpieIntegrationTester:
    def __init__(self):
        self.heroes_api_url = "http://localhost:8000"
        self.potpie_api_url = "http://localhost:8001"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_heroes_platform_health(self):
        """Test Heroes Platform health endpoint"""
        try:
            async with self.session.get(f"{self.heroes_api_url}/health") as response:
                if response.status == 200:
                    print("✅ Heroes Platform API is healthy")
                    return True
                else:
                    print(f"❌ Heroes Platform API health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Heroes Platform API connection failed: {e}")
            return False

    async def test_potpie_health(self):
        """Test Potpie health endpoint"""
        try:
            async with self.session.get(f"{self.potpie_api_url}/health") as response:
                if response.status == 200:
                    print("✅ Potpie API is healthy")
                    return True
                else:
                    print(f"❌ Potpie API health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Potpie API connection failed: {e}")
            return False

    async def test_potpie_available_agents(self):
        """Test Potpie available agents endpoint"""
        try:
            async with self.session.get(f"{self.potpie_api_url}/api/v1/list-available-agents/?list_system_agents=true") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Potpie available agents: {len(data.get('agents', []))} agents found")
                    return True
                else:
                    print(f"❌ Potpie available agents check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Potpie available agents check failed: {e}")
            return False

    async def test_database_connections(self):
        """Test database connections"""
        # Test Heroes Platform database
        try:
            # This would require a database health endpoint in Heroes Platform
            print("⚠️  Heroes Platform database health check not implemented")
        except Exception as e:
            print(f"❌ Heroes Platform database check failed: {e}")

        # Test Potpie database
        try:
            async with self.session.get(f"{self.potpie_api_url}/api/v1/health") as response:
                if response.status == 200:
                    print("✅ Potpie database connection is healthy")
                    return True
                else:
                    print(f"❌ Potpie database health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Potpie database check failed: {e}")
            return False

    async def test_integration_workflow(self):
        """Test basic integration workflow"""
        print("\n🔄 Testing integration workflow...")
        
        # 1. Test Heroes Platform MCP tools
        try:
            from heroes_platform.heroes_mcp.src.heroes_mcp_server import HeroesMCPServer
            print("✅ Heroes Platform MCP server can be imported")
        except Exception as e:
            print(f"❌ Heroes Platform MCP server import failed: {e}")
            return False

        # 2. Test Potpie API endpoints
        try:
            async with self.session.get(f"{self.potpie_api_url}/api/v1/") as response:
                if response.status == 200:
                    print("✅ Potpie API root endpoint accessible")
                else:
                    print(f"❌ Potpie API root endpoint failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Potpie API root endpoint failed: {e}")
            return False

        return True

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Potpie Integration Tests...\n")
        
        tests = [
            ("Heroes Platform Health", self.test_heroes_platform_health),
            ("Potpie Health", self.test_potpie_health),
            ("Potpie Available Agents", self.test_potpie_available_agents),
            ("Database Connections", self.test_database_connections),
            ("Integration Workflow", self.test_integration_workflow),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Integration is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the configuration.")
            return False

async def main():
    """Main test function"""
    async with PotpieIntegrationTester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
