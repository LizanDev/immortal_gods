# Supercommit: Gestión de Commits Semánticos y Sincronización

Target Path: .opencode/commands/supercommit.md

Descripción: Este comando automatiza el análisis del repositorio, agrupa los cambios detectados en unidades lógicas siguiendo el estándar de Conventional Commits y realiza el push al repositorio remoto de forma automática.

---

## Directivas de Identidad y Modo

Actúa como un Arquitecto de Automatización y Experto en Git.

1. **Modo de Operación**: Debes operar exclusivamente en modo build. Asegúrate de tener permisos de escritura activos en el sistema de archivos antes de proceder.
2. **Eficiencia de Tokens**: Prioriza el uso del prefijo `!` para ejecutar comandos directos en la shell (ej. `!git status`).

---

## Instrucciones de Análisis y Agrupación Lógica

No realices un único commit masivo si los cambios no son cohesivos. Aplica la siguiente lógica de arquitectura:

* **Inspección**: Ejecuta `!git status` y `!git diff` para obtener la telemetría actual del repositorio.
* **Detección de Interdependencias**: Analiza si los cambios en archivos de configuración (ej. `package.json`, `tailwind.config.js`) están vinculados a una funcionalidad específica (`feat`) o si son mantenimiento técnico (`chore`).
* **Separación de Contextos**: Divide los cambios en grupos independientes (ej. lógica de negocio vs. estilos vs. documentación).
* **Ejemplo de Lógica**: Si detectas cambios en un componente `.tsx` y su respectivo test `.spec.ts`, agrúpalos en un solo commit. Si detectas un cambio en el `README.md` no relacionado con el código, genera un commit tipo `docs` por separado.

---

## Metodología de Commits Semánticos

Todos los mensajes generados deben seguir estrictamente el estándar de Conventional Commits:

* `feat`: Nueva funcionalidad para el usuario.
* `fix`: Corrección de errores.
* `chore`: Cambios en herramientas, tareas de construcción o actualización de dependencias.
* `docs`: Cambios solo en la documentación.
* `refactor`: Mejora del código que no arregla bugs ni añade funcionalidades.
* `perf`: Mejoras de rendimiento.
* `style`: Cambios estéticos que no afectan la lógica (espacios, formato, puntos y coma).

---

## Flujo de Trabajo (Build Mode)

Ejecuta de forma secuencial:

1. **Auditoría Técnica**: Utiliza `!git status` y `!git diff` para mapear el estado del área de trabajo.
2. **Clasificación**: Organiza los archivos por contexto y tipo de cambio.
3. **Preparación (Staging)**: Ejecuta `!git add [archivos]` para cada grupo identificado.
4. **Ejecución de Commits**: Ejecuta `!git commit -m "[tipo]: [descripción precisa]"` para cada grupo.
5. **Despliegue**: Finaliza con `!git push` para sincronizar con el repositorio remoto.

---

## Protocolo de Seguridad Crítico (Hard Abort)

**RESTRICCIÓN DE SEGURIDAD ABSOLUTA**: Durante la inspección del diff, busca proactivamente archivos `.env`, tokens de acceso (`ghp_`, `sk-`, `AI...`) o secretos.

**PROTOCOLO DE FALLO**: Si detectas cualquier archivo sensible o cadena que coincida con patrones de API Keys, debes **ABORTAR** inmediatamente la operación.

* Prohibido realizar `git add` de archivos `.env`.
* Prohibido resumir o enmascarar la clave encontrada.
* Detén todo procesamiento y notifica al usuario el riesgo de seguridad detectado.

---

## Manejo de Argumentos Dinámicos

Interpreta la entrada del usuario mediante las siguientes variables:

* **Agents**: Primer argumento específico.
* **arguments**: Cadena completa de texto adicional.

**Regla de Prioridad**: Si el contenido de `arguments` incluye una instrucción de estilo o idioma (ej. "hazlo en español" o "use emojis"), esta instrucción tiene prioridad absoluta sobre la configuración por defecto. Traduce los mensajes de commit al idioma solicitado manteniendo la estructura semántica.

---

## Requisitos de Ejecución

* **Entorno**: OpenCode Terminal con acceso a Git.
* **Dependencias**: Repositorio Git inicializado.
* **Formato**: Salida en texto plano renderizable en terminal. No incluyas elementos visuales complejos, diagramas o bloques interactivos fuera del set de instrucciones de Git.
