#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Cordatus Jtop Service Setup
# This script installs the systemd service for cordatus-jtop-service

import os
import sys
import logging
from jtop.service import (
    install_service,
    set_service_permission,
    install_variables,
    status_service,
    remove_deprecated_data
)

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)


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
    import jtop
    package_root = os.path.dirname(os.path.abspath(jtop.__file__))
    package_root = os.path.dirname(package_root)  # Go up one level to get package root

    print(f"\n📦 Package location: {package_root}")

    try:
        # Remove deprecated data (from original jetson-stats)
        print("\n🧹 Cleaning up old installations...")
        remove_deprecated_data()

        # Set service permissions
        print("\n👥 Setting up service permissions...")
        set_service_permission()

        # Install variables
        print("\n📝 Installing environment variables...")
        install_variables(package_root, copy=True)

        # Install service
        print("\n🔧 Installing systemd service...")
        install_service(package_root, copy=True)

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
