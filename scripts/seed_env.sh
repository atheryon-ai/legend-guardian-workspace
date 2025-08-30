
#!/bin/bash

if [ -f .env ]; then
    echo ".env file already exists."
else
    cp deploy/local/.env.example .env
    echo ".env file created."
fi
