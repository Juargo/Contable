# Makefile para facilitar operaciones comunes con Docker

.PHONY: up down build logs ps restart shell-backend shell-frontend mysql-cli clean help

# Variables
DOCKER_COMPOSE = docker-compose -f docker/docker-compose.yml

# Comandos principales
up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

build:
	$(DOCKER_COMPOSE) build

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

restart:
	$(DOCKER_COMPOSE) restart

# Acceso a contenedores
shell-backend:
	$(DOCKER_COMPOSE) exec backend bash

shell-frontend:
	$(DOCKER_COMPOSE) exec frontend sh

mysql-cli:
	$(DOCKER_COMPOSE) exec mysql mysql -u contable_user -pcontable_password contable_db

# Limpieza
clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	
# Ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make up            # Inicia todos los contenedores"
	@echo "  make down          # Detiene todos los contenedores"
	@echo "  make build         # Construye todos los contenedores"
	@echo "  make logs          # Muestra los logs de todos los contenedores"
	@echo "  make ps            # Lista todos los contenedores"
	@echo "  make restart       # Reinicia todos los contenedores"
	@echo "  make shell-backend # Accede a una shell en el contenedor del backend"
	@echo "  make shell-frontend # Accede a una shell en el contenedor del frontend"
	@echo "  make mysql-cli     # Accede al cliente MySQL"
	@echo "  make clean         # Elimina contenedores, redes y volúmenes"

# Por defecto
default: help
