import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckan.lib.activity_streams import \
    activity_stream_string_functions as activity_streams

import urllib2
import json
import datetime, dateutil.parser
import pytz


def most_recent_datasets(num=5):
    """Return a list of recent datasets."""

    # the current_package_list_with_resources action returns private resources
    # which need to be filtered

    datasets = []
    i = 0
    while len(datasets) < num:
        datasets += filter(lambda ds: not ds['private'],
                           tk.get_action('current_package_list_with_resources')({},
                                         {'limit': num, 'offset': i * num}))
        i += 1

    return datasets[:num]


def showcases(num=24):
    """Return a list of showcases."""

    showcases = []

    showcases = tk.get_action('ckanext_showcase_list')({},{})

    sorted_showcases = sorted(showcases, key=lambda k: k['metadata_modified'], reverse=True)  

    return sorted_showcases[:num]


def groups(num=14):
    """Return a list of groups"""

    groups = tk.get_action('group_list')({}, {'all_fields': True, 'sort': 'packages'})

    return groups[:num]


def latest_topic_list(num=5):
    """Return a list of talk topics"""

    local_tz = pytz.timezone('US/Eastern')

    response = urllib2.urlopen("https://talk.beta.nyc/latest.json")
    data = json.load(response)
    topics = data['topic_list']['topics']

    """Convert to datetime"""
    for topic in topics:
        dt = dateutil.parser.parse(topic['last_posted_at'])
        local_dt = dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        topic['last_posted_at'] = local_dt.strftime('%B %d, %Y %I:%M%p')

    """Get topics that are not pinned"""
    topics[:] = [x for x in topics if x.get('pinned') == False]

    return topics[:num]


class Datacity_ThemePlugin(plugins.SingletonPlugin):
    """DataCity theme plugin."""

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        tk.add_template_directory(config_, 'templates')
        tk.add_public_directory(config_, 'public')
        tk.add_resource('fanstatic', 'datacity_theme')

    def get_helpers(self):
        """Register datacity_theme_* helper functions"""

        return {'datacity_theme_most_recent_datasets': most_recent_datasets,
                'datacity_theme_showcases': showcases,
                'datacity_theme_groups': groups,
                'datacity_theme_latest_topic_list': latest_topic_list,}
