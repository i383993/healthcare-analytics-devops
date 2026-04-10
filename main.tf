provider "aws" {
  region = "us-east-1"  # Change to your preferred region
}

# Security Group for Spark and Streamlit
resource "aws_security_group" "spark_sg" {
  name_prefix = "spark-sg-"

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow Streamlit access
  }

  ingress {
    from_port   = 4040
    to_port     = 4040
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow Spark UI access
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SSH access
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance for Spark Master
resource "aws_instance" "spark_master" {
  ami           = "ami-0c55b159cbfafe1d0"  # Amazon Linux 2 AMI, update as needed
  instance_type = "t3.medium"
  key_name      = "your-key-pair"  # Replace with your key pair

  security_groups = [aws_security_group.spark_sg.name]

  tags = {
    Name = "Spark-Master"
  }

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y java-17-amazon-corretto-headless
    # Install Docker
    amazon-linux-extras install docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    # Pull and run your Docker image
    docker run -d -p 8501:8501 -p 4040:4040 your-dockerhub-username/your-app:latest
  EOF
}

# EC2 Instance for Spark Worker 1
resource "aws_instance" "spark_worker_1" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t3.medium"
  key_name      = "your-key-pair"

  security_groups = [aws_security_group.spark_sg.name]

  tags = {
    Name = "Spark-Worker-1"
  }

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y java-17-amazon-corretto-headless
    # Install Docker
    amazon-linux-extras install docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    # Configure as Spark worker
    # Add commands to join the master
  EOF
}

# EC2 Instance for Spark Worker 2
resource "aws_instance" "spark_worker_2" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t3.medium"
  key_name      = "your-key-pair"

  security_groups = [aws_security_group.spark_sg.name]

  tags = {
    Name = "Spark-Worker-2"
  }

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y java-17-amazon-corretto-headless
    # Install Docker
    amazon-linux-extras install docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    # Configure as Spark worker
    # Add commands to join the master
  EOF
}