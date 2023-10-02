resource "aws_s3_bucket" "terraform-state" {
  bucket = "${var.name}-terraform-state"

  force_destroy = true

  tags = merge({ Name = "S3 remote terraform state store" }, var.tags)

  lifecycle {
    ignore_changes = [
      server_side_encryption_configuration,
    ]
  }
}
resource "aws_s3_bucket_versioning" "terraform-state-s3-versioning" {
  bucket = aws_s3_bucket.terraform-state.bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform-state-lock" {
  name = "${var.name}-terraform-state-lock"

  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = merge({ Name = "DynamoDB table for locking terraform state store" }, var.tags)
}
