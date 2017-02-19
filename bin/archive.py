#!/usr/bin/env python

# Script that downloads and archives documents from an
# Indigo (https://github.com/Code4SA/indigo) server.

import os
import requests
import subprocess
import errno
import json
import fnmatch
import codecs
import urlparse


API_ENDPOINT = os.environ.get('INDIGO_API_URL', "http://indigo.openbylaws.org.za/api")
BASE_DIR = os.getcwd()
TARGET_DIR = os.path.join(BASE_DIR, 'by-laws')

session = requests.Session()


def make_path(uri, doc):
    return os.path.join(TARGET_DIR, uri[1:])


def delete(uri, doc):
    print "Deleting: %s" % uri
    path = make_path(uri, doc)
    git_rm(path, True)


def git_rm(fname, recursive=False):
    args = '-f'
    if recursive:
        args += 'r'
    subprocess.call(['git', 'rm', args, fname])


def git_add(fname):
    subprocess.check_call(['git', 'add', fname])


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        pass


def archive(uri, doc):
    """ Archive this document.

    metadata.json
    main.xml
    attachments/foo
    """
    path = make_path(uri, doc)
    print "Archiving: %s -> %s" % (uri, path)
    mkdir_p(path)

    resp = session.get(doc['content_url'] + '.json')
    resp.raise_for_status()
    fname = os.path.join(path, 'main.xml')
    with codecs.open(fname, 'w', 'utf-8') as f:
        f.write(resp.json()['content'])
    git_add(fname)

    # add alternate forms
    if doc['links']:
        for title in ['Standalone HTML', 'ePUB', 'PDF']:
            link = [link for link in doc['links'] if link['title'] == title]
            if link:
                link = link[0]

                resp = session.get(link['href'])
                resp.raise_for_status()

                fname = urlparse.urlsplit(link['href']).path
                _, ext = os.path.splitext(fname)

                fname = os.path.join(path, 'main' + ext)
                with open(fname, 'wb') as f:
                    f.write(resp.content)
                git_add(fname)

    archive_attachments(uri, doc)

    fname = os.path.join(path, 'metadata.json')
    with codecs.open(fname, 'w', 'utf-8') as f:
        json.dump(doc, f)
    git_add(fname)


def archive_attachments(uri, doc):
    path = os.path.join(make_path(uri, doc), 'attachments')
    mkdir_p(path)
    manifest = os.path.join(path, 'attachments.json')

    if os.path.isfile(manifest):
        with open(manifest, 'r') as f:
            local = json.load(f)
    else:
        local = []
    local = {a['filename']: a for a in local}

    resp = session.get(doc['attachments_url'] + '.json')
    resp.raise_for_status()
    remote = resp.json()['results']
    remote = {a['filename']: a for a in remote}

    for fname, att in remote.iteritems():
        loc = local.get(fname)
        if not loc or loc['updated_at'] < att['updated_at']:
            # update it
            print "Archiving attachment: %s" % fname
            resp = session.get(att['download_url'])
            resp.raise_for_status()

            fname = os.path.join(path, fname)
            with open(fname, 'wb') as f:
                f.write(resp.content)
            git_add(fname)

        else:
            print "Same attachment: %s" % fname

    deleted = list(set(local.keys()) - set(remote.keys()))
    for fname in deleted:
        print "Deleting attachment: %s" % fname
        git_rm(os.path.join(path, fname))

    with codecs.open(manifest, 'w') as f:
        json.dump(remote.values(), f)
    git_add(manifest)


def reconcile(local, remote):
    for uri, doc in remote.iteritems():
        loc_doc = local.get(uri)

        if not loc_doc or loc_doc['updated_at'] < doc['updated_at']:
            # changed or new
            archive(uri, doc)
        else:
            print "Same: %s" % uri

    deleted = list(set(local.keys()) - set(remote.keys()))
    for uri in deleted:
        delete(uri, local[uri])


def get_local_documents():
    docs = []
    paths = []
    for root, dirnames, filenames in os.walk(TARGET_DIR):
        for filename in fnmatch.filter(filenames, 'metadata.json'):
            paths.append(os.path.join(root, filename))

    for p in paths:
        with open(p, 'r') as f:
            docs.append(json.load(f))

    return docs


def get_remote_documents():
    resp = session.get(API_ENDPOINT + '/documents.json')
    resp.raise_for_status()
    docs = resp.json()['results']
    # only published docs
    return [d for d in docs if not d['draft']]


def expression_uri(doc):
    return '/'.join([doc['frbr_uri'], doc['language'], doc['expression_date'] or doc['publication_date']])


def archive_tree():
    print "Archiving documents from %s to %s" % (API_ENDPOINT, BASE_DIR)
    local = get_local_documents()
    local = {expression_uri(d): d for d in local}
    print "Local: %d" % len(local)

    remote = get_remote_documents()
    remote = {expression_uri(d): d for d in remote}
    print "Remote: %d" % len(remote)

    reconcile(local, remote)


if __name__ == '__main__':
    archive_tree()
