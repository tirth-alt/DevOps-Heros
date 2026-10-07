# S3: Simple Storage Service (Storage)

**Name:** Tirth Shah  
**Roll Number:** 10316

## What is S3?

S3 is AWS **object storage**. You store any amount of data, such as images, backups, logs and videos, and read it back over the internet or from other AWS services.

- **Durable:** designed for 99.999999999% (eleven nines) durability. Data is copied across several facilities.
- **Scalable:** no storage limit and no servers to manage.
- **Pay per use:** you pay for the storage, the requests and the data transferred out.

S3 stores objects, not files on a disk. You cannot install an operating system on it or edit part of an object in place.

## Buckets

A **bucket** is the container that holds objects.

- The name must be **globally unique** across all of AWS, using lowercase letters, numbers and hyphens.
- A bucket lives in **one region**, which you choose when you create it.
- Everything inside is private by default.
- The structure is flat. A name like `photos/2026/cat.jpg` only looks like folders. `photos/2026/` is just part of the key.

## Objects

An **object** is one stored item.

| Part | Meaning |
|---|---|
| Key | The unique name inside the bucket, such as `photos/cat.jpg` |
| Value | The data itself, up to 5 TB per object |
| Metadata | Name and value pairs, such as content type |
| Version ID | Identifies a version when versioning is on |
| Tags | Labels used for cost tracking and policies |

Uploads above 100 MB should use **multipart upload**, which is required above 5 GB.

```bash
aws s3 cp photo.jpg s3://my-bucket/photos/photo.jpg
aws s3 ls s3://my-bucket/photos/
aws s3 sync ./site s3://my-bucket/
```

## Storage classes

A storage class trades price against how fast and how often you need the data.

| Class | Best for | Retrieval |
|---|---|---|
| Standard | Frequently accessed data | Immediate |
| Intelligent-Tiering | Unknown or changing access | Immediate, moves data automatically |
| Standard-IA | Infrequent access, needs fast retrieval | Immediate, with a retrieval fee |
| One Zone-IA | Infrequent, re-creatable data | Immediate, stored in one AZ only |
| Glacier Instant Retrieval | Archives read about once a quarter | Milliseconds |
| Glacier Flexible Retrieval | Archives | Minutes to hours |
| Glacier Deep Archive | Long-term archives, the cheapest | Hours |

## Versioning

With **versioning** on, S3 keeps every version of an object.

- Overwriting an object creates a new version instead of replacing it.
- Deleting adds a **delete marker**, and the old versions are still there.
- You can restore an earlier version, which protects against accidental overwrites and deletes.
- Once enabled it can only be **suspended**, not removed. Old versions keep costing storage.

## Lifecycle policies

A **lifecycle policy** automatically moves or deletes objects by age.

```
Day 0    Standard
Day 30   ──► Standard-IA
Day 90   ──► Glacier Flexible Retrieval
Day 365  ──► Deleted
```

It can also expire old versions and clean up incomplete multipart uploads. This keeps storage costs down without manual work.

## Encryption

| Type | Who manages the key |
|---|---|
| SSE-S3 | S3 manages the keys. **On by default** for all new objects. |
| SSE-KMS | Keys in AWS KMS, with an audit trail and fine-grained control |
| SSE-C | You supply the key with each request |
| Client-side | You encrypt the data before uploading it |

Data is also protected in transit by using HTTPS. A bucket policy can deny any request that does not use HTTPS.

## Bucket policies

A **bucket policy** is a JSON resource-based policy attached to the bucket. It defines who may do what to the bucket and its objects.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadFromOneRole",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::123456789012:role/app-role" },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

- **Block Public Access** is a safety switch that overrides any policy that would make data public. Keep it on unless the bucket really hosts a public site.
- **ACLs** are an older mechanism and are disabled by default on new buckets. Use policies instead.
- Access is granted if either an IAM policy or a bucket policy allows it, and an explicit deny always wins.

## Common use cases

- Storing user uploads, images and videos for an application.
- Hosting a **static website** such as a React build.
- Backups and disaster recovery copies.
- A **data lake** for analytics.
- Application logs and audit logs.
- Storing build artifacts and software packages.
- Remote **Terraform state** files.

## Summary

S3 stores objects in globally named, regional buckets. Choose a storage class to control cost, turn on versioning for protection, use lifecycle policies to age data out, keep Block Public Access on, and control access with IAM and bucket policies. Encryption at rest is on by default.
