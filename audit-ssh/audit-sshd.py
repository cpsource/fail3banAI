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
        self.config = {}
        self.comments = []
        self.issues = []
        
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
    
    def parse_config(self) -> bool:
        """Parse the SSH configuration file."""
        if not os.path.exists(self.config_path):
            print(f"❌ Error: SSH config file not found: {self.config_path}")
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
        except PermissionError:
            print(f"❌ Error: Permission denied reading {self.config_path}")
            print("   Try running with sudo for complete analysis")
            return False
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                if line.startswith('#'):
                    self.comments.append((line_num, line))
                continue
            
            # Parse key-value pairs
            parts = line.split(None, 1)
            if len(parts) >= 2:
                key = parts[0].lower()
                value = parts[1].strip()
                self.config[key] = value
            elif len(parts) == 1:
                # Handle boolean-only directives
                self.config[parts[0].lower()] = "yes"
        
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
    
    def generate_report(self, target_level: SecurityLevel) -> None:
        """Generate a comprehensive security audit report."""
        print("🔒 SSH CONFIGURATION SECURITY AUDIT")
        print("=" * 60)
        print(f"📁 Configuration file: {self.config_path}")
        print(f"🎯 Target security level: {target_level.value.upper()}")
        print(f"📝 {self.recommendations[target_level]['description']}")
        print(f"🏢 Use case: {self.recommendations[target_level]['use_case']}")
        print()
        
        # Check for dangerous configurations first
        dangerous_issues = self.check_dangerous_configurations()
        if dangerous_issues:
            print("🚨 CRITICAL SECURITY ISSUES FOUND:")
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
        
        # Generate configuration recommendations
        self.generate_config_template(target_level)
        
        # Overall assessment
        total_issues = len(dangerous_issues) + len(level_issues)
        critical_issues = len([i for i in dangerous_issues if i["severity"] == "critical"])
        
        print("\n🏁 OVERALL ASSESSMENT:")
        print("-" * 40)
        
        if critical_issues > 0:
            print("🔴 CRITICAL: System has severe security vulnerabilities!")
            print(f"   {critical_issues} critical issues must be fixed immediately")
        elif total_issues == 0:
            print("✅ EXCELLENT: Configuration meets target security level")
        elif total_issues <= 3:
            print("🟡 GOOD: Minor improvements needed")
            print(f"   {total_issues} issues to address")
        else:
            print("🟠 NEEDS IMPROVEMENT: Multiple security issues found")
            print(f"   {total_issues} issues to address")
        
        print(f"\n📊 Summary: {total_issues} total issues found")
        if dangerous_issues:
            print(f"   🚨 {len(dangerous_issues)} critical/dangerous configurations")
        if level_issues:
            print(f"   📋 {len(level_issues)} security level improvements")
    
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

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSH Configuration Security Auditor")
    parser.add_argument("--config", default="/etc/ssh/sshd_config", 
                       help="Path to sshd_config file")
    parser.add_argument("--level", choices=["none", "low", "medium", "high"], 
                       default="high", help="Target security level")
    parser.add_argument("--template-only", action="store_true",
                       help="Only generate configuration template")
    
    args = parser.parse_args()
    
    # Convert string to enum
    level_map = {
        "none": SecurityLevel.NONE,
        "low": SecurityLevel.LOW, 
        "medium": SecurityLevel.MEDIUM,
        "high": SecurityLevel.HIGH
    }
    target_level = level_map[args.level]
    
    auditor = SSHConfigAuditor(args.config)
    
    if args.template_only:
        print(f"🔒 SSH {args.level.upper()} SECURITY CONFIGURATION TEMPLATE")
        print("=" * 60)
        auditor.generate_config_template(target_level)
        return
    
    # Parse and audit configuration
    if not auditor.parse_config():
        sys.exit(1)
    
    auditor.generate_report(target_level)

if __name__ == "__main__":
    main()
