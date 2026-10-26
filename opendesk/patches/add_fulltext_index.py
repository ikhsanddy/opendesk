from opendesk.setup.install import add_fts_index


def execute():
    print("Adding FULLTEXT Index")
    add_fts_index()
