# DynamoDB and RDS: Database Services

**Name:** Tirth Shah  
**Roll Number:** 10316

AWS offers a managed database for different needs. **DynamoDB** is a NoSQL key-value and document database. **RDS** runs traditional relational databases. Both are managed, so AWS handles the servers, patching and backups.

---

## DynamoDB

### NoSQL

NoSQL databases do not use fixed tables with joins. DynamoDB is **serverless**, fully managed, and gives single-digit millisecond responses at almost any scale. There are no servers to size or patch.

### Tables, items and attributes

| Term | Relational equivalent | Meaning |
|---|---|---|
| Table | Table | A collection of items |
| Item | Row | One record |
| Attribute | Column | One piece of data in an item |

Unlike SQL columns, items in the same table can have **different attributes**. Only the key attributes are required.

```json
{
  "UserId": "u-101",
  "OrderDate": "2026-10-07",
  "Total": 499,
  "Items": ["book", "pen"]
}
```

### Partition key

The **partition key** is the required main key. DynamoDB hashes it to decide which physical partition stores the item, so it spreads the data and the load.

- Choose a key with many different values, such as `UserId`, so no single partition gets all the traffic.
- Reading by partition key is the fast path.

### Sort key

The optional **sort key** orders the items that share one partition key.

- Together they form a **composite primary key**, and the pair must be unique.
- It allows range queries such as "all orders for user u-101 in October".

```
Partition key   Sort key      Other attributes
u-101           2026-10-01    Total: 120
u-101           2026-10-07    Total: 499
u-102           2026-10-03    Total: 75
```

### Other features

- **Capacity modes:** on-demand (pay per request) or provisioned (set read and write capacity).
- **Secondary indexes** let you query by attributes other than the key.
- **TTL** deletes items automatically after a set time.
- Data is replicated across **three AZs**, with optional global tables across regions.

### Use cases

Shopping carts, user sessions and profiles, gaming leaderboards, IoT data, and any workload with predictable access patterns that needs huge scale and low latency.

```bash
aws dynamodb list-tables
aws dynamodb scan --table-name Orders
```

---

## RDS: Relational Database Service

### Relational database

A **relational database** stores data in tables with rows and columns, uses **SQL**, and supports joins, transactions and strict schemas. RDS is a **managed** service, so AWS does the setup, patching, backups and failover, while you design the schema and queries.

### Supported engines

| Engine | Notes |
|---|---|
| MySQL | Popular open source |
| PostgreSQL | Open source with advanced features |
| MariaDB | MySQL fork |
| Oracle | Commercial, license included or bring your own |
| SQL Server | Microsoft, license included |
| Db2 | IBM |
| Aurora | AWS-built, MySQL and PostgreSQL compatible, higher performance |

### DB instances

A **DB instance** is the database server. You pick the engine and version, an **instance class** (CPU and memory, such as `db.t3.micro`) and the storage type and size. A **subnet group** tells RDS which subnets of your VPC it may use.

### Security

- Run the database in **private subnets** with no public access.
- A **security group** allows the database port only from the application's security group.
- **Encryption at rest** with KMS, chosen when the database is created, and TLS for connections in transit.
- Optional **IAM database authentication**.
- Keep the master password in **Secrets Manager**, not in code.

### Backups

- **Automated backups** take a daily snapshot and store transaction logs, which allows **point-in-time recovery** to any second within the retention period of up to 35 days.
- **Manual snapshots** are kept until you delete them.
- A restore always creates a **new** instance.

### Multi-AZ

A **Multi-AZ** deployment keeps a synchronized **standby** copy in a different Availability Zone.

- If the primary fails, RDS **fails over** automatically to the standby, usually within one to two minutes.
- The standby is only for **high availability**. You do not read from it.
- Maintenance and backups can run with less impact.

### Read replicas

A **read replica** is a copy that receives changes from the primary **asynchronously**.

- It serves **read** traffic, so it improves performance for read-heavy applications.
- Can be in another region.
- Can be promoted to a standalone database.
- Data may lag slightly behind the primary.

| | Multi-AZ | Read replica |
|---|---|---|
| Purpose | High availability | Read scaling |
| Replication | Synchronous | Asynchronous |
| Serves read traffic | No | Yes |
| Failover | Automatic | Manual promotion |

### Use cases

Web and mobile back ends, e-commerce, banking and ERP systems, and anything that needs SQL, joins, transactions and a fixed schema.

```bash
aws rds describe-db-instances
aws rds describe-db-snapshots
```

---

## DynamoDB vs RDS

| | DynamoDB | RDS |
|---|---|---|
| Type | NoSQL key-value and document | Relational (SQL) |
| Schema | Flexible items | Fixed tables and columns |
| Queries | By key and index | Any SQL query with joins |
| Scaling | Automatic, virtually unlimited | Bigger instance, plus read replicas |
| Servers | None to manage (serverless) | You choose an instance class |
| Transactions | Supported, limited | Full ACID with joins |
| Best for | Huge scale, simple access patterns | Complex queries and relationships |

## Summary

Choose DynamoDB when you need very large scale and low latency with simple key-based access. Choose RDS when you need SQL, joins and transactions. Use Multi-AZ for availability and read replicas for read performance on RDS.
