import sys
import os
import asyncio
import argparse
import subprocess
from pathlib import Path
from loguru import logger
from .auth.manager import AuthManager
from .installer import BinaryInstaller
from .package_manager import PackageManager


def setup_logging(verbose: bool = False):
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level
    )


async def login_command():
    try:
        auth_manager = AuthManager()
        result = await auth_manager.login()
        print(f"\n✓ Successfully authenticated as {result.get('email', result.get('user_id'))}")
        print(f"  Token expires: {result['expires_at']}")
        print("  You can now access Synvex SaaS features\n")
    except FileNotFoundError as e:
        print(f"\n✗ Configuration error: {e}")
        print("  Create .zitadel-config.json in project root or ~/.nexroo/\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}\n")
        sys.exit(1)


async def logout_command():
    try:
        auth_manager = AuthManager()
        await auth_manager.logout()
        print("\n✓ Logged out successfully\n")
    except Exception as e:
        print(f"\n✗ Logout failed: {e}\n")
        sys.exit(1)


async def status_command():
    try:
        auth_manager = AuthManager()

        if not auth_manager.is_authenticated():
            print("\n✗ Not authenticated")
            print("  Run 'nexroo login' to authenticate\n")
            return

        is_valid = await auth_manager.verify_authentication()
        token_data = auth_manager.storage.load_token()

        if is_valid:
            print("\n✓ Authenticated")
            if token_data:
                print(f"  Token expires: {token_data.get('expires_at')}")
            print("  Synvex SaaS features available\n")
        else:
            print("\n⚠ Token expired")
            print("  Run 'nexroo login' to re-authenticate\n")

    except FileNotFoundError:
        print("\n✗ No authentication configuration found")
        print("  Create .zitadel-config.json in project root or ~/.nexroo/\n")
    except Exception as e:
        print(f"\n⚠ Status check failed: {e}\n")


async def ensure_binary_installed():
    installer = BinaryInstaller()

    if not installer.is_installed():
        logger.info("nexroo-engine not found. Installing...")
        try:
            await installer.install()
        except Exception as e:
            logger.error(f"Failed to install nexroo-engine: {e}")
            sys.exit(1)


async def install_command(args):
    try:
        installer = BinaryInstaller()

        if installer.is_installed():
            print("\n✓ nexroo-engine already installed")
            print("\n  Run 'nexroo update' to update to latest version\n")
            return

        print("\nInstalling nexroo-engine...")
        await installer.install()
        print("\n✓ nexroo-engine installed successfully!\n")

    except Exception as e:
        print(f"\n✗ Installation failed: {e}\n")
        sys.exit(1)


async def update_command():
    try:
        installer = BinaryInstaller()
        current_version = installer._get_installed_version()
        await installer.update()
        new_version = installer._get_installed_version()

        if current_version == new_version and current_version:
            print(f"\n✓ Already up to date ({current_version})\n")
        else:
            print("\n✓ nexroo-engine updated successfully\n")
    except Exception as e:
        print(f"\n✗ Update failed: {e}\n")
        sys.exit(1)


def uninstall_command(args):
    try:
        from pathlib import Path
        import shutil

        installer = BinaryInstaller()
        nexroo_dir = Path.home() / ".nexroo"

        if not nexroo_dir.exists() and not installer.is_installed():
            print("\n✓ Nothing to uninstall\n")
            return

        print("\nThis will remove:")
        print(f"  - nexroo-engine package")
        print(f"  - All addons")
        print(f"  - Authentication tokens")
        print(f"  - All data in {nexroo_dir}")
        print()

        if not args.yes:
            response = input("Continue? [y/N]: ").strip().lower()
            if response != 'y':
                print("\n✗ Uninstall cancelled\n")
                return

        installer.uninstall()

        if nexroo_dir.exists():
            shutil.rmtree(nexroo_dir)

        print("\n✓ Uninstalled successfully")
        print("\nTo remove the CLI package, run:")
        print("  pip uninstall nexroo-cli\n")

    except Exception as e:
        print(f"\n✗ Uninstall failed: {e}\n")
        sys.exit(1)


