# Operations (Local & On-Prem)

- docker-compose orchestrates all services.
- No external cloud services required.
- For k8s, port: Postgres StatefulSet, Redis Deployment, MinIO Tenant, API & Web Deployments, Nginx Ingress.
- Backups: pg_dump cron + MinIO lifecycle rules.
