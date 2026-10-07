# Values for the variables declared in variables.tf.
# S3 bucket names are global across AWS, so this one carries a personal suffix.
aws_region    = "ap-south-1"
project_name  = "session19"
vpc_cidr      = "10.20.0.0/16"
subnet_cidr   = "10.20.1.0/24"
instance_type = "t3.micro"
bucket_name   = "Tirth-10316-session19-artifacts"
