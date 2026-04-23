aws_region        = "us-east-1"
name_prefix       = "matchmaking-dev"
image_tag         = "latest"
ecs_desired_count = 1

# Set secrets via environment (TF_VAR_*) or a private tfvars file not committed to git.
