# Portfolio en CC:Tweaked (ComputerCraft)

Almacena y visualiza operaciones financieras en una base de datos, mostrándolas en **CC:Tweaked**, un mod de computadoras dentro de Minecraft. Este proyecto permite visualizar un portafolio financiero *a modo básico* dentro del juego.

![Vista del Portfolio + Piechart](images/Muestra1.png)
![Profit por ticker](images/Muestra2.1.png)
![Vista de operaciones por ticker](images/Muestra3.1.png)

## Tecnologías utilizadas

- **PostgreSQL**: para la base de datos de operaciones financieras.
- **Python (FastAPI)**: como servidor API para conectar ComputerCraft con la base de datos.
- [**Basalt UI Framework**](https://github.com/Pyroxenium/Basalt): para programar la GUI en ComputerCraft.
- **API del Broker**: para importar tus operaciones financieras.
- **CC:Tweaked (ComputerCraft) Mod**: El propósito principal de este proyecto, para verlo dentro del juego.

Actualmente la importación de operaciones está implementada con la API de IOL, pero este script puede ser fácilmente extendido a la API de PPI si se requiere.

## Instalación server-side

Clona este repositorio, `cd` hacia el directorio raíz del mismo

renombra el archivo .env.example a .env y ábrelo con tu editor de texto de preferencia

Para obtener una contraseña aleatoria puedes usar el comando `openssl rand -hex 32` o [usar esta página web para generar uno](https://codebeautify.org/generate-random-hexadecimal-numbers)

Ahora ingresa a la carpeta portfolio con `cd portfolio`, lo mismo, renombra el .env.example a .env

En este archivo deberás configurar los datos acorde a tu broker, para InvertirOnline primero debes solicitar la autorización para el uso de la API (puedes ver el cómo en la [página de la documentación](https://api.invertironline.com/)), posteriormente debes colocar el usuario y contraseña de tu cuenta en este archivo .env, [tal cual como lo indica la documentación de autenticación de IOL](https://api.invertironline.com/).

"fecha_desde" significa desde qué fecha importaremos las operaciones de tu broker hacia la base de datos

> [!NOTE]
> IOL te cobrará un recargo de 500$ (pesos) si tienes más de 25.000 llamadas a la API en un mes. Este proyecto implementa un sistema caché para evitar recargos, pero tenlo en cuenta si operas hace mucho tiempo y tienes una excesiva cantidad de operaciones en tu cuenta.

Ejecuta `docker compose up -d` para iniciar los containers de Postgres (DB) y Quickchart (para los pie-charts del portfolio), además del servidor API principal y ya estarás listo server-side.

## Preparar operaciones del portfolio

Una vez ya configurado los datos de la API de tu broker, ejecuta el main.py ubicado en src/ con `python3 main.py` para importar todas tus operaciones hacia la base de datos

## Instalación client-side (in-game)

Primero debes abrir la configuración del mundo, esta se encuentra en `/directorioMinecraft/saves/TUMUNDO/serverconfig/computercraft-server.toml`

debes modificar 2 datos:

- Agrega un 0 al límite de almacenamiento de las computadoras "COMPUTER_SPACE_LIMIT" (es para poder renderizar los pie charts, no los pude comprimir más)

- [En caso de que tu servidor API corra en la red local, permite el acceso a IP's locales](https://tweaked.cc/guide/local_ips.html)

Descarga el install.lua hacia la computadora in-game con este comando
`wget run https://raw.githubusercontent.com/JoaGamo/Portfolio-CC/refs/heads/main/src/computercraft/install.lua`

Se descargarán todos los archivos automáticamente, deberás configurar el archivo .env.example (y renombrarlo a .env) con el comando `edit` para colocar la URL del servidor API, al terminar ejecuta el main.lua con `./main.lua`

## Limitaciones

- Debido a la limitada paleta de colores en ComputerCraft (16 colores) y, que hay colores que Sanjuuni (librería gráfica) no procesa de manera perfecta y colores que no sirven (por ej, color negro siendo que tenemos un fondo negro), en total nos quedaron 9 colores. Si tu portfolio tiene más de 9 tickers, verás que en el pie-chart habrán tickers con colores repetidos. Es sólo un bug visual.

- No encontré una API gratuita para manejar los SPLITS de CEDEARs, por lo tanto, si ocurrió un split/reverse split mientras poseías un stock y recibiste acciones adicionales, estas no se registrarán en la base de datos (al menos, con la API de IOL)

- API de IOL: la API no permite manejar (obtener datos precisos de) dividendos, por lo tanto, no los verás registrados en la base de datos.

