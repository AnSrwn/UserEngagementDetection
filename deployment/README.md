# How to deploy to Plesk
The application is deployed to Plesk by only using docker containers. The database image can be pulled from a public repository, the custom frontend and backend images must be uploaded and loaded.   
Additionally nginx directives must be set.   
If you want to manage the database with a tool, Adminer can be installed.

## How to import a custom docker image into Plesk
1. Move the packed image (e.g. backend-fastpi-prod.tar.gz) to the server by using (S)FTP or SSH.
2. Unpack and load the image by using the following command:
    ```
    docker load -i backend-fastpi-prod.tar.gz
    ```
3. The image is now visible in Plesk on the Docker page.


## nginx Settings
1. Remove index files. Maybe you need to enter a space, so that it does not reset.  
    <img src="images/nginx-index-files.png" alt="Remove index files" width="600">   

2. Disable Apache Proxy   
    <img src="images/nginx-apache.png" alt="Disable Apache Proxy" width="400">   

3. Add additional reverse proxy directives   
    <img src="images/nginx-directives.png" alt="Additional nginx directives" width="400">   

    ```
    # Frontend Nuxt   
    location / {  
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $http_host;
    }

    # Adminer DB Managing   
    location /adminer {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $http_host;
    }

    # Backend FastApi   
    location ^~/api/v1/ {
        rewrite  ^/api/v1/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
    }
    ```


## Database
1. Search for "postgres" in the `Docker Image Catalog` in Plesk and download "postgres:15". Other versions should work as well, but 15 is tested.
2. Click `Run(local)`
3. Enable `Automatic start after system reboot`, disable `Automatic port mapping` and click OK.   
    <img src="images/frontend-run.png" alt="Run database docker image" width="600">    

4. Go to container settings.    
5. Add `Manual Mapping`. You cann use 5432 or any other free port.
6. Add the following environment variables:   
`POSTGRES_DB`: database name   
`POSTGRES_USER`: database user   
`POSTGRES_PASSWORD`: user password    
    <img src="images/database-container-settings.png" alt="Container Settings" width="600">     

7. Click OK to restart the container.    

## Adminer (Optional)
1. Search for "adminer" in the `Docker Image Catalog` in Plesk and download the "latest".
2. Click `Run(local)`
3. Enable `Automatic start after system reboot`, disable `Automatic port mapping` and click OK.
4. Go to container settings.
5. Add `Manual Mapping`. You cann use 8080 or any other free port.
6. Click OK to restart the container.

### How to use Adminer
1. Go to https://domain.com/adminer
2. Select PostgreSQL as database system, enter server (domain.com or domain.com:5432) and add database credentials.   

    <img src="images/adminer-login.png" alt="Adminer Login" width="400">


## Backend
1. Import the [backend-fastapi-prod](backend-fastapi-prod.tar.gz) image into Plesk.
2. Click `Run(local)`
3. Enable `Automatic start after system reboot`, disable `Automatic port mapping` and click OK.
4. Go to container settings.
5. Add `Manual Mapping`. You cann use 8000 or any other free port.
6. Update environment variable `DATABASE_URL` with your database data.
    ```
    postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_DB_HOST/$POSTGRES_DB
    ```
    to something like this:
    ```
    postgresql://db_user:db_password@domain.com:5432/db_1
    ```
7. Click OK to restart the container.

### Additional info to environment variables
`ROOT_PATH`: Prefix of the backend. When this variable is changed, the nginx config and `NUXT_PUBLIC_BASE_URL` in Frontend must be udpated. (Default value: /api/v1)   
`HOST`: Host IP (Default value: 0.0.0.0)   
`PORT`: Exposed Port of the docker container. (Default value: 8000)   
`DATABASE_URL`: Describes the connection to the database.   
`UVICORN_FORWARDED_ALLOW_IPS`: List of trusted IPs. As long the application is run behind a trusted proxy, all connections can be trusted. Otherwise this should be updated. (Default value: *)

## Frontend
1. Import the [frontend-nuxt-prod](frontend-nuxt-prod.tar.gz) image into Plesk.
2. Click `Run(local)`
3. Enable `Automatic start after system reboot`, disable `Automatic port mapping` and click OK.
4. Go to container settings.
5. Add `Manual Mapping`. You cann use 3000 or any other free port.
6. Change environment variable `NUXT_PUBLIC_BASE_URL` to your backend URL. Propably something like https://domain.com/api/v1.
7. Click OK to restart the container.

### Additional info to environment variables
`NUXT_PUBLIC_BASE_URL`: URL of the backend   
`NUXT_PUBLIC_STUN_SERVER_URL`: URL of the STUN Server. If another STUN Server should be used, this can be changed. The STUN Server is necessary for WebRTC and when frontend and backend are behind reverse proxies. (Default value: stun:stun.l.google.com:19302)    
`HOST`: Host IP (Default value: 0.0.0.0)    
`PORT`: Exposed Port of the docker container. (Default value: 3000)    
