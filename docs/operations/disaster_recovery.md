# Disaster Recovery Playbook

## 1. Database Failure (PostgreSQL)
- **Backup Strategy**: Nightly `pg_dump` pushed to S3/MinIO bucket.
- **Restore Procedure**: 
  1. Scale down application pods to 0.
  2. Restore from snapshot: `pg_restore -d veridex < backup.dump`
  3. Scale up pods.

## 2. Vector DB Failure (Qdrant)
- **Backup Strategy**: Snapshot API `/collections/{name}/snapshots`.
- **Restore Procedure**: If Qdrant goes completely offline, use the ingestion pipeline's replay mechanism to re-embed source documents.

## 3. Worker Node Loss
- **Recovery**: Automatic. The Kubernetes HPA and Deployment configs ensure new Pods are automatically provisioned. Celery `late_acks` ensures tasks are redelivered to healthy nodes.
