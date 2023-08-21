# Flask JQuery application project

## Instructions
1. Enable port 80 and 443 in ufw or your installed firewall.
2. Install and run certbot `sudo certbot certonly -d your_domain -n --standalone --agree-tos --email your_email`  with your domain.
3. Change "your_domain" inside the /app/start_app.sh script
4. Create the virtual environment by doing `python3 -m venv venv` within the "app" folder
5. Inside the app folder, run `source venv/bin/activate` and `pip install -r requirements.txt`
6. Go back to root project folder and run `docker-compose build && docker-compose up -d`
7. crontab -e `43 6 * * * certbot renew`

## Information

Master branch is supposed to have a domain registered since its using port 443 and certbot.
For local development or using port 80, use dev branch.