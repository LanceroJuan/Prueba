# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito del repositorio

Repositorio centralizado de herramientas para estudios de sistemas eléctricos de potencia: scripts de cálculo, plantillas de informes, automatizaciones y documentación técnica.

## Estructura y dónde colocar cada cosa

| Carpeta | Contenido |
|---|---|
| `calculos/cortocircuito/` | Scripts de fallas trifásica/bifásica/monofásica, métodos IEC 60909 y ANSI/IEEE |
| `calculos/flujo_de_cargas/` | Flujo de potencia (Newton-Raphson, Gauss-Seidel), contingencias N-1, OPF |
| `calculos/protecciones/` | Coordinación de relés 50/51/21, curvas TCC, diferencial de transformadores |
| `plantillas_informes/` | Plantillas Word/LaTeX para memorias de cálculo e informes técnicos |
| `scripts_automatizacion/` | Procesamiento de datos SCADA, generación de reportes, interoperabilidad entre software |
| `documentacion_tecnica/` | Bases teóricas, resúmenes normativos, guías de uso, glosario, ADRs |

## Convenciones

### Nomenclatura de archivos de informe
`INFORME_<TIPO_ESTUDIO>_<PROYECTO>_<REV>.docx`
Ejemplo: `INFORME_CORTOCIRCUITO_SUBESTACION_A_REV2.docx`

### Scripts Python
- Cada script o módulo debe ir acompañado de su `requirements.txt` con las dependencias exactas.
- Librerías de referencia por área: flujo de cargas → `pandapower`, `PyPSA`; automatización → según tarea.

### Documentación técnica
Organizar en subcarpetas `normas/`, `metodologias/` y `guias_uso/` dentro de `documentacion_tecnica/`.

## Normas técnicas de referencia

Los cálculos deben indicar explícitamente la norma utilizada. Normas principales del dominio:
- **IEC 60909** — Corrientes de cortocircuito en sistemas de CA
- **IEEE Std 141 / 242 / 399** — Estudios eléctricos industriales
- **IEC 60255 / IEEE C37.112** — Relés de protección y curvas de operación
- **RETIE / NTC** — Normativa colombiana aplicable (si corresponde)
