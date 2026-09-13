from parsers.dns import DnsDistributor

dns = DnsDistributor(ollama_model="qwen3:8b")
results = dns.search("MSI 27")
for item in results:
    print(item)