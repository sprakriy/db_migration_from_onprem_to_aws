provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "migration_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "Enterprise-Migration-VPC" }
}

resource "aws_subnet" "public_az1" {
  vpc_id            = aws_vpc.migration_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true
  tags = { Name = "Migration-Subnet-1" }
}

resource "aws_subnet" "public_az2" {
  vpc_id            = aws_vpc.migration_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true
  tags = { Name = "Migration-Subnet-2" }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.migration_vpc.id
  tags   = { Name = "Migration-Gateway" }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.migration_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public_az1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.public_az2.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "enterprise-rds-subnet-group"
  subnet_ids = [aws_subnet.public_az1.id, aws_subnet.public_az2.id]
}

resource "aws_security_group" "rds_sg" {
  name   = "allow_mysql"
  vpc_id = aws_vpc.migration_vpc.id
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "target_rds" {
  allocated_storage      = 20
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro" 
  db_name                = "corporate_data_cloud"
  username               = "cloud_admin"
  password               = "CloudSecurePass2026!"
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = true
}

output "rds_endpoint" {
  value = aws_db_instance.target_rds.endpoint
}
