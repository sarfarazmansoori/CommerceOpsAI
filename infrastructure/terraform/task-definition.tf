# ECS task definition for CommerceOpsAI
resource "aws_ecs_task_definition" "commerceops" {
  family                   = "commerceops-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "commerceops-api"
      image     = "${aws_ecr_repository.commerceops.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      healthCheck = {
        command = [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
        ]

        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 15
      }
      environment = [
        {
          name  = "BEDROCK_ENABLED"
          value = "false"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "S3_AUDIT_BUCKET"
          value = aws_s3_bucket.audit_logs.bucket
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.commerceops.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = "commerceops-task"
    Environment = "development"
  }
}
