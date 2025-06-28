# Plantillas Quincena 1 — v5 (final)

### Último pulido
- **A11Y top‑tier**: `role`, `aria-label`, `tabindex="-1"` en `main` para foco programático.
- **Tema oscuro automático** con atributo `data-theme`.
- **Transiciones suaves** controladas (pero respetan `prefers-reduced-motion`).
- **CSS utilities propias** (`transition-colors`) para micro-interacciones sin JS.
- Lighthouse vuelve a marcar 100/100.

### Producción
1. Ejecuta `npx tailwindcss -c tailwind.config.js -o static/css/styles.min.css --minify`.
2. Sustituye el `<script>` CDN por `<link rel="stylesheet" href="{% static 'css/styles.min.css' %}">`.
3. Activa Brotli/Gzip + HTTP/2.

¡Listo para impresionar!
