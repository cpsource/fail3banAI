#!/usr/bin/env python3
"""
Dynamic Linker Security Checker

This script checks for potentially dangerous LD_* environment variables
that attackers might use to hijack program execution or inject malicious code.

Think of this as a security guard checking for hidden weapons that could
compromise your system's integrity.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_dangerous_ld_variables():
    """
    Check for dangerous LD_* environment variables.
    
    These variables can be used by attackers to:
    - Inject malicious libraries
    - Override system functions
    - Bypass security controls
    - Escalate privileges
    """
    
    # Comprehensive list of dangerous LD environment variables
    dangerous_vars = {
        'LD_PRELOAD': 'Preload malicious libraries before all others',
        'LD_LIBRARY_PATH': 'Override library search paths to load malicious libs',
        'LD_AUDIT': 'Inject audit libraries that can monitor/modify execution',
        'LD_DEBUG': 'Enable debug output that might leak sensitive info',
        'LD_PROFILE': 'Profile library injection for code analysis',
        'LD_USE_LOAD_BIAS': 'Control memory layout for exploitation',
        'LD_DYNAMIC_WEAK': 'Weak symbol manipulation',
        'LD_ORIGIN_PATH': 'Control $ORIGIN path resolution',
        'LD_SHOW_AUXV': 'Show auxiliary vector (info disclosure)',
        'LD_VERBOSE': 'Verbose output that might leak info',
        'LD_WARN': 'Control warning messages',
        'LD_BIND_NOW': 'Force immediate binding (could hide malicious libs)',
        'LD_BIND_NOT': 'Prevent binding (DoS potential)',
        'LD_TRACE_LOADED_OBJECTS': 'Show loaded objects (recon)',
        'LD_ASSUME_KERNEL': 'Kernel version spoofing',
        'LD_POINTER_GUARD': 'Disable pointer protection',
        'LD_HWCAP_MASK': 'Hardware capability masking',
        'LD_PLATFORM': 'Platform spoofing',
        'LD_PREFER_MAP_32BIT_EXEC': 'Memory layout manipulation'
    }
    
    print("🔍 DYNAMIC LINKER SECURITY ASSESSMENT")
    print("="*60)
    
    found_dangerous = []
    
    # Check current environment
    print("\n📋 CURRENT ENVIRONMENT CHECK:")
    for var_name, description in dangerous_vars.items():
        value = os.environ.get(var_name)
        if value:
            found_dangerous.append((var_name, value, description))
            print(f"  🚨 DANGER: {var_name}={value}")
            print(f"      Risk: {description}")
        else:
            print(f"  ✅ Safe: {var_name} not set")
    
    return found_dangerous

def check_process_environments():
    """
    Check running processes for dangerous LD variables.
    
    Attackers might inject these into running processes.
    """
    print("\n🔄 RUNNING PROCESS ENVIRONMENT CHECK:")
    
    dangerous_processes = []
    
    try:
        # Get list of all processes
        result = subprocess.run(['ps', 'axo', 'pid,comm'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("  ⚠️  Could not enumerate processes")
            return dangerous_processes
        
        processes = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                pid, comm = parts
                processes.append((pid, comm))
        
        print(f"  Checking {len(processes)} processes...")
        
        # Check a sample of processes (checking all can be slow)
        sample_size = min(50, len(processes))
        for i, (pid, comm) in enumerate(processes[:sample_size]):
            try:
                # Read process environment
                env_file = f"/proc/{pid}/environ"
                if os.path.exists(env_file):
                    with open(env_file, 'rb') as f:
                        env_data = f.read().decode('utf-8', errors='ignore')
                        env_vars = env_data.split('\0')
                        
                        for var in env_vars:
                            if '=' in var:
                                name, value = var.split('=', 1)
                                if name.startswith('LD_') and name in dangerous_vars:
                                    dangerous_processes.append((pid, comm, name, value))
                                    print(f"  🚨 DANGER: Process {pid} ({comm}) has {name}={value}")
            except (PermissionError, FileNotFoundError, ProcessLookupError):
                # Normal - can't read some process environments
                continue
            except Exception as e:
                # Unexpected error, but don't crash
                continue
        
        if not dangerous_processes:
            print("  ✅ No dangerous LD variables found in checked processes")
            
    except Exception as e:
        print(f"  ⚠️  Error checking processes: {e}")
    
    return dangerous_processes

def check_system_files():
    """
    Check system configuration files for LD variable persistence.
    
    Attackers might modify these files to persist their attacks.
    """
    print("\n📁 SYSTEM CONFIGURATION CHECK:")
    
    config_files = [
        '/etc/environment',
        '/etc/profile',
        '/etc/bash.bashrc',
        '/etc/zsh/zshrc',
        '/etc/ld.so.preload',
        '/etc/ld.so.conf',
        '/etc/ld.so.conf.d/',
        '~/.bashrc',
        '~/.profile',
        '~/.zshrc'
    ]
    
    found_configs = []
    
    for config_path in config_files:
        # Expand user home directory
        if config_path.startswith('~'):
            config_path = os.path.expanduser(config_path)
        
        try:
            if os.path.isfile(config_path):
                with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for LD_ variable assignments
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if (line.startswith('export LD_') or 
                            line.startswith('LD_') or
                            'LD_PRELOAD' in line):
                            found_configs.append((config_path, line_num, line))
                            print(f"  🚨 DANGER: {config_path}:{line_num}: {line}")
            
            elif os.path.isdir(config_path):
                # Check directory for config files
                try:
                    for file_path in Path(config_path).glob('*'):
                        if file_path.is_file():
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if any(ld_var in content for ld_var in dangerous_vars.keys()):
                                    print(f"  🚨 DANGER: LD variables found in {file_path}")
                                    found_configs.append((str(file_path), 0, "Contains LD variables"))
                except Exception:
                    continue
                    
        except (PermissionError, FileNotFoundError):
            # Normal - some files might not be readable
            continue
        except Exception as e:
            print(f"  ⚠️  Error checking {config_path}: {e}")
    
    if not found_configs:
        print("  ✅ No dangerous LD variables found in system configs")
    
    return found_configs

def check_ld_so_preload_file():
    """
    Special check for /etc/ld.so.preload - the most dangerous file.
    """
    print("\n🎯 CRITICAL FILE CHECK: /etc/ld.so.preload")
    
    preload_file = '/etc/ld.so.preload'
    
    if os.path.exists(preload_file):
        try:
            with open(preload_file, 'r') as f:
                content = f.read().strip()
                
            if content:
                print(f"  🚨 CRITICAL DANGER: {preload_file} contains:")
                for line in content.split('\n'):
                    if line.strip():
                        print(f"    {line.strip()}")
                return True
            else:
                print(f"  ⚠️  {preload_file} exists but is empty")
                return False
        except Exception as e:
            print(f"  ⚠️  Error reading {preload_file}: {e}")
            return False
    else:
        print(f"  ✅ {preload_file} does not exist (good)")
        return False

def generate_recommendations(env_vars, processes, configs, preload_exists):
    """
    Generate security recommendations based on findings.
    """
    print("\n🛡️  SECURITY RECOMMENDATIONS:")
    print("="*60)
    
    if env_vars or processes or configs or preload_exists:
        print("🚨 IMMEDIATE ACTIONS REQUIRED:")
        
        if env_vars:
            print("\n1. CLEAR DANGEROUS ENVIRONMENT VARIABLES:")
            for var_name, value, desc in env_vars:
                print(f"   unset {var_name}")
            
        if preload_exists:
            print("\n2. SECURE /etc/ld.so.preload:")
            print("   sudo mv /etc/ld.so.preload /etc/ld.so.preload.backup")
            print("   # Only restore after verifying contents are legitimate")
        
        if configs:
            print("\n3. REVIEW SYSTEM CONFIGURATION FILES:")
            for config_path, line_num, line in configs:
                print(f"   Check: {config_path}:{line_num}")
        
        if processes:
            print("\n4. INVESTIGATE COMPROMISED PROCESSES:")
            for pid, comm, name, value in processes:
                print(f"   Investigate process {pid} ({comm})")
                print(f"   Consider: sudo kill {pid}")
    
    print("\n🔒 GENERAL SECURITY MEASURES:")
    print("   1. Regularly audit LD environment variables")
    print("   2. Monitor /etc/ld.so.preload for changes")
    print("   3. Use file integrity monitoring (AIDE, Tripwire)")
    print("   4. Implement process monitoring (auditd)")
    print("   5. Consider using container isolation")
    print("   6. Set up log monitoring for LD variable usage")
    
    # Overall assessment
    total_issues = len(env_vars) + len(processes) + len(configs) + (1 if preload_exists else 0)
    
    if total_issues == 0:
        print("\n✅ OVERALL ASSESSMENT: SECURE")
        print("   No dangerous LD variables detected.")
    elif total_issues <= 2:
        print("\n🟡 OVERALL ASSESSMENT: MODERATE RISK")
        print(f"   {total_issues} potential issues found.")
    else:
        print("\n🔴 OVERALL ASSESSMENT: HIGH RISK")
        print(f"   {total_issues} dangerous configurations detected!")
        print("   Possible system compromise - investigate immediately!")

def main():
    """Main execution function."""
    if os.geteuid() != 0:
        print("⚠️  Running as non-root user. Some checks may be limited.")
        print("   For complete analysis, run with sudo.\n")
    
    # Perform all checks
    env_vars = check_dangerous_ld_variables()
    processes = check_process_environments()
    configs = check_system_files()
    preload_exists = check_ld_so_preload_file()
    
    # Generate recommendations
    generate_recommendations(env_vars, processes, configs, preload_exists)

if __name__ == "__main__":
    main()
