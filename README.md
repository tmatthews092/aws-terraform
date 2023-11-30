# AWS Terraform Integration

Using Terraform we are deploying Python3 Lambda Function, an S3 Bucket, IAM Policy, and Log Group to a AWS Account where we can upload .fasta files.

### Lambda Function

Uses a deployed trigger from main.tf to fire when a .fasta file is uploaded to the S3 bucket *aws-terraform-s3-generic-file-collector*

We use the .count function to determine all instances of a specified substring within the .fasta file. After counting we create a JSON file which is uploaded to the results folder in the S3 Bucket.

### Requirements

- Install [terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Authenticate the AWS Account with `aws configure`

### TODO

- Improve security by using IAM access tokens
- Abstract out main.tf file and values
- Add parameterization for substring_to_search
- Improve error catching + reporting in Lambda function
