terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project               = var.project_id
  region                = var.region
  billing_project       = var.project_id
  user_project_override = true
}

# ============================================================================
# DATA SOURCES — reference networking created by the vpc-foundation layer
# (bdau-basic-vpc/scenarios/gdc-pm)
# ============================================================================

data "google_compute_network" "vpc" {
  name    = var.vpc_name
  project = var.project_id
}

data "google_compute_subnetwork" "gke_subnet" {
  name    = var.gke_subnet_name
  region  = var.region
  project = var.project_id
}
