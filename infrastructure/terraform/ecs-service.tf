# ECS service for CommerceOpsAI
resource "aws_ecs_service" "commerceops" {
  name            = "commerceops-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.commerceops.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.public_a.id,
      aws_subnet.public_b.id
    ]

    security_groups = [
      aws_security_group.api.id
    ]

    assign_public_ip = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_execution
  ]

  tags = {
    Name        = "commerceops-api-service"
    Environment = "development"
  }
}
