# DEV Stake Pool - Developer Notes

## Firewall setup
#### On the relay
	sudo ufw allow proto tcp from any to any port <CARDANO_PORT>
	sudo ufw allow proto tcp from any to any port <SSH_PORT>
#### On the block producer
	sudo ufw allow proto tcp from <IP_RELAY> to any port <CARDANO_PORT>
	sudo ufw allow proto tcp from any to any port <SSH_PORT>	
