# IOS-XE Hardening Verification Tool (HVT)

**Version 6.5.0** | Python 3.8+ | Modular OOP Architecture | 65 Security Checks | PDF Generation | Excel Export | NX-OS Detection

Una herramienta automatizada para verificar la configuración de seguridad de dispositivos Cisco IOS, IOS-XE y NX-OS (detección) basada en las mejores prácticas y guías oficiales de Cisco. Genera reportes HTML modernos con tema azul profesional, PDFs completos para entrega a clientes, y archivos Excel multi-hoja con tablas dinámicas para análisis detallado.

---

## ⚡ Quick Start (5 Minutos)

**¿Primera vez usando HVT6?** Prueba esto para ver resultados inmediatamente:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Colocar archivos en repo/ (necesitas 3 archivos por dispositivo)
repo/router1_sh_ver.txt    # salida de: show version
repo/router1_sh_inv.txt    # salida de: show inventory
repo/router1_sh_run.cfg    # salida de: show running-config

# 3. Ejecutar análisis
python hvt6.py

# 4. Ver reportes
open index.html
```

**¡Listo!** Verás reportes HTML con:

- ✅ Análisis de 65 verificaciones de seguridad (CIS/NIST/STIG)
- 📊 Puntuación global y por categoría (271 puntos totales)
- 🎨 Dashboard moderno con tema azul profesional
- ⚠️ Advertencias si la versión está por debajo de la línea base de Cisco
- 🔒 Credenciales seguras vía variables de entorno (.env)

**¿Necesitas más control?** Ver sección detallada "Inicio Rápido" abajo para opciones avanzadas como generación de PDF, modo verbose, y configuración personalizada.

---

## 🚀 Inicio Rápido (Detallado)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Colocar archivos de dispositivos en repo/
#    Por cada dispositivo, necesitas 3 archivos:
#    - {hostname}_sh_ver.txt   (show version)
#    - {hostname}_sh_inv.txt   (show inventory)
#    - {hostname}_sh_run.cfg   (show running-config)

# 3. Ejecutar análisis
python hvt6.py --customer "NombreCliente"

# 3b. Ejecutar análisis con PDF para entregar al cliente
python hvt6.py --customer "NombreCliente" --generate-pdf

# 3c. Ejecutar análisis con Excel para análisis detallado (NUEVO en v6.5)
python hvt6.py --customer "NombreCliente" --generate-excel

# 3d. Generar todos los formatos (PDF + Excel)
python hvt6.py --customer "NombreCliente" --generate-pdf --generate-excel

# 4. Ver reportes
open index.html
open results/Security_Audit_NombreCliente_YYYYMMDD.pdf   # Si usaste --generate-pdf
open results/Security_Audit_NombreCliente_YYYYMMDD.xlsx  # Si usaste --generate-excel
```

**Salida:** Reportes HTML individuales (tema azul moderno) + dashboard consolidado + CSV de resultados + PDF completo (opcional) + Excel multi-hoja con tablas dinámicas (opcional)

---

## ⚠️ HVT5 Archivado (Legacy Version)

**HVT5 (v2.2.2) ha sido movido a `legacy/hvt5/`**

Si estabas usando hvt5.py previamente, ahora se encuentra en el directorio `legacy/hvt5/` para preservación. **HVT5 ya no recibe soporte activo** - se recomienda migrar a HVT6.

- **Usar HVT5 (solo para comparación):** `python legacy/hvt5/hvt5.py`
- **Migrar a HVT6:** Ver [HVT6_MIGRATION_GUIDE.md](docs/guides/HVT6_MIGRATION_GUIDE.md)
- **Documentación HVT5:** Ver [legacy/hvt5/README.md](legacy/hvt5/README.md)

**Razón del cambio:** HVT5 y HVT6 representan arquitecturas completamente diferentes. HVT6 ofrece arquitectura modular OOP, detección inteligente de versiones, generación de PDFs, y reportes HTML modernos.

---

## ✨ Novedades en Versión 6.3 (2025-11-05)

### 🔍 Detección de Dispositivos NX-OS (NEW)

HVT6 ahora detecta automáticamente dispositivos Cisco Nexus (NX-OS) y captura metadatos completos:

- **Detección Inteligente**: Identifica OS NX-OS mediante cadena explícita "Cisco Nexus Operating System (NX-OS)"
- **Extracción de Metadatos**: Captura versión NX-OS (ej: 10.5(3)), modelo (ej: Nexus9000 C93108TC-FX) y número de serie
- **Validación de Versión**: Compara contra línea base recomendada (NX-OS 9.3.10+)
- **Advertencia Clara**: Panel visual indica que verificaciones de seguridad NX-OS aún no están implementadas
- **Metadata Preservada**: Información del dispositivo capturada para análisis futuro

