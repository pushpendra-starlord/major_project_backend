# major_project_backend
This is a social network project who have all the features like instagram except ig tv


## Initial setup
git clone https://github.com/kushaldazzle/major_project_backend
pip install virtualenv <br />
virtualenv env <br />
.\env\Scripts\activate <br />
pip install -r requirements.txt<br />
python manage.py migrate


## Running project
.\env\Scripts\activate<br />
python manage.py runserver



## Final System relaod
```
sudo systemctl daemon-reload
sudo systemctl restart redis-server
sudo systemctl restart daphne
sudo systemctl restart nginx
```