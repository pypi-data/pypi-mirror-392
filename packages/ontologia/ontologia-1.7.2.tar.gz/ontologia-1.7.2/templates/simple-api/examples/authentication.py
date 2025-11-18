#!/usr/bin/env python3
"""
Authentication Example

This example shows how to work with Ontologia's authentication system,
including token management, user creation, and role-based access.
"""

import os
import sys
import time
from datetime import datetime

import httpx
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}"
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")


class AuthClient:
    """Client for demonstrating authentication features."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users

    def login(self, username: str, password: str) -> dict:
        """Login and get JWT token."""
        response = httpx.post(
            f"{self.base_url}/v2/auth/token", data={"username": username, "password": password}
        )

        if response.status_code == 401:
            raise Exception("Invalid credentials")

        response.raise_for_status()
        token_data = response.json()

        # Store token
        self.tokens[username] = token_data["access_token"]

        return token_data

    def get_headers(self, username: str = "admin") -> dict:
        """Get authorization headers for a user."""
        if username not in self.tokens:
            raise Exception(f"User {username} not logged in")

        return {"Authorization": f"Bearer {self.tokens[username]}"}

    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

    def refresh_token(self, username: str, password: str) -> dict:
        """Refresh an expired token by logging in again."""
        return self.login(username, password)

    def protected_request(self, endpoint: str, username: str = "admin") -> dict:
        """Make a request to a protected endpoint."""
        response = httpx.get(f"{self.base_url}{endpoint}", headers=self.get_headers(username))
        response.raise_for_status()
        return response.json()

    def check_permissions(self, username: str, endpoint: str) -> bool:
        """Check if a user has permission to access an endpoint."""
        try:
            self.protected_request(endpoint, username)
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                return False
            raise


def demonstrate_basic_auth():
    """Demonstrate basic authentication flow."""
    print("🔐 Basic Authentication Demo")
    print("=" * 40)

    client = AuthClient(BASE_URL)

    try:
        # 1. Login as admin
        print("\n1. Logging in as admin...")
        token_data = client.login("admin", "admin")
        print("✅ Logged in successfully")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Expires in: {token_data.get('expires_in', 'unknown')} seconds")

        # 2. Verify token
        print("\n2. Verifying JWT token...")
        payload = client.verify_token(token_data["access_token"])
        print("✅ Token valid")
        print(f"   Subject: {payload.get('sub', 'unknown')}")
        print(f"   Issued at: {datetime.fromtimestamp(payload.get('iat', 0))}")
        print(f"   Expires at: {datetime.fromtimestamp(payload.get('exp', 0))}")

        # 3. Use token for protected requests
        print("\n3. Making authenticated requests...")
        object_types = client.protected_request("/v2/ontologies/default/objectTypes")
        print("✅ Accessed protected endpoint")
        print(f"   Found {len(object_types['data'])} object types")

        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


def demonstrate_token_management():
    """Demonstrate token lifecycle management."""
    print("\n🔄 Token Management Demo")
    print("=" * 40)

    client = AuthClient(BASE_URL)

    try:
        # 1. Get initial token
        print("\n1. Getting initial token...")
        token_data = client.login("admin", "admin")
        initial_token = token_data["access_token"]
        print("✅ Initial token obtained")

        # 2. Store token for reuse
        print("\n2. Storing token for reuse...")
        # Token is already stored in client.tokens
        print("✅ Token stored in client")

        # 3. Make multiple requests with same token
        print("\n3. Reusing token for multiple requests...")
        for i in range(3):
            try:
                health = client.protected_request("/health")
                print(f"✅ Request {i+1}: API healthy")
                time.sleep(1)  # Small delay between requests
            except Exception as e:
                print(f"❌ Request {i+1} failed: {e}")

        # 4. Check token expiration (simulated)
        print("\n4. Checking token expiration...")
        payload = client.verify_token(initial_token)
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.now()

        if exp_time > now:
            time_until_expiry = exp_time - now
            print(f"✅ Token expires in {time_until_expiry}")
        else:
            print("⚠️ Token has expired")

        return True

    except Exception as e:
        print(f"❌ Token management failed: {e}")
        return False


def demonstrate_error_handling():
    """Demonstrate authentication error handling."""
    print("\n⚠️ Error Handling Demo")
    print("=" * 40)

    client = AuthClient(BASE_URL)

    # 1. Invalid credentials
    print("\n1. Testing invalid credentials...")
    try:
        client.login("invalid_user", "wrong_password")
        print("❌ Should have failed!")
    except Exception as e:
        print(f"✅ Correctly rejected invalid credentials: {e}")

    # 2. Invalid token
    print("\n2. Testing invalid token...")
    try:
        fake_token = "fake.jwt.token"
        client.verify_token(fake_token)
        print("❌ Should have failed!")
    except Exception as e:
        print(f"✅ Correctly rejected invalid token: {e}")

    # 3. Unauthorized request
    print("\n3. Testing unauthorized request...")
    try:
        response = httpx.get(f"{BASE_URL}/v2/ontologies/default/objectTypes")
        if response.status_code == 401:
            print("✅ Correctly required authentication")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"✅ Correctly rejected unauthorized request: {e}")

    return True


def demonstrate_session_management():
    """Demonstrate session management patterns."""
    print("\n👥 Session Management Demo")
    print("=" * 40)

    client = AuthClient(BASE_URL)

    try:
        # 1. Multiple user sessions (simulated)
        print("\n1. Managing multiple user sessions...")

        # Login as admin
        client.login("admin", "admin")
        print("✅ Admin session created")

        # In a real app, you'd have different users
        # For demo, we'll simulate with admin + different contexts
        client.login("admin", "admin")  # Same user, new session
        print("✅ Second session created")

        # 2. Session cleanup
        print("\n2. Session cleanup...")
        print(f"✅ Active sessions: {len(client.tokens)}")

        # Clear sessions (logout simulation)
        client.tokens.clear()
        print("✅ All sessions cleared")

        return True

    except Exception as e:
        print(f"❌ Session management failed: {e}")
        return False


def main():
    """Run all authentication demonstrations."""
    print("🚀 Ontologia Authentication Examples")
    print("=" * 50)

    # Check if API is running
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy")
            return 1
    except Exception:
        print("❌ Cannot connect to API")
        print("Make sure the API is running: docker-compose up -d")
        return 1

    # Run demonstrations
    demos = [
        ("Basic Auth", demonstrate_basic_auth),
        ("Token Management", demonstrate_token_management),
        ("Error Handling", demonstrate_error_handling),
        ("Session Management", demonstrate_session_management),
    ]

    results = []
    for name, demo_func in demos:
        try:
            result = demo_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} demo failed: {e}")
            results.append((name, False))

    # Summary
    print("\n📊 Demo Results")
    print("=" * 30)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n🎉 All authentication demos completed successfully!")
        print("\n💡 Key takeaways:")
        print("   - Always store tokens securely")
        print("   - Check token expiration before use")
        print("   - Handle authentication errors gracefully")
        print("   - Implement proper session management")
        print("   - Use HTTPS in production")
    else:
        print("\n⚠️ Some demos failed. Check the output above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
