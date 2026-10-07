# EC2: Elastic Compute Cloud (Compute)

**Name:** Tirth Shah  
**Roll Number:** 10316

## What is EC2?

EC2 provides **virtual servers**, called **instances**, that you can start in minutes and pay for by the second or hour. You choose the operating system, the CPU and memory, the storage and the network, and you control the server like any other computer.

It is **IaaS** (Infrastructure as a Service): AWS runs the physical hardware, and you manage the operating system and everything on it.

```
Launch an instance = AMI + instance type + key pair + security group + storage + network
```

## AMI: Amazon Machine Image

An **AMI** is the template an instance starts from. It holds the operating system, installed software and settings.

| Kind | Example |
|---|---|
| AWS provided | Amazon Linux 2023, Ubuntu, Windows Server |
| AWS Marketplace | Vendor images with software preinstalled |
| Your own | A custom image made from a configured instance |

AMIs are regional. A "golden AMI" lets you launch identical servers quickly.

## Instance types

An instance type sets the CPU, memory, storage and network speed. The name is read like this:

```
t3.micro
│ │  └── size (nano, micro, small, medium, large, xlarge, ...)
│ └───── generation
└─────── family
```

| Family | Optimized for | Example use |
|---|---|---|
| T | Burstable, low cost | Small websites, dev and test |
| M | Balanced CPU and memory | Application servers |
| C | Compute | Batch processing, game servers |
| R | Memory | Databases, in-memory caches |
| G / P | GPU | Machine learning, graphics |
| I / D | Storage | High disk throughput |

Pricing options: **On-Demand** (pay as you go), **Reserved or Savings Plans** (commit for a discount), **Spot** (spare capacity, much cheaper, can be interrupted).

## Key pairs

A key pair lets you log in to a Linux instance over SSH without a password.

- AWS stores the **public key** and places it on the instance.
- You keep the **private key** (a `.pem` file). AWS cannot give it to you again.

```bash
chmod 400 my-key.pem
ssh -i my-key.pem ec2-user@<public-ip>
```

Losing the private key means losing SSH access. Never share it or commit it to Git.

## Security groups

A **security group** is a virtual firewall attached to an instance.

- It has only **allow** rules. Anything not allowed is blocked.
- It is **stateful**: if a request is allowed in, the reply is allowed out automatically.
- Rules name a protocol, a port and a source, such as `TCP 22 from my IP`.

| Port | Used for | Source to allow |
|---|---|---|
| 22 | SSH | Only your own IP, never `0.0.0.0/0` |
| 80 | HTTP | Anywhere |
| 443 | HTTPS | Anywhere |

## EBS: Elastic Block Store

**EBS** provides network-attached disks for instances.

- A volume lives in **one Availability Zone** and attaches to an instance there.
- Data **persists** when the instance stops, unlike instance store storage, which is wiped.
- You can take **snapshots**, stored in S3, as backups.
- Common types: `gp3` (general purpose SSD, the default choice), `io2` (high-performance SSD), `st1` and `sc1` (low-cost HDD).

The root volume holds the operating system. Extra volumes can be added for data.

## Public vs private IP

| | Private IP | Public IP |
|---|---|---|
| Reachable from | Inside the VPC only | The internet |
| Assigned | Always | Only if enabled for the subnet or instance |
| Changes on stop and start | No | **Yes** |
| Use | Server to server traffic | Reaching the instance from outside |

An **Elastic IP** is a static public address you keep until you release it. Unused Elastic IPs and public IPv4 addresses can incur a charge.

## Instance lifecycle

```
pending ──► running ──► stopping ──► stopped ──► pending (start again)
               │
               └──► shutting-down ──► terminated
```

| State | Meaning | Billed for compute? |
|---|---|---|
| pending | Starting up | No |
| running | Ready to use | Yes |
| stopping / stopped | Shut down, disks kept | No (EBS storage still billed) |
| shutting-down / terminated | Deleted for good | No |

- **Stop** keeps the instance and its EBS volumes so you can start it again.
- **Terminate** deletes the instance, and the root volume is deleted by default.
- **Hibernate** saves memory to disk so the instance resumes where it left off.

## Common use cases

- Hosting websites and web applications.
- Backend application servers and APIs.
- Running databases that need full control.
- Batch jobs, data processing and build servers.
- Dev and test environments that start and stop on demand.
- Machine learning on GPU instances.

## Useful CLI commands

```bash
aws ec2 describe-instances
aws ec2 describe-instance-types --instance-types t3.micro
aws ec2 describe-key-pairs
aws ec2 describe-security-groups
aws ec2 stop-instances --instance-ids <id>
aws ec2 terminate-instances --instance-ids <id>
```

## Summary

An EC2 instance is a virtual server built from an AMI, sized by its instance type, secured by a security group and key pair, and backed by EBS storage. Stop an instance to pause compute billing, terminate it to delete it, and remember that a public IP changes unless you use an Elastic IP.
