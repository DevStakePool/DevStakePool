# DEV Stake Pool - Developer Notes

## Firewall setup
#### On the relay
	sudo ufw allow proto tcp from any to any port <CARDANO_PORT>
	sudo ufw allow proto tcp from any to any port <SSH_PORT>
	
	# grafana http port
	sudo ufw allow proto tcp from any to any port 3000
#### On the block producer
	sudo ufw allow proto tcp from <IP_RELAY> to any port <CARDANO_PORT>
	sudo ufw allow proto tcp from any to any port <SSH_PORT>
	
	# monitoring ports:
	sudo ufw allow proto tcp from <IP_RELAY> to any port 12798
	sudo ufw allow proto tcp from <IP_RELAY> to any port 9100
	
## Turn off some traces to reduce the missed slots
The mainnet config json file has the following traces
```
mainnet-config.json:  "TraceAcceptPolicy": true,
mainnet-config.json:  "TraceBlockFetchDecisions": true,
mainnet-config.json:  "TraceChainDb": true,
mainnet-config.json:  "TraceConnectionManager": true,
mainnet-config.json:  "TraceDNSResolver": true,
mainnet-config.json:  "TraceDNSSubscription": true,
mainnet-config.json:  "TraceDiffusionInitialization": true,
mainnet-config.json:  "TraceErrorPolicy": true,
mainnet-config.json:  "TraceForge": true,
mainnet-config.json:  "TraceInboundGovernor": true,
mainnet-config.json:  "TraceIpSubscription": true,
mainnet-config.json:  "TraceLedgerPeers": true,
mainnet-config.json:  "TraceLocalErrorPolicy": true,
mainnet-config.json:  "TraceLocalRootPeers": true,
mainnet-config.json:  "TracePeerSelection": true,
mainnet-config.json:  "TracePeerSelectionActions": true,
mainnet-config.json:  "TracePublicRootPeers": true,
mainnet-config.json:  "TraceServer": true,
```

You should keep on at least the following ones, after you are sure that everything is working as it should
```
- TraceBlockFetchDecisions
- TraceChainDb
- TraceForge
- TraceServer
```

