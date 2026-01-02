resource "google_container_cluster" "gke_test_cluster"{
    name = "gke-test-cluster"
    location = "us-west2"

    remove_default_node_pool = true
    initial_node_count = 1

    deletion_protection = false
}

resource "google_container_node_pool" "gke_test_cluster"{
    name = "gke-worker-node-pool"
    cluster = google_container_cluster.gke_test_cluster.name
    location = "us-west2"
    node_count = 1

    node_config {
        machine_type = "e2-small"

        oauth_scopes = [
            "https://www.googleapis.com/auth/cloud-platform"
        ]
    }
}