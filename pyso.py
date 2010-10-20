#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
pyso.py - Python Stack Overflow library, aka a love letter to @frankythebadcop.
"""
import gzip
import itertools
import math
import time
try:
    import json
except ImportError:
    import simplejson as json
import urllib
import urllib2

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__version__ = "0.1"
__author__ = "Jonathon Watney <jonathonwatney@gmail.com>"
#__all__ = ("APIError")

__base_url = "http://api.stackoverflow.com"
__api_version = "1.0"
__default_page_size = 100
__default_page = 1
__question_orders = ("activity", "views", "creation", "votes")
__answer_orders = ("activity", "views", "creation", "votes")
__comment_orders = ("creation", "votes")
__user_orders = ("reputation", "creation", "name")

http_proxy = None # Not yet.
api_key = "" # Set this here or before calling any of the functions.


class APIError(Exception):
    """Raised when an error occurs."""
    def __init__(self, url, code, message):
        self.url = url
        self.code = code
        self.message = message


# Miscellaneous and utility site functions.
def get_sites():
    """Returns a list of all the sites in the Stack Exchange Network."""
    return __fetch("sites", "api_sites")

def get_stats():
    """Gets various system statistics."""
    return next(__fetch("stats", "statistics"))

def get_errors(id):
    """Simulates an error given its code."""
    return __fetch("errors/%s" % id, None)

def get_all_badges():
    """Gets all badges, in alphabetical order."""
    return __fetch("badges", "badges")

def get_all_standard_badges():
    """Gets all standard, non-tag-based badges in alphabetical order."""
    return __fetch("badges/name", "badges")

def get_all_tag_based_badges():
    """Gets all tag-based badges in alphabetical order."""
    return __fetch("badges/tags", "badges")

def get_badges(ids, start_date=None, end_date=None):
    """Gets the users that have been awarded the badges identified in 'id'."""
    path = "badges/%s" % __join(ids)
    params = __translate(locals().copy(), ("popular", "activity", "name"))

    return __fetch(path, "badges", **params)

def get_tags(name_contains=None, start_date=None, end_date=None):
    """Gets the tags on all questions, along with their usage counts."""
    params = __translate(locals().copy(), ("popular", "activity", "name"))

    return __fetch("tags", "tags", **params)

# Question, answer and post functions.
def get_comments(ids, order_by=None, start_date=None, end_date=None):
    """Gets comments by ids."""
    path = "comments/%s" % __join(ids)
    params = __translate(locals().copy(), __comment_orders)

    return __fetch(path, "comments", **params)

def get_posts_comments(ids, order_by=None, start_date=None, end_date=None):
    """Gets the comments associated with a set of posts (questions/answers)."""
    path = "posts/%s/comments" % __join(ids)
    params = __translate(locals().copy(), __comment_orders)

    return __fetch(path, "comments", **params)

def get_posts_revisions(ids, start_date=None, end_date=None):
    """Gets the post history revisions for a set of posts."""
    path = "revisions/%s" % __join(ids)
    params = __translate(locals().copy())

    return __fetch(path, "revisions", **params)

def get_posts_revision(ids, revision_id, start_date=None, end_date=None):
    """Get a specific post revision."""
    path = "revisions/%s/%s" % (__join(ids), revision_id)
    params = __translate(locals().copy())

    return __fetch(path, "revisions", **params)

def get_all_questions(order_by=None, tags=None, body=False, comments=False, start_date=None, end_date=None):
    """
    Gets all questions ordered by activity. Other valid sort orders are
    "featured", "hot", "week", "month", "votes". Provide a list of tags to get
    questions with only those tags. order_by is ignored if tags is not None.
    """
    path = "questions"
    params = __translate(locals().copy(), ("activity", "votes", "creation", "featured", "hot", "week", "month"))

    return __fetch(path, "questions", **params)

def get_all_unanswered_questions(order_by=None, tags=None, body=False, comments=False, start_date=None, end_date=None):
    """
    Gets all questions ordered by activity. Other valid sort orders are
    "featured", "hot", "week", "month", "votes". Provide a list of tags to get
    questions with only those tags. order_by is ignored if tags is not None.
    """
    path = "questions"
    params = __translate(locals().copy(), ("votes", "creation"))

    return __fetch(path, "questions", **params)

def get_question(question_id, body=False, comments=False, start_date=None, end_date=None):
    """Get the question with the given question_id."""
    return next(get_questions([question_id], body, comments, start_date, end_date))

def get_questions(ids, order_by=None, body=False, comments=False, start_date=None, end_date=None):
    """
    Gets the set of questions given by question_ids. Valid sort orders
    are "activity", "views", "creation", or "votes".
    """
    path = "questions/%s" % __join(ids)
    params = __translate(locals().copy(), __question_orders)

    return __fetch(path, "questions", **params)

def get_questions_answers(ids, order_by=None, body=False, comments=False, start_date=None, end_date=None):
    """
    Gets any comments to the questions given by question_ids. Valid sort orders
    are "activity", "views", "creation", or "votes".
    """
    path = "questions/%s/answers" % __join(ids)
    params = __translate(locals().copy(), __question_orders)

    return __fetch(path, "comments", **params)

def get_questions_comments(ids, order_by=None, start_date=None, end_date=None):
    """
    Gets any answers to the questions given by question_ids. Valid sort orders
    are "creation", or "votes".
    """
    path = "questions/%s/comments" % __join(ids)
    params = __translate(locals().copy(), __comment_orders)

    return __fetch(path, "comments", **params)

def get_questions_timeline(ids, start_date=None, end_date=None):
    """Get the timelines for the given question_ids."""
    path = "questions/%s/timeline" % __join(ids)
    params = __translate(locals().copy())

    return __fetch(path, "post_timelines", **params)

def get_answers(ids, order_by=None, body=False, start_date=None, end_date=None):
    """
    Get all answers with the given answer_ids ordered by most activity. Other
    valid orders are "activity", "views", "creation" and "votes".
    """
    path = "answers/%s" % __join(ids)
    params = __translate(locals().copy(), __answer_orders)

    return __fetch(path, "answers", **params)

def get_answers_comments(ids, order_by=None, start_date=None, end_date=None):
    """
    Get all answers with the given answer_ids ordered by most activity. Other
    valid orders are "activity", "views", "creation" and "votes".
    """
    path = "answers/%s" % __join(ids)
    params = __translate(locals().copy(), __comment_orders)

    return __fetch(path, "comments", **params)

# User based fucntions.
def get_all_users(name_contains=None, order_by=None, start_date=None, end_date=None):
    """Gets user summary information."""
    path = "users"
    params = __translate(locals().copy(), __user_orders)

    if name_contains:
        params["filter"] = name_contains

    return __fetch(path, "users", **params)

def get_user(user_id):
    """Gets a user by user_id."""
    return next(get_users([user_id]))

def get_users(ids, order_by=None):
    """Gets summary information for a set of users."""
    print locals().copy()

    path = "users/%s" % __join(ids)
    params = __translate(locals().copy(), __user_orders)

    return __fetch(path, "users", **params)

def get_users_questions(ids, order_by=None, body=False, comments=False, start_date=None, end_date=None):
    """
    Get all the questions asked by a user with the given user_id ordered by
    recent "activity". Other valid sort orders are "views", "newest" and "votes".
    """
    path = "users/%s/questions" % __join(ids)
    params = __translate(locals().copy(), __question_orders)

    return __fetch(path, "questions", **params)

def get_users_answers(ids, order_by=None, body=False, comments=False):
    """
    Get all answers for the given user_id ordered by most activity. Other
    valid orders are "activity", "views", "creation" and "votes".
    """
    path = "users/%s/answers" % __join(ids)
    params = __translate(locals().copy(), __answer_orders)

    return __fetch(path, "answers", **params)

def get_users_comments(ids, mentioned_user_id=None, order_by=None, start_date=None, end_date=None):
    """
    Get all comments for the given user_id ordered by most recent. Other valid
    orders are "score".
    """
    path = "users/%s/comments" % __join(ids)
    params = __translate(locals().copy(), __comment_orders)

    if mentioned_user_id:
        path += "/%s" % mentioned_user_id

    return __fetch(path, "comments", **params)

def get_users_timelines(ids, start_date=None, end_date=None):
    """Gets users' timelines by user_ids."""
    path = "users/%s/timeline" % __join(ids)
    params = __translate(locals().copy())

    return __fetch(path, "user_timelines", **params)

