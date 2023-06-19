# DSS Tool to calculated Environmental Flows and Water Quality Index

The tool calculates environmental flow using the class and the release data given as input by the user and also supports calculating the water quality index from a csv output of Qual2k model.

## Steps to run

```
pip install -r requirements.txt
streamlit run main.py
```

## For Environmental Flow Estimation

1. Add the "release_input.csv" file to the web app
2. Choose a preferred EMC
3. Click Submit

## For Qual2k

1. Add the "inputdata.csv" file in the first file uploader
2. Add the "temperature.csv" file in the second file uploader
