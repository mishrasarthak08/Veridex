# Disaster Recovery & Backup Runbook

## Overview
This runbook details how to recover the database from a backup using our managed provider (Supabase).

## Automated Backups & PITR
- **Daily Backups:** Supabase automatically creates daily logical backups of our entire database.
- **Point-in-Time Recovery (PITR):** PITR is enabled (Pro plan+), backing up WAL (Write-Ahead Logs) continuously. This allows restoring the database to any exact second.

## How to Perform a Restore Drill

### 1. Identify the Target Time
Determine the exact UTC timestamp or logical backup ID you want to restore to.

### 2. Initiate Restore via Supabase Dashboard
1. Log in to the [Supabase Dashboard](https://app.supabase.com).
2. Select the `Veridex` project.
3. Navigate to **Database > Backups**.
4. If using PITR:
   - Select the **Point in Time** tab.
   - Enter the target UTC timestamp.
   - Click **Restore to this point**.
5. If using Daily Backups:
   - Select the **Scheduled Backups** tab.
   - Find the desired backup date.
   - Click the **Restore** button next to it.

### 3. Verify Restoration
Once the dashboard indicates the restore is complete:
1. Connect to the database via `psql`.
2. Run sanity checks to ensure the data matches expectations for that point in time.
3. Check the application dashboards (Frontend/CLI) to confirm connectivity.

### 4. Post-Restore
- Notify the team that the restore drill was successful.
- Document any issues or latency experienced during the recovery process.
