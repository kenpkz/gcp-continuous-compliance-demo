terraform {
  backend "gcs" {
    bucket = "you-bucket"
    prefix = "env/dev"
  }
}

provider "google" {
  project = "${var.project}"
  region = "${var.region}"
}
