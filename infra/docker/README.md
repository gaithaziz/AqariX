# Local Docker

Use Docker Compose for local service separation.

```bash
docker compose up --build
docker compose down
docker compose logs -f api
```

Services:

- `api`: FastAPI backend.
- `jobs`: placeholder Python worker.
- `db`: local PostgreSQL with PostGIS and pgvector.

Production uses Render, Neon, Vercel, Clerk, and Cloudflare R2. Do not introduce Kubernetes for the MVP.
