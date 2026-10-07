# Terraform: AWS Infrastructure

**Name:** Tirth Shah · **Roll Number:** 10316

Terraform builds the AWS infrastructure that runs the app in the cloud: a VPC and an EKS Kubernetes cluster. It uses the official community modules.

| Resource | Details |
|---|---|
| VPC | `10.30.0.0/16`, DNS hostnames enabled |
| Public subnets | 2, one per Availability Zone, tagged for internet-facing load balancers |
| Private subnets | 2, one per Availability Zone, where the worker nodes run |
| NAT gateway | 1, so private nodes can pull images (one per AZ in production) |
| EKS cluster | `stockwise-dev-eks`, Kubernetes 1.34, public API endpoint |
| Managed node group | `t3.medium`, minimum 2, desired 2, maximum 4 |
| Add-ons | CoreDNS, kube-proxy, VPC CNI, EKS Pod Identity Agent |

| File | Purpose |
|---|---|
| `versions.tf` | Terraform and AWS provider versions, region, default tags |
| `variables.tf` | Inputs with defaults |
| `main.tf` | `module "vpc"` (terraform-aws-modules/vpc 6.7) and `module "eks"` (terraform-aws-modules/eks 21.26) |
| `outputs.tf` | VPC and subnet IDs, cluster name and endpoint, the kubeconfig command |
| `terraform.tfvars.example` | Example values. Copy it to `terraform.tfvars`, which is gitignored. |

No AWS credentials are stored in these files. Terraform reads them from `aws configure`.

## Workflow

```bash
cd final-devops-project/terraform
cp terraform.tfvars.example terraform.tfvars
aws sts get-caller-identity

terraform init
terraform fmt -recursive
terraform validate
terraform plan            # about 60 resources to add
terraform apply           # takes 15 to 20 minutes
aws eks update-kubeconfig --region ap-south-1 --name stockwise-dev-eks
kubectl get nodes         # 2 worker nodes Ready
```

![terraform fmt, validate and providers](../screenshots/terraform-validate.png)

## Deploy the app to EKS

```bash
kubectl apply -f ../kubernetes/namespace.yaml
helm upgrade --install stockwise ../helm/stockwise -n stockwise \
  --set backend.image.tag=<commit-sha> --set frontend.image.tag=<commit-sha> \
  --set ingress.enabled=false
```

EKS has no ingress controller by default. Either install ingress-nginx, or keep the Ingress disabled and port-forward the frontend.

## Destroy

**EKS and the NAT gateway cost money every hour.** Destroy everything as soon as you have your screenshots.

```bash
terraform plan -destroy
terraform destroy
```

## Status

`init`, `fmt` and `validate` pass. `plan`, `apply` and `destroy` need an AWS account allowed to create VPC, EC2, IAM and EKS resources. The account available while building this project was read-only, so those three steps are listed under "Screenshots to add" in the root README.
