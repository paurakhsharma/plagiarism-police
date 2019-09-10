# plagiarism-police
Handy API to find similarity between two sentences.

Installation instructions


## Method 1 - local installation
1) Clone the repo and `cd` into the directory
2) create python virtual environment using `python -m venv ./venv`
3) `cd` into `server` directory
4) Install required dependency using `pip install -r requirements.txt`
5) Download model using `python -m spacy download en_core_web_sm`
4) Set enviromnent variable for ADMIN_PW `export ADMIN_PW='test_password'`
5) Run app using `python app.py` *Make sure your mongodb server is running*



## Method 2 - Docker method
1) From the root directory run `docker-composer build`
2) And then run `docker-composer up`


# voila 🚀
