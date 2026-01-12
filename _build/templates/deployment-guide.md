# Deployment Guide Template

Documentation template for deployment procedures and production configuration.

## Deployment Documentation

```markdown
# [Project Name] - Deployment Guide

## Deployment Targets

| Environment | URL | Branch | Auto-deploy |
|-------------|-----|--------|-------------|
| Production | app.example.com | main | No (manual) |
| Staging | staging.example.com | develop | Yes |
| Preview | pr-*.example.com | PR branches | Yes |

## Prerequisites

- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates configured
- [ ] DNS records set up
- [ ] Monitoring configured

## Environment Variables

### Required
```env
# Application
NODE_ENV=production
APP_URL=https://app.example.com

# Database
DATABASE_URL=postgresql://...

# Auth
AUTH_SECRET=<generated-secret>

# External Services
SMTP_HOST=smtp.example.com
SMTP_PORT=587
```

### Optional
```env
# Monitoring
SENTRY_DSN=https://...
ANALYTICS_ID=UA-...

# Feature Flags
ENABLE_NEW_FEATURE=false
```

## Deployment Steps

### Vercel (Recommended)

1. **Connect Repository**
   ```bash
   vercel link
   ```

2. **Set Environment Variables**
   ```bash
   vercel env add DATABASE_URL production
   vercel env add AUTH_SECRET production
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Docker

1. **Build Image**
   ```bash
   docker build -t app:latest .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name app \
     -p 3000:3000 \
     --env-file .env.production \
     app:latest
   ```

### Manual (VPS/Server)

1. **Clone and Build**
   ```bash
   git clone [repo] /var/www/app
   cd /var/www/app
   pnpm install --frozen-lockfile
   pnpm build
   ```

2. **Configure Process Manager**
   ```bash
   pm2 start ecosystem.config.js --env production
   pm2 save
   ```

3. **Configure Nginx**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name app.example.com;

       ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

       location / {
           proxy_pass http://127.0.0.1:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

## Database Migrations

### Pre-deployment
```bash
# Backup database first
pg_dump -Fc $DATABASE_URL > backup-$(date +%Y%m%d).dump

# Run migrations
pnpm db:migrate:deploy
```

### Rollback
```bash
# Restore from backup
pg_restore -d $DATABASE_URL backup-YYYYMMDD.dump
```

## Health Checks

### Endpoints
| Endpoint | Expected | Purpose |
|----------|----------|---------|
| `/api/health` | 200 OK | Basic health |
| `/api/health/db` | 200 OK | Database connectivity |
| `/api/health/ready` | 200 OK | Full readiness |

### Monitoring
- **Uptime:** Pingdom / UptimeRobot
- **Errors:** Sentry / GlitchTip
- **Metrics:** Grafana / Datadog
- **Logs:** Loki / CloudWatch

## Rollback Procedure

### Vercel
```bash
vercel rollback
```

### Docker
```bash
docker stop app
docker run -d --name app app:previous-tag
```

### Manual
```bash
cd /var/www/app
git checkout <previous-tag>
pnpm install --frozen-lockfile
pnpm build
pm2 restart all
```

## Post-Deployment Checklist

- [ ] Verify health check endpoints
- [ ] Test critical user flows
- [ ] Check error monitoring
- [ ] Verify database migrations applied
- [ ] Monitor performance metrics
- [ ] Update status page if applicable

## Incident Response

### P1 - Site Down
1. Check health endpoints
2. Review error logs
3. Rollback if needed
4. Investigate root cause
5. Post-mortem within 24h

### P2 - Degraded Performance
1. Check metrics dashboard
2. Identify bottleneck
3. Scale if needed
4. Implement fix
5. Document findings
```

---

**Template Version:** 1.0
**Used By:** appgen (Phase 7), webgen (Phase 6)
**Lines:** ~180
