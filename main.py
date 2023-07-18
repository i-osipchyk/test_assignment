from flask import Flask, jsonify, render_template, redirect, request, url_for
import requests
from datetime import datetime, timedelta
import numpy as np
import os

# date format to count tim edifference
date_format = "%Y-%m-%dT%H:%M:%SZ"

# username and repo name that were used for testing
# username = "josephmisiti"
# repo = "awesome-machine-learning"

# github repositories url
base_url = "https://api.github.com/repos"

# events that are tracked
events_list = ["WatchEvent", "PullRequestEvent", "IssuesEvent"]

# events per page
per_page = 100

# exporting API TOKEN
API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
headers = {
    "Authorization": "token " + API_TOKEN,
    "accept": "application/vnd.github+json"
}


# function to get all events from the repo
def get_repo_events(url):

    all_events = []
    i = 1

    while True:
        params = {
            "per_page": per_page,
            "page": i
        }

        response = requests.get(url, headers=headers, params=params)
        curr_page_events = response.json()

        # if the page contains events it has list type. otherwise it has a dict type.
        # the results of the current page are added to the results of all previous pages.
        # when there are no more events, the loop breaks
        if isinstance(curr_page_events, list):
            all_events = all_events + curr_page_events
            i+=1
        else:
            break

    # return all the events from the query
    return all_events


# function to count average period between pull requests
def count_average_period_pull_r(events):

    pull_req_time = []

    # add creation time of all pull request events to the list
    for event in events:
        if event['type'] == events_list[1]:
            pull_req_time.append(datetime.strptime(event['created_at'], date_format))

    # new list with time differences
    differences = [(pull_req_time[i]-pull_req_time[i+1]).total_seconds() for i in range(len(pull_req_time)-1)]
    
    # counts the average value of the differences
    average_period = np.mean(differences)

    # additionally returns differences for data visualization
    return average_period, differences


# function to count needed events in the list of all events
def count_different_events(events, offset_minutes):

    # dict to couunt events
    events_dict = {
        "WatchEvent": 0,
        "PullRequestEvent": 0, 
        "IssuesEvent": 0
    }

    # offset in minutes
    offset_seconds = int(offset_minutes) * 60

    # define the threshhold time
    current_time = datetime.utcnow()
    threshold_time = current_time - timedelta(seconds=offset_seconds)

    for event in events:
        if event['type'] in events_list:
            events_dict[event['type']] += 1
        # break if the time threshold is reached
        if datetime.strptime(event['created_at'], date_format) < threshold_time:
            break

    # returns the dictionary where key is the name of the event and value is the number of those events
    return events_dict


# initialize Flask application
app = Flask(__name__)


# homepage with form for repo owner and repo name
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        owner = request.form.get('owner')
        repo = request.form.get('repo')
        offset = request.form.get('offset')
        # if submit is clicked redirects to the page with data 
        return redirect(url_for('get_data', owner=owner, repo=repo, offset=offset))
    
    # returns homepage with form 
    return render_template('index.html')

# page with the data
@app.route('/data/<owner>/<repo>/<offset>', methods=['GET', 'POST'])
def get_data(owner, repo, offset):

    # create a query url and get the events
    url = f"{base_url}/{owner}/{repo}/events"
    events = get_repo_events(url)

    # count average, differences and number of events
    avg, diff = count_average_period_pull_r(events)
    events_dict = count_different_events(events, offset)

    # cast differences to string in order to use in the url
    differences = ','.join(str(x) for x in diff)

    # if 'Visualize' is clicked redirects to the page with visualization
    if request.method == 'POST':
        return redirect(url_for('visualize', differences=differences))
    
    # dictionary with the average in different units 
    data = {
        "Average in seconds": "{:.0f}".format(avg),
        "Average in minutes": "{:.0f}".format(avg/60),
        "Average in hours": "{:.2f}".format(avg/3600),
        "Average in days": "{:.2f}".format(avg/(3600*24)),
    }

    # returns page with data
    return render_template('data.html', data=data, counts=events_dict, differences=differences)


# page with the visualization
@app.route('/visualization', methods=['GET', 'POST'])
def visualize():
    # retrieve differences from the url
    diff_str = request.args.get('differences')

    # cast back to list
    diff_list = [float(item) for item in diff_str.split(',')]

    # return visualization page with differences
    return render_template('visualization.html', differences=diff_list)


# run the app
if __name__ == '__main__':
    app.run(port=5000)