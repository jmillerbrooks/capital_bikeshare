<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** jmillerbrooks, capital_bikeshare, twitter_handle, email
-->





<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
-->





## Repository Navigation

[Notebooks][notebooks]

[Package Files][cabi]

[Figures][figures]

[Slide Deck][presentation-folder]


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [The Business Problem](#business-problem)
  * [Approach](#approach)
* [Data Science Process](#data-science-process)
* [Model Evaluation](#evaluation)
* [Results and Business Recommendations](#results)
* [Future Improvement](#future-improvement)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



<!-- THE BUSINESS PROBLEM -->
## The Business Problem

![Empty Bike Dock][empty-dock]
<sub>Image retrieved from https://www.popville.com/2014/09/problems-with-capital-bikeshare-for-commuting/ </sub>


There are common patterns of commuter behavior with users of the Capital Bikeshare system. This results in uneven patterns of supply and demand for both bikes (as in the above image), and parking space (wherever all those folks went!). We develop recommendations for planning and fleet rebalancing using a number of different time series techniques on trip data obtained from CaBi's <a href="https://s3.amazonaws.com/capitalbikeshare-data/index.html"> historical ride sets.</a>

There has been a fair amount of work done modeling various aspect of stations within the CaBi system, as well as other docked bikeshare systems worldwide. However, the recent <a href="https://dcist.com/story/20/07/07/capital-bikeshare-electric-bikes-return-lyft/"> introduction of ebikes</a> in July represents the early stages of a slightly more nuanced modeling problem. The main difference between the new ebikes, and the traditional docked bikes (other than the pedal assist), is that the ebikes do not need to be parked in a dock at the end of a ride. Though around 75% of ebike rides followed traditional docking behavior in the first month of operation, the "dockless" trend grew from just a few rides initially to greater numbers toward the end of the month.

In light of this development, it seems the future modeling problem may well be centered more around modeling more abstract geographic locations than individual stations. We attempt a first approach at a geographically centered solution, by prototyping on the existing Advisory Neighborhood Commission boundaries, which divide the District of Columbia into 40 unique geographies. Within each ANC we then attempt to answer the following three items described below.

![Stations by ANC][stations-by-anc]
<sub>Capital Bikeshare Station Locations displayed over map of DC Advisory Neighborhood Commissions </sub>


### Approach

Within each ANC we seek to answer:

1. How many times will bikes need to be rebalanced throughout the day, and can we consistently anticipate short term local spikes in either bike build up, or bike depletion?
2. How well can we forecast rebalancing demand for the next 2 week period, in order to better manage employee scheduling?
* What ANCs have the largest and most consistent rebalancing needs over time (i.e. where net gain/loss in a 1 hr period is usually substantially larger than other areas)? 



<!-- DATA SCIENCE PROCESS -->
## Data Science Process and Setup

The data were obtained from CaBi's <a href="https://s3.amazonaws.com/capitalbikeshare-data/index.html"> historical ride sets.</a> The steps to import clean and transform them can be found in the notebooks "Setup" and "ETL", as well as in the cabi package script: cleaning, and the submodule "etl". The setup portion of the analysis can be reproduced readily with the following steps.

1. Initiate a PostgreSQL database. If you do not have PostgreSQL, it can be installed via homebrew on mac or from https://www.postgresql.org/download/
2. Clone this repository
3. Create a file called "config.py" in the cabi/etl directory with the following items filled in according to your postgres instance:
    def connection_params():
        return """postgresql://\<username>:\<password>@\<address>:\<port>/\<database>"""

4. Navigate to the home folder of the repository directory from your command line.
5. Run "python3 setup.py install" -- This will install the project 'cabi' as a package so that you can use all functions accross all notebooks  
6. Run the cells in "Setup.ipynb" -- This will pull the raw csvs from source (warning, this is a large amount of data), you could also only pull the last few months instead without sacrificing results, as we have not yet modeled on the data prior to that.
7. Run the cells in ETL. This will reshape the data and load into postgres.
8. Modeling and Analysis of models can be found in "Modeling" and "Scratch" notebooks.
    
Our modeling approach is described in the Modeling and Scratch files. We attempted to fit Holt-Winters and SARIMA models for each ANC, initially selecting parameters based off of AIC score, and then best models based on RMSE. Our baseline model for comparison was a persistence model based off of a lag of six hours, since we attempted to predict spikes in bike over or undersupply over six hour periods. The seasonal component to each model was set at the frequency equivalent to a one day period for each set, as there is a pronounced seasonal daily component in each ANC. Our cross validation procedure was aided by pmdarima's SlidingWindowForecast.

<!-- evaluation -->
## Model Evaluation

Our error metrics yielded RMSE for most of the larger "hotspot" ANCs of around 5-8 for a 24 hour prediction period of six hour change in bikes (i.e. +/- 5-8 bikes change over six hours incorrectly for each six hour window in the day). Our additional criteria of SMAPE paints a less forgiving picture as it indicated we were typically off by between 30-50% with widely varying estimates. This makes the model less useful from a practical perspective, although we argue that it is typically either randomly wrong by a little bit in either direction, or consistently underpredicting at predictable intervals (weekends) where the direction of prediction (gain/loss in bikes) is generally correct. This was due to the inability to account accurately for a varying but pronounced weekly seasonality concurrently with the more regular daily pattern. This does however leave the door open for decent use case. Since the errors are usually not large, or large but predictable.



<!-- Results -->
## Results and Business Recommendations

We recommend implementing a test case of our model, where the weekend peak/troughs are manually adjusted by the average factor of prediction error to actual value of the last four 1 week periods in a roughly three hour window around the extrema. Recommended use case is to preemptively redistribute bikes from areas of predicted build up (oversupply) to areas of predicted drain (high demand), approximately 3 hours before 6 hour gain/loss peaks/troughs. The weekend periods during the ongoing COVID period represent an especially good time to test the approach of manually supplementing the model by an error factor as discussed above, due to the increased variability resulting in consistently uneven distributions of bicycle supply.
    
![Example Model Results][example-model-results]
<sub>Example Model Forecast </sub>



<!-- Future Improvement -->
## Future Improvement

Next Steps

A major limitation of the modeling approach we implemented was that it was tied to an implicit variable (space) which was semi-arbitrarily selected. This is worse than being a completely arbitrary political unit, because Advisory Neighborhood Commissions vary widely in density, and thus some spatial patterns may be influencing the units we modeled without being fully accounted for as this is not a holistic system. We therefore recommend first and foremost either a density based clustering of spatial areas as model units, or a hierarchical aggregation of results as a HiTS (Hierarchical Time Series) approach.

The Markov method is also a strong next step as soon as out of sample predictions are supported.







<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Jake Miller Brooks - [![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/jake-miller-brooks-a37a64106/)

Project Link: [https://github.com/jmillerbrooks/capital_bikeshare](https://github.com/jmillerbrooks/capital_bikeshare)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Please find sources in the slide deck in the [Presentations Folder][presentation-folder] and additional sources in the Technical notebook in notebooks.





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/jmillerbrooks/repo.svg?style=flat-square
[contributors-url]: https://github.com/jmillerbrooks/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/jmillerbrooks/repo.svg?style=flat-square
[forks-url]: https://github.com/jmillerbrooks/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/jmillerbrooks/repo.svg?style=flat-square
[stars-url]: https://github.com/jmillerbrooks/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/jmillerbrooks/repo.svg?style=flat-square
[issues-url]: https://github.com/jmillerbrooks/repo/issues
[license-shield]: https://img.shields.io/github/license/jmillerbrooks/repo.svg?style=flat-square
[license-url]: https://github.com/jmillerbrooks/repo/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/jmillerbrooks
[empty-dock]: figures/capital_bikeshare_shortage.jpeg
[stations-by-anc]: figures/stationsByANC.png
[example-model-results]: figures/sample_prediction1A.png
[presentation-folder]: /presentation
[notebooks]: /notebooks
[cabi]: /cabi
[figures]: /figures
