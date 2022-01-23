# Register Stake Pool with HW Wallet (variant of CoinCashew guide registration of the stake pool)
**Sources:**
* https://www.coincashew.com/coins/overview-ada/guide-how-to-build-a-haskell-stakepool-node#9.-generate-block-producer-keys
* https://github.com/vacuumlabs/cardano-hw-cli/blob/develop/docs/poolRegistration.md
* https://www.coincashew.com/coins/overview-ada/guide-how-to-build-a-haskell-stakepool-node/18.-operational-and-maintenance-tips#18.14-secure-your-pool-pledge-with-a-2nd-pool-owner-using-a-hardware-wallet

This guide assumes that you followed the CoinCashew guide to set up your relay/block-producer nodes

### Generate the KES key pair
First, we need to generate the stake pool KES and VRF public/private keys
```shell
# On the block producer
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

**WARN:**
The `kes.skey` and `vrf.skey` must be deleted from the block producer and moved to the air-gapped machine.

### Generate HW Wallet public keys
When using the HW walled, we don't create `cold.skey` cold key file that usually holds private key, instead we are creating `cold.hwsfile` that contains only public key and mapping for Ledger Nano devices.

```shell
#This code runs on a local computer that can access the Ledger Nano
cardano-hw-cli node key-gen \
  --path 1853H/1815H/0H/0H \
  --hw-signing-file cold.hwsfile \
  --cold-verification-key-file cold.vkey \
  --operational-certificate-issue-counter-file cold.counter
```
This operation should generate the files
* cold.hwsfile (_copy this file to your air-gapped machine_)
* cold.vkey
* cold.counter

### Calculate KES Period
**NOTE:** Before continuing, your node must be fully synchronized to the blockchain. Otherwise, you won't calculate the latest KES period.

```shell
#Run this on the block-producer

slotsPerKESPeriod=$(cat $NODE_HOME/${NODE_CONFIG}-shelley-genesis.json | jq -r '.slotsPerKESPeriod')
slotNo=$(cardano-cli query tip --mainnet | jq -r '.slot')
kesPeriod=$((${slotNo} / ${slotsPerKESPeriod}))
startKesPeriod=${kesPeriod}
echo slotsPerKESPeriod: ${slotsPerKESPeriod}
echo slotNo: ${slotNo}
echo kesPeriod: ${kesPeriod}
echo startKesPeriod: ${startKesPeriod}
```
With this calculation, you can generate an operational certificate for your pool.

### Issue the operator certificate
use the `$startKesPeriod` in the next command, replace the placeholder with the right value or set a bash variable in your environment.
```shell
#Run this on local computer that has access to the HW wallet
cardano-hw-cli node issue-op-cert \
    --kes-verification-key-file kes.vkey \
    --hw-signing-file cold.hwsfile \
    --operational-certificate-issue-counter cold.counter \
    --kes-period ${startKesPeriod} \
    --out-file node.cert
```

This following  command creates `owner-stake.vkey` and `owner-stake.hwsfile` files. These files are the staking keys of your HW wallet necessary for stake delegation and creating a witness of a stake pool registration where this hardware device is its owner.

```shell
#Run this on local computer that has access to the HW wallet
cardano-hw-cli address key-gen \
    --path 1852H/1815H/0H/2/0 \
    --hw-signing-file owner-stake.hwsfile \
    --verification-key-file owner-stake.vkey
```

Do something similar for the payment address. This will be the address where the stake pool rewards will be paid to.

**NOTE:** Make sure the HW path (e.g., 1852H/1815H/0H/0/0) you choose is a good one with at least 500+fees ADA to register the stake pool. You can use CCVault light wallet to explore the addresses. You can also pick an empty one and do a 500+ ADA internal transaction to the address chosen.
```shell
cardano-hw-cli address key-gen \ 
    --path 1852H/1815H/0H/0/1 \
    --verification-key-file owner-payment.vkey \
    --hw-signing-file owner-payment.hwsfile
```

Move the `owner-payment.vkey` and the `owner-stake.vkey` to your block producer node

### Create reward and payment addresses 

```shell
#This run on the block-producer
cardano-cli stake-address build \
    --stake-verification-key-file owner-stake.vkey \
    --out-file owner-stake.addr \
    --mainnet
```

Make sure that the generated `owner-stake.addr` contains a string that starts with `stake1u8uekde7...`. You can always double-check if the stake address is the correct one, online (e.g., https://pool.pm/).

```shell
#This run on the block-producer
cardano-cli address build \
    --payment-verification-key-file owner-payment.vkey \
    --stake-verification-key-file owner-stake.vkey \
    --out-file owner-payment.addr \
    --mainnet
```
The generated owner-payment.addr should contain your payment address `addr1qxthrv5g...`
You can check the validity in https://pool.pm/

### Create JSON metadata and its hash
Create the hash of the metadata JSON file (needs to be crated manually)
```shell
#run this on the block-producer
cardano-cli stake-pool metadata-hash \
  --pool-metadata-file metadata.json > metadata.json.hash
