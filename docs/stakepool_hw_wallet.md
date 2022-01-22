# Register Stake Pool with HW Wallet (Based on CoinCashew guide)
**Sources:**
* https://www.coincashew.com/coins/overview-ada/guide-how-to-build-a-haskell-stakepool-node#9.-generate-block-producer-keys
* https://github.com/vacuumlabs/cardano-hw-cli/blob/develop/docs/poolRegistration.md
* https://www.coincashew.com/coins/overview-ada/guide-how-to-build-a-haskell-stakepool-node/18.-operational-and-maintenance-tips#18.14-secure-your-pool-pledge-with-a-2nd-pool-owner-using-a-hardware-wallet
### Generate the KES key pair
_This code runs on the block-producer node_
```shell
cd $NODE_HOME
cardano-cli node key-gen-KES \
    --verification-key-file kes.vkey \
    --signing-key-file kes.skey
    
cardano-cli node key-gen-VRF \
--verification-key-file vrf.vkey \
--signing-key-file vrf.skey
```

**INFO:**
KES (key evolving signature) keys are created to secure your stake pool against hackers who might compromise your keys. On mainnet, you will need to regenerate the KES key every 90 days.

### Generate HW Wallet public keys
The first difference is that we don't create `cold.skey` cold key file that usually holds private key, instead we are creating `cold.hwsfile` that contains only public key and mapping for Ledger.

_This code runs on your local machine or block-producer node if hosted at home_
```shell
cardano-hw-cli node key-gen \
--path 1853H/1815H/0H/0H \
--hw-signing-file cold.hwsfile \
--cold-verification-key-file cold.vkey \
--operational-certificate-issue-counter-file cold.counter
```
This operation should generate the files
* cold.hwsfile (_copy this file to your airgapped machine_)
* cold.vkey
* cold.counter

### Calculate KES Period
**NOTE:** Before continuing, your node must be fully synchronized to the blockchain. Otherwise, you won't calculate the latest KES period.

_This code runs on the block-producer node_
```shell
pushd +1
slotsPerKESPeriod=$(cat $NODE_HOME/${NODE_CONFIG}-shelley-genesis.json | jq -r '.slotsPerKESPeriod')
echo slotsPerKESPeriod: ${slotsPerKESPeriod}
slotNo=$(cardano-cli query tip --mainnet | jq -r '.slot')
echo slotNo: ${slotNo}
kesPeriod=$((${slotNo} / ${slotsPerKESPeriod}))
echo kesPeriod: ${kesPeriod}
startKesPeriod=${kesPeriod}
echo startKesPeriod: ${startKesPeriod}
```
With this calculation, you can generate an operational certificate for your pool.
Copy `kes.vkey` to your cold environment.

### Issue the operator certificate
_This code runs on the airgapped machine_
```shell
cardano-hw-cli node issue-op-cert \
    --kes-verification-key-file kes.vkey \
    --hw-signing-file cold.hwsfile \
    --operational-certificate-issue-counter cold.counter \
    --kes-period ${startKesPeriod} \
    --out-file node.cert
```

_This code runs on the local machine connected to the HW wallet_
```shell
cardano-hw-cli address key-gen \
    --path 1852H/1815H/0H/2/0 \
    --hw-signing-file owner-stake.hwsfile \
    --verification-key-file owner-stake.vkey
```
This command creates `owner-stake.vkey` and `owner-stake.hwsfile` files. These files are the staking keys of your HW wallet necessary for stake delegation and creating a witness of a stake pool registration where this hardware device is its owner.

Do something similar for the payment address. This will be the address where the stake pool rewards will be payed to.
```shell
cardano-hw-cli address key-gen \
    --path 1852H/1815H/0H/0/0 \
    --verification-key-file owner-payment.vkey \
    --hw-signing-file owner-payment.hwsfile
```

### Create reward address
_This code runs on the block-producer node_
```shell
cardano-cli stake-address build \
    --stake-verification-key-file owner-stake.vkey \
    --out-file owner-stake.addr \
    --mainnet
```
This command creates a reward address, where all the pool rewards will go.

Finally, create the payment address
```shell
cardano-cli address build \
    --payment-verification-key-file owner-payment.vkey \
    --stake-verification-key-file owner-stake.vkey \
    --out-file owner-payment.addr \
    --mainnet
```

You can always check both owner-stake.addr content and owner-payment.addr on https://pool.pm/ to make sure they are the right ones

### Create JSON metadata and its hash
_On the block producer, run the following code to create the hash of the metadata JSON file (needs to be crated manually)_
```shell
cardano-cli stake-pool metadata-hash --pool-metadata-file metadata.json > metadata.json.hash
```

### Create pool registration certificate
Double check every argument you pass to the following command. Any mistake will require creation of a new registration certificate.

_This code runs on the block-producer node_
```shell
cardano-cli stake-pool registration-certificate \
    --cold-verification-key-file cold.vkey \
    --vrf-verification-key-file vrf.vkey \
    --pool-pledge 50000000000 \
    --pool-cost 340000000 \
    --pool-margin 0.01 \
    --pool-reward-account-verification-key-file owner-stake.vkey \
    --pool-owner-stake-verification-key-file owner-stake.vkey \
    --mainnet \
    --pool-relay-ipv4 54.228.75.154 \
    --pool-relay-port 3000 \
    --pool-relay-ipv4 54.228.75.155 \
    --pool-relay-ipv6 24ff:7801:33a2:e383:a5c4:340a:07c2:76e5 \
    --pool-relay-port 3000 \
    --single-host-pool-relay aaaa.bbbb.com \
    --pool-relay-port 3000 \
    --multi-host-pool-relay aaaa.bbbc.com \
    --metadata-url https://www.vacuumlabs.com/sampleUrl.json \
    --metadata-hash 790be88f23c12ffa0fde8124814ceb97779fa45b1e0d654e52055e1d8cab53a0 \
    --out-file pool-registration.cert
```
