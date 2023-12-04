# ----------------------------------------------------------------------------------------------------------------------
# CREATE A S3 BUCKET
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket" "bucket" {
  bucket = var.aws_s3_bucket_name
  force_destroy = true
  tags = {
    name        = "Generic File Collector"
    environment = "Dev"
  }
}
