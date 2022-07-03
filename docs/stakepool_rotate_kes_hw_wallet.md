# KES keys rotation of a Stake Pool using HW Wallet
Your stake pool requires an operational certificate to verify that the pool has the authority to run. A current KES key pair is required to establish an operational certificate for your stake pool. A KES period indicates the time span when an operational certificate is valid. An operational certificate expires 90 days after the KES period defined in the operational certificate. You must generate a new KES key pair and operational certificate every 90 days, (better sooner), for your stake pool to mint blocks.

## Generate new KES keys
Backup the previous ones and generate new KES keys.
```
cardano-cli node key-gen-KES \
    --verification-key-file kes.vkey \
    --signing-key-file kes.skey
```

Copy the `kes.vkey` file that you generated to your air-gapped, offline computer where you have will connect with the HW Wallet and `cardano-hw-cli`.

I use this script to calculate the KES period
```bash
#!/bin/bash

slotsPerKESPeriod=$(cat $NODE_HOME/${NODE_CONFIG}-shelley-genesis.json | jq -r '.slotsPerKESPeriod')
echo "slotsPerKESPeriod: ${slotsPerKESPeriod}"
slotNo=$(cardano-cli query tip --mainnet | jq -r '.slot')
echo "slotNo:            ${slotNo}"
kesPeriod=$((${slotNo} / ${slotsPerKESPeriod}))
echo "kesPeriod:         ${kesPeriod}"
startKesPeriod=${kesPeriod}
echo "startKesPeriod:    ${startKesPeriod}"
```

## Increase the counter in your `node.counter` file
The file contains a line like this
```
"description": "Next certificate issue number: <CertificateIssueNumber>",
```
Increase the `<CertificateIssueNumber>` by 1 and save the file

## Generate a new `node.cert` file with `cardano-hw-cli`
```
cardano-hw-cli node issue-op-cert \
    --kes-verification-key-file kes.vkey \
    --hw-signing-file cold.hwsfile \
    --operational-certificate-issue-counter cold.counter \
    --kes-period ${startKesPeriod} \
    --out-file node.cert
```
Where `${startKesPeriod}` is the number calculated before by the bash script.
