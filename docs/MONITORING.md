# Monitoring and Alerting Guide

This guide covers setting up monitoring and alerting for AccrediTrack.

## Overview

Monitoring helps track application health, performance, and errors. This guide provides options for both simple and comprehensive monitoring setups.

## Built-in Health Checks

### Health Check Endpoint

The application includes a health check endpoint:

```bash
curl http://your-domain.com/health/
# Returns: {"status": "ok"}
```

### Docker Health Checks

Health checks are configured in `docker-compose.yml` for all services:
- Database: Checks PostgreSQL readiness
- Backend: Checks `/health/` endpoint
- Frontend: Checks HTTP response
- Nginx: Checks HTTP response

View health status:
```bash
docker compose ps
```

## Logging

### Django Logs

Logs are configured in `backend/config/settings.py`:

- **Console**: All logs (JSON format in production)
- **File**: `backend/logs/django.log` (rotating, 10MB, 5 backups)
- **Error File**: `backend/logs/django_errors.log` (errors only)

View logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

### Log Levels

- **DEBUG**: Detailed information (development only)
- **INFO**: General information
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

## Option 1: Simple Monitoring with Docker Stats

### Basic Resource Monitoring

```bash
# CPU and memory usage
docker stats

# Disk usage
docker system df

# Container logs
docker compose logs -f
```

### Simple Uptime Check

Create a cron job:

```bash
# Add to crontab: crontab -e
*/5 * * * * curl -f http://your-domain.com/health/ || echo "Health check failed" | mail -s "Alert" admin@example.com
```

## Option 2: Prometheus + Grafana (Recommended for Production)

### Architecture

```
Application → Prometheus (metrics) → Grafana (visualization)
                      ↓
                  Alertmanager (alerts)
```

### Setup

#### 1. Install Prometheus Exporter

Add to `backend/requirements.txt`:
```
django-prometheus>=2.3.0
```

Update `backend/config/settings.py`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... existing middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Add metrics endpoint
urlpatterns = [
    # ... existing patterns
    path('metrics/', include('django_prometheus.urls')),
]
```

#### 2. Add Prometheus Service

Update `infra/docker-compose.yml`:
```yaml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
  ports:
    - "9090:9090"
  networks:
    - app-network

grafana:
  image: grafana/grafana:latest
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/provisioning:/etc/grafana/provisioning
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  networks:
    - app-network
  depends_on:
    - prometheus

volumes:
  prometheus_data:
  grafana_data:
```

#### 3. Create Prometheus Configuration

Create `infra/prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### Key Metrics to Monitor

- **Request Rate**: Requests per second
- **Error Rate**: 4xx/5xx responses per second
- **Response Time**: P50, P95, P99 latencies
- **Database Connections**: Active connections
- **Memory Usage**: Container memory usage
- **CPU Usage**: Container CPU usage
- **Disk Usage**: Database and log disk usage

## Option 3: Cloud Monitoring Services

### Google Cloud Monitoring

If deployed on Google Cloud:

1. Enable Cloud Monitoring API
2. Install Cloud Monitoring agent
3. Create dashboards in Cloud Console

### AWS CloudWatch

If deployed on AWS:

1. Install CloudWatch agent
2. Configure log groups
3. Set up CloudWatch dashboards

### Datadog / New Relic

For comprehensive APM:

1. Sign up for service
2. Install agent
3. Configure application
4. Set up dashboards and alerts

## Alerting

### Alert Conditions

Set up alerts for:

1. **Health Check Failures**
   - Endpoint returns non-200 status
   - Service is down for > 1 minute

2. **High Error Rate**
   - > 5% of requests return 5xx errors
   - Sustained for > 5 minutes

3. **High Response Time**
   - P95 latency > 2 seconds
   - Sustained for > 10 minutes

4. **Resource Exhaustion**
   - Memory usage > 90%
   - Disk usage > 85%
   - CPU usage > 90% (sustained)

5. **Database Issues**
   - Connection pool exhausted
   - Slow queries (> 1 second)
   - Replication lag (if applicable)

### Alert Channels

- **Email**: For critical alerts
- **Slack**: For team notifications
- **PagerDuty**: For on-call escalation
- **SMS**: For critical production issues

### Example: Prometheus Alert Rules

Create `infra/prometheus/alerts.yml`:
```yaml
groups:
  - name: accreditrack
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: ServiceDown
        expr: up{job="backend"} == 0
        for: 1m
        annotations:
          summary: "Backend service is down"
```

## Log Aggregation

### Option 1: Docker Logs (Simple)

```bash
# Follow all logs
docker compose logs -f

# Export logs
docker compose logs > logs.txt
```

### Option 2: ELK Stack (Elasticsearch, Logstash, Kibana)

For centralized log management:

1. Add ELK services to docker-compose.yml
2. Configure log shipping from containers
3. Create Kibana dashboards

### Option 3: Cloud Logging

- **Google Cloud**: Cloud Logging
- **AWS**: CloudWatch Logs
- **Azure**: Azure Monitor

## Uptime Monitoring

### External Services

Use third-party services for external uptime monitoring:

- **UptimeRobot**: Free tier available
- **Pingdom**: Comprehensive monitoring
- **StatusCake**: Free tier available

Configure to check:
- `https://your-domain.com/health/` every 5 minutes
- Alert if down for > 2 minutes

## Performance Monitoring

### Application Performance Monitoring (APM)

Consider APM tools for detailed performance insights:

- **Sentry**: Error tracking and performance
- **New Relic**: Full-stack APM
- **Datadog**: Infrastructure and APM
- **Django Debug Toolbar**: Development only

### Database Monitoring

Monitor database performance:

```sql
-- Slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Connection stats
SELECT count(*) FROM pg_stat_activity;
```

## Recommended Monitoring Stack

For production, recommended minimum:

1. **Health Checks**: Docker health checks + external uptime monitor
2. **Logging**: Django file logs + Docker logs
3. **Metrics**: Prometheus + Grafana (or cloud equivalent)
4. **Alerts**: Email + Slack notifications
5. **Error Tracking**: Sentry (optional but recommended)

## Maintenance

### Regular Tasks

- **Weekly**: Review error logs and metrics
- **Monthly**: Review and optimize slow queries
- **Quarterly**: Review and update alert thresholds
- **As needed**: Investigate and resolve alerts

### Log Rotation

Logs are automatically rotated (10MB, 5 backups). Monitor disk usage:

```bash
docker system df
du -sh backend/logs/
```

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Django Logging](https://docs.djangoproject.com/en/stable/topics/logging/)
- [Docker Logging Drivers](https://docs.docker.com/config/containers/logging/)