def get_user_reputation_changes(ids, start_date=None, end_date=None):
    """Gets a users' reputations by user_ids."""
    path = "users/%s/reputation" % __join(ids)
    params = __translate(locals().copy())

    return __fetch(path, "rep_changes", **params)

def get_users_mentions(ids, order_by=None, start_date=None, end_date=None):
    """Gets user mentions by user_ids."""
    path = "users/%s/mentioned" % __join(ids)
    params = __translate(locals().copy(), ("creation", "name"))

    return __fetch(path, "comments", **params)

def get_users_badges(ids):
    """Gets the badges that have been awarded to a set of users."""
    path = "users/%s/badges" % __join(ids)

    return __fetch(path, "badges")

def get_users_tags(ids, order_by=None):
    """ 
    Gets the tags that a set of users has participated in. Valid orders are
    "asc" and "desc".
    """
    path = "users/%s/tags" % __join(ids)
    params = __translate(locals().copy(), ("popular", "activity", "name"))

    return __fetch(path, "tags", **params)

def get_users_favorites(ids, order_by=None, body=False, comments=False, start_date=None, end_date=None):
    """Gets summary information for the questions that have been favorited by a set of users."""
    path = "users/%s/favorites" % __join(ids)
    params = __translate(locals().copy(), __question_orders)

    return __fetch(path, "questions", **params)

