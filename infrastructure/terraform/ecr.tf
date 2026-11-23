# ECR repository for CommerceOpsAI Docker images
resource "aws_ecr_repository" "commerceops" {
  name                 = "commerceops-ai"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "commerceops-ai"
    Environment = "development"
    Project     = "CommerceOpsAI"
  }
}
