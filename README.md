#### Created by Ihor Prokopenko <i.prokopenko.dev@gmail.com>

## Project Description
This application serves as a comprehensive system for managing members, teams, and users. It offers a set of functionalities through various endpoints to facilitate the management of these entities.

## Getting Started

- Clone project with following command:
    - ```git clone https://github.com/Ihor-Prokopenko/teams-app.git```

- Create env file:
  - create new `.env` file in the root dir and fill it with `.env.example` content
  - or just rename `.env.example` to `.env`

    
- Make sure You have installed Docker and Docker Daemon is running:
    - ```docker ps``` - command to check


- Navigate to the root project dir (which contains docker-compose.yml) and use following commands to run application:
    - ```docker-compose build```
    - ```docker-compose up```


- The admin user will be created automatically with following creds:
    - ```admin@example.com``` - login
    - ```admin``` - password
    - try admin panel here http://127.0.0.1:8000/admin/
    - #### Remember that this is insecure and You must remove this option if You want use this application in real project

- Now you can check and try API endpoints at http://127.0.0.1:8000/swagger/

#### NOTE: To make Google OAUTH available, add your real google application creds to the next variables to .env:
    - GOOGLE_OAUTH2_CLIENT_ID=set_the_client_id
    - GOOGLE_OAUTH2_CLIENT_SECRET=set_the_client_secret
    - GOOGLE_OAUTH2_PROJECT_ID=set_the_project_id

#### NOTE2: Google OAUTH doesn't work with swagger documentation, to auth with google use url directly: http://127.0.0.1:8000/api/v1/users/oauth/google/redirect/ 




