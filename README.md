# AWS Terraform Integration

Using Terraform we are deploying Python3 Lambda Function, an S3 Bucket, IAM Policy, and Log Group to a AWS Account where we can upload .fasta files.

### Lambda Function

Uses a deployed trigger from main.tf to fire when a .fasta file is uploaded to the S3 bucket *aws-terraform-s3-generic-file-collector*

We use the .count function to determine all instances of a specified substring within the .fasta file. After counting we create a JSON file which is uploaded to the /results folder in the S3 Bucket.

### Requirements

- Install [terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Create or have an AWS Account and be in the us-east-2 region
- Authenticate the AWS Account with `aws configure`
    - When the CLI requests the Access Key + Access Secret please provide your own AWS Access Keys

### How to Use

- Use the `terraform init` cmd to build the .terraform folder in your local
- Use the `terraform apply` cmd to build deploy the AWS resources from the main.tf file
    - Enter `yes` when prompted
    - It will take a minute or two for all the changes to apply to the AWS Account
- Enter the AWS Console and navigate to the S3 Bucket
- Upload a .fasta file
- Refresh the S3 Bucket a /results folder should appear
- In the /results folder there should be a file that has JSON data of the match results from the .fasta file that was uploaded. Download or Open to verify results
- There are also CloudWatch log files available through the Lambda function
- When you want to remove all the deployed resources from the AWS Account use `terraform destroy`

### TODO

- Improve security by using IAM access tokens
- Abstract out main.tf file and values
- Add parameterization for substring_to_search
- Improve error catching + reporting in Lambda function
- Integrate biopython library for scalable read of sequences
- Clean up main.py

### Limitations

- If changing regions via the aws provider (eg us-east-2 -> us-east-1) there's a bug which occurs on `terraform apply`. https://github.com/hashicorp/terraform-provider-aws/issues/23221
