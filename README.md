The whole product consists of 2 applications: frontend and backend parts

Backend part is written with the help of Flask framework.

It has three main functions: home(), get_data() and visualize().
Each of them is used to display a separate webpage within the application.

It also uses three function that are used inside the main functions.
These are:
    1. get_repo_events() - get all the events from the given repo
    2. count_average_period_pull_r() - counts differences between pull requests and calculates the mean value of them
    3. count_different_events() - count different events from the given repo

More detailed description of functions is in main.py script.

----------

Frontend part is written in pure HTML with the help of py-script API.

There are three web-pages on the frontend side:
    1. index.html - main page that contains for for owner name, repo name and timeframe to get events. It also redirects the user to the page with the data
    2. data.html - page that dispays the data and redirects the user to the page with the visualization
    3. visualization.html - page that displays the visualization of the differences between pull requests and average of these differences.
    It also uses a py-script API to display a python code on the webpage. There is an import of the API in the 'head' section. Then it uses 'py-script' tag to display the code.

More detailed description of the code is in .html files.

