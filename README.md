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
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">

  <h3 align="center">Balancing Capital Bikeshare Deployment</h3>

  <p align="center">
    Modeling the flow of Capital Bikeshare rides across ANC locations.
    <br />
    <a href="https://github.com/jmillerbrooks/capital_bikeshare"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/jmillerbrooks/capital_bikeshare">View Demo</a>
    ·
    <a href="https://github.com/jmillerbrooks/capital_bikeshare/issues">Report Bug</a>
    ·
    <a href="https://github.com/jmillerbrooks/capital_bikeshare/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [The Business Problem](#business-problem)
  * [Approach](#approach)
* [Data Science Process](#data-science-process)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



<!-- THE BUSINESS PROBLEM -->
## The Business Problem

![Empty Bike Dock][empty-dock]
<sub>Image retrieved from https://www.popville.com/2014/09/problems-with-capital-bikeshare-for-commuting/ </sub>


There are common patterns of commuter behavior with users of the Capital Bikeshare system. This results in uneven patterns of supply and demand for both bikes (as in the above image), and parking space (wherever all those folks went!). We develop recommendations for planning and fleet rebalancing using a number of different time series techniques on trip data obtained from CaBi's <a href="https://s3.amazonaws.com/capitalbikeshare-data/index.html"> historical ride sets.</a>

There has been a fair amount of work done (INSERT LINKS) modeling various aspect of stations within the CaBi system, as well as other docked bikeshare systems worldwide. However, the recent <a href="https://dcist.com/story/20/07/07/capital-bikeshare-electric-bikes-return-lyft/"> introduction of ebikes</a> in July represents the early stages of a slightly more nuanced modeling problem. The main difference between the new ebikes, and the traditional docked bikes (other than the pedal assist), is that the ebikes do not need to be parked in a dock at the end of a ride. Though around 75% of ebike rides followed traditional docking behavior in the first month of operation, the "dockless" trend grew from just a few rides initially to greater numbers toward the end of the month.

In light of this development, it seems the future modeling problem may well be centered more around modeling more abstract geographic locations than individual stations. We attempt a first approach at a geographically centered solution, by prototyping on the existing Advisory Neighborhood Commission boundaries, which divide the District of Columbia into 40 unique geographies. Within each ANC we then attempt to answer the following three items described below.

**INSERT ANC MAP**


### Approach

Within each ANC we seek to answer:

1. How many times will bikes need to be rebalanced throughout the day, and can we consistently anticipate short term local spikes in either bike build up, or bike depletion?
2. How well can we forecast rebalancing demand for the next 2 week period, in order to better manage employee scheduling?
* What ANCs have the largest and most consistent rebalancing needs over time (i.e. where net gain/loss in a 1 hr period is usually substantially larger than other areas)? 



<!-- DATA SCIENCE PROCESS -->
## Data Science Process

To get a local copy up and running follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
```sh
npm install npm@latest -g
```

### Installation

1. Clone the repo
```sh
git clone https://github.com/jmillerbrooks/capital_bikeshare.git
```
2. Install NPM packages
```sh
npm install
```



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/jmillerbrooks/capital_bikeshare/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Jake Miller Brooks - [![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/jake-miller-brooks-a37a64106/)

Project Link: [https://github.com/jmillerbrooks/capital_bikeshare](https://github.com/jmillerbrooks/capital_bikeshare)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* []()
* []()
* []()





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