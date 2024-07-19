# 📕 Sdamgia bot
`RU` locale only

![GitHub License](https://img.shields.io/github/license/Tapeline/Sdamgiabot)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Tapeline/Sdamgiabot/deploy.yml)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/Tapeline/Sdamgiabot)

Bot for exercising GIA (EGE) exams

<!-- TOC -->
* [📕 Sdamgia bot](#-sdamgia-bot)
  * [Starting](#starting)
    * [Deploying remotely](#deploying-remotely)
    * [Running locally](#running-locally)
  * [Usage](#usage)
  * [Tech stack](#tech-stack)
  * [Developer](#developer)
  * [License](#license)
<!-- TOC -->

## Starting
### Deploying remotely
Bot uses Docker+Docker Compose for deployment.
```shell
git clone https://github.com/Tapeline/Sdamgiabot.git
cd Sdamgiabot
docker compose up -d
```
Provide `BOT_TOKEN` environment variable when starting Compose.

### Running locally
For running locally bot requires `wkhtmltopdf` installed. More info
about this requirement at [imgkit page](https://pypi.org/project/imgkit/)
and [wkhtmltopdf page](https://wkhtmltopdf.org/). 
> **Attention!**
> 
> On Windows you must explicitly pass the path to `wkhtmltoimage.exe`
> through env `WKHTMLTOIMAGE_BIN`

All pip requirements are listed in `requirements.txt`.

## Usage
Bot supports several commands (no buttons, because I'm too lazy)

All info about them is listed in `/help`

## Tech stack
![Aiogram 3](https://img.shields.io/badge/aiogram%203-blue?style=for-the-badge)
![Peewee ORM](https://img.shields.io/badge/peewee%20orm-3333FF?style=for-the-badge)
![Postgres](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![APScheduler](https://img.shields.io/badge/APScheduler-FF3366?style=for-the-badge)
![BS4](https://shields.io/badge/BeautifulSoup-4-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/Tech-Docker-informational?style=for-the-badge&logo=docker&color=2496ED)

## Developer
Project is being developed by [@Tapeline](https://www.github.com/Tapeline)

## License
This work is licensed under GNU General Public License v3.0
