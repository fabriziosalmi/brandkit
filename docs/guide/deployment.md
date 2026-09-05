---
title: Deployment
description: Putting BrandKit on a network safely — reverse proxy, TLS, authentication and hardening.
---

# Deployment

BrandKit has **no authentication of any kind**. Every endpoint is anonymous, and every generated file under `/static/uploads/` is publicly readable by anyone who knows the URL. That is a deliberate design for a personal tool on `localhost`.

The moment you expose it beyond your own machine, authentication is your job. This page covers how.

::: danger Do not put BrandKit directly on the public internet
Not because it is riddled with holes, but because it is an unauthenticated image-processing service. Anyone who finds it can burn your CPU, fill your disk, and read every asset any other user has generated. Always terminate at a proxy that authenticates.
:::

## Recommended shapes

| Situation | Shape |
| --- | --- |
| Just you, on your laptop | `docker compose up`, bound to `127.0.0.1` — done |
| Small team, private network | reverse proxy with TLS + HTTP basic auth or SSO |
| Remote access without opening ports | Cloudflare Tunnel + Access policy |
| Behind an existing corporate proxy | forward-auth / OIDC at the proxy layer |

## Bind to localhost first

The stock `docker-compose.yml` publishes `"8000:8000"`, which listens on **every interface**. On a machine with a public IP, that is the whole problem. Change it:

```yaml
    ports:
      - "127.0.0.1:8000:8000"
```

Now only a proxy on the same host — or an SSH tunnel — can reach it.

## Caddy: TLS and basic auth

Caddy gets you automatic Let's Encrypt certificates and authentication in about ten lines.

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

Two details that matter:

- **`request_body max_size` must be at least as large as `BRANDKIT_MAX_UPLOAD_MB`**, or the proxy will reject large uploads with a `413` before Flask ever sees them, and the error message will be confusing.
- **`basic_auth` protects `/static/` too**, because it applies to the whole site. That is exactly what you want — it is the only thing standing between a stranger and your generated assets.

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

        proxy_read_timeout 300s;   # background removal is slow
    }
}
```

`proxy_read_timeout` is not optional. A first-run background removal that downloads the ONNX model can take well over 60 seconds, and Nginx's default timeout will cut it off with a `504`.

::: warning Rate limiting sees the proxy's IP
Flask-Limiter keys on `get_remote_address()`, which reads the socket peer — the proxy — unless you tell Flask to trust forwarded headers. Behind a proxy, **all clients share one rate-limit bucket**, so the 5-uploads-per-minute limit becomes a global limit. Enforce per-client limits at the proxy instead (`limit_req` in Nginx, `rate_limit` in Caddy), or wrap the app with Werkzeug's `ProxyFix`.
:::

## Cloudflare Tunnel + Access (no open ports)

This is the strongest option, and it gives you real SSO instead of a shared password.

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
2. Under **Access → Applications**, add a self-hosted application for that hostname.
3. Attach an identity provider and an Allow policy — for example, "emails ending in `@yourcompany.com`".

No inbound firewall rule, no certificate management, and unauthenticated requests never reach the container.

::: tip Cloudflare's upload limit
The free plan caps request bodies at 100 MB, and the practical limit for a slow upstream is lower. Keep `BRANDKIT_MAX_UPLOAD_MB` well under it.
:::

## Production checklist

- [ ] Container bound to `127.0.0.1` or on an internal network only
- [ ] TLS terminated at the proxy
- [ ] Authentication in front of **everything**, including `/static/`
- [ ] Proxy body-size limit ≥ `BRANDKIT_MAX_UPLOAD_MB`
- [ ] Proxy read timeout ≥ 300 s
- [ ] Per-client rate limiting at the proxy layer
- [ ] Container memory limit set (background removal spikes)
- [ ] Retention shortened from the 24-hour default if the instance is shared — see [Performance](/guide/performance#file-cleanup)
- [ ] `BRANDKIT_SECRET_KEY` set to a stable value ([why](/reference/environment#brandkit-secret-key)) — required before raising the gunicorn worker count
- [ ] `FLASK_ENV` **not** set to `development` (that would enable the debugger)
- [ ] Dependencies current — `pip install -r requirements.txt --upgrade` and watch Dependabot

## HTTPS and Talisman

Flask-Talisman is initialised with `force_https=False`, because the app normally sits behind a proxy that has already done TLS. That means **BrandKit itself will not redirect HTTP to HTTPS or emit HSTS** — your proxy must. Caddy does it automatically; for Nginx, add:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```
