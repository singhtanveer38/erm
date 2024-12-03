# erm

An analytics dashboard for educational institutions to get insights of student's marks in various exams.

The marksheet of the whole class should have the columns `roll no`, `name`, followed by subject columns in which marks are stored for each subject. THe filename follows a specific rule like `class_10_section_examname_totalmarks.csv`. Here is the sample for the file [class\_10\_A\_pt1\_40_.csv](class_10_A_pt1_40_.csv).

Create a python virtual environment and activate it

```bash
python3 -m venv venv
./venv/bin/activate
```
Install all the dependencies by running:
```bash
pip3 install -r requirements.txt
```

Create a folder and drop all the csv's to be processed. In `config.yaml`, update `data_dir` with this folder's location. In `processed_dir`, give a location where the processed data will be stored. After setting up the config file, run:

```python
python3 setup.py
```
This will setup the database. Then execute:
```python
python3 load.py
```
This will extract the data from the `data_dir`, transform it and load it into the database. Also, the transformed data will be stored in `processed_dir`. Now, execute: 

```python
waitress-serve --host 0.0.0.0 app:server
```
which will serve the dashboard at [http://127.0.0.1:8080/](http://127.0.0.1:8080/). To add new data to dashboard, copy files into `data_dir` and execute `load.py` file.
