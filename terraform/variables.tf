variable "project_id" {
  type        = string
  description = "The GCP Project ID (must already exist — created by vpc-foundation layer)"
}

variable "region" {
  type        = string
  description = "The default GCP region"
  default     = "us-east4"
}

variable "vpc_name" {
  type        = string
  description = "Name of the VPC created by the vpc-foundation layer"
  default     = "gdc-pm-vpc"
}

variable "gke_subnet_name" {
  type        = string
  description = "Name of the GKE subnet created by the vpc-foundation layer"
  default     = "subnet-gke"
}
