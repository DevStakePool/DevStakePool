# Cardano Leaderlog using Daedalus wallet
LeaderLog is a very useful utility which is part of the [CNCLI](https://github.com/AndrewWestberg/cncli/) tool. This application is used by a Cardano SPO when there is teh need to get a prediction of the assigned blocks to a given Stake Pool, to be minted in the coming epoch.

The main issue with this tool is that it has to run together with the `cardano-node` and the RAM consumption is usually very high (sometimes higher that the available RAM on a running node) and therefore (at least for me) it was very tricky to run the utility on by relay/block-producer node, having only 16 GB of RAM available.

## Goal
This guide wasts to show how to use the `CNCLI` utility on a home computer that runs linux and has enough RAM memory. To speed up things, I decided to use the `cardano-node` that is running together with the [Daedalus](https://daedaluswallet.io/) full-node wallet.

## Install Daedalus
Install Daedalus on your linux machine. This is a very simple operation to do. There's the need to [download the Daedalus Linux](https://daedaluswallet.io/en/download/) version from the official site and execute the `.bin` file to install it.

Once done, start up the wallet and wait for a full synchronization with the Cardano blockchain. This operation will probably take few hours.

## Install `cardano-cli` & `cncli`
While Daedalus is syncing, let's install the `cardano-cli` and the `cncli` tool.

### `cardano-cli`
I would suggest you to copy the `cardano-cli` binaries directly from one of your stake pool nodes.

### `cncli`
Execute the following commands:
```bash
RELEASETAG=$(curl -s https://api.github.com/repos/AndrewWestberg/cncli/releases/latest | jq -r .tag_name)
VERSION=$(echo ${RELEASETAG} | cut -c 2-)
echo "Installing release ${RELEASETAG}"
curl -sLJ https://github.com/AndrewWestberg/cncli/releases/download/${RELEASETAG}/cncli-${VERSION}-x86_64-unknown-linux-gnu.tar.gz -o /tmp/cncli-${VERSION}-x86_64-unknown-linux-gnu.tar.gz
```
```bash
sudo tar xzvf /tmp/cncli-${VERSION}-x86_64-unknown-linux-gnu.tar.gz -C /usr/local/bin/
```

Once completed, you should be able to execute `cncli --version` which should give you an output like the following:
```bash
$ cncli --version
cncli 4.0.4
```

## Scripts to execute the LeaderLog
If you want to take a snapshot of the current epoch, you can use the    `ledger-set` argument with the value `current`.

This script expects you to change the following:
* `<USER_HOME>` the path of your home directory. This usually where Daedalus is installed.
* `<PORT>` This is the TCP port that the local `cardano-node` is listening to. You can find it by executing this command:
```bash
ps aux | grep 'cardano-node run' | egrep -o '\-\-port [0-9]+' | awk '{print $2}'
```
* `<STAKE_POOL_ID>` Your stake pool ID
* `<NODE_HOME>` This is where the `vrf.skey` and the `mainnet-*-genesis.json` files are located. You can copy them from your block producer node.
```bash
export CARDANO_NODE_SOCKET_PATH="/<USER_HOME>/.local/share/Daedalus/mainnet/cardano-node.socket"
cncli sync --host 127.0.0.1 --port <PORT> --no-service

MYPOOLID="<STAKE_POOL_ID>"
echo "LeaderLog - My Pool - $MYPOOLID"
NODE_HOME="<NODE_HOME>"

SNAPSHOT=$(cardano-cli query stake-snapshot --stake-pool-id $MYPOOLID --mainnet)
POOL_STAKE=$(echo "$SNAPSHOT" | grep -oP '(?<=    "poolStakeSet": )\d+(?=,?)')
ACTIVE_STAKE=$(echo "$SNAPSHOT" | grep -oP '(?<=    "activeStakeSet": )\d+(?=,?)')
MYPOOL=`cncli leaderlog --pool-id $MYPOOLID \
    --pool-vrf-skey ${NODE_HOME}/vrf.skey \
    --byron-genesis ${NODE_HOME}/mainnet-byron-genesis.json \
    --shelley-genesis ${NODE_HOME}/mainnet-shelley-genesis.json \
    --pool-stake $POOL_STAKE --active-stake $ACTIVE_STAKE --ledger-set current`
echo $MYPOOL | jq .

EPOCH=`echo $MYPOOL | jq .epoch`
echo "Epoch ${EPOCH}:"

SLOTS=`echo $MYPOOL | jq .epochSlots`
IDEAL=`echo $MYPOOL | jq .epochSlotsIdeal`
PERFORMANCE=`echo $MYPOOL | jq .maxPerformance`

echo "My Pool:  ${SLOTS} slot(s) assigned"
echo "          ${PERFORMANCE}% max performance"
echo "          ${IDEAL} ideal slots"
```

In order to calculate the upcoming epoch performance, you can run this script below 1.5 days before the end of the current epoch:
```bash
export CARDANO_NODE_SOCKET_PATH="/<USER_HOME>/.local/share/Daedalus/mainnet/cardano-node.socket"
cncli sync --host 127.0.0.1 --port <PORT> --no-service

MYPOOLID="<STAKE_POOL_ID>"
echo "LeaderLog - My Pool - $MYPOOLID"
NODE_HOME="<NODE_HOME>"

SNAPSHOT=$(cardano-cli query stake-snapshot --stake-pool-id $MYPOOLID --mainnet)
POOL_STAKE=$(echo "$SNAPSHOT" | grep -oP '(?<=    "poolStakeMark": )\d+(?=,?)')
ACTIVE_STAKE=$(echo "$SNAPSHOT" | grep -oP '(?<=    "activeStakeMark": )\d+(?=,?)')
MYPOOL=`cncli leaderlog --pool-id $MYPOOLID \
    --pool-vrf-skey ${NODE_HOME}/vrf.skey \
    --byron-genesis ${NODE_HOME}/mainnet-byron-genesis.json \
    --shelley-genesis ${NODE_HOME}/mainnet-shelley-genesis.json \
    --pool-stake $POOL_STAKE --active-stake $ACTIVE_STAKE --ledger-set next`
echo $MYPOOL | jq .

EPOCH=`echo $MYPOOL | jq .epoch`
echo "Epoch ${EPOCH}:"

SLOTS=`echo $MYPOOL | jq .epochSlots`
IDEAL=`echo $MYPOOL | jq .epochSlotsIdeal`
PERFORMANCE=`echo $MYPOOL | jq .maxPerformance`

echo "My Pool:  ${SLOTS} slot(s) assigned"
echo "          ${PERFORMANCE}% max performance"
echo "          ${IDEAL} ideal slots"
```

The execution can take quite some time to complete, depending on the machine power and status of the synchronization. 

You should have an output like the following, if everything goes ok:
```bash
$ ./leaderlog_current_epoch.sh 
 2022-02-13T17:08:10.887Z WARN  cardano_ouroboros_network::protocols::chainsync > rollback to slot: 53205664
 2022-02-13T17:08:10.887Z INFO  cardano_ouroboros_network::protocols::chainsync > block 6877930 of 6877933, 100.00% synced
 2022-02-13T17:08:10.903Z INFO  cardano_ouroboros_network::protocols::chainsync > block 6877933 of 6877933, 100.00% synced
 2022-02-13T17:08:10.919Z INFO  cncli::nodeclient::sync                         > Exiting...
LeaderLog - My Pool - ca97f539e6a878e7a7d87d762982a016ac6959d76719c8212a4a39e0
{
  "status": "ok",
  "epoch": 320,
  "epochNonce": "5bba572be9f7abafbfbbc7b440bfa95ac1b881a75b6008285daf72a59fabe48e",
  "epochSlots": 0,
  "epochSlotsIdeal": 0.05,
  "maxPerformance": 0,
  "poolId": "ca97f539e6a878e7a7d87d762982a016ac6959d76719c8212a4a39e0",
  "sigma": 2.086160397187094e-06,
  "activeStake": 49103458257,
  "totalActiveStake": 23537719498083360,
  "d": 0,
  "f": 0.05,
  "assignedSlots": []
}
Epoch 320:
My Pool:  0 slot(s) assigned
          0% max performance
          0.05 ideal slots
```