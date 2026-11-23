# ECS cluster for CommerceOpsAI
resource "aws_ecs_cluster" "main" {
  name = "commerceops-cluster"

  tags = {
    Name        = "commerceops-cluster"
    Environment = "development"
    Project     = "CommerceOpsAI"
  }
}
