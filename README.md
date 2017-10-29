# bitbucket-knowledge-insight
Code project insight using bitbucket API


The tool is built using Bitbucket rest api, allows:
1. See a person code contribution to the company.
2. View colleague's contribution in term of code contribution and pull request approved by him. and the measure of that person responsiveness to approving pull request.
3. Search by area to find the people who are familiar with that area.
4. See rank of the people in the company in term of pull request opened on him/here, and code contribution done by him/here.


To view the information you first need to collect it:
go to connection_info.py file and add user name/password path to your bitbucket
Then simply run:
```python
python refresher_impl.py
```
And wait for it to finish.

After letting the tool to collect the information you can view the result in the website
```python
python bitbucket_knowledge_insight.py
```

The page available are:

Top Contributors page
---------------------

![Top Contributors page](https://raw.githubusercontent.com/ohade/bitbucket-knowledge-insight/master/doc/topContributors.png)


Top pull requesters page
------------------------

![Top pull requesters page](https://raw.githubusercontent.com/ohade/bitbucket-knowledge-insight/master/doc/pullRequesters.png)


Search by area page
-------------------

![Search by area page](https://raw.githubusercontent.com/ohade/bitbucket-knowledge-insight/master/doc/searchByArea.png)


Contributor page
----------------

![Contributor page](https://raw.githubusercontent.com/ohade/bitbucket-knowledge-insight/master/doc/contributor.png)


Contribution view in contributor page
-------------------------------------

![Contribution page](https://raw.githubusercontent.com/ohade/bitbucket-knowledge-insight/master/doc/contribution.png)
