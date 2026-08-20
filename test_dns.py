from parsers.dns import DnsDistributor

dns = DnsDistributor(ollama_model="qwen2.5-coder:3b")
results = dns.search("MSI 27")
for item in results:
    print(item)