async def addon_list_command(args):
    try:
        pkg_manager = PackageManager()

        if args.available:
            packages = pkg_manager.registry.get_packages(refresh=args.refresh)
            if not packages:
                print("\nNo packages found\n")
                return

            print(f"\nAvailable addons ({len(packages)}):\n")
            names = sorted([pkg['name'].replace('-rooms-pkg', '') for pkg in packages])
            for name in names:
                print(f"  {name}")
            print()
        else:
            installed = pkg_manager.list_installed()
            if not installed:
                print("\nNo addons installed\n")
                print("  Run 'nexroo addon list --available' to see available packages")
                print("  Run 'nexroo addon install <name>' to install\n")
                return

            print(f"\nInstalled addons ({len(installed)}):\n")
            for pkg in installed:
                short_name = pkg['name'].replace('-rooms-pkg', '')
                if pkg["location"] == "bundled":
                    print(f"  {short_name} v{pkg['version']} [bundled]")
                else:
                    print(f"  {short_name} v{pkg['version']}")
                if pkg.get("description"):
                    print(f"    {pkg['description']}")
            print()

    except Exception as e:
        print(f"\nFailed to list packages: {e}\n")
        sys.exit(1)


async def addon_search_command(args):
    try:
        pkg_manager = PackageManager()
        results = pkg_manager.registry.search_packages(args.query)

        if not results:
            print(f"\nNo packages found matching '{args.query}'\n")
            return

        print(f"\nSearch results for '{args.query}' ({len(results)}):\n")
        for pkg in results:
            short_name = pkg['name'].replace('-rooms-pkg', '')
            print(f"  {short_name}")
            if pkg.get("description"):
                print(f"    {pkg['description']}")
        print()

    except Exception as e:
        print(f"\nSearch failed: {e}\n")
        sys.exit(1)


