# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker Compose PHP development environment that provides a complete LEMP stack with multiple PHP versions support. The project includes Nginx, MariaDB, MailHog, Adminer, and various PHP versions from 5.6 to 8.4.

## Common Commands

### Docker Management
- `make up` - Start all containers (`docker compose up -d`)
- `make upb` - Start containers with rebuild (`docker compose up -d --build`)
- `make stop` - Stop all containers
- `make ps` - Show container status
- `make logs name=<container>` - View logs for specific container (e.g., `make logs name=php-84`)

### Development Commands
- `make php` - Access PHP shell (auto-detects active PHP container)
- `make exec name=<container>` - Execute shell in specific container
- `make mycli` - Access MySQL CLI client
- `make mysqltuner mem=<MB>` - Run MySQL tuner with memory specification
- `make node` - Access Node.js shell
- `make ssl d="<domains>"` - Generate SSL certificates with acme.sh

### Service Shortcuts
- `make nlogs` - View Nginx logs
- `make dblogs` - View database logs
- `make nrs` - Restart Nginx
- `make rs name=<container>` - Restart specific container

## Architecture

### PHP Version Support
The project supports multiple PHP versions through separate containers:
- **PHP-FPM versions**: 8.4, 8.3, 8.2, 8.1, 8.0, 7.4
- **Apache mod_php versions**: 8.1, 7.4, 5.6

Each PHP version has its own directory structure:
- `docker/php-<version>/` - PHP-FPM containers
- `docker/apache-php-<version>/` - Apache mod_php containers
- `templates/docker-compose-php-<version>.yml` - Docker compose templates

### Directory Structure
- `docker/` - Container configurations and Dockerfiles
- `templates/` - Docker compose templates for different PHP versions
- `projects/` - Web project files (mounted to containers)
- `db/data/` - MariaDB data persistence
- `docker/nginx/config/` - Nginx virtual host configurations
- `docker/nginx/config/templates/` - Nginx config templates for different PHP versions

### Key Services
- **nginx**: Reverse proxy with basic auth (super:demo)
- **db**: MariaDB database
- **mailhog**: Email testing interface (port 8025)
- **adminer**: Database management interface (port 8080)
- **php-<version>**: PHP-FPM containers
- **apache-php-<version>**: Apache with mod_php

## Configuration

### Environment Setup
1. Copy `mysql.env.example` to `mysql.env` and configure database settings
2. Copy appropriate Nginx config template for your PHP version
3. Add domains to `/etc/hosts` (e.g., `127.0.0.1 site.test`)

### PHP Version Switching
1. Copy the appropriate template from `templates/` to `docker-compose.yml`
2. Copy corresponding Nginx config template
3. For Apache: update Apache virtual host config
4. Run `make upb` to rebuild and start

### Customization
- PHP settings: `docker/php-<version>/config/php.ini`
- PHP-FPM settings: `docker/php-<version>/config/www.conf`
- Nginx virtual hosts: `docker/nginx/config/`
- Basic auth: `docker/nginx/.htpasswd`
- User/group mapping: Uncomment and modify ID in Dockerfile

## Network Ports
- **80**: HTTP (Nginx)
- **443**: HTTPS (disabled by default)
- **8025**: MailHog interface
- **8080**: Adminer database interface