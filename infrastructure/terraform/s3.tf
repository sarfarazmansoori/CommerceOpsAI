# Private S3 bucket for CommerceOpsAI audit logs
resource "aws_s3_bucket" "audit_logs" {
  bucket_prefix = "commerceops-ai-audit-"

  force_destroy = false

  tags = {
    Name        = "commerceops-audit-logs"
    Environment = "development"
    Project     = "CommerceOpsAI"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
