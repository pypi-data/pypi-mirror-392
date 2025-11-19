# Models

This section describes the models used by `django-simple-dms`.

## Document

The `Document` model stores the document.




Tags
A Tag is a logical namespace for Documents.

A tag is defined in a hierarchical taxonomy. Each tag is identified by a unique slug prefixed by a dot-separated list of its ancestors tags and a dot. Example: alfa.beta.charlie where charlie is the tag and beta and alfa are its ancestors tags in ascending order.

A document can have 0..n tags. The first tag in the list identifies the document primary "nature" (ie the structural folder in a strictly hierarchical classification)
