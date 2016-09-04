import dns.resolver
answers = dns.resolver.query('en.lichess.org', 'A')
for rdata in answers:
    print(rdata)
