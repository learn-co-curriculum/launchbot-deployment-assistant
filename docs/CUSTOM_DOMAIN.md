# Optional Custom Domain Note

The EC2 public DNS is enough for this lesson:

```text
http://ec2-...compute.amazonaws.com
```

For a capstone or portfolio project, you may want a friendlier domain such as:

```text
http://launchbot.example.com
```

At a high level, you would:

1. Register or use a domain.
2. Create a DNS hosted zone or use your domain provider's DNS manager.
3. Create a record for a subdomain.
4. Point that record to your EC2 instance.
5. Add HTTPS before treating the app as production-ready.

A stable custom domain usually needs a stable public address. AWS Elastic IPs can provide a stable public IPv4 address, but public IPv4 and Elastic IP resources can create charges. Check AWS pricing before adding one, and release unused resources when finished.
