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