async def addon_install_command(args):
    try:
        pkg_manager = PackageManager()
        success = await pkg_manager.install(
            args.package,
            version=args.version,
            url=args.url,
            upgrade=args.upgrade
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nInstallation failed: {e}\n")
        sys.exit(1)


async def addon_uninstall_command(args):
    try:
        pkg_manager = PackageManager()
        success = await pkg_manager.uninstall(args.package, force=args.yes)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nUninstallation failed: {e}\n")
        sys.exit(1)


async def addon_update_command(args):
    try:
        pkg_manager = PackageManager()

        if args.all:
            results = await pkg_manager.update_all()
            successes = sum(1 for v in results.values() if v)
            print(f"\nUpdated {successes}/{len(results)} packages\n")
            sys.exit(0 if successes == len(results) else 1)
        else:
            success = await pkg_manager.update(args.package)
            sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\nUpdate failed: {e}\n")
        sys.exit(1)


async def run_command(args):
    is_authenticated = False
    auth_token = None

    await ensure_binary_installed()

    if not args.no_auth:
        try:
            auth_manager = AuthManager()

            if auth_manager.is_authenticated():
                is_valid = await auth_manager.verify_authentication()

                if is_valid:
                    logger.info("✓ Authenticated - SaaS features enabled")
                    is_authenticated = True
                    auth_token = auth_manager.get_token()
                else:
                    logger.warning("⚠ Authentication expired")
                    logger.info("  Run 'nexroo login' to re-authenticate")
                    logger.info("  Continuing without SaaS features...")
            else:
                logger.info("ℹ Not authenticated")
                logger.info("  Run 'nexroo login' to access SaaS features")

        except FileNotFoundError:
            logger.debug("No auth configuration found")
        except Exception as e:
            logger.warning(f"Auth check failed: {e}")

    env = os.environ.copy()
    if is_authenticated and auth_token:
        env['SYNVEX_AUTH_TOKEN'] = auth_token
        env['SYNVEX_SAAS_ENABLED'] = 'true'

    cmd = ["nexroo-engine", str(args.workflow)]

    if args.entrypoint:
        cmd.append(args.entrypoint)

    if args.verbose:
        cmd.append('-v')
    if args.mock:
        cmd.append('--mock')
    if args.dry_run:
        cmd.append('--dry-run')
    if args.mock_config:
        cmd.extend(['--mock-config', args.mock_config])
    if args.payload:
        cmd.extend(['--payload', args.payload])
    if args.payload_file:
        cmd.extend(['--payload-file', args.payload_file])

    try:
        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)
    except Exception as e:
        logger.error(f"Failed to run workflow: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='nexroo',
        description='Nexroo CLI - Workflow orchestration with Zitadel authentication',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        metavar=''
    )

    install_parser = subparsers.add_parser('install', help='Install nexroo-engine')

    subparsers.add_parser('login', help='Authenticate with Zitadel to access SaaS features')
    subparsers.add_parser('logout', help='Clear saved authentication credentials')
    subparsers.add_parser('status', help='Show authentication status')
    subparsers.add_parser('update', help='Update nexroo-engine to latest version')

    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall nexroo-engine, addons, and all data')
    uninstall_parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')

    addon_parser = subparsers.add_parser('addon', help='Manage addon packages')
    addon_subparsers = addon_parser.add_subparsers(
        dest='addon_command',
        title='addon commands',
        metavar=''
    )

    addon_list_parser = addon_subparsers.add_parser('list', help='List installed or available addons')
    addon_list_parser.add_argument('--available', action='store_true', help='List available packages')
    addon_list_parser.add_argument('--refresh', action='store_true', help='Refresh package cache')

    addon_search_parser = addon_subparsers.add_parser('search', help='Search for addon packages')
    addon_search_parser.add_argument('query', help='Search query')

    addon_install_parser = addon_subparsers.add_parser('install', help='Install an addon package')
    addon_install_parser.add_argument('package', help='Package name')
    addon_install_parser.add_argument('--version', help='Specific version to install')
    addon_install_parser.add_argument('--url', help='Custom URL to install from')
    addon_install_parser.add_argument('--upgrade', action='store_true', help='Upgrade if already installed')

    addon_uninstall_parser = addon_subparsers.add_parser('uninstall', help='Uninstall an addon package')
    addon_uninstall_parser.add_argument('package', help='Package name')
    addon_uninstall_parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')

    addon_update_parser = addon_subparsers.add_parser('update', help='Update addon package(s)')
    addon_update_parser.add_argument('package', nargs='?', help='Package name (optional)')
    addon_update_parser.add_argument('--all', action='store_true', help='Update all packages')

    run_parser = subparsers.add_parser('run', help='Run a workflow')
    run_parser.add_argument('workflow', type=Path, help='Path to workflow JSON file')
    run_parser.add_argument('entrypoint', nargs='?', help='Entrypoint ID (optional)')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    run_parser.add_argument('--mock', action='store_true', help='Run in mock mode')
    run_parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
    run_parser.add_argument('--mock-config', help='Path to mock configuration file')
    run_parser.add_argument('--payload', help='JSON payload string')
    run_parser.add_argument('--payload-file', help='Path to JSON payload file')
    run_parser.add_argument('--no-auth', action='store_true', help='Skip authentication (no SaaS features)')

    args = parser.parse_args()

    setup_logging(verbose=getattr(args, 'verbose', False))

    if args.command == 'install':
        asyncio.run(install_command(args))
    elif args.command == 'login':
        asyncio.run(login_command())
    elif args.command == 'logout':
        asyncio.run(logout_command())
    elif args.command == 'status':
        asyncio.run(status_command())
    elif args.command == 'update':
        asyncio.run(update_command())
    elif args.command == 'uninstall':
        uninstall_command(args)
    elif args.command == 'addon':
        if args.addon_command == 'list':
            asyncio.run(addon_list_command(args))
        elif args.addon_command == 'search':
            asyncio.run(addon_search_command(args))
        elif args.addon_command == 'install':
            asyncio.run(addon_install_command(args))
        elif args.addon_command == 'uninstall':
            asyncio.run(addon_uninstall_command(args))
        elif args.addon_command == 'update':
            asyncio.run(addon_update_command(args))
        else:
            addon_parser.print_help()
            sys.exit(1)
    elif args.command == 'run':
        asyncio.run(run_command(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