def get_all_moderators(name_contains=None, start_date=None, end_date=None):
    """Gets all the moderators on this site."""
    path = "users/moderators"
    params = __translate(locals().copy(), __user_orders)

    return __fetch(path, "users", **params)

def __fetch(path, results_key, **url_params):
    """
    Fetches all the results for a given path where path is the API URL path.
    results_key is the key of the results list. If url_params is given it's
    key/value pairs are used to as part of the API query string.
    """
    base_url = "%s/%s/%s" % (__base_url, __api_version, path)
    params = {
        "key": api_key,
        "pagesize": __default_page_size,
        "page": __default_page
        }

    params.update(url_params)

    while True:
        query = urllib.urlencode(params)
        url = "%s?%s" % (base_url, query)#; print url
        data = __get_response_data(url)
        response = json.loads(data)
        count = 0

        if "error" in response:
            error = response["error"]
            code = error["Code"]
            message = error["Message"]

            raise APIError(url, code, message)

        if results_key:
            results = response[results_key]
        else:
            results = response

        if len(results) < 1:
            break

        for result in results:
            yield result

        if len(results) < params["pagesize"]:
            break

        params["page"] += 1

def __get_response_data(url):
    """Gets the response encoded as a string."""
    request = urllib2.Request(url)

    request.add_header("Accept-Encoding", "gzip")

    response = None

    try:
        response = urllib2.urlopen(request)
        data = response.read()

        if response.headers.get("content-encoding") == "gzip":
            data = gzip.GzipFile(fileobj=StringIO(data)).read()
    finally:
        if response:
            response.close()
    
    return data

def __join(ids):
    """Joins a sequence of ids into a semicolon delimited string."""
    return ";".join((str(id) for id in ids))

def __translate(kwargs, orders=[]):
    """Translates function kwargs into URL params."""
    params = dict()

    for key, value in kwargs.items():
        if key == "order_by" and value in orders:
            params["sort"] = value
        elif key == "start_date" and value:
            params["fromdate"] = int(time.mktime(value.timetuple()))
        elif key == "end_date" and value:
            params["todate"] = int(time.mktime(value.timetuple()))
        elif key == "body" and value:
            params["body"] = "true"
        elif key == "answers" and value:
            params["answers"] = "true"
        elif key == "comments" and value:
            params["comments"] = "true"
        elif key == "tags" and value:
            params["tagged"] = ";".join(value)
        elif key == "name_contains" and value:
            params["filter"] = value
        elif key == "title_contains" and value:
            params["filter"] = value

    return params
