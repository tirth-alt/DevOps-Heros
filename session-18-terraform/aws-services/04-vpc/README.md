# VPC: Virtual Private Cloud (Networking)

**Name:** Tirth Shah  
**Roll Number:** 10316

## What is a VPC?

A **VPC** is your own isolated virtual network inside AWS. You decide its IP address range, how it is split into subnets, and what can talk to the internet. Resources such as EC2 instances and databases are launched inside a VPC.

- A VPC belongs to **one region** and spans all of that region's Availability Zones.
- Every account has a **default VPC** in each region so that instances work out of the box.
- Different VPCs are isolated from each other until you connect them.

## CIDR

**CIDR** notation writes an IP range as an address plus a prefix length.

```
10.0.0.0/16
         └── the first 16 bits are fixed
```

| CIDR | Number of addresses |
|---|---|
| `/16` | 65,536 |
| `/24` | 256 |
| `/28` | 16 |

- Use the private ranges `10.0.0.0/8`, `172.16.0.0/12` or `192.168.0.0/16`.
- A VPC can be between `/16` and `/28`.
- Plan ranges so that VPCs you may connect later do not overlap.

## Subnets

A **subnet** is a slice of the VPC's range that sits in **one Availability Zone**.

```
VPC 10.0.0.0/16
├── Subnet 10.0.1.0/24   AZ a   (public)
├── Subnet 10.0.2.0/24   AZ b   (public)
├── Subnet 10.0.11.0/24  AZ a   (private)
└── Subnet 10.0.12.0/24  AZ b   (private)
```

AWS reserves **5 addresses** in every subnet, so a `/24` has 251 usable addresses. Using subnets in at least two AZs keeps an application running if one AZ fails.

## Route tables

A **route table** is a set of rules that decide where network traffic goes. Every subnet is associated with one.

| Destination | Target | Meaning |
|---|---|---|
| `10.0.0.0/16` | `local` | Traffic inside the VPC stays inside |
| `0.0.0.0/0` | `igw-xxxx` | Everything else goes to the internet |

The route table is what makes a subnet public or private. The `local` route is always present.

## Internet Gateway

An **Internet Gateway (IGW)** connects the VPC to the internet. It is horizontally scaled, highly available and free.

To give an instance internet access you need all of these:

1. An IGW attached to the VPC.
2. A route to the IGW (`0.0.0.0/0 → igw`) in the subnet's route table.
3. A public IP on the instance.
4. Security group and network ACL rules that allow the traffic.

## NAT Gateway

A **NAT Gateway** lets instances in a **private** subnet reach the internet for things like software updates, **without** being reachable from the internet.

- It is placed in a **public** subnet and has an Elastic IP.
- The private subnet's route table sends `0.0.0.0/0` to the NAT Gateway.
- Traffic can only start from inside. Connections from outside are not allowed.
- It is **billed per hour and per GB**, so it is one of the larger VPC costs.

## Security groups

A **security group** is a firewall at the **instance** level.

- Allow rules only, and everything else is denied.
- **Stateful:** reply traffic is allowed automatically.
- Can reference another security group as a source, such as "allow the database port from the app security group".
- All rules are evaluated together.

## Network ACLs

A **network ACL (NACL)** is a firewall at the **subnet** level.

- Has both **allow and deny** rules, checked in number order, and the first match wins.
- **Stateless:** you must allow the reply traffic in the other direction too.
- The default NACL allows all traffic.

| | Security group | Network ACL |
|---|---|---|
| Applies to | Instance | Subnet |
| Rules | Allow only | Allow and deny |
| State | Stateful | Stateless |
| Evaluation | All rules | In order, first match |

## Public vs private subnet

| | Public subnet | Private subnet |
|---|---|---|
| Route to the internet | `0.0.0.0/0 → IGW` | None, or `0.0.0.0/0 → NAT Gateway` |
| Instances have public IPs | Usually yes | No |
| Reachable from the internet | Yes, if allowed | No |
| Typical contents | Load balancers, bastion hosts, NAT Gateway | App servers, databases |

A subnet is public only because of its route table. Creating an IGW does not make a subnet public by itself.

## Typical architecture

```
                    Internet
                       │
                 ┌─────▼─────┐
                 │    IGW    │
                 └─────┬─────┘
 ┌─────────────────────▼──────────────────────────┐
 │ VPC 10.0.0.0/16                                │
 │  ┌───────────────────┐   ┌──────────────────┐  │
 │  │ Public subnet     │   │ Private subnet   │  │
 │  │ load balancer     │──►│ app + database   │  │
 │  │ NAT Gateway       │◄──│ (outbound only)  │  │
 │  └───────────────────┘   └──────────────────┘  │
 └────────────────────────────────────────────────┘
```

## Useful CLI commands

```bash
aws ec2 describe-vpcs
aws ec2 describe-subnets
aws ec2 describe-route-tables
aws ec2 describe-internet-gateways
aws ec2 describe-security-groups
```

## Summary

A VPC is a private network with an IP range. It is divided into subnets, one per Availability Zone. Route tables decide where traffic goes, an Internet Gateway gives public subnets internet access, and a NAT Gateway gives private subnets outbound-only access. Security groups protect instances and network ACLs protect subnets.
