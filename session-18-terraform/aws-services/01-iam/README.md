# IAM: Identity and Access Management (Governance)

**Name:** Tirth Shah  
**Roll Number:** 10316

## What is IAM?

IAM is the AWS service that controls **who** can sign in (authentication) and **what** they are allowed to do (authorization). Every request to AWS is checked against IAM.

- It is **global**. Users, roles and policies are not tied to one region.
- It is **free**. You pay only for the resources people create.
- Everything is **denied by default**. Access exists only when a policy allows it.

```
Who are you?  ──►  Authentication  (user, role, access key, MFA)
What can you do? ──►  Authorization   (policies)
```

## Core building blocks

### Root user

The identity created with the AWS account. It has unlimited power and cannot be restricted. Use it only for a few account tasks, protect it with MFA, and never create access keys for it.

### Users

A **user** is one person or application with long-term credentials: a console password and optionally access keys.

```bash
aws iam create-user --user-name dev-alice
aws iam list-users
```

### Groups

A **group** is a collection of users. Attach a policy to the group and every member gets it. A group cannot contain other groups, and a group cannot sign in.

```
Group: Developers ──► policy: AmazonEC2ReadOnlyAccess
   ├── dev-alice
   └── dev-bob
```

### Roles

A **role** is an identity with **no permanent password or keys**. Someone or something *assumes* the role and receives temporary credentials from AWS STS that expire.

- An EC2 instance assumes a role to read S3 without keys stored on the server.
- A user in one account assumes a role to work in another account.
- A Lambda function, ECS task or CI pipeline assumes a role to deploy.

Each role has a **trust policy** (who may assume it) and **permission policies** (what it may do).

### Policies

A **policy** is a JSON document that lists permissions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

| Element | Meaning |
|---|---|
| `Effect` | `Allow` or `Deny` |
| `Action` | The API calls covered, such as `s3:GetObject` |
| `Resource` | The things the actions apply to, written as ARNs |
| `Condition` | Optional extra rules, such as source IP or MFA required |

Policy types:

| Type | Description |
|---|---|
| AWS managed | Created and kept up to date by AWS, for example `ReadOnlyAccess` |
| Customer managed | Written by you and reusable across identities |
| Inline | Embedded in one user, group or role only |
| Resource-based | Attached to a resource, such as an S3 bucket policy |

## Permissions

How AWS decides a request:

1. Everything starts as **denied**.
2. Any matching **Allow** grants access.
3. Any matching **explicit Deny** overrides every Allow.

A permission has three parts: the action, the resource, and the condition under which it applies.

## Least privilege

Give an identity **only the permissions it needs, for only as long as it needs them**.

- Start with no access and add what is required.
- Name exact actions and resources instead of `"Action": "*"` and `"Resource": "*"`.
- Use IAM Access Analyzer and last-accessed data to remove permissions nobody uses.
- Prefer a role scoped to one job over a shared admin user.

| Too broad | Better |
|---|---|
| `"Action": "s3:*"` on `"Resource": "*"` | `s3:GetObject` on one bucket's objects |
| Everyone in `AdministratorAccess` | Developers in a group with only the services they use |

## IAM best practices

1. Turn on **MFA** for the root user and for every human user.
2. **Do not use the root user** for daily work.
3. Use **roles** with temporary credentials for applications and services, not long-term access keys.
4. If access keys are needed, **rotate** them and delete unused ones.
5. Manage access with **groups**, not by attaching policies to individual users.
6. Apply **least privilege** and review permissions regularly.
7. Use **IAM Identity Center** (single sign-on) for people instead of many IAM users.
8. Never commit keys to Git. Use a secrets manager or role-based access.
9. Enable **CloudTrail** to record who did what.
10. Set a strong **password policy**.

## Common use cases

| Scenario | IAM solution |
|---|---|
| A new developer joins | Create a user, add them to the Developers group, require MFA |
| An app on EC2 reads from S3 | Attach an instance profile with a role that allows only that bucket |
| A CI pipeline deploys to AWS | A role the pipeline assumes, scoped to deployment actions |
| Access to a second AWS account | A cross-account role with a trust policy |
| Contractor needs temporary access | A role with a time-limited session |
| Block deleting production data | An explicit `Deny` on delete actions |

## Useful CLI commands

```bash
aws sts get-caller-identity          # who am I right now
aws iam list-users
aws iam list-groups
aws iam list-roles
aws iam list-attached-user-policies --user-name dev-alice
```

## Summary

IAM answers two questions: who are you, and what may you do. Users and roles are the identities, groups organize users, and policies grant permissions. Everything is denied by default, an explicit deny always wins, and least privilege with MFA and roles keeps an account safe.
