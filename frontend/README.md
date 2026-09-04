# RS CLIMAS — Frontend

Frontend demonstrativo reconstruído a partir das referências visuais existentes em `doc_referencias` do projeto RS-CLIMAS.

## Rodar localmente

```bash
npm install
npm run dev
```

## Build para Vercel

```bash
npm run build
```

Configuração Vercel quando o repositório possui `frontend/` na raiz:

- Framework: Vite
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

O frontend funciona com dados mockados e não depende do backend para renderizar as telas. Isso permite validar a interface primeiro e conectar a API depois.
