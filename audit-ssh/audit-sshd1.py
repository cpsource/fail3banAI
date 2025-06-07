#!/usr/bin/env python3
"""
SSH Configuration Security Auditor

This script audits /etc/ssh/sshd_config for security best practices.
It evaluates configurations against different security levels and provides
specific recommendations for hardening SSH access.

Think of this as a security consultant specifically for SSH - it knows
all the ways SSH can be compromised and how to prevent them.
"""

import os
import re
import sys
from pathlib import Path
from enum import Enum
from typing import Dict, List, Tuple, Optional

class SecurityLevel(Enum):
    NONE = "none"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"

class SSHConfigAuditor:
    def __init__(self, config_path: str = "/etc/ssh/sshd_config"):
        self.config_path = config_path
        self.config_dir = "/etc/ssh/sshd_config.d"
        self.config = {}
        self.comments = []
        self.issues = []
        self.parsed_files = []
        
        # Security recommendations by level
        self.recommendations = {
            SecurityLevel.NONE: {
                "description": "Minimal security - basic SSH functionality",
                "use_case": "Development environments, internal networks only"
            },
            SecurityLevel.LOW: {
                "description": "Basic security hardening",
                "use_case": "Internal servers with some network isolation"
            },
            SecurityLevel.MEDIUM: {
                "description": "Strong security for most production environments", 
                "use_case": "Production servers, business environments"
            },
            SecurityLevel.HIGH: {
                "description": "Maximum security hardening",
                "use_case": "Critical systems, high-value targets, compliance requirements"
            }
        }
        
        # Define security rules for each level
        self.security_rules = self._define_security_rules()
    
    def _define_security_rules(self) -> Dict[SecurityLevel, Dict]:
        """Define security configuration rules for each security level."""
        return {
            SecurityLevel.NONE: {
                "Port": {"value": "22", "required": False},
                "PasswordAuthentication": {"value": "yes", "required": False},
                "PermitRootLogin": {"value": "yes", "required": False},
                "PubkeyAuthentication": {"value": "yes", "required": False},
            },
            
            SecurityLevel.LOW: {
                "Port": {"value": "2222", "required": True, "reason": "Non-standard port reduces automated attacks"},
                "PasswordAuthentication": {"value": "no", "required": True, "reason": "Prevent brute force attacks"},
                "PermitRootLogin": {"value": "no", "required": True, "reason": "Prevent direct root access"},
                "PubkeyAuthentication": {"value": "yes", "required": True, "reason": "Enable key-based authentication"},
                "Protocol": {"value": "2", "required": True, "reason": "Use secure SSH protocol version"},
                "X11Forwarding": {"value": "no", "required": True, "reason": "Disable X11 forwarding"},
                "MaxAuthTries": {"value": "3", "required": True, "reason": "Limit authentication attempts"},
            },
            
            SecurityLevel.MEDIUM: {
                "Port": {"value": "2222", "required": True, "reason": "Non-standard port reduces automated attacks"},
                "PasswordAuthentication": {"value": "no", "required": True, "reason": "Prevent brute force attacks"},
                "PermitRootLogin": {"value": "no", "required": True, "reason": "Prevent direct root access"},
                "PubkeyAuthentication": {"value": "yes", "required": True, "reason": "Enable key-based authentication"},
                "Protocol": {"value": "2", "required": True, "reason": "Use secure SSH protocol version"},
                "X11Forwarding": {"value": "no", "required": True, "reason": "Disable X11 forwarding"},
                "MaxAuthTries": {"value": "2", "required": True, "reason": "Limit authentication attempts"},
                "ClientAliveInterval": {"value": "300", "required": True, "reason": "Timeout idle connections"},
                "ClientAliveCountMax": {"value": "2", "required": True, "reason": "Limit keepalive messages"},
                "AllowUsers": {"value": "", "required": True, "reason": "Whitelist specific users only"},
                "DenyUsers": {"value": "root", "required": True, "reason": "Explicitly deny dangerous users"},
                "LoginGraceTime": {"value": "30", "required": True, "reason": "Reduce login timeout window"},
                "MaxStartups": {"value": "2", "required": True, "reason": "Limit concurrent connections"},
                "PermitEmptyPasswords": {"value": "no", "required": True, "reason": "Prevent empty password login"},
                "StrictModes": {"value": "yes", "required": True, "reason": "Check file permissions"},
                "IgnoreRhosts": {"value": "yes", "required": True, "reason": "Ignore insecure .rhosts"},
                "HostbasedAuthentication": {"value": "no", "required": True, "reason": "Disable host-based auth"},
                "PermitUserEnvironment": {"value": "no", "required": True, "reason": "Prevent environment manipulation"},
                "Ciphers": {"value": "chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr", "required": True, "reason": "Use only secure ciphers"},
                "MACs": {"value": "hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha2-512", "required": True, "reason": "Use secure MAC algorithms"},
                "KexAlgorithms": {"value": "curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512", "required": True, "reason": "Use secure key exchange"},
            },
            
            SecurityLevel.HIGH: {
                "Port": {"value": "2222", "required": True, "reason": "Non-standard port reduces automated attacks"},
                "PasswordAuthentication": {"value": "no", "required": True, "reason": "Prevent brute force attacks"},
                "ChallengeResponseAuthentication": {"value": "no", "required": True, "reason": "Disable challenge-response"},
                "KerberosAuthentication": {"value": "no", "required": True, "reason": "Disable Kerberos unless specifically needed"},
                "GSSAPIAuthentication": {"value": "no", "required": True, "reason": "Disable GSSAPI unless specifically needed"},
                "PermitRootLogin": {"value": "no", "required": True, "reason": "Prevent direct root access"},
                "PubkeyAuthentication": {"value": "yes", "required": True, "reason": "Enable key-based authentication"},
                "AuthorizedKeysFile": {"value": ".ssh/authorized_keys", "required": True, "reason": "Standard key location"},
                "Protocol": {"value": "2", "required": True, "reason": "Use secure SSH protocol version"},
                "X11Forwarding": {"value": "no", "required": True, "reason": "Disable X11 forwarding"},
                "X11UseLocalhost": {"value": "yes", "required": True, "reason": "Secure X11 if enabled"},
                "PrintMotd": {"value": "no", "required": True, "reason": "Reduce information disclosure"},
                "PrintLastLog": {"value": "no", "required": True, "reason": "Reduce information disclosure"},
                "TCPKeepAlive": {"value": "no", "required": True, "reason": "Prevent connection hijacking"},
                "UseLogin": {"value": "no", "required": True, "reason": "Prevent login program bypass"},
                "MaxAuthTries": {"value": "1", "required": True, "reason": "Minimize authentication attempts"},
                "ClientAliveInterval": {"value": "150", "required": True, "reason": "Aggressive timeout for idle connections"},
                "ClientAliveCountMax": {"value": "0", "required": True, "reason": "No keepalive tolerance"},
                "Compression": {"value": "no", "required": True, "reason": "Prevent compression attacks"},
                "AllowUsers": {"value": "", "required": True, "reason": "Whitelist specific users only (configure manually)"},
                "DenyUsers": {"value": "root bin daemon adm lp sync shutdown halt mail operator games ftp nobody", "required": True, "reason": "Deny system accounts"},
                "AllowGroups": {"value": "", "required": True, "reason": "Whitelist specific groups only"},
                "LoginGraceTime": {"value": "15", "required": True, "reason": "Minimal login timeout window"},
                "MaxStartups": {"value": "1:30:2", "required": True, "reason": "Severely limit concurrent connections"},
                "MaxSessions": {"value": "1", "required": True, "reason": "One session per connection"},
                "PermitEmptyPasswords": {"value": "no", "required": True, "reason": "Prevent empty password login"},
                "PermitTunnel": {"value": "no", "required": True, "reason": "Disable tunnel capabilities"},
                "PermitTTY": {"value": "yes", "required": True, "reason": "Allow TTY for legitimate use"},
                "StrictModes": {"value": "yes", "required": True, "reason": "Strict file permission checking"},
                "IgnoreRhosts": {"value": "yes", "required": True, "reason": "Ignore insecure .rhosts"},
                "IgnoreUserKnownHosts": {"value": "yes", "required": True, "reason": "Ignore user known_hosts"},
                "HostbasedAuthentication": {"value": "no", "required": True, "reason": "Disable host-based authentication"},
                "PermitUserEnvironment": {"value": "no", "required": True, "reason": "Prevent environment variable manipulation"},
                "AcceptEnv": {"value": "", "required": True, "reason": "Disable environment variable passing"},
                "AllowAgentForwarding": {"value": "no", "required": True, "reason": "Disable SSH agent forwarding"},
                "AllowTcpForwarding": {"value": "no", "required": True, "reason": "Disable TCP forwarding"},
                "GatewayPorts": {"value": "no", "required": True, "reason": "Disable gateway ports"},
                "PermitOpen": {"value": "none", "required": True, "reason": "Disable port forwarding"},
                "ForceCommand": {"value": "", "required": False, "reason": "Force specific command (optional)"},
                "ChrootDirectory": {"value": "", "required": False, "reason": "Chroot users (configure if needed)"},
                "Banner": {"value": "/etc/ssh/banner", "required": True, "reason": "Display legal banner"},
                "VersionAddendum": {"value": "", "required": True, "reason": "Hide SSH version info"},
                "DebianBanner": {"value": "no", "required": True, "reason": "Hide Debian version banner"},
                "LogLevel": {"value": "VERBOSE", "required": True, "reason": "Detailed logging for security monitoring"},
                "SyslogFacility": {"value": "AUTHPRIV", "required": True, "reason": "Log to secure facility"},
                "UseDNS": {"value": "no", "required": True, "reason": "Disable DNS lookups"},
                "AddressFamily": {"value": "inet", "required": True, "reason": "IPv4 only (or inet6 for IPv6)"},
                "ListenAddress": {"value": "0.0.0.0", "required": True, "reason": "Specify bind address"},
                "RekeyLimit": {"value": "512M 1h", "required": True, "reason": "Force periodic key renegotiation"},
                "Ciphers": {"value": "chacha20-poly1305@openssh.com,aes256-gcm@openssh.com", "required": True, "reason": "Only strongest ciphers"},
                "MACs": {"value": "hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com", "required": True, "reason": "Only strongest MAC algorithms"},
                "KexAlgorithms": {"value": "curve25519-sha256@libssh.org", "required": True, "reason": "Only strongest key exchange"},
                "HostKeyAlgorithms": {"value": "ssh-ed25519,ssh-ed25519-cert-v01@openssh.com", "required": True, "reason": "Only strongest host key algorithms"},
                "PubkeyAcceptedKeyTypes": {"value": "ssh-ed25519,ssh-ed25519-cert-v01@openssh.com", "required": True, "reason": "Only strongest public key types"},
                "AuthenticationMethods": {"value": "publickey", "required": True, "reason": "Require specific auth methods"},
                "RequiredRSASize": {"value": "4096", "required": True, "reason": "Minimum RSA key size"},
            }
        }
    
    def parse_config_file(self, file_path: str) -> Tuple[Dict, List]:
        """Parse a single SSH configuration file."""
        config = {}
        comments = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except PermissionError:
            print(f"⚠️  Warning: Permission denied reading {file_path}")
            return config, comments
        except Exception as e:
            print(f"⚠️  Warning: Error reading {file_path}: {e}")
            return config, comments
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                if line.startswith('#'):
                    comments.append((line_num, line))
                continue
            
            # Parse key-value pairs
            parts = line.split(None, 1)
            if len(parts) >= 2:
                key = parts[0].lower()
                value = parts[1].strip()
                # SSH config uses last-match-wins for most directives
                config[key] = value
            elif len(parts) == 1:
                # Handle boolean-only directives
                config[parts[0].lower()] = "yes"
        
        return config, comments

    def parse_config(self) -> bool:
        """Parse the SSH configuration file and any include files."""
        # Parse main config file
        if not os.path.exists(self.config_path):
            print(f"❌ Error: SSH config file not found: {self.config_path}")
            return False
        
        print(f"📖 Parsing main configuration file: {self.config_path}")
        main_config, main_comments = self.parse_config_file(self.config_path)
        self.config.update(main_config)
        self.comments.extend(main_comments)
        self.parsed_files.append(self.config_path)
        
        # Parse configuration directory files
        if os.path.exists(self.config_dir) and os.path.isdir(self.config_dir):
            print(f"📁 Checking configuration directory: {self.config_dir}")
            try:
                config_files = []
                for file_name in os.listdir(self.config_dir):
                    file_path = os.path.join(self.config_dir, file_name)
                    # Only process .conf files
                    if os.path.isfile(file_path) and file_name.endswith('.conf'):
                        config_files.append((file_name, file_path))
                
                # Sort files to ensure consistent processing order
                config_files.sort()
                
                if config_files:
                    print(f"   Found {len(config_files)} configuration files:")
                    for file_name, file_path in config_files:
                        print(f"   📄 Parsing: {file_name}")
                        file_config, file_comments = self.parse_config_file(file_path)
                        # Later files override earlier ones (SSH behavior)
                        self.config.update(file_config)
                        self.comments.extend(file_comments)
                        self.parsed_files.append(file_path)
                else:
                    print("   ℹ️  No .conf files found in configuration directory")
                    
            except PermissionError:
                print(f"⚠️  Warning: Permission denied accessing {self.config_dir}")
            except Exception as e:
                print(f"⚠️  Warning: Error processing config directory: {e}")
        else:
            print(f"ℹ️  Configuration directory not found: {self.config_dir}")
        
        # Check for Include directives in parsed config
        if 'include' in self.config:
            print(f"ℹ️  Found Include directive: {self.config['include']}")
            print("   Note: Include files should be processed by SSH automatically")
        
        print(f"✅ Successfully parsed {len(self.parsed_files)} configuration files")
        return True
    
    def audit_security_level(self, level: SecurityLevel) -> List[Dict]:
        """Audit configuration against a specific security level."""
        issues = []
        rules = self.security_rules[level]
        
        for directive, rule_config in rules.items():
            key = directive.lower()
            expected_value = rule_config["value"]
            required = rule_config["required"]
            reason = rule_config.get("reason", "Security best practice")
            
            current_value = self.config.get(key, "")
            
            if required and key not in self.config:
                issues.append({
                    "severity": "high" if level in [SecurityLevel.HIGH, SecurityLevel.MEDIUM] else "medium",
                    "directive": directive,
                    "issue": "missing",
                    "current": "not set",
                    "expected": expected_value,
                    "reason": reason
                })
            elif key in self.config and current_value.lower() != expected_value.lower():
                if expected_value:  # Only flag if we have a specific expected value
                    issues.append({
                        "severity": "medium",
                        "directive": directive,
                        "issue": "incorrect_value",
                        "current": current_value,
                        "expected": expected_value,
                        "reason": reason
                    })
        
        return issues
    
    def check_dangerous_configurations(self) -> List[Dict]:
        """Check for inherently dangerous configurations."""
        dangerous_issues = []
        
        # Critical security checks that apply to all levels
        critical_checks = [
            {
                "directive": "PermitRootLogin",
                "dangerous_values": ["yes"],
                "reason": "Direct root login is extremely dangerous"
            },
            {
                "directive": "PasswordAuthentication", 
                "dangerous_values": ["yes"],
                "reason": "Password authentication vulnerable to brute force"
            },
            {
                "directive": "PermitEmptyPasswords",
                "dangerous_values": ["yes"],
                "reason": "Empty passwords provide no security"
            },
            {
                "directive": "Protocol",
                "dangerous_values": ["1", "1,2"],
                "reason": "SSH protocol version 1 has known vulnerabilities"
            },
            {
                "directive": "MaxAuthTries",
                "dangerous_threshold": 6,
                "reason": "Too many authentication attempts enable brute force"
            }
        ]
        
        for check in critical_checks:
            directive = check["directive"]
            key = directive.lower()
            
            if key in self.config:
                current_value = self.config[key]
                
                # Check dangerous values
                if "dangerous_values" in check:
                    if current_value.lower() in [v.lower() for v in check["dangerous_values"]]:
                        dangerous_issues.append({
                            "severity": "critical",
                            "directive": directive,
                            "issue": "dangerous_value",
                            "current": current_value,
                            "reason": check["reason"]
                        })
                
                # Check dangerous thresholds
                if "dangerous_threshold" in check:
                    try:
                        if int(current_value) > check["dangerous_threshold"]:
                            dangerous_issues.append({
                                "severity": "high",
                                "directive": directive,
                                "issue": "threshold_exceeded",
                                "current": current_value,
                                "threshold": str(check["dangerous_threshold"]),
                                "reason": check["reason"]
                            })
                    except ValueError:
                        pass
        
        return dangerous_issues
    
    def calculate_security_score(self, target_level: SecurityLevel) -> Tuple[int, int, str]:
        """Calculate security score for the target level."""
        dangerous_issues = self.check_dangerous_configurations()
        level_issues = self.audit_security_level(target_level)
        
        # Critical issues are automatic failures
        critical_issues = len([i for i in dangerous_issues if i["severity"] == "critical"])
        if critical_issues > 0:
            return 0, critical_issues + len(level_issues), "FAIL"
        
        # Calculate score based on compliance
        total_rules = len(self.security_rules[target_level])
        failed_rules = len(level_issues)
        compliance_percentage = ((total_rules - failed_rules) / total_rules) * 100 if total_rules > 0 else 100
        
        # Determine pass/fail based on target level requirements
        pass_thresholds = {
            SecurityLevel.NONE: 50,    # Very lenient
            SecurityLevel.LOW: 70,     # Basic compliance
            SecurityLevel.MEDIUM: 85,  # Good compliance  
            SecurityLevel.HIGH: 95     # Near perfect compliance
        }
        
        threshold = pass_thresholds[target_level]
        result = "PASS" if compliance_percentage >= threshold else "FAIL"
        
        return int(compliance_percentage), len(dangerous_issues) + len(level_issues), result

    def generate_report(self, target_level: SecurityLevel) -> None:
        """Generate a comprehensive security audit report."""
        print("🔒 SSH CONFIGURATION SECURITY AUDIT")
        print("=" * 60)
        print(f"📁 Configuration files analyzed:")
        for file_path in self.parsed_files:
            print(f"   • {file_path}")
        print(f"🎯 Target security level: {target_level.value.upper()}")
        print(f"📝 {self.recommendations[target_level]['description']}")
        print(f"🏢 Use case: {self.recommendations[target_level]['use_case']}")
        print()
        
        # Calculate security score
        score, total_issues, result = self.calculate_security_score(target_level)
        
        # Display pass/fail prominently
        result_icon = "✅" if result == "PASS" else "❌"
        result_color = "PASS" if result == "PASS" else "FAIL"
        print(f"🏆 SECURITY ASSESSMENT RESULT: {result_icon} {result_color}")
        print(f"📊 Compliance Score: {score}% ({total_issues} issues found)")
        print("=" * 60)
        
        # Check for dangerous configurations first
        dangerous_issues = self.check_dangerous_configurations()
        if dangerous_issues:
            print("\n🚨 CRITICAL SECURITY ISSUES FOUND:")
            print("-" * 40)
            for issue in dangerous_issues:
                severity_icon = "🔴" if issue["severity"] == "critical" else "🟠"
                print(f"{severity_icon} {issue['directive']}: {issue['current']}")
                print(f"   Issue: {issue['reason']}")
                if "threshold" in issue:
                    print(f"   Threshold exceeded: {issue['current']} > {issue['threshold']}")
                print()
        
        # Audit against target level
        level_issues = self.audit_security_level(target_level)
        
        if level_issues:
            print(f"📋 {target_level.value.upper()} SECURITY LEVEL ISSUES:")
            print("-" * 40)
            
            # Group by severity
            by_severity = {}
            for issue in level_issues:
                severity = issue["severity"]
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)
            
            for severity in ["high", "medium", "low"]:
                if severity in by_severity:
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[severity]
                    print(f"\n{severity_icon} {severity.upper()} PRIORITY:")
                    
                    for issue in by_severity[severity]:
                        if issue["issue"] == "missing":
                            print(f"   ❌ {issue['directive']} is not configured")
                            if issue["expected"]:
                                print(f"      Should be: {issue['expected']}")
                        else:
                            print(f"   ⚠️  {issue['directive']}: {issue['current']}")
                            print(f"      Should be: {issue['expected']}")
                        print(f"      Reason: {issue['reason']}")
                        print()
        
        # Show what's configured correctly
        if score > 0:
            print(f"\n✅ CORRECTLY CONFIGURED ITEMS:")
            print("-" * 40)
            rules = self.security_rules[target_level]
            correct_count = 0
            for directive, rule_config in rules.items():
                key = directive.lower()
                expected_value = rule_config["value"]
                current_value = self.config.get(key, "")
                
                if key in self.config and current_value.lower() == expected_value.lower():
                    print(f"   ✓ {directive}: {current_value}")
                    correct_count += 1
            
            if correct_count == 0:
                print("   (No items meet the target security level requirements)")
        
        # Generate configuration recommendations if failed
        if result == "FAIL":
            print(f"\n📝 TO ACHIEVE {target_level.value.upper()} SECURITY LEVEL:")
            print("-" * 40)
            print("Apply the following configuration changes:")
            self.generate_config_template(target_level)
        
        # Final assessment with specific guidance
        print(f"\n🏁 FINAL ASSESSMENT:")
        print("-" * 40)
        
        if result == "PASS":
            print(f"🎉 CONGRATULATIONS! Your SSH configuration meets {target_level.value.upper()} security standards.")
            if total_issues > 0:
                print(f"   Minor improvements available: {total_issues} optional enhancements")
            print("   Your system is appropriately secured for its intended use case.")
        else:
            critical_count = len([i for i in dangerous_issues if i["severity"] == "critical"])
            if critical_count > 0:
                print("🚨 IMMEDIATE ACTION REQUIRED!")
                print(f"   {critical_count} critical vulnerabilities must be fixed NOW")
                print("   System is at HIGH RISK of compromise")
            else:
                print(f"🔧 CONFIGURATION IMPROVEMENTS NEEDED")
                print(f"   {total_issues} issues prevent meeting {target_level.value.upper()} security level")
                print("   Address the issues above to improve security posture")
        
        print(f"\n📊 Final Summary:")
        print(f"   Security Level: {target_level.value.upper()}")
        print(f"   Compliance Score: {score}%")
        print(f"   Total Issues: {total_issues}")
        print(f"   Result: {result}")
        
        if result == "FAIL":
            print(f"\n💡 Next Steps:")
            print("   1. Review and fix CRITICAL issues immediately")
            print("   2. Apply recommended configuration changes")
            print("   3. Test configuration: sudo sshd -t")
            print("   4. Reload SSH service: sudo systemctl reload sshd")
            print("   5. Re-run this audit to verify improvements")
    
    def generate_config_template(self, level: SecurityLevel) -> None:
        """Generate a secure configuration template."""
        print(f"\n📝 RECOMMENDED {level.value.upper()} SECURITY CONFIGURATION:")
        print("-" * 60)
        print("# Copy this configuration to /etc/ssh/sshd_config")
        print("# Remember to backup the original file first!")
        print("# sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup")
        print()
        
        rules = self.security_rules[level]
        
        # Group directives by category
        categories = {
            "Basic Settings": ["Port", "Protocol", "AddressFamily", "ListenAddress"],
            "Authentication": ["PasswordAuthentication", "PubkeyAuthentication", "PermitRootLogin", 
                             "AuthenticationMethods", "MaxAuthTries", "LoginGraceTime", "PermitEmptyPasswords"],
            "Cryptography": ["Ciphers", "MACs", "KexAlgorithms", "HostKeyAlgorithms", "PubkeyAcceptedKeyTypes", "RekeyLimit"],
            "Access Control": ["AllowUsers", "DenyUsers", "AllowGroups", "MaxStartups", "MaxSessions"],
            "Forwarding": ["X11Forwarding", "AllowTcpForwarding", "AllowAgentForwarding", "GatewayPorts", "PermitTunnel"],
            "Timeouts": ["ClientAliveInterval", "ClientAliveCountMax", "TCPKeepAlive"],
            "Logging": ["LogLevel", "SyslogFacility"],
            "Security": ["StrictModes", "IgnoreRhosts", "HostbasedAuthentication", "PermitUserEnvironment", "UseDNS"]
        }
        
        for category, directives in categories.items():
            has_directives = any(d in rules for d in directives)
            if has_directives:
                print(f"# {category}")
                for directive in directives:
                    if directive in rules and rules[directive]["value"]:
                        value = rules[directive]["value"]
                        print(f"{directive} {value}")
                print()
        
        # Add any remaining directives not in categories
        other_directives = set(rules.keys()) - set(sum(categories.values(), []))
        if other_directives:
            print("# Additional Settings")
            for directive in sorted(other_directives):
                if rules[directive]["value"]:
                    value = rules[directive]["value"]
                    print(f"{directive} {value}")
            print()
        
        print("# After updating configuration:")
        print("# sudo sshd -t  # Test configuration")
        print("# sudo systemctl reload sshd  # Apply changes")

