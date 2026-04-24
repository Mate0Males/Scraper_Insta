  # Instagram Scraper

  Extrae perfil, posts y los primeros 3 comentarios de cuentas públicas de Instagram.
  Incluye backend en Flask y UI en React + Vite.

  ## Requisitos

  - Python 3.10+
  - Node.js 18+

  ## Instalación

  *Backend:*
  bash
  pip install -r requirements.txt

  Frontend:
  npm install

  Configuración

  1. Abrir Instagram en el navegador con sesión iniciada
  2. F12 → Application → Cookies → www.instagram.com
  3. Copiar el valor de la cookie sessionid
  4. Pegarlo en scraper.py en la variable SESSION_ID

  ▎ El session ID expira con el tiempo. Si aparece error 401, repetir el paso anterior.

  Uso

  Abrir dos terminales en la carpeta del proyecto:

  Terminal 1 — backend:
  python api.py

  Terminal 2 — frontend:
  npm run dev

  Abrir http://localhost:5173 en el navegador.

  Estructura del proyecto

  Scraper_Insta/
  ├── scraper.py          ← lógica principal de scraping
  ├── api.py              ← servidor Flask
  ├── requirements.txt
  ├── index.html
  ├── package.json
  ├── vite.config.js
  └── src/
      ├── main.jsx
      ├── App.jsx
      ├── App.css
      └── components/
          ├── SearchForm.jsx
          ├── ProfileCard.jsx
          └── PostCard.jsx

  Qué extrae

  - Nombre, bio, seguidores, seguidos, cantidad de posts
  - Hasta 20 posts del perfil
  - Los 3 primeros comentarios de cada post

  Notas

  - Solo funciona con cuentas públicas
  - El archivo *_data.json generado no se sube al repositorio
  - Las dos terminales deben estar corriendo al mismo tiempo