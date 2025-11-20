#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Cordatus Jtop Service Setup
# This script installs the systemd service for cordatus-jtop-service

import os
import sys
import logging
import shutil
from jtop.service import (
    install_service,
    set_service_permission,
    status_service,
    uninstall_service,
    unset_service_permission
)
from jtop.core.jetson_variables import install_variables, uninstall_variables

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)


def remove_data(file_name):
    """Remove old files or directories if they exist"""
    try:
        if os.path.isfile(file_name):
            print(f"  Removing file: {file_name}")
            os.remove(file_name)
        elif os.path.isdir(file_name):
            print(f"  Removing directory: {file_name}")
            shutil.rmtree(file_name)
    except Exception as e:
        log.warning(f"Could not remove {file_name}: {e}")


def remove_deprecated_data():
    """Remove old jetson-stats installations if they exist"""
    print("  Checking for old jetson-stats installations...")

    # Remove old service files (but not jtop.service - that's ours!)
    uninstall_service('jetson_performance.service')
    uninstall_service('jetson_stats_boot.service')
    uninstall_service('jetson_stats.service')

    # Remove old variable definitions (but not jtop_env.sh - that's ours!)
    uninstall_variables('jetson_env.sh')

    # Remove old permission and group (but not jtop - that's ours!)
    unset_service_permission('jetson_stats')

    # Remove old scripts
    remove_data("/usr/local/bin/jetson-docker")
    # Note: We don't remove jetson-release anymore as it's part of cordatus-jtop-service

    # Remove old folders
    # NOTE: We do NOT remove /usr/local/jetson_stats - that's where OUR files are installed!
    remove_data("/opt/jetson_stats")
    remove_data("/etc/jetson-swap")
    remove_data("/etc/jetson_easy")


def is_superuser():
    return os.getuid() == 0


def main():
    """Setup cordatus-jtop-service systemd service"""

    print("=" * 60)
    print("Cordatus Jtop Service Setup")
    print("=" * 60)

    # Check if running as root
    if not is_superuser():
        print("\n❌ ERROR: This script must be run with sudo/root privileges")
        print("\nPlease run:")
        print("  sudo cordatus-jtop-setup")
        sys.exit(1)

    # Get package installation directory
    import sysconfig

    # Get the data directory where data_files are installed
    # This is typically /usr/local or /usr depending on installation
    data_root = sysconfig.get_path('data')
    if data_root is None:
        data_root = '/usr/local'

    # data_files installs to {data_root}/jetson_stats/
    package_root = os.path.join(data_root, 'jetson_stats')

    print(f"\n📦 Package location: {package_root}")

    # Verify files exist
    if not os.path.exists(os.path.join(package_root, 'jtop.service')):
        print(f"⚠️  Warning: Service file not found in {package_root}")
        print(f"   Trying alternate location...")
        # Fallback to common locations
        for alt_path in ['/usr/local/jetson_stats', '/usr/jetson_stats']:
            if os.path.exists(os.path.join(alt_path, 'jtop.service')):
                package_root = alt_path
                print(f"   Found in: {package_root}")
                break

    try:
        # Set service permissions FIRST
        print("\n👥 Setting up service permissions...")
        set_service_permission()

        # Install variables (before removing old data, so we have the files)
        print("\n📝 Installing environment variables...")
        install_variables(package_root, copy=True)

        # Install service (before removing old data, so we have the files)
        print("\n🔧 Installing systemd service...")
        install_service(package_root, copy=True)

        # NOW remove deprecated data (from original jetson-stats) AFTER we've installed ours
        print("\n🧹 Cleaning up old jetson-stats installations...")
        # Note: We skip removing /usr/local/jetson_stats since that's where our files are now
        remove_deprecated_data()

        # Check service status
        if status_service():
            print("\n✅ Service installed and running successfully!")
            print("\n📊 You can now use 'jtop' command")
            print("💡 Tip: You may need to log out and log back in for group permissions to take effect")
        else:
            print("\n⚠️  Service installed but not running. Try:")
            print("  sudo systemctl status jtop.service")

    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        log.error("Installation error", exc_info=True)
        sys.exit(1)

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
