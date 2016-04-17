# South Africa's By-laws [![Build Status](https://travis-ci.org/longhotsummer/za-by-laws.svg)](http://travis-ci.org/longhotsummer/za-by-laws)

This is a collection of South Africa's by-laws, freely available, easy to read,
share and build upon. Visit [http://openbylaws.org.za](http://openbylaws.org.za) to view them online.

For each by-law, we have:

* PDF, ePUB, and standalone HTML versions of the by-law,
* the Akoma Ntoso XML for the by-law, and
* any attachments linked to the by-law (which are usually the original/source versions used to capture the by-law).

## How this repo works

Both this repo and openbylaws.org.za pull the bylaws and related content from
the Open By-laws Indigo server at [https://indigo.openbylaws.org.za](https://indigo.openbylaws.org.za).

When Travis CI builds this repo, it fetches updated content from Indigo and stores it in the repo. If the build
is of the master branch then Travis pushes the updated content back up to GitHub.

Travis CI builds must be started manually.

## Akoma Ntoso

The by-laws are stored primarily in [Akoma Ntoso](http://www.akomantoso.org/) 2.0 format.
Akoma Ntoso is an open XML format for amongst other things, legislative documents.
It allows us to capture the structure and some of the semantics of the documents.
