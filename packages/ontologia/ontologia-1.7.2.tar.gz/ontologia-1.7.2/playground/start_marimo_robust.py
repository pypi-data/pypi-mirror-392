#!/usr/bin/env python3
"""Robust Marimo server starter with error handling"""

import subprocess
import sys
import time

import requests


def start_marimo_server():
    """Start Marimo server with robust configuration"""

    print("🚀 Starting robust Marimo server...")

    # Kill any existing marimo processes
    subprocess.run(["pkill", "-f", "marimo edit"], capture_output=True)
    time.sleep(2)

    # Start new server with robust settings
    cmd = [
        "uv",
        "run",
        "marimo",
        "edit",
        "notebooks/demo_standalone.py",
        "--host",
        "0.0.0.0",
        "--port",
        "8888",
        "--headless",
        "--no-token",
        "--no-skew-protection",
    ]

    print(f"🔧 Running command: {' '.join(cmd)}")

    # Start the server
    process = subprocess.Popen(
        cmd, cwd=".", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(10):
        time.sleep(2)
        try:
            response = requests.get("http://localhost:8888", timeout=5)
            if response.status_code == 200:
                print("✅ Marimo server started successfully!")
                print("🌐 Access at: http://localhost:8888")
                print("📝 Notebook: demo_standalone.py")
                print(f"🔧 Process ID: {process.pid}")
                return process
        except:
            print(f"   Attempt {i+1}/10...")
            continue

    # If we get here, server failed to start
    print("❌ Failed to start Marimo server")
    print("🔍 Checking logs...")

    # Get any error output
    stdout, stderr = process.communicate(timeout=5)
    if stdout:
        print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)

    return None


def main():
    """Main function"""
    try:
        process = start_marimo_server()

        if process:
            print("\n🎯 Server is running! Press Ctrl+C to stop.")
            print("📚 Available notebooks:")
            print("   - demo_standalone.py (current)")
            print("   - 05_agents_standalone.py")
            print("   - 00_data_examples.py")
            print("   - All other notebooks in notebooks/")

            # Keep running until interrupted
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")
        else:
            print("❌ Could not start server")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
