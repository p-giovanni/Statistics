# CoronaVirus
This project contains some Jupyter notebooks that create some charts about the COVID19 spread in Italy.

The data sets are downloaded, as pdf file, from this site [www.salute.gov.it](http://www.salute.gov.it/portale/news/p3_2.html), transformed to a pandas dataframe and written in a csv file (see [csv data files](./data)).

The results are in this directory:
  - [images](./images)

A second data source, from [**Istat**](https://www.istat.it/) is the number of daily deaths registered in a set of Italian cities in the years:

- 2020
- 2019
- 2018
- ...

This new data source allows the comparison of deaths, in the same period but in different years.

See this chart: [weekly mortality rate](./images/MortalityRate-DailyDeaths.png).

## Project status
```diff
! Doing
```
## Notebooks

- [CoronaVirus](notebook/CoronaVirus.ipynb): produces the model chart and various other charts about the Italian and Lombardy COVID-19 virus spread;
- [CoronaVirus-SecondaryCharts](notebook/CoronaVirus-SecondaryCharts.ipynb): comparative charts on various datasets;
- [DataDownloader](notebook/DataDownloader.ipynb): download the datasets from [www.salute.gov.it](http://www.salute.gov.it/portale/news/p3_2_Mobile.html);  
- [MortalitaGiornaliera](notebook/MortalitaGiornaliera.ipynb): comparative charts on the [Istat](https://www.istat.it/) daily deaths rate;

## Disclaimer
I do know very well Pandas, Matplotlib and I had a fairly good education in statistics but, as all the programmers, I do bugs.
So beware, I have checked the results as carefully as I can but nevertheless do not take for granted my result, check by yourself my 
code and decide if it it is correct or not.

## COVID-19 spread charts
The charts that follow are about the increased deaths due to the covid-19 spread. 
The most interesting one is, in my opinion, the chart that compares the total deaths in Italy in the years 2018,2019 and 2020. In this it is clear the disaster and the tragedy that my country is living in these months.
![Hospitalized](./images/MortalityRate-DeathsByAgeClass.png?)



### Virus spread charts examples
Lombardy virus spread chart:
![Virus spread](./images/RegionWeekly-TotalInfected-Lombardia.png?)
Lombardy intensive care chart:
![Virus spread](./images/RegionWeekly-IntensiveCare-Lombardia.png?)