**Estado Actual**: Dispositivos NX-OS son detectados pero el análisis de seguridad se omite con advertencia. El análisis completo de seguridad NX-OS está planificado para v6.4.0 basado en [Cisco NX-OS Security Hardening Guide](https://sec.cloudapps.cisco.com/security/center/resources/securing_nx_os.html).

**Salida de Ejemplo**:
```
⚠ NX-OS Device Detected

Device: BVS-LAB-NXCORE
OS: NX-OS 10.5(3)
Model: N9K-C93108TC-FX

NX-OS security checks are not yet implemented.
Device metadata has been captured, but security analysis will be skipped.

NX-OS support is planned for a future release (v6.4.0).
```

### 🛡️ Verificaciones de Seguridad Complejas (QW-001 Wave 3)

**65 verificaciones (+8% desde v6.2) | 271 puntos (+12%)**

#### Verificaciones Implementadas (+5 checks, 30 puntos)

1. **Infrastructure ACL Protection (iACL)** (10 pts, STIG V-215852) - CRITICAL
   Verifica que exista ACL de protección de infraestructura aplicada a control-plane o VTY. Protege contra acceso SSH/SNMP no autorizado y ataques de protocolos de enrutamiento dirigidos al dispositivo.

2. **BGP Neighbor Security** (4 pts, CIS 5.4.1)
   Valida autenticación MD5 y/o TTL security (GTSM) en vecinos BGP. Previene hijacking de sesiones y ataques DoS. Crítico para routers con conexión a Internet.

3. **OSPF MD5 Authentication** (4 pts, CIS 5.3.1)
   Verifica autenticación message-digest en áreas OSPF y claves MD5 en interfaces. Previene inyección de rutas falsas por routers maliciosos.

4. **EIGRP MD5 Authentication** (4 pts, CIS 5.3.2)
   Valida key chains y autenticación MD5 en interfaces EIGRP. Protege contra vecinos maliciosos y manipulación de rutas.

5. **Unused Interfaces Shutdown** (8 pts, CIS 3.2.1)
   Identifica interfaces físicas sin configuración que están activas. Reducción de superficie de ataque mediante deshabilitación de puertos no utilizados.

### 🎯 Arquitectura de Verificaciones Complejas

Todas las verificaciones de Wave 3 implementan clases Python personalizadas:

- **InfrastructureACLCheck**: Validación multi-ubicación (control-plane, VTY, interfaces) con análisis de contenido ACL
- **BGPSecurityCheck**: Iteración de vecinos con validación dual (MD5 + TTL)
- **OSPFAuthenticationCheck**: Validación dos niveles (área + interfaz)
- **EIGRPAuthenticationCheck**: Validación de key chains + autenticación de interfaz
- **UnusedInterfacesCheck**: Enumeración de interfaces con clasificación multi-criterio

### 📊 Cobertura de Estándares Ampliada

- **CIS Benchmark:** 72% → ~80% de cobertura (Nivel 1)
- **NIST SP 800-53:** Controles SC-8, SC-23, SC-5, SC-7, AC-4, CM-7, AU-4
- **DISA STIG:** V-215852 (Infrastructure ACL) implementado
- **Control Plane:** 9% → ~13% (+44% relativo) - Seguridad de enrutamiento mejorada
- **Data Plane:** 6% → ~7% (+16% relativo) - Interfaces no utilizadas

### 🔧 Implementación Técnica

- **5 clases personalizadas** (~890 líneas de código)
- **5 plantillas Jinja2** (~340 líneas) con tablas, gráficos y recomendaciones
- **Templates interactivos**: Tablas de vecinos BGP, áreas OSPF, key chains EIGRP
- **Validación robusta**: Manejo de ACLs faltantes, protocolos no configurados, casos límite
- **Compatibilidad total**: Cero cambios incompatibles con v6.2

### 📚 Plantillas de Reporte Nuevas

- `infrastructure_acl.j2` - Análisis detallado de iACL con score de calidad (0-100)
- `bgp_security.j2` - Tabla de seguridad de vecinos BGP (MD5 + TTL)
- `ospf_auth.j2` - Estado de autenticación por área e interfaz
- `eigrp_auth.j2` - Key chains y autenticación de interfaces
- `unused_interfaces.j2` - Clasificación de interfaces (en uso / shutdown / activas no usadas)

---

## ✨ Novedades en Versión 6.2 (2025-11-05)

### 🔒 Gestión Segura de Credenciales (QW-003)

- **Variables de Entorno**: Credenciales ahora se cargan desde archivo `.env` en lugar de YAML en texto plano
- **Sistema de Prioridad**: .env → YAML (deprecado) → prompt interactivo
- **Abstración de Credenciales**: Nueva clase `CredentialManager` preparada para HashiCorp Vault (v7.0+)
- **Documentación Completa**:
  - `SECURITY.md` (750+ líneas) con guía de rotación de contraseñas
  - `.env.example` con ejemplos para CI/CD, Docker, Kubernetes
  - Sección completa en README con troubleshooting
- **Advertencias de Deprecación**: Alertas visibles cuando se usan credenciales YAML
- **Mitigación**: Si usaste v6.0-6.1, las contraseñas están en historial de Git (ver SECURITY.md para rotación)

### 🛡️ Expansión de Verificaciones de Seguridad (QW-001)

**60 verificaciones (+20% desde v6.1) | 241 puntos (+25%)**

#### Wave 1: Verificaciones Rápidas (+5 checks, 21 puntos)

1. **no ip source-route** (5 pts) - Previene ataques de source routing (CIS 2.1.1)
2. **login block-for** (5 pts) - Protección contra fuerza bruta (CIS 1.4.1, NIST AC-7)
3. **login delay** (3 pts) - Retardo entre intentos de login (CIS 1.4.2)
4. **login on-failure log** (3 pts) - Registro de fallos de autenticación (CIS 1.4.3)
5. **security passwords min-length** (5 pts) - Longitud mínima de contraseña ≥12 (CIS 1.1.3)

#### Wave 2: Verificaciones a Nivel de Interfaz (+5 checks, 27 puntos)

6. **no ip redirects** (5 pts) - Deshabilita ICMP redirects por interfaz (CIS 2.2.1)
7. **Unicast RPF (uRPF)** (8 pts) - Anti-spoofing con validación de ruta inversa (CIS 2.3.1)
8. **RSA key size ≥ 2048** (5 pts) - Fortaleza criptográfica para SSH/HTTPS (CIS 1.2.2)
9. **NTP authentication** (5 pts) - Autenticación de servidores de tiempo (CIS 4.3.1)
10. **logging buffered ≥ 32KB** (4 pts) - Capacidad de buffer de logs (CIS 4.1.1)

### 📊 Cobertura de Estándares Mejorada

- **CIS Benchmark:** 60% → 72% de cobertura (Nivel 1)
- **NIST SP 800-53:** +11 familias de controles (AC-7, SC-7, SC-5, SC-13, IA-5, AU-3, AU-4, AU-8, AU-12)
- **DISA STIG:** Preparación para V-215852 (Infrastructure ACL) en Sprint 3
- **Metadatos de Compliance**: Todas las verificaciones incluyen `cis_control`, `nist_controls`, `stig_id`

### 🎯 Rebalanceo de Planos de Seguridad

- **Control Plane:** 6% → 9% (+50% relativo) - Source routing, redirects, uRPF
- **Data Plane:** 4% → 6% (+50% relativo) - Protección anti-spoofing mejorada
- **Management Plane:** 88% → 85% - Mantiene cobertura fuerte con login hardening

### 🔧 Mejoras Técnicas

- **Verificaciones por Interfaz**: Patrón `InterfaceCheck` reutilizado para checks de ip_redirects y uRPF
- **Validación de Valores**: Patrón `ValueCheck` para umbrales numéricos (RSA ≥2048, logging ≥32KB)
- **Sin Código Python Nuevo**: Todas las verificaciones usan clases base existentes
- **Compatibilidad Total**: Cero cambios incompatibles, funciona con configs existentes

### 📚 Documentación Actualizada

- `SECURITY.md` - Política de seguridad completa con guías de rotación
- `.env.example` - Plantilla con ejemplos de CI/CD
- Metadatos CIS/NIST en todas las 60 verificaciones
- Preparación para CHECK_CATALOG.md (próximamente)

---

## ✨ Novedades en Versión 6.1 (2025-10-30)

### 🎨 Reportes HTML Modernizados

- **Tema Azul Profesional**: Nuevo diseño con gradiente azul (#1e3a8a → #3b82f6)
- **Indicadores con Iconos**: ✓ verde para aprobado, ⚠ amarillo para fallido (sin texto)
- **Secciones Colapsables**: Click en encabezados de categorías para expandir/colapsar
- **Botones de Filtrado**: Mostrar todos / Solo aprobados / Solo fallidos
- **Separadores Modernos**: Líneas sutiles con iconos, sin arte ASCII
- 27 templates personalizados actualizados con diseño consistente

### 📄 Generación de PDF Profesional

- **Reporte Completo para Clientes**: PDF de 130 páginas con portada, resumen ejecutivo y recomendaciones
- **Portada con Logo Centrado**: Branding del cliente y logo HVT6
- **Resumen Ejecutivo**: Calificación global (A-F), tabla de dispositivos, top 5 hallazgos críticos
- **Reportes Individuales**: 1-2 páginas por dispositivo con metadata y verificaciones fallidas
- **Recomendaciones Priorizadas**: Prioridad 1 (>75% afectados), Prioridad 2 (>50% afectados)
- **Apéndice de Metodología**: Sistema de puntuación y categorías de seguridad
- **Formato A4 Portrait**: Números de página y pie de página con cliente y fecha
- Uso: `python hvt6.py --customer "Cliente" --generate-pdf`
- Output: `results/Security_Audit_Cliente_YYYYMMDD.pdf`

### 📊 Exportación Excel con Tablas Dinámicas (NUEVO v6.5)

- **Reportes Multi-Hoja**: Archivo .xlsx con 3 hojas para análisis completo
  - **Hoja 1 - Summary**: Resumen ejecutivo con tabla de dispositivos y agregados por categoría
  - **Hoja 2 - Devices**: Detalles de cada dispositivo con metadata, puntuaciones y calificaciones
  - **Hoja 3 - Check Results**: Datos denormalizados listos para tablas dinámicas (pivot tables)
- **Formato Condicional Automático**: Celdas con colores según puntuación
  - Verde: ≥80% (alta conformidad)
  - Amarillo: 60-79% (conformidad media)
  - Rojo: <60% (baja conformidad)
- **Columnas Auto-ajustadas**: Anchos optimizados según contenido
- **Listo para Análisis**: La hoja "Check Results" permite crear tablas dinámicas en Excel para:
  - Análisis por categoría de seguridad
  - Comparación entre dispositivos
  - Identificación de verificaciones más falladas
  - Filtrado por plano de seguridad (Management/Control/Data)
- Uso: `python hvt6.py --customer "Cliente" --generate-excel`
- Output: `results/Security_Audit_Cliente_YYYYMMDD.xlsx`
- **Tamaño**: ~110KB para 17 dispositivos (864 filas de checks)
- **Compatible con**: Microsoft Excel 2010+, LibreOffice Calc, Google Sheets

**Ejemplo de Tabla Dinámica**:
```
1. Abrir archivo .xlsx generado
2. Seleccionar hoja "Check Results"
3. Insertar → Tabla Dinámica
4. Configurar:
   - Filas: Category
   - Valores: Promedio de Percentage
   - Filtro: Status = "FAIL"
```

### 🔧 Dependencias Nuevas

- **WeasyPrint v66.0+**: Conversión HTML a PDF de alta calidad
- **pypdf**: Manipulación y verificación de PDFs generados
- **openpyxl v3.1.2+**: Generación de archivos Excel con formato condicional (NUEVO v6.5)

---

## ✨ Novedades en Versión 6.0 (2025-10-29)

### Arquitectura Modular

- Refactorización completa de hvt5.py (1131 líneas) → hvt6.py (350 líneas) con paquete `hvt6/`
- Reducción del 69% en complejidad del código
- Separación de responsabilidades: core, checks, scoring, reporting

### Sistema de Archivos Separados

- **sh_ver.txt**: Extracción de versión y tipo de OS (IOS vs IOS-XE)
- **sh_inv.txt**: Información de hardware (modelo, serial)
- **sh_run.cfg**: Análisis de configuración de seguridad

### Detección Inteligente de IOS/IOS-XE

- Heurística basada en versión (v16+ = IOS-XE, v15- = IOS)
- Detección por arquitectura (X86_64_LINUX = IOS-XE)
- Manejo robusto de formatos de versión complejos (12.2(33)SXJ, 15.7(3)M8, etc.)

### Sistema de Advertencias de Versión

- Auditoría de **todos los dispositivos** independientemente de la versión
- Advertencias visuales para versiones antiguas:
  - IOS < 12.4(6)
  - IOS-XE < 16.6.4
- Banners amarillos e iconos ⚠️ en reportes
- Mensajes en español

### Configuración YAML

- Migración de test3.csv → checks.yaml (50+ verificaciones)
- hvt6_settings.yaml para configuración de aplicación
- Validación de esquema y detección de errores

---

## 📋 Requisitos e Instalación

### Requisitos del Sistema

- Python 3.8 o superior
- Sistema operativo: Linux, macOS, Windows (WSL recomendado)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-org/ios-xe_hardening.git
cd ios-xe_hardening

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Dependencias Principales

- **ciscoconfparse2**: Parser de configuraciones Cisco
- **jinja2**: Motor de templates para reportes HTML/PDF
- **weasyprint**: Conversión HTML a PDF de alta calidad (v66.0+)
- **pypdf**: Manipulación y verificación de PDFs
- **pandas**: Procesamiento de datos y exportación CSV
- **loguru**: Sistema de logging avanzado
- **ruamel.yaml**: Parser YAML con preservación de comentarios
- **tabulate**: Generación de tablas en formato texto

---

## 🔒 Configuración de Seguridad (IMPORTANTE)

### Configuración de Credenciales

**⚠️ CRÍTICO**: Desde la versión 6.2, HVT6 utiliza variables de entorno para credenciales en lugar de archivos YAML con contraseñas en texto plano.

#### Paso 1: Configurar el Archivo .env

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tus credenciales
nano .env  # o usar tu editor preferido
```

#### Paso 2: Configurar Credenciales

```bash
# .env - Configuración de credenciales
DEVICE_USERNAME=admin
DEVICE_PASSWORD=tu_contraseña_aquí
DEVICE_SECRET=tu_enable_secret_aquí
SNMP_COMMUNITY=tu_community_string

# Opcional: Nombre del cliente
CUSTOMER=nombre_del_cliente
```

#### Paso 3: Proteger el Archivo .env

```bash
# Permisos restrictivos (solo propietario puede leer/escribir)
chmod 600 .env

# Verificar que .env está en .gitignore (ya incluido)
cat .gitignore | grep .env
```

### Prioridad de Credenciales

HVT6 carga credenciales en el siguiente orden de prioridad:

1. **Variables de entorno (.env)** ← **RECOMENDADO**
2. **Archivos YAML (inventory/defaults.yaml)** ← **DEPRECADO** (será removido en v7.0)
3. **Prompt interactivo** ← Solo para uso manual

**Advertencia de Deprecación**: Si utilizas credenciales en archivos YAML, verás advertencias al iniciar. **Migra a .env lo antes posible**.

### Características de Seguridad

#### ✅ Buenas Prácticas Implementadas

- ✅ **Variables de entorno**: Credenciales fuera del control de versiones
- ✅ **.gitignore automático**: El archivo .env nunca se sube a Git
- ✅ **Soporte de lectura sola**: Las credenciales solo necesitan permisos de lectura en dispositivos
- ✅ **Validación con advertencias**: Alertas si faltan credenciales sin bloquear ejecución
- ✅ **Futura integración con Vault**: Arquitectura preparada para HashiCorp Vault (v7.0+)

#### 🔐 Comandos Ejecutados en Dispositivos

HVT6 utiliza el **módulo collector** para conectarse vía SSH y ejecutar **únicamente comandos de lectura**:

```cisco
show version          # Información de versión y OS
show inventory        # Información de hardware
show running-config   # Configuración actual (requiere privilegios)
```

**Nota de Seguridad**: Se requieren privilegios enable (`DEVICE_SECRET`) para ejecutar `show running-config` en la mayoría de los dispositivos Cisco.

#### ⚠️ Consideraciones de Seguridad

**IMPORTANTE: Contraseña Expuesta en Git**

Si previamente usaste HVT6 v6.0-6.1 con credenciales en `inventory/defaults.yaml`, **esas contraseñas están en el historial de Git**.

**Acciones Recomendadas**:

1. **Rotar contraseñas inmediatamente**: Cambiar las contraseñas expuestas en todos los dispositivos
2. **Revisar SECURITY.md**: Ver guía detallada de rotación de credenciales
3. **Limpiar historial de Git (opcional)**: Ver sección de limpieza en SECURITY.md

```bash
# Verificar si hay credenciales en historial
git log --all --full-history --source --pickaxe-all -S 'password'

# Para limpieza del historial (ver SECURITY.md para instrucciones completas)
# ADVERTENCIA: Requiere force-push y coordinación con el equipo
```

### Migración desde YAML (v6.0-6.1)

Si tienes credenciales en `inventory/defaults.yaml`:

```bash
# 1. Copiar credenciales actuales a .env
DEVICE_USERNAME=$(grep 'username:' inventory/defaults.yaml | awk '{print $2}')
DEVICE_PASSWORD=$(grep 'password:' inventory/defaults.yaml | awk '{print $2}')
echo "DEVICE_USERNAME=$DEVICE_USERNAME" >> .env
echo "DEVICE_PASSWORD=$DEVICE_PASSWORD" >> .env

# 2. Remover credenciales de YAML (mantener estructura)
# Editar inventory/defaults.yaml y comentar las líneas de credenciales

# 3. Probar carga desde .env
python collect.py --host nombre_dispositivo --verbose
```

### Variables de Entorno Avanzadas

#### Credenciales por Dispositivo (Próximamente v6.3+)

```bash
# Override para dispositivos específicos
DEVICE_ROUTER1_PASSWORD=contraseña_diferente
DEVICE_SWITCH1_USERNAME=usuario_readonly
```

#### Integración con HashiCorp Vault (Próximamente v7.0+)

```bash
# Configuración de Vault
VAULT_ADDR=https://vault.example.com:8200
VAULT_TOKEN=tu_token_vault
VAULT_NAMESPACE=hvt6
VAULT_SECRET_PATH=secret/data/network/devices
```

### Integración CI/CD

#### GitHub Actions

```yaml
# .github/workflows/audit.yml
env:
  DEVICE_USERNAME: ${{ secrets.DEVICE_USERNAME }}
  DEVICE_PASSWORD: ${{ secrets.DEVICE_PASSWORD }}
  DEVICE_SECRET: ${{ secrets.DEVICE_SECRET }}
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
variables:
  DEVICE_USERNAME: $DEVICE_USERNAME # Desde Settings > CI/CD > Variables
  DEVICE_PASSWORD: $DEVICE_PASSWORD
```

#### Docker

```bash
# Pasar como variables de entorno
docker run \
  -e DEVICE_USERNAME=admin \
  -e DEVICE_PASSWORD=pass \
  -e DEVICE_SECRET=secret \
  hvt6:latest
```

### Troubleshooting de Credenciales

#### Error: "Missing required credentials"

```bash
# Verificar que .env existe
ls -la .env

# Verificar contenido (sin mostrar valores)
cat .env | grep -E '^DEVICE_' | sed 's/=.*$/=***/'

# Verificar carga correcta
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Username:', os.getenv('DEVICE_USERNAME'))"
```

#### Advertencia: "Loading credentials from YAML (deprecated)"

**Solución**: Migrar a .env siguiendo la sección "Migración desde YAML" arriba.

#### Error: "Authentication failed"

```bash
# 1. Verificar credenciales manualmente
ssh $DEVICE_USERNAME@dispositivo

# 2. Verificar enable secret
# En el dispositivo: enable
# Debería aceptar DEVICE_SECRET

# 3. Revisar logs del collector
tail -f config_analyzer.log | grep -i auth
```

### Recursos Adicionales

- **Plantilla completa**: Ver `.env.example` para todas las opciones
- **Guía de seguridad**: Ver `SECURITY.md` para rotación de contraseñas
- **Arquitectura de credenciales**: Ver `CLAUDE.md` (sección Credential Management System)
- **Documentación del collector**: Ver `collector/README.md` (sección Credential Configuration)

---

## 📁 Archivos de Entrada

### Convención de Nombres

Para cada dispositivo, HVT6 requiere **3 archivos** en el directorio `repo/`:

```
{hostname}_sh_ver.txt    → Información de versión y sistema operativo
{hostname}_sh_inv.txt    → Inventario de hardware (modelo, serial)
{hostname}_sh_run.cfg    → Configuración en ejecución
```

### Ejemplo de Estructura

```
repo/
├── router1_sh_ver.txt
├── router1_sh_inv.txt
├── router1_sh_run.cfg
├── switch1_sh_ver.txt
├── switch1_sh_inv.txt
└── switch1_sh_run.cfg
```

### Recopilación de Archivos desde Dispositivos

```bash
# Conectarse al dispositivo
ssh admin@router1

# En el dispositivo Cisco
enable
terminal length 0

# Exportar archivos a flash
show version | redirect flash:sh_ver.txt
show inventory | redirect flash:sh_inv.txt
show running-config | redirect flash:sh_run.cfg

# Copiar a servidor TFTP/SCP
copy flash:sh_ver.txt tftp://192.168.1.100/router1_sh_ver.txt
copy flash:sh_inv.txt tftp://192.168.1.100/router1_sh_inv.txt
copy flash:sh_run.cfg tftp://192.168.1.100/router1_sh_run.cfg
```

### ¿Por Qué Archivos Separados?

| Beneficio        | Descripción                                              |
| ---------------- | -------------------------------------------------------- |
| **Velocidad**    | Extracción de versión sin parsear configuración completa |
| **Precisión**    | Detección de IOS/IOS-XE desde salida de `show version`   |
| **Claridad**     | Inventario separado de configuración                     |
| **Flexibilidad** | Actualizar config sin re-parsear versión                 |

---

## 🔧 Uso

### Comandos Básicos

```bash
# Ejecución estándar
python hvt6.py

# Especificar cliente
python hvt6.py --customer "Acme Corp"

# Modo verbose (debug)
python hvt6.py --verbose

# Directorios personalizados
python hvt6.py --repo-dir ./configs --output-dir ./output

# Solo formato HTML
python hvt6.py --format html

# Dry-run (parsear sin generar reportes)
python hvt6.py --dry-run
```

### Opciones de Línea de Comandos

```
--customer NAME      Nombre del cliente para reportes
--repo-dir DIR       Directorio de archivos de configuración (default: ./repo)
--output-dir DIR     Directorio de salida de reportes (default: ./reports)
--format FORMAT      Formato de reporte: html, csv, json, all (default: all)
--verbose, -v        Habilitar logging de debug
--dry-run            Parsear configuraciones sin generar reportes
--help               Mostrar ayuda
```

### Variables de Entorno

Crear archivo `.env` en el directorio raíz:

```bash
CUSTOMER=NombreCliente
```

---

## ⚙️ Archivos de Configuración

### checks.yaml

Define las **50+ verificaciones de seguridad** a ejecutar:

```yaml
checks:
  - check_id: ssh_003
    check_name: ip ssh version 2
    check_type: regex
    category: acceso
    security_plane: management
    max_score: 5
    regex_pattern: '^ip\s+ssh\s+version\s+2'
    negated: false
    description: Verifica que solo SSHv2 esté habilitado
    recommendation: Configurar 'ip ssh version 2'
    enabled: true
```

**Categorías disponibles:**

- `general`: Verificaciones de infraestructura base
- `operativa`: Configuraciones operacionales
- `control`: Plano de control
- `acceso`: Control de acceso y autenticación
- `monitoreo`: Logging, NTP, NetFlow

### hvt6_settings.yaml

Configuración de la aplicación:

```yaml
# Directorios
repo_dir: "./repo"
reports_dir: "./reports"
results_dir: "./results"

# Versiones Mínimas Recomendadas por Cisco
min_ios_version: "12.4.6" # IOS plano
min_ios_xe_version: "16.6.4" # IOS-XE

# Generación de Reportes
generate_html: true
generate_csv: true
generate_json: false

# Ponderación por Categoría
category_weights:
  general: 1.0
  operativa: 1.0
  control: 1.5 # Mayor peso para seguridad del plano de control
  acceso: 1.5 # Mayor peso para control de acceso
  monitoreo: 1.0
```

---

## 📊 Soporte de Versiones y Advertencias

### Versiones Soportadas

| Sistema Operativo | Línea Base | Detección                          |
| ----------------- | ---------- | ---------------------------------- |
| **IOS**           | 12.4(6)+   | Versión < 16                       |
| **IOS-XE**        | 16.6.4+    | Versión ≥ 16 o arquitectura X86_64 |

### Sistema de Detección de OS

HVT6 detecta automáticamente IOS vs IOS-XE usando:

1. **Cadena explícita**: `"Cisco IOS XE Software"` en show version
2. **Heurística de versión**: Versión mayor ≥ 16 → IOS-XE
3. **Arquitectura**: `X86_64_LINUX_IOSD` → IOS-XE

### Sistema de Advertencias

Los dispositivos con versiones antiguas son **auditados completamente** pero muestran advertencias prominentes:

**Indicadores Visuales:**

- 🟨 Banner amarillo en reportes individuales
- ⚠️ Icono en tabla de resumen y secciones de OS
- Tooltips con explicación detallada
- Mensajes en español en logs

**Ejemplo de Advertencia:**

```
⚠️ Advertencia de Versión
La versión 12.2(33)SXJ está por debajo de la línea base recomendada por
Cisco 12.4.6. Las verificaciones de seguridad pueden no ser totalmente
aplicables a esta versión.
```

### Ajustar Líneas Base

Editar `hvt6_settings.yaml`:

```yaml
# Más permisivo (aceptar versiones antiguas)
min_ios_version: '12.0.0'
min_ios_xe_version: '15.0.0'

# Más estricto (requerir versiones recientes)
min_ios_version: '12.4.25'
min_ios_xe_version: '17.3.1'

# Deshabilitar advertencias completamente
min_ios_version: '0.0.0'
min_ios_xe_version: '0.0.0'
```

---

## 🛡️ Verificaciones de Seguridad

HVT implementa **50+ verificaciones** basadas en las guías oficiales de Cisco, divididas en 3 planos de seguridad:

### Management Plane

El plano de gestión maneja el tráfico enviado al dispositivo Cisco IOS-XE e incluye aplicaciones y protocolos como SSH y SNMP.

#### Verificaciones Implementadas:

**Usuarios y Contraseñas:**

- ✓ `enable secret` preferido sobre `enable password`
- ✓ `service password-encryption` global
- ✓ Contraseñas type 9 (scrypt)
- ✓ Login Password Retry Lockout
- ✓ `no service password-recovery`

**Protocolos de Acceso:**

- ✓ Telnet deshabilitado (VTY transport input ssh)
- ✓ SSH versión 2 habilitado
- ✓ SSH protegido con ACLs (access-class)
- ✓ exec-timeout configurado en VTY
- ✓ SSH usando interfaz loopback
- ✓ HTTP/HTTPS deshabilitado
- ✓ FTP/TFTP deshabilitado

**SNMP:**

- ✓ Community strings configurados
- ✓ SNMPv2c mínimo
- ✓ SNMP protegido con ACLs
- ✓ SNMP trap host configurado
- ✓ SNMP trap source interface

**AAA (Authentication, Authorization, Accounting):**

- ✓ TACACS+ o RADIUS habilitado
- ✓ AAA new-model configurado
- ✓ Autenticación de login
- ✓ Autorización de exec
- ✓ Accounting de comandos

**Servicios:**

- ✓ `no service tcp-small-servers`
- ✓ `no service udp-small-servers`
- ✓ `no service finger`
- ✓ `no ip bootp server`
- ✓ `no ip domain-lookup` (opcional)
- ✓ `service tcp-keepalives-in`
- ✓ `service tcp-keepalives-out`

**Monitoreo:**

- ✓ NTP configurado
- ✓ NTP autenticado
- ✓ Syslog habilitado
- ✓ Syslog source interface
- ✓ Logging timestamps
- ✓ Login on-success log

**Banners:**

- ✓ Banner login configurado
- ✓ Banner exec configurado

**CDP/LLDP:**

- ✓ CDP deshabilitado globalmente (`no cdp run`)
- ✓ LLDP habilitado (opcional para gestión)

**Management Plane Protection:**

- ✓ Interfaz de gestión definida
- ✓ Management interface restringida

**VTY y Puertos AUX:**

- ✓ VTY 0-4 asegurado
- ✓ VTY 5-15 asegurado
- ✓ VTY 16-31 asegurado (si existe)
- ✓ AUX 0 deshabilitado (`transport none`)

### Control Plane

El plano de control procesa el tráfico crítico para mantener la funcionalidad de la infraestructura de red, incluyendo BGP, EIGRP, OSPF.

#### Verificaciones Implementadas:

**Control Plane Protection:**

- ✓ CoPP (Control Plane Policing) habilitado
- ✓ Control-plane host management-interface configurado

**Protecciones ICMP:**

- ✓ IP ICMP redirects deshabilitado
- ✓ ICMP unreachables deshabilitado

**Seguridad de Interfaces:**

- ✓ Proxy ARP deshabilitado
- ✓ Interfaces no utilizadas shutdown

**Enrutamiento:**

- ✓ Autenticación de protocolos de enrutamiento
- ✓ Passive interfaces configuradas

### Data Plane

El plano de datos reenvía datos a través del dispositivo de red. No incluye tráfico destinado al dispositivo local.

#### Verificaciones Implementadas:

**IP Options:**

- ✓ IP options deshabilitado
- ✓ IP source routing deshabilitado

**ICMP:**

- ✓ ICMP redirects deshabilitado en interfaces
- ✓ IP directed-broadcasts limitado
- ✓ ICMP packet filtering (permitir solo redes conocidas)

**Fragmentos IP:**

- ✓ ACL para fragmentos IP
- ✓ Verificación en interfaces críticas

**Protecciones Anti-Spoofing:**

- ✓ Unicast RPF habilitado
- ✓ IP Source Guard (en switches)
- ✓ Port Security (en switches)
- ✓ ACLs anti-spoofing

---

## 📈 Reportes y Salida

### Archivos Generados

```
reports/
├── {hostname}_YYYYMMDD.html    # Reportes individuales por dispositivo
└── ...

results/
├── hostnames.csv               # Tabla resumen con todos los dispositivos
└── hostnames.json              # (opcional) Resultados en JSON

index.html                      # Dashboard consolidado con estadísticas
config_analyzer.log             # Logs detallados de ejecución
```

### Dashboard Consolidado (index.html)

**Contenido:**

- Resumen general (dispositivos auditados, puntuación promedio)
- Mejor y peor dispositivo
- Resultados por categoría (barras de progreso)
- Tabla de dispositivos con puntuaciones
- Iconos ⚠️ para versiones antiguas

### Reportes Individuales

**Contenido:**

- Puntuación global de seguridad
- Información del dispositivo (tipo, modelo, OS, versión, serial)
- Banner de advertencia (si versión antigua)
- Resultados por categoría con detalles:
  - Estado de cada verificación (✓ ✗)
  - Evidencia encontrada
  - Recomendaciones de remediación

### CSV de Resultados

Formato de tabla para análisis:

```csv
Hostname,Device Type,Model,OS,Version,Total Score,Percentage,Passed,Total Checks
router1,router,ISR4331,IOS-XE,16.12.01,156/193,80.8%,38,49
switch1,switch,C9300-24P,IOS-XE,17.06.04,142/193,73.6%,35,49
```

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
ios-xe_hardening/
├── hvt6.py                     # Orquestador principal
├── hvt6/                       # Paquete modular
│   ├── core/
│   │   ├── config.py          # Carga de YAML (settings, checks)
│   │   ├── models.py          # Dataclasses (DeviceInfo, CheckResult, etc.)
│   │   ├── enums.py           # Enumeraciones (DeviceType, Category, etc.)
│   │   └── exceptions.py      # Jerarquía de excepciones personalizadas
│   ├── checks/
│   │   ├── base.py            # SecurityCheck ABC y implementaciones
│   │   └── registry.py        # CheckRegistry para gestión de checks
│   ├── scoring/
│   │   └── calculator.py      # ScoreCalculator y ScoreAggregator
│   └── reporting/
│       └── builder.py          # ReportBuilder para múltiples formatos
├── checks.yaml                 # Definiciones de 50+ verificaciones
├── hvt6_settings.yaml          # Configuración de aplicación
├── templates/                  # Plantillas Jinja2
│   ├── device_report.j2       # Reporte individual
│   ├── index.j2               # Dashboard consolidado
│   └── *.j2                   # Plantillas de checks específicos
├── repo/                       # Directorio de entrada (archivos de dispositivos)
├── reports/                    # Reportes HTML individuales (salida)
├── results/                    # CSV/JSON de resultados (salida)
└── config_analyzer.log         # Logs de ejecución
```

### Flujo de Datos

```
Archivos de entrada (repo/)
    ↓
discover_device_file_groups() → Agrupa por hostname
    ↓
parse_version_file() → Extrae OS, versión, modelo, serial
parse_inventory_file() → Extrae PID, serial (prioridad)
parse_config_file() → CiscoConfParse del running-config
    ↓
extract_device_info() → DeviceInfo consolidado
validate_version() → Advertencias si versión < baseline
    ↓
CheckRegistry.execute_all() → Ejecuta 50+ verificaciones
    ↓
ScoreCalculator → Calcula puntuaciones por categoría
    ↓
ReportBuilder → Genera reportes en múltiples formatos
    ↓
Salida (reports/, results/, index.html)
```

Para más detalles, ver: [docs/ARCHITECTURE.md](./HVT6_ARCHITECTURE.md)

---

## 🔄 Migración desde HVT5

Si estás usando hvt5.py (monolítico), consulta la guía de migración para actualizar a hvt6:

👉 [HVT6_MIGRATION_GUIDE.md](./HVT6_MIGRATION_GUIDE.md) _(próximamente)_

**Cambios principales:**

- test3.csv → checks.yaml
- Archivo único de config → 3 archivos separados (ver, inv, run)
- hvt5.py → hvt6.py + paquete hvt6/

**Compatibilidad hacia atrás:**

- hvt5.py sigue funcional (legacy)
- Ambas versiones pueden ejecutarse en paralelo durante la transición

---

## 🛠️ Solución de Problemas

### No se encontraron archivos de configuración

**Síntoma:**

```
WARNING | No device configuration files found
```

**Solución:**

```bash
# Verificar archivos en repo/
ls repo/*.cfg repo/*.txt

# Verificar naming convention
# Debe ser: {hostname}_sh_ver.txt, {hostname}_sh_inv.txt, {hostname}_sh_run.cfg
```

### Plantillas no encontradas

**Síntoma:**

```
WARNING | device_report.j2 not found, using fallback template
```

**Solución:**

```bash
# Verificar templates
ls templates/*.j2

# Debe existir:
# - templates/device_report.j2
# - templates/index.j2
# - templates/*.j2 (checks individuales)
```

### Error al parsear versión

**Síntoma:**

```
WARNING | Could not parse version: 12.4(24)T5 - ...
```

**Solución:**

- Verificar formato de sh_ver.txt
- hvt6 maneja: 12.2(33)SXJ, 15.7(3)M8, 17.06.04, etc.
- Si falla parsing, se permite procesamiento (no se bloquea)

### Dispositivo detectado con OS incorrecto

**Síntoma:**

- Dispositivo IOS-XE 16.5 detectado como "IOS 16.5"

**Solución:**

- Verificar sh_ver.txt contiene información de versión
- hvt6 usa heurística: v16+ = IOS-XE, v15- = IOS
- Verificar arquitectura X86_64_LINUX indica IOS-XE

### Logs detallados

```bash
# Ver logs completos
tail -f config_analyzer.log

# Filtrar errores
grep ERROR config_analyzer.log

# Filtrar advertencias
grep WARNING config_analyzer.log
```

---

## 📚 Referencias y Estándares

### Guías Oficiales de Cisco

1. **IOS-XE Hardening Guide:**
   https://sec.cloudapps.cisco.com/security/center/resources/IOS_XE_hardening

2. **IOS Security Configuration Guide:**
   https://www.cisco.com/c/en/us/support/docs/ip/access-lists/13608-21.html

3. **Management Plane Protection:**
   https://www.cisco.com/c/en/us/td/docs/ios/security/configuration/guide/sec_mgmt_plane_prot.html

4. **Cisco NX-OS Software Hardening Guide:**
   https://sec.cloudapps.cisco.com/security/center/resources/securing_nx_os

### Otros Recursos

5. **CISA Enhanced Visibility and Hardening Guidance:**
   https://www.cisa.gov/resources-tools/resources/enhanced-visibility-and-hardening-guidance-communications-infrastructure

6. **CIS Cisco IOS-XE STIG:**
   https://www.stigviewer.com/stig/cisco_ios_xe_router_ndm/2022-09-15/finding/V-215846

---

## 🤝 Contribuciones y Soporte

### Agregar Nueva Verificación

Método rápido (YAML):

```yaml
# En checks.yaml
- check_id: custom_001
  check_name: Mi Verificación
  check_type: regex
  category: operativa
  security_plane: management
  max_score: 5
  regex_pattern: '^mi\s+comando'
  description: Descripción de la verificación
  recommendation: Configurar 'mi comando'
  enabled: true
```

Método avanzado (Python):

```python
# En hvt6/checks/base.py o nuevo módulo
class CustomCheck(SecurityCheck):
    def execute(self, parsed_config: CiscoConfParse) -> CheckResult:
        # Tu lógica aquí
        pass

# Registrar en CheckRegistry
registry.register_check(CustomCheck(check_config))
```

### Documentación Adicional

- **Arquitectura completa:** [HVT6_ARCHITECTURE.md](./HVT6_ARCHITECTURE.md)
- **Guía rápida:** [HVT6_QUICKSTART.md](./HVT6_QUICKSTART.md)
- **Sistema de archivos:** [HVT6_FILE_HANDLING.md](./HVT6_FILE_HANDLING.md) _(próximamente)_
- **Sistema de advertencias:** [HVT6_VERSION_WARNINGS.md](./HVT6_VERSION_WARNINGS.md)
- **Guía del desarrollador:** [CLAUDE.md](./CLAUDE.md)

### Reportar Problemas

Para reportar bugs o solicitar funcionalidades, abrir un issue en el repositorio.

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos especificados en el archivo LICENSE.

---

## 🎯 Roadmap

### Próximas Funcionalidades

- [ ] Procesamiento paralelo de dispositivos (ThreadPoolExecutor)
- [ ] Soporte para plantillas de reportes personalizadas
- [ ] Integración con APIs de gestión (DNA Center, vManage)
- [ ] Exportación a formatos adicionales (PDF, Excel)
- [ ] Dashboard web interactivo
- [ ] Comparación histórica de auditorías
- [ ] Generación automática de scripts de remediación

---

**Hardening Verification Tool v6.0** | Desarrollado con ❤️ para seguridad de redes Cisco
