# Backend for project

## Local(!) deploying
0. Make sure that you have already installed:
```
python 3
pip
git
```
1. Clone the repository
```
git clone https://github.com/Biseliss/dpdapi.git && cd dpdapi
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Configure database connection:
   1. Set db credentials in file [configs/db.json.example](./configs/db.json.example)
   2. Rename the config file to `db.json`
4. Run code
```
uvicorn app.main:app --reload
```

## API documentation

You can use interactive documentation at http://localhost:8000/docs
