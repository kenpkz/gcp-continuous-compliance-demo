terraform {
  backend "gcs" {
    bucket = "your-bucket"
    prefix = "env/dev"
  }
}

provider "google" {
  project = "${var.project}"
  region = "${var.region}"
}
