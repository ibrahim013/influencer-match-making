resource "random_password" "master" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.name_prefix}-db-subnets"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.name_prefix}-db-subnets"
  }
}

resource "aws_db_instance" "main" {
  identifier                 = "${var.name_prefix}-postgres"
  engine                     = "postgres"
  engine_version             = "16"
  instance_class             = var.instance_class
  allocated_storage          = var.allocated_storage
  storage_type               = "gp3"
  storage_encrypted          = true
  db_name                    = var.db_name
  username                   = var.db_username
  password                   = random_password.master.result
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = var.vpc_security_group_ids
  publicly_accessible        = false
  skip_final_snapshot        = true
  backup_retention_period    = 1
  auto_minor_version_upgrade = true
  deletion_protection        = false

  tags = {
    Name = "${var.name_prefix}-postgres"
  }
}
