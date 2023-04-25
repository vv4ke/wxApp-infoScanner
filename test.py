import re

public_ip_regex = r'\b(?:\d{1,3}\.){3}\d{1,3}\b(?<!10\.|172\.(?:1[6-9]|2\d|3[01])\.|192\.168\.)(?<!\b127\.0\.0\.1\b)(?!255\.255\.255\.255)\b'

test_data = [
    '192.168.0.1',
    '10.0.0.1',
    '172.16.0.1',
    '172.31.255.255',
    'http://192.168.0.1/a',
    'The IP address is 10.10.10.10, which is a private IP address',
    'Our local network uses the IP address 192.168.10.1',
    'This IP address 172.20.1.1 is not valid',
    'a10.0.0.1b',
    '192.168.1.256',
    '10.256.0.1',
    'This is a public IP address: 216.58.194.174',
    'Another public IP address is 151.101.1.69',
    'The IP address 192.168.0.1 is private, but 8.8.8.8 is public'
]

for data in test_data:
    matches = re.findall(public_ip_regex, data)
    print(f"{data}: {matches}")