```

### Create pool registration certificate
Double check every argument you pass to the following command. Any mistake will require creation of a new registration certificate.

First, check the network minimal pool costs
```shell
# Run this on the block producer
grep minPoolCost mainnet-shelley-genesis.json
```
It will show an output like the following: `"minPoolCost": 340000000,`

```shell
#Run this on the air-gapped machine
# On the air gapped machine
cardano-cli stake-pool registration-certificate \
    --cold-verification-key-file hwkeys/cold.vkey \
    --vrf-verification-key-file keskeys/vrf.vkey \
    --pool-pledge 30000000000 \
    --pool-cost 340000000 \
    --pool-margin 0.01 \
    --pool-reward-account-verification-key-file hwkeys/owner-stake.vkey \
    --pool-owner-stake-verification-key-file hwkeys/owner-stake.vkey \
    --mainnet \
    --single-host-pool-relay <RELAY_DNS_NAME> \
    --pool-relay-port 6000 \
    --metadata-url <METADATA_URL_MAX_64CHAR> \
    --metadata-hash <METADATA_HASH> \
    --out-file stake-pool-registration.cert
```

Copy the output file `stake-pool-registration.cert` to your block producer machine

### Create pool registration transaction
Get the TX Hash and the TXIX of the payment address
```shell
#runs on the block producer
cardano-cli query utxo --address $(cat keys/owner-payment.addr) --mainnet
```
This will produce something like this
```shell
                           TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
aed460cb9be023ef1dd16df448yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyxxxxxxxxx    0        550000000 lovelace + TxOutDatumNone
...
```
Pick the one at the top and save the `TxHash#TxId` (note the `#` separator)

Draft the transaction

```shell
#run on the block producer
cardano-cli transaction build-raw \
    --tx-in aed460cb9be023ef1dd16df448yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyxxxxxxxxx#0 \
    --tx-out $(cat owner-payment.addr)+0 \
    --ttl 0 \
    --fee 0 \
    --out-file tx.draft \
    --certificate-file stake-pool-registration.cert \
    --mary-era
```

Before calculating the min fees, get the protocol file
```shell
#run on the block producer
cardano-cli query protocol-parameters \
    --mainnet \
    --out-file params.json
```

Then calculate the transaction fee
```shell
#run on the block producer
cardano-cli transaction calculate-min-fee \
    --tx-body-file tx.draft \
    --tx-in-count 1 \
    --tx-out-count 1 \
    --mainnet \
    --witness-count 1 \
    --byron-witness-count 0 \
    --protocol-params-file params.json
```
This will generate an output like `182969 Lovelace`

Calculate the tx-out correct value: `TOT WALLET Balance - 500000000 - 182969` (all in Lovelace):

```shell
expr 550000000 - 500000000 - 182969
```
It will output `49817031`

**NOTE:** In my case the transaction submission failed saying that the correct fee was 186225. You might have the same issue.

Build the transaction draft. Remember the `--ttl` is the tip of the blockchain plus margin (use the relay viewer)
```shell
#run on the block producer
cardano-cli transaction build-raw \
    --tx-in aed460cb9be023ef1dd16df448yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyxxxxxxxxx#0 \
    --tx-out $(cat owner-payment.addr)+49817031 \
    --ttl 51368175 \
    --fee 182969 \
    --out-file tx.draft \
    --certificate-file stake-pool-registration.cert \
    --mary-era

```
Send the `tx.draft` to the local computer that can connect to the ledger nano.

We need to witness the transaction with:
* the cold hwsfile (identifying the pool itself)
* the owner-payment hwsfile (the payment address)
* the owner-stake hwsfile (the stake address)
```shell
#runs in the local machine with access to the ledger nano
cardano-hw-cli transaction witness \
    --tx-body-file tx.draft \
    --hw-signing-file owner-payment.hwsfile \
    --hw-signing-file cold.hwsfile \
    --mainnet \
    --out-file owner-payment.witness \
    --out-file pool.witness
```

```shell
cardano-hw-cli transaction witness \
    --tx-body-file ../tx.draft \
    --hw-signing-file owner-stake.hwsfile \
    --mainnet \
    --out-file owner-stake.witness
```
Copy the `*.witness` files to the airgapped machine in order to assemble the multi-sig transaction

```shell
# runs on the air gapped machine
cardano-cli transaction assemble \
    --tx-body-file tx.draft \
    --witness-file pool.witness \
    --witness-file owner-payment.witness \
    --witness-file owner-stake.witness \
    --out-file tx.signed
```
Send the `tx.signed` to the block producer.

Finally, submit the transaction on the blockchain
```shell
#runs on the block producer 
cardano-cli transaction submit --tx-file tx.signed --mainnet
```
If you see an output like this `Transaction successfully submitted.`, congratulations, your pool is registered!

Now you can follow the rest of this: https://www.coincashew.com/coins/overview-ada/guide-how-to-build-a-haskell-stakepool-node#13.-locate-your-stake-pool-id-and-verify-everything-is-working
