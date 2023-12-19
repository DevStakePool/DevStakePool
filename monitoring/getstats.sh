curl https://js.cexplorer.io/api-static/pool/pool1e2tl2w0x4puw0f7c04mznq4qz6kxjkwhvuvusgf2fgu7q4d6ghv.json 2>/dev/null \
| jq '.data' | jq 'del(.stats, .url , .img, .updated, .handles, .pool_id, .name, .pool_id_hash)' \
| tr -d \"{},: \
| awk NF \
| sed -e 's/^[ \t]*/adapools_/' \
| sed -e 's/adapools_stake /adapools_total_stake /' \
| sed -e 's/adapools_stake_active /adapools_active_stake /' \
| sed -e 's/adapools_position /adapools_rank /' \
| sed -e 's/adapools_blocks_est_epoch /adapools_blocks_estimated /' \
| sed -e 's/adapools_saturation /adapools_saturated /' \
| sed -e 's/adapools_roa_short /adapools_roa /' > /home/cardano/cnode/poolStat/poolStat.prom
