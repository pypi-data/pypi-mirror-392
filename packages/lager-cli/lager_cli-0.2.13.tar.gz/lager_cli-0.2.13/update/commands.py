"""
    lager.update.commands

    Update gateway code on DUTs from GitHub repository
"""
import click
import subprocess
import time
from ..dut_storage import resolve_and_validate_dut, get_dut_user
from ..context import get_default_gateway


@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='DUT name or IP to update')
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
@click.option('--skip-restart', is_flag=True, help='Skip container restart after update')
@click.option('--version', required=False, help='Gateway version/branch to update to (e.g., staging, main)')
@click.option('--branch', required=False, hidden=True, help='(Deprecated: use --version) Git branch to pull from')
@click.option('--check-jlink', is_flag=True, help='Check for J-Link and offer to install if missing')
def update(ctx, box, dut, yes, skip_restart, version, branch, check_jlink):
    """
    Update gateway code on a box from GitHub repository

    This command will:
    1. Connect to the gateway via SSH
    2. Ensure udev_rules directory is tracked (sparse checkout)
    3. Pull the latest code from GitHub (git pull)
    4. Install/update udev rules for USB instrument access
    5. Restart Docker containers to apply changes
    6. Verify services are running correctly
    7. (Optional) Check for J-Link and offer to install if missing
    8. Store version information on gateway and in local config

    Example:
        lager update --box JUL-3
        lager update --box HYP-3 --yes
        lager update --box JUL-FRESH --check-jlink
        lager update --box JUL-3 --version staging
    """
    from ..dut_storage import update_dut_version
    from .. import __version__ as cli_version

    # Handle version/branch compatibility (version takes precedence)
    if not version and not branch:
        # Default to main if neither specified
        target_version = 'main'
    elif version:
        # Use --version if provided
        target_version = version
    else:
        # Fall back to --branch for backward compatibility
        target_version = branch

    # Use box or dut (box takes precedence)
    resolved = box or dut

    # Use default gateway if no box/dut specified
    if not resolved:
        resolved = get_default_gateway(ctx)

    dut = resolved

    # Resolve DUT name to IP address
    resolved_dut = resolve_and_validate_dut(ctx, dut)

    # Get username (defaults to 'lagerdata' if not specified)
    username = get_dut_user(dut) or 'lagerdata'

    ssh_host = f'{username}@{resolved_dut}'

    # Display update information
    click.echo()
    click.secho('Gateway Update', fg='blue', bold=True)
    click.echo(f'Target:  {dut} ({resolved_dut})')
    click.echo(f'Version: {target_version}')
    click.echo(f'CLI:     {cli_version}')
    click.echo()

    # Confirm before proceeding
    if not yes:
        if not click.confirm('This will update the gateway code and restart services. Continue?'):
            click.secho('Update cancelled.', fg='yellow')
            ctx.exit(0)

    # Step 1: Check SSH connectivity
    click.echo('Checking connectivity...', nl=False)
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes',
             ssh_host, 'echo test'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            click.secho(' FAILED', fg='red')
            click.secho(f'Error: Cannot connect to {ssh_host}', fg='red', err=True)
            click.echo('Please ensure SSH keys are configured correctly.', err=True)
            ctx.exit(1)
        click.secho(' OK', fg='green')
    except subprocess.TimeoutExpired:
        click.secho(' TIMEOUT', fg='red')
        click.secho(f'Error: Connection to {ssh_host} timed out', fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(' FAILED', fg='red')
        click.secho(f'Error: {str(e)}', fg='red', err=True)
        ctx.exit(1)

    # Step 2: Check if gateway directory exists and is a git repo
    click.echo('Checking gateway repository...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, 'test -d ~/gateway/.git'],
        capture_output=True
    )
    if result.returncode != 0:
        click.secho(' FAILED', fg='red')
        click.secho('Error: Gateway directory is not a git repository', fg='red', err=True)
        click.echo()
        click.echo('The gateway may have been deployed with rsync instead of git clone.')
        click.echo('Please re-deploy the gateway using the latest deployment script.')
        ctx.exit(1)
    click.secho(' OK', fg='green')

    # Step 3: Show current version
    click.echo('Current version:', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, 'cd ~/gateway && git log -1 --format="%h - %s (%cr)"'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        click.echo(f' {result.stdout.strip()}')
    else:
        click.echo(' (unknown)')

    # Step 4: Fetch and check for updates
    click.echo(f'Fetching updates from origin/{target_version}...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, f'cd ~/gateway && git fetch origin {target_version}'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        click.secho(' FAILED', fg='red')
        click.secho('Error: Failed to fetch updates from GitHub', fg='red', err=True)
        if result.stderr:
            click.echo(result.stderr, err=True)
        click.echo()
        click.echo('This may indicate:')
        click.echo('  - Network connectivity issues')
        click.echo('  - GitHub access problems (check deploy key)')
        click.echo('  - Invalid branch name')
        ctx.exit(1)
    click.secho(' OK', fg='green')

    # Check if there are updates available
    result = subprocess.run(
        ['ssh', ssh_host, f'cd ~/gateway && git rev-list HEAD..origin/{target_version} --count'],
        capture_output=True,
        text=True
    )

    needs_pull = False
    if result.returncode == 0:
        commits_behind = int(result.stdout.strip())
        if commits_behind == 0:
            click.secho('✓ Gateway code is already up to date!', fg='green')
            needs_pull = False
        else:
            click.echo(f'Updates available: {commits_behind} new commit(s)')
            needs_pull = True

    if needs_pull:
        # Step 5: Ensure udev_rules and cli/__init__.py are tracked in sparse checkout
        click.echo('Ensuring required files are tracked...', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host,
             'cd ~/gateway && '
             'git sparse-checkout list | grep -q "^udev_rules$" || git sparse-checkout add udev_rules && '
             'git sparse-checkout list | grep -q "^cli/__init__.py$" || git sparse-checkout add cli/__init__.py'],
            capture_output=True,
            text=True
        )
        # Ignore errors - sparse checkout add is idempotent and may not be needed
        click.secho(' OK', fg='green')

        # Step 6: Checkout the specified version/branch
        click.echo(f'Checking out version {target_version}...', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, f'cd ~/gateway && git checkout {target_version}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.secho(' FAILED', fg='red')
            click.secho(f'Error: Failed to checkout version {target_version}', fg='red', err=True)
            if result.stderr:
                click.echo(result.stderr, err=True)
            ctx.exit(1)
        click.secho(' OK', fg='green')

        # Step 7: Reset to match remote (force pull, handles divergent branches)
        click.echo(f'Updating to match origin/{target_version}...', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, f'cd ~/gateway && git reset --hard origin/{target_version}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.secho(' FAILED', fg='red')
            click.secho('Error: Failed to update branch', fg='red', err=True)
            if result.stderr:
                click.echo(result.stderr, err=True)

            # Check if it's a sparse checkout issue
            if 'sparse' in result.stderr.lower():
                click.echo()
                click.echo('This may be a sparse checkout configuration issue.')
                click.echo('Try re-deploying the gateway with the latest deployment script.')
            ctx.exit(1)
        click.secho(' OK', fg='green')

        # Show new version
        click.echo('New version:', nl=False)
        result = subprocess.run(
            ['ssh', ssh_host, 'cd ~/gateway && git log -1 --format="%h - %s (%cr)"'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            click.echo(f' {result.stdout.strip()}')

    # Step 8: Install udev rules (if they exist)
    click.echo()
    click.echo('Installing udev rules...', nl=False)

    # Check if udev_rules directory exists
    result = subprocess.run(
        ['ssh', ssh_host, 'test -d ~/gateway/udev_rules'],
        capture_output=True
    )

    if result.returncode == 0:
        # Copy udev rules to /tmp, then install with sudo
        install_cmd = (
            'cp ~/gateway/udev_rules/99-instrument.rules /tmp/ && '
            'sudo cp /tmp/99-instrument.rules /etc/udev/rules.d/ && '
            'sudo chmod 644 /etc/udev/rules.d/99-instrument.rules && '
            'sudo udevadm control --reload-rules && '
            'sudo udevadm trigger && '
            'rm /tmp/99-instrument.rules'
        )

        result = subprocess.run(
            ['ssh', ssh_host, install_cmd],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            click.secho(' OK', fg='green')
        else:
            click.secho(' SKIPPED', fg='yellow')
            if 'password' in result.stderr.lower() or 'sudo' in result.stderr.lower():
                click.echo('  (Passwordless sudo not configured for udev operations)')
                click.echo('  Run deployment script to set up passwordless sudo')
            else:
                click.echo(f'  ({result.stderr.strip()[:50]}...)')
    else:
        click.secho(' SKIPPED (no udev_rules directory)', fg='yellow')

    # Step 8b: Fix sparse checkout nested directory issue
    # Sparse checkout may create gateway/gateway/* structure - copy files to correct location
    click.echo('Checking for sparse checkout nested directories...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host,
         'if [ -d ~/gateway/gateway ]; then '
         '  echo "nested"; '
         'else '
         '  echo "normal"; '
         'fi'],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0 and 'nested' in result.stdout:
        click.secho(' NESTED', fg='yellow')
        click.echo('  Copying files from nested gateway directory...', nl=False)

        # Copy all necessary files from gateway/gateway/* to gateway/*
        copy_result = subprocess.run(
            ['ssh', ssh_host,
             'cd ~/gateway && '
             'cp -rf gateway/lager . 2>/dev/null && '
             'cp -rf gateway/udev_rules . 2>/dev/null && '
             'cp -f gateway/start_lager.sh . 2>/dev/null && '
             'cp -f gateway/start_all_containers_hyphen.sh . 2>/dev/null || true'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if copy_result.returncode == 0:
            click.secho(' OK', fg='green')

            # Remove the nested directory after successful copy
            click.echo('  Cleaning up nested directory...', nl=False)
            cleanup_result = subprocess.run(
                ['ssh', ssh_host, 'rm -rf ~/gateway/gateway'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if cleanup_result.returncode == 0:
                click.secho(' OK', fg='green')
            else:
                click.secho(' WARNING', fg='yellow')
                click.echo('  (Could not remove nested directory, but files were copied successfully)')
        else:
            click.secho(' FAILED', fg='red')
            click.secho('Error: Failed to copy files from nested directory', fg='red', err=True)
            if copy_result.stderr:
                click.echo(copy_result.stderr, err=True)
            ctx.exit(1)
    else:
        click.secho(' OK', fg='green')

    # Step 8c: Verify and enforce gateway security
    click.echo()
    click.echo('Checking gateway security...', nl=False)

    # Check if UFW is installed and active
    security_check = subprocess.run(
        ['ssh', ssh_host, 'which ufw >/dev/null 2>&1 && sudo ufw status | grep -q "Status: active"'],
        capture_output=True,
        text=True
    )

    if security_check.returncode == 0:
        # UFW is active, verify rules are correct
        rules_check = subprocess.run(
            ['ssh', ssh_host,
             'sudo ufw status | grep -E "(5000|8301|8765).*(ALLOW|DENY)" | grep -q "on tailscale0\\|on docker0\\|on lo"'],
            capture_output=True,
            text=True
        )

        if rules_check.returncode == 0:
            click.secho(' OK', fg='green')
        else:
            click.secho(' NEEDS CONFIGURATION', fg='yellow')
            click.echo('  Configuring firewall rules...', nl=False)

            # Check if security script exists on gateway
            script_exists = subprocess.run(
                ['ssh', ssh_host, 'test -f ~/gateway/lager/scripts/secure_gateway_firewall.sh'],
                capture_output=True
            )

            if script_exists.returncode == 0:
                # Run security script from gateway repo
                security_fix = subprocess.run(
                    ['ssh', ssh_host,
                     'cd ~/gateway/lager/scripts && chmod +x secure_gateway_firewall.sh && sudo ./secure_gateway_firewall.sh'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if security_fix.returncode == 0:
                    click.secho(' OK', fg='green')
                else:
                    click.secho(' FAILED', fg='red')
                    click.echo('  Warning: Could not configure firewall automatically')
                    click.echo('  Run manually: sudo ~/gateway/lager/scripts/secure_gateway_firewall.sh')
            else:
                click.secho(' SKIPPED', fg='yellow')
                click.echo('  (security script not found in gateway repo)')
                click.echo('  Update gateway repo to latest version for security features')
    else:
        # UFW not installed or not active - install and configure automatically
        click.secho(' NOT CONFIGURED', fg='yellow')
        click.echo('  Installing and configuring firewall...', nl=False)

        # Check if security script exists on gateway
        script_exists = subprocess.run(
            ['ssh', ssh_host, 'test -f ~/gateway/lager/scripts/secure_gateway_firewall.sh'],
            capture_output=True
        )

        if script_exists.returncode == 0:
            # Install UFW and run security script
            security_setup = subprocess.run(
                ['ssh', ssh_host,
                 'sudo apt-get update -qq && sudo apt-get install -y ufw && '
                 'cd ~/gateway/lager/scripts && chmod +x secure_gateway_firewall.sh && sudo ./secure_gateway_firewall.sh'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if security_setup.returncode == 0:
                click.secho(' OK', fg='green')
                click.echo('  ✓ Firewall installed and configured')
            else:
                click.secho(' FAILED', fg='red')
                click.echo('  Warning: Could not configure firewall automatically')
                click.echo('  Please contact your administrator for gateway security setup')
        else:
            click.secho(' SKIPPED', fg='yellow')
            click.echo('  (security script not found in gateway repo)')
            click.echo('  Gateway may need to be updated to latest version first')

    # Step 9: Restart containers (unless skipped)
    if skip_restart:
        click.echo()
        click.secho('Skipping container restart (--skip-restart flag set)', fg='yellow')
        click.echo('Run this manually to apply changes:')
        click.echo(f'  ssh {ssh_host} "cd ~/gateway && ./start_lager.sh"')
        ctx.exit(0)

    click.echo()
    click.echo('Rebuilding Docker containers (this may take several minutes)...')
    click.echo('  (This will install fresh dependencies like yoctopuce)')

    # Stop and remove existing containers and images
    click.echo('  Stopping containers...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host,
         'cd ~/gateway && '
         'docker stop $(docker ps -aq) 2>/dev/null || true && '
         'docker rm $(docker ps -aq) 2>/dev/null || true && '
         'docker rmi lager python controller lagerdata/controller 2>/dev/null || true'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        click.secho(' OK', fg='green')
    else:
        click.secho(' WARNING', fg='yellow')

    # Rebuild Lager container with --no-cache to ensure fresh dependencies
    click.echo('  Rebuilding Lager container (no cache)...')
    click.echo()

    # Stream build output to show progress
    process = subprocess.Popen(
        ['ssh', ssh_host,
         'cd ~/gateway/lager && '
         'docker build --no-cache -f docker/gatewaypy3.Dockerfile -t lager .'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Stream output line by line
    if process.stdout:
        for line in process.stdout:
            click.echo(f'    {line}', nl=False)

    return_code = process.wait(timeout=600)

    click.echo()
    if return_code != 0:
        click.secho('  Lager container rebuild FAILED', fg='red', bold=True)
        click.secho('Error: Failed to rebuild Lager container', fg='red', err=True)
        ctx.exit(1)
    click.secho('  Lager container rebuild complete!', fg='green', bold=True)

    # Start containers using the startup script
    click.echo('  Starting containers...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host, 'cd ~/gateway && chmod +x start_lager.sh && ./start_lager.sh'],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        click.secho(' FAILED', fg='red')
        click.secho('Error: Failed to restart containers', fg='red', err=True)
        if result.stderr:
            click.echo(result.stderr, err=True)
        click.echo()
        click.echo('You may need to manually restart containers:')
        click.echo(f'  ssh {ssh_host}')
        click.echo('  cd ~/gateway && chmod +x start_lager.sh && ./start_lager.sh')
        ctx.exit(1)

    click.secho(' OK', fg='green')

    # Step 10: Wait for containers to stabilize
    click.echo('Waiting for services to start...', nl=False)
    time.sleep(5)
    click.secho(' OK', fg='green')

    # Step 11: Verify containers are running
    click.echo('Verifying container status...', nl=False)
    result = subprocess.run(
        ['ssh', ssh_host,
         "docker ps --filter 'name=lager' --format '{{.Names}}' | wc -l"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        running_count = int(result.stdout.strip())
        if running_count >= 1:
            click.secho(' OK', fg='green')
        else:
            click.secho(f' WARNING (lager container not running)', fg='yellow')
    else:
        click.secho(' FAILED', fg='red')

    # Show final status
    click.echo()
    click.secho('Container Status:', fg='blue', bold=True)
    result = subprocess.run(
        ['ssh', ssh_host,
         "docker ps --filter 'name=lager' "
         "--format 'table {{.Names}}\t{{.Status}}'"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        click.echo(result.stdout.strip())

    # Step 12: Read gateway CLI version from the checked-out code
    click.echo()
    click.echo('Reading gateway CLI version...', nl=False)

    # Read __version__ from cli/__init__.py on the gateway
    read_version_cmd = (
        'cd ~/gateway && '
        'grep -E "^__version__\\s*=\\s*" cli/__init__.py | '
        'sed -E "s/__version__\\s*=\\s*[\\x27\\x22]([^\\x27\\x22]+)[\\x27\\x22]/\\1/"'
    )

    result = subprocess.run(
        ['ssh', ssh_host, read_version_cmd],
        capture_output=True,
        text=True
    )

    if result.returncode == 0 and result.stdout.strip():
        gateway_cli_version = result.stdout.strip()
        click.secho(f' {gateway_cli_version}', fg='green')
    else:
        # Fallback to branch name if we can't read the version
        gateway_cli_version = target_version
        click.secho(f' (using branch name: {target_version})', fg='yellow')

    # Step 13: Store version information on gateway
    click.echo('Storing version information...', nl=False)

    # Store the gateway CLI version (not the branch name)
    # Format: <gateway_version>|<current_local_cli_version>
    version_content = f'{gateway_cli_version}|{cli_version}'

    # Try to store in /etc/lager/version (should be writable without sudo)
    # /etc/lager is mounted into the Docker container, so the container can read it
    store_version_cmd = f'echo "{version_content}" > /etc/lager/version'

    result = subprocess.run(
        ['ssh', ssh_host, store_version_cmd],
        capture_output=True,
        text=True
    )

    # If direct write fails, try with sudo (fallback for restricted permissions)
    if result.returncode != 0:
        sudo_cmd = (
            f'sudo mkdir -p /etc/lager && '
            f'echo "{version_content}" | sudo tee /etc/lager/version > /dev/null && '
            f'sudo chmod 644 /etc/lager/version'
        )
        result = subprocess.run(
            ['ssh', ssh_host, sudo_cmd],
            capture_output=True,
            text=True
        )

    if result.returncode == 0:
        click.secho(' OK', fg='green')

        # Update version in local DUT storage with gateway CLI version
        if dut:  # Only if we have a DUT name (not just IP)
            if update_dut_version(dut, gateway_cli_version):
                click.echo(f'  Updated local config: {dut} → {gateway_cli_version}')
            else:
                # DUT not in local storage (might be using IP directly)
                pass
    else:
        click.secho(' FAILED', fg='red')
        if result.stderr:
            click.echo(f'  Error: {result.stderr.strip()[:100]}')

    # Check for J-Link installation if requested
    if check_jlink:
        click.echo()
        click.secho('Checking J-Link Installation...', fg='blue', bold=True)

        # Check if J-Link is installed on gateway
        jlink_check = subprocess.run(
            ['ssh', ssh_host, 'test -f /home/$USER/third_party/JLink_*/JLinkGDBServerCLExe'],
            capture_output=True
        )

        if jlink_check.returncode == 0:
            click.secho('✓ J-Link is already installed on this gateway', fg='green')
        else:
            click.secho('⚠ J-Link is not installed on this gateway', fg='yellow')
            click.echo()
            click.echo('J-Link is required for debug commands. You have two options:')
            click.echo()
            click.echo('Option 1: Copy from another gateway that has J-Link')
            click.echo('  Run this from your local machine:')
            click.echo(f'  ssh {username}@<source-gateway-ip> "cd /home/{username}/third_party && tar czf - JLink_*" | \\')
            click.echo(f'    ssh {ssh_host} "cd /home/{username} && mkdir -p third_party && cd third_party && tar xzf -"')
            click.echo()
            click.echo('Option 2: Manual download from SEGGER')
            click.echo('  1. Visit: https://www.segger.com/downloads/jlink/')
            click.echo('  2. Download: JLink_Linux_V794a_x86_64.tgz (requires license acceptance)')
            click.echo('  3. Save to: /tmp/JLink_Linux_V794a_x86_64.tgz on your local machine')
            click.echo('  4. Run these commands:')
            click.echo(f'     scp /tmp/JLink_Linux_V794a_x86_64.tgz {ssh_host}:~/third_party/')
            click.echo(f'     ssh {ssh_host} "cd ~/third_party && tar xzf JLink_Linux_V794a_x86_64.tgz && rm JLink_Linux_V794a_x86_64.tgz"')
            click.echo()
            click.echo('After installing J-Link, restart containers:')
            click.echo(f'  lager update --box {dut} --skip-restart=false')
            click.echo()

            if not yes:
                if click.confirm('Would you like to copy J-Link from another gateway now?'):
                    source_gateway = click.prompt('Enter source gateway IP (e.g., 100.91.127.26)')
                    source_ssh = f'{username}@{source_gateway}'

                    click.echo(f'Copying J-Link from {source_gateway}...')
                    try:
                        # First verify source has J-Link
                        verify_result = subprocess.run(
                            ['ssh', source_ssh, 'test -f /home/$USER/third_party/JLink_*/JLinkGDBServerCLExe'],
                            capture_output=True,
                            timeout=10
                        )

                        if verify_result.returncode != 0:
                            click.secho(f'✗ Source gateway {source_gateway} does not have J-Link installed', fg='red')
                        else:
                            # Create third_party directory on target
                            subprocess.run(
                                ['ssh', ssh_host, f'mkdir -p /home/{username}/third_party'],
                                check=True
                            )

                            # Copy J-Link directory
                            copy_cmd = (
                                f'ssh {source_ssh} "cd /home/{username}/third_party && tar czf - JLink_*" | '
                                f'ssh {ssh_host} "cd /home/{username}/third_party && tar xzf -"'
                            )

                            result = subprocess.run(
                                copy_cmd,
                                shell=True,
                                capture_output=True,
                                text=True,
                                timeout=120
                            )

                            if result.returncode == 0:
                                click.echo()
                                click.secho('✓ J-Link copied successfully!', fg='green', bold=True)
                                click.echo('Restarting containers to apply changes...')

                                # Restart containers
                                restart_result = subprocess.run(
                                    ['ssh', ssh_host, 'cd ~/gateway && ./start_all_containers.sh'],
                                    capture_output=True,
                                    text=True,
                                    timeout=60
                                )

                                if restart_result.returncode == 0:
                                    click.secho('✓ Containers restarted successfully', fg='green')
                                else:
                                    click.secho('⚠ Container restart may have failed', fg='yellow')
                            else:
                                click.secho(f'✗ Failed to copy J-Link: {result.stderr}', fg='red')

                    except subprocess.TimeoutExpired:
                        click.secho('✗ Copy operation timed out', fg='red')
                    except Exception as e:
                        click.secho(f'✗ Error copying J-Link: {str(e)}', fg='red')

    # Final success message
    click.echo()
    click.secho('✓ Gateway update completed successfully!', fg='green', bold=True)
    click.echo()
    click.echo('You can verify connectivity with:')
    click.echo(f'  lager hello --dut {dut}')
    click.echo()
