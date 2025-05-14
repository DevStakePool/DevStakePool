# Change of Stake Pool parameters with HW Wallet

First you need to regenerate a new certificate

```shell
# runs on airdropped machine
cardano-cli latest stake-pool registration-certificate \
    --cold-verification-key-file hwkeys/cold.vkey \
    --vrf-verification-key-file keskeys/vrf.vkey \
    --pool-pledge 40000000000 \
    --pool-cost 340000000 \
    --pool-margin 0.0199 \
    --pool-reward-account-verification-key-file hwkeys/owner-stake.vkey \
    --pool-owner-stake-verification-key-file hwkeys/owner-stake.vkey \
    --mainnet \
    --single-host-pool-relay relay-host-name.com \
    --pool-relay-port 6000 \
    --metadata-url https://foo/bar/metadata.json \
    --metadata-hash 9d6f69d03df0024da24XXXXXXXXXXXXXXXXXXXX \
    --out-file stake-pool-registration-$(date '+%Y-%m-%dT%H%M%S').cert
```

Check your payment addr balance:
```shell
cardano-cli query utxo --address $(cat owner-payment.addr) --mainnet
```
you'll get something like this:
```
                           TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
282f1f9ecdfba373f70a0c29babbc4XXXXXXXXXXXXXXXXXXXXXXX                0        10000000 lovelace + TxOutDatumNone
```

Start building your Transaction to submit the new certificate
```shell

#run on the block producer
cardano-cli transaction build-raw \
    --tx-in 282f1f9ecdfba373f70a0c29babbc4XXXXXXXXXXXXXXXXXXXXXXX#0 \
    --tx-out $(cat owner-payment.addr)+0 \
    --ttl 0 \
    --fee 0 \
    --out-file tx.draft \
    --certificate-file stake-pool-registration-*********.cert \
    --alonzo-era 
```
Move the file `tx.draft` to the block producer

```shell
# Calculate min fees
# run this on the block producer 
cardano-cli transaction calculate-min-fee \
--tx-body-file tx.draft \
--tx-in-count 1 \
--tx-out-count 1 \
--mainnet \
--witness-count 3 \
--byron-witness-count 0 \
--protocol-params-file params.json
```
The output should be similar to 
```
195201 Lovelace
```
I always round up higher because sometimes it's not accurate. So in this case I'll consider `200000 Lovelace`

Substract this value to the address amount:
```shell
expr 10000000 - 200000
9800000
```

Create the TX pre-signature.
The ttl is the blockchain tip + margin
```shell
cardano-cli transaction build-raw \
--tx-in "282f1f9ecdfba373f70a0c29babbc4XXXXXXXXXXXXXXXXXXXXXXX#0" \
--tx-out $(cat owner-payment.addr)+9800000 \
--ttl 84326409 \
--fee 200000 \
--out-file tx.tosign \
--certificate-file stake-pool-registration-*********.cert \
--alonzo-era
```

Move the file `tx.tosign` to the airgapped machine connected to the HW wallet.

Witness and sign:
```shell
cardano-hw-cli transaction transform \
--tx-file tx.tosign \
--out-file tx.transformed

cardano-hw-cli transaction witness \
--tx-file tx.transformed \
--hw-signing-file owner-payment.hwsfile \
--hw-signing-file cold.hwsfile \
--mainnet \
--out-file operator.witness \
--out-file pool.witness

cardano-hw-cli transaction witness \
--tx-file tx.transformed \
--hw-signing-file owner-stake.hwsfile \
--mainnet \
--out-file owner.witness

cardano-cli transaction assemble \
--tx-body-file tx.transformed \
--witness-file operator.witness \
--witness-file pool.witness \
--witness-file owner.witness \
--out-file tx.signed
```

Move the file `tx.signed` to the block producer to submit the TX:
```shell
cardano-cli transaction submit --tx-file tx.signed --mainnet
```
