source "google_container_cluster" "gke_test_cluster"{
    name = "gke_test_cluster"
    location = "us-west2"

    remove_default_node_pool = true
    initial_node_count = 1

    deletion_protection = false
}

resource "google_container_node_pool" "worker_nodes"{
    name = "gke_worker_node_pool"
    cluster = google_container_cluster.gke_test_cluster
    location = "us-west2"
    node_count = 1

    node_config {
        machine_types = "e2-medium"

        oauth_scopes = [
            "https://www.googleapis.com/auth/cloud-platform"
        ]
    }
}