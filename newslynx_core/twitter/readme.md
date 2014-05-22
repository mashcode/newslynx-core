# Query launcher for table registry / concourse location
postgres://postgres:gr33enp0int#9@10.0.1.159:5432/launcher
```
Select username, pass, address, db from servers where server_name in ('concourse', 'enigmabase')
```
# Query table registry for table names
```
select tablename, datapath from table_registry order by created_timest desc
```
# Build queries
