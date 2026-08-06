variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment stage environment"
}

variable "region" {
  type        = string
  default     = "eu-west-1"
  description = "AWS / Cloud region"
}

variable "app_name" {
  type        = string
  default     = "context-router"
  description = "Application service name"
}
