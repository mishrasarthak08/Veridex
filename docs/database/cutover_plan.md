# Cloud Database Cutover Plan

## Overview
This runbook details the procedure for migrating data from the local `postgres:16-alpine` development container to the managed Supabase PostgreSQL instance.

## Pre-requisites
- The new Supabase instance is provisioned.
- Connection strings for both direct (`DATABASE_URI`) and pooled (`DATABASE_URL_POOLER`) access are available.
- `pg_dump` and `pg_restore` CLI tools are installed on the machine running this migration.

## Cutover Steps

### Step 1: Lock the Local Application
To prevent writes to the database during migration, either scale down the application containers or pause incoming API requests:
```bash
docker-compose stop api workers
```

### Step 2: Backup Local Database
Dump the local development database schema and data into a custom-format backup file:
```bash
pg_dump -U veridex -h localhost -d veridex_db -F c -f veridex_local_dump.backup
```

### Step 3: Run Alembic Migrations on Cloud DB
Ensure the remote Supabase database has the correct schema initialized via Alembic.
```bash
# Set env var pointing to Supabase direct connection
export DATABASE_URI="postgresql+asyncpg://postgres:SUPABASE_PASSWORD@db.xxxx.supabase.co:5432/postgres"

# Apply migrations
uv run alembic upgrade head
```
*Note: We apply Alembic directly instead of restoring the schema from `pg_dump` to ensure the Alembic `alembic_version` table is correctly registered.*

### Step 4: Restore Data to Cloud DB
Restore the data-only (no schema definitions) from the local dump into the cloud database:
```bash
pg_restore -U postgres -h db.xxxx.supabase.co -d postgres --data-only -1 veridex_local_dump.backup
```

### Step 5: Update Application Configurations
Update the application configuration (`.env` or Secrets Manager) with the new credentials:
- `POSTGRES_SERVER` -> db.xxxx.supabase.co
- `DATABASE_URL_POOLER` -> pooled connection string

### Step 6: Restart & Verify
Restart the application containers:
```bash
docker-compose up -d api workers
```
Verify the `/api/v1/projects` endpoint returns the migrated data successfully.
