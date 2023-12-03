# ----------------------------------------------------------------------------------------------------------------------
# DEPLOY AN IAM ROLE
# ----------------------------------------------------------------------------------------------------------------------

# AWS ROLE
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# DEPLOY POLICIES FOR CLOUDWATCH, S3 AND LAMBDA
# ----------------------------------------------------------------------------------------------------------------------

#cloudwatch
resource "aws_iam_policy" "logging_policy" {
  name   = "logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:*"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# S3 Policy
resource "aws_iam_policy" "s3_policy" {
  name   = "s3-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "s3:*"
        ],
        Effect : "Allow",
        "Resource": "arn:aws:s3:::*"
      }
    ]
  })
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam-for-lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = [
    aws_iam_policy.logging_policy.arn, 
    aws_iam_policy.s3_policy.arn
  ]
}
