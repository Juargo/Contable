# Migración de npm a pnpm en MoneyDairy

Este documento detalla los pasos para migrar el proyecto de npm a pnpm.

## ¿Por qué pnpm?

- **Eficiencia en almacenamiento**: pnpm utiliza un almacén único para todos los módulos, ahorrando espacio en disco.
- **Instalación más rápida**: gracias al linking en lugar de copiar archivos, las instalaciones son más rápidas.
- **Gestión de dependencias estricta**: previene dependencias fantasma, haciendo que el proyecto sea más predecible.
- **Soporte para monorepos**: gestión integrada de workspaces sin herramientas adicionales.

## Pasos para migrar un proyecto existente

### 1. Instalar pnpm globalmente

```bash
npm install -g pnpm
```

### 2. Eliminar node_modules y lock files

Desde la carpeta raíz del proyecto:

```bash
# Eliminar node_modules
rm -rf node_modules
rm -rf frontend/node_modules

# Eliminar archivos de lock de npm o yarn
rm package-lock.json
rm yarn.lock
rm frontend/package-lock.json
rm frontend/yarn.lock
```

### 3. Instalar dependencias con pnpm

```bash
# En la carpeta raíz
pnpm install

# En la carpeta frontend
cd frontend
pnpm install
```

### 4. Actualizar scripts

Los scripts en package.json han sido actualizados para usar pnpm en lugar de npm.

### 5. Workspace Configuration

Se ha añadido un archivo `pnpm-workspace.yaml` en la raíz del proyecto para configurar el workspace de pnpm.

## Solución de problemas comunes

### Incompatibilidades de peerDependencies

pnpm es más estricto con las peerDependencies. Si encuentras errores, intenta:

```bash
pnpm install --shamefully-hoist
```

Esto simula el comportamiento de npm, pero se recomienda resolver adecuadamente las dependencias en su lugar.

### Dependencias que faltan en package.json

Si algunos paquetes funcionaban antes pero ahora fallan, es posible que estuvieras usando "dependencias fantasma". Agrégalas explícitamente:

```bash
pnpm add <nombre-paquete>
```

## Comandos útiles de pnpm

- `pnpm add <package>`: Agregar una dependencia
- `pnpm add -D <package>`: Agregar una dependencia de desarrollo
- `pnpm update`: Actualizar dependencias
- `pnpm prune`: Eliminar dependencias innecesarias
- `pnpm why <package>`: Ver por qué un paquete está instalado
- `pnpm exec <command>`: Ejecutar un comando en el contexto de pnpm
