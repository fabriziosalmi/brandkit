---
title: Deployment
description: "Putting BrandKit on a network safely: reverse proxy, TLS, authentication, and hardening."
---

# Deployment

BrandKit has **no authentication of any kind**. Every endpoint is anonymous, and every generated file under `/static/uploads/` is publicly readable by anyone who knows the URL. That is a deliberate design for a personal tool on `localhost`.

The moment you expose it beyond your own machine, authentication is your responsibility. This page covers how to deploy it securely.

::: danger Do not put BrandKit directly on the public internet
BrandKit is an unauthenticated image-processing service. Exposing it directly allows unauthorized users to consume CPU and disk resources, and read generated assets. Always terminate requests at an authenticating reverse proxy.
:::

## Recommended architectures

| Environment | Architecture |
| --- | --- |
| Local workstation | `docker compose up`, bound to `127.0.0.1` |
| Small team / private network | Reverse proxy with TLS + HTTP basic auth or SSO |
| Remote access without open ports | Cloudflare Tunnel + Access policy |
| Enterprise intranet | Forward-auth / OIDC at the corporate proxy layer |

## Bind to localhost first

The default `docker-compose.yml` publishes `"8000:8000"`, which listens on all network interfaces. On a machine with a public IP, bind exclusively to loopback:

```yaml
    ports:
      - "127.0.0.1:8000:8000"
```

Now only a proxy on the same host (or an SSH tunnel) can reach the container.

## Caddy: TLS and basic auth

Caddy provides automatic TLS certificate provisioning and basic authentication in a concise configuration:

```yaml
# docker-compose.yml
services:
  brandkit:
    build: .
    restart: unless-stopped
    expose:
      - "8000"                    # internal only, no `ports:`
    volumes:
      - ./static/uploads:/app/static/uploads
    environment:
      - FLASK_ENV=production
      - BRANDKIT_MAX_UPLOAD_MB=32
    networks: [web]

  caddy:
    image: caddy:latest
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    networks: [web]

networks:
  web:

volumes:
  caddy_data:
  caddy_config:
```

```nginx
# Caddyfile
brandkit.example.com {
    encode zstd gzip

    basic_auth {
        # generate with: docker run --rm caddy caddy hash-password --plaintext 'yourpassword'
        alice $2a$14$replace.this.with.a.real.bcrypt.hash
    }

    request_body {
        max_size 32MB          # keep in step with BRANDKIT_MAX_UPLOAD_MB
    }

    reverse_proxy brandkit:8000
}
```

Key operational requirements:

- **`request_body max_size` must equal or exceed `BRANDKIT_MAX_UPLOAD_MB`**: Otherwise the proxy rejects large uploads with HTTP 413 before Flask inspects the payload.
- **`basic_auth` protects `/static/` as well**: Applying authentication site-wide prevents unauthorized enumeration of generated assets.

## Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name brandkit.example.com;

    ssl_certificate     /etc/letsencrypt/live/brandkit.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/brandkit.example.com/privkey.pem;

    auth_basic           "BrandKit";
    auth_basic_user_file /etc/nginx/.htpasswd;

    client_max_body_size 32m;      # match BRANDKIT_MAX_UPLOAD_MB

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        proxy_read_timeout 300s;   # background removal requires extended processing
    }
}
```

Setting `proxy_read_timeout` is mandatory. Initial background removal runs that download the ONNX model can exceed 60 seconds, which triggers an HTTP 504 gateway timeout under default proxy settings.

::: warning Rate limiting sees the proxy's IP
Flask-Limiter inspects `get_remote_address()`, reading the socket peer (the reverse proxy) unless configured to evaluate forwarded headers. Behind a proxy, clients share a single rate-limit bucket. Enforce per-client limits at the reverse proxy layer (`limit_req` in Nginx, `rate_limit` in Caddy), or configure Werkzeug's `ProxyFix`.
:::

## Cloudflare Tunnel + Access (no open ports)

This configuration enables identity provider authentication without opening inbound firewall ports:

```yaml
services:
  brandkit:
    build: .
    restart: unless-stopped
    expose: ["8000"]
    networks: [internal]

  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel --no-autoupdate run
    environment:
      - TUNNEL_TOKEN=${CF_TUNNEL_TOKEN}     # from a .env file, never committed
    networks: [internal]

networks:
  internal:
```

1. Create a tunnel in the [Cloudflare Zero Trust dashboard](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) and route a public hostname to `http://brandkit:8000`.
2. Under **Access → Applications**, create a self-hosted application for that hostname.
3. Configure an identity provider and define an Allow rule (e.g. emails matching `@yourcompany.com`).

No inbound firewall rule is required, certificate issuance is managed automatically, and unauthenticated requests are dropped at the edge.

::: tip Cloudflare upload limit
Cloudflare free tier caps request bodies at 100 MB. Ensure `BRANDKIT_MAX_UPLOAD_MB` is kept safely within upstream limits.
:::

## Production checklist

- [ ] Container bound to `127.0.0.1` or on an internal Docker network only
- [ ] TLS terminated at the reverse proxy
- [ ] Authentication enforced site-wide, including `/static/`
- [ ] Proxy request body limit ≥ `BRANDKIT_MAX_UPLOAD_MB`
- [ ] Proxy read timeout ≥ 300 s
- [ ] Per-client rate limiting enforced at the proxy layer
- [ ] Container memory limits configured
- [ ] Retention shortened from 24 hours on multi-user instances (see [Performance](/guide/performance#file-cleanup))
- [ ] `BRANDKIT_SECRET_KEY` configured with a persistent value ([rationale](/reference/environment#brandkit-secret-key)) before scaling Gunicorn workers
- [ ] `FLASK_ENV` set to `production`
- [ ] Dependencies tracked for security advisories using `pip-audit`

## HTTPS and Talisman

Flask-Talisman is configured with `force_https=False` because production instances sit behind a reverse proxy that terminates TLS. BrandKit does not redirect HTTP or emit HSTS headers directly; configure this at your proxy. For Nginx:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```