def prompt_for_security_level() -> SecurityLevel:
    """Interactively prompt user for desired security level."""
    print("🔒 SSH SECURITY LEVEL SELECTION")
    print("=" * 50)
    print("Please choose your desired security level:\n")
    
    levels = [
        (SecurityLevel.NONE, "🟢 NONE", "Minimal security - basic SSH functionality", 
         "• Development environments\n• Internal networks only\n• No security restrictions"),
        
        (SecurityLevel.LOW, "🟡 LOW", "Basic security hardening",
         "• Internal servers\n• Some network isolation\n• Basic authentication controls"),
        
        (SecurityLevel.MEDIUM, "🟠 MEDIUM", "Strong security for production environments",
         "• Production servers\n• Business environments\n• Comprehensive security controls"),
        
        (SecurityLevel.HIGH, "🔴 HIGH", "Maximum security hardening", 
         "• Critical systems\n• High-value targets\n• Compliance requirements\n• Zero-trust environments")
    ]
    
    for i, (level, name, desc, details) in enumerate(levels, 1):
        print(f"{i}. {name}")
        print(f"   {desc}")
        print(f"   Use cases:")
        for line in details.split('\n'):
            if line.strip():
                print(f"     {line}")
        print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                selected_level = levels[int(choice) - 1][0]
                selected_name = levels[int(choice) - 1][1]
                print(f"\n✓ Selected: {selected_name}")
                print(f"  {levels[int(choice) - 1][2]}")
                confirm = input("\nConfirm this selection? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return selected_level
                else:
                    print("\nPlease make another selection:\n")
                    continue
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)
        except EOFError:
            print("\nExiting...")
            sys.exit(0)

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSH Configuration Security Auditor")
    parser.add_argument("--config", default="/etc/ssh/sshd_config", 
                       help="Path to sshd_config file")
    parser.add_argument("--level", choices=["none", "low", "medium", "high"], 
                       help="Target security level (if not specified, will prompt)")
    parser.add_argument("--template-only", action="store_true",
                       help="Only generate configuration template")
    parser.add_argument("--no-interactive", action="store_true",
                       help="Disable interactive prompts (use with --level)")
    
    args = parser.parse_args()
    
    # Determine security level
    if args.level:
        level_map = {
            "none": SecurityLevel.NONE,
            "low": SecurityLevel.LOW, 
            "medium": SecurityLevel.MEDIUM,
            "high": SecurityLevel.HIGH
        }
        target_level = level_map[args.level]
    elif args.no_interactive:
        print("Error: --no-interactive requires --level to be specified")
        sys.exit(1)
    else:
        target_level = prompt_for_security_level()
    
    auditor = SSHConfigAuditor(args.config)
    
    if args.template_only:
        print(f"🔒 SSH {target_level.value.upper()} SECURITY CONFIGURATION TEMPLATE")
        print("=" * 60)
        auditor.generate_config_template(target_level)
        return
    
    # Parse and audit configuration
    if not auditor.parse_config():
        sys.exit(1)
    
    auditor.generate_report(target_level)

if __name__ == "__main__":
    main()
