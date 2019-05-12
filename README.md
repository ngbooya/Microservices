
# Blog Microservices

> Four microservices, hosted as four separate applications. Use of a reverse proxy and load balancer, running multiple load-balanced instances of each microservice, and implementing the Backend for Frontend pattern to generate RSS feeds for a blog platform.

---

***THIS IS THE LOAD BALANCER IN ACTION:***

<img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/737555/load-balancer.png?raw=true" width="850">



---


## Installation

- `pip3 install foreman`

- `pip3 install tavern`

- `sudo apt install python-pytest`

- `sudo apt install ruby-foreman`

- `sudo apt install --yes nginx-extras`

- `sudo pip3 install Flask-BasicAuth`

- `sudo pip3 install httpcache`


---

##First Actions
- Create a cache folder "cache" at this location: /etc/nginx/cache/
- Go to the directory /etc/nginx/ and then use this command: mkdir cache
- You may need to run the commands as sudo.
- Also change out the default nginx configuration in sites-enabled to the included one.
- Install scylla DB and start it as in the project documents.
- Run this command: docker exec -it scylla cqlsh
- Run this cqlsh command: CREATE KEYSPACE blog WITH replication = {'class':'SimpleStrategy', 'replication_factor':'3'};



## Setup

- To run the formation:


### Step 1

- Open a terminal and change directory to the location of all the files.

### Step 2

- Run the following command:

```shell
$ foreman start --formation Articles-Test=3,Comments-Test=3,Tags-Test=3,Users-Test=3,Syndication-Test=3
```


- Note: Make sure the supplied default Nginx configuration file called ‘default’ is in the default Nginx location (on the test system this is: /etc/nginx/sites-enabled/default)


---


### Before you can add an article, comment or tag, you must create a user and log in.



### To create a user:

- Send a POST response to /users/create with JSON in this format:

```javascript
{
    “id”: id,
    “email”: “email”,
    “password”: “password”
}
```



### To add an article:

- Send a POST response to localhost/articles/post with JSON in the following format:

```javascript
{

    “title”: “title”,
    “body”: “body”,
    “author”: “author”
}
```



### To create a comment:

- Send a POST response to localhost/comments/article/post/<int:article_number> with json in the following format:

```javascript
{
    "comment_id": number,
    “comment_text”: “comment”
}
```




### To create a tag:

- Send a POST response to localhost/tags/add/article/<article_number> with json in the following format:

```javascript
{
    "tag_id":number,
    “tag”: “tag”
}
```



---

## Team

| William Dalessi | Hector Bernal | Kevin Nguyen |
| :---: |:---:| :---:|
| Ops  | Dev 1| Dev 2|

---


## Resources


Foreman

    http://blog.daviddollar.org/2011/05/06/introducing-foreman.html

Nginx

    https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-subrequest-authentication/




---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
