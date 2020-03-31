# CoronaVirus
This project contains a Jupyter notebook that creates some charts about the COVID19 spread in Italy.

The results are in this directory:
  - [images](./images)

## Project status
```diff
! Doing
```
## Notebooks

- [CoronaVirus](notebook/CoronaVirus.ipynb): produces the model chart and various other charts about the Italian and Lombardy COVID-19 virus spread;
- [CoronaVirus-SecondaryCharts](notebook/CoronaVirus-SecondaryCharts.ipynb): comparative charts on various datasets;
- [DataDownloader](notebook/DataDownloader.ipynb): get the data for the Italian provices from GitHum and other sources. No charts since now;  

## Disclaimer
I do know very well Pandas, Matplotlib and I had a fairly good education in statistics but, as all the programmers, I do bugs.
So beware, I have checked the results as carefully as I can but nevertheless do not take for granted my result, check by yourself my 
code and decide if it it is correct or not.

## COVID-19 spread charts
Chart with a predictive model (a logistic function) fitted for the Italian data set:
![Italy chart with comparative logistic model](./images/covid19_IT_with_logistic_model_chart.png?)

Daily total figures about infected, recovered and deads:
![Italy chart](./images/covid19_daily_infected_chart.png?)

Chart with the virus spread in Italy as whole and the Lombardy region:
![Italy and Lombardy composite chart](./images/covid19_composed_chart.png?)

Virus spread in Italy:
![Italy chart](./images/covid19_chart.png?)

