resource "aws_s3_bucket" "main" {
  bucket = var.name
  acl    = var.public ? "public-read" : "private"

  tags = merge({
    Name        = var.name
    Description = "S3 bucket for ${var.name}"
  }, var.tags)
}

resource "aws_s3_bucket_versioning" "main-versioning" {
  bucket = aws_s3_bucket.main.bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}