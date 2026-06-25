# Neon Setup

Create separate Neon databases for development, staging, and production.

Required extensions:

```sql
create extension if not exists postgis;
create extension if not exists vector;
```

Use the pooled connection string for application traffic and the direct connection string for migrations if Neon recommends it for the project.
