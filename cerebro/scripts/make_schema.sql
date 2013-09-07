CREATE EXTENSION IF NOT EXISTS plv8;

CREATE TYPE doc_rev AS (doc_id integer, doc_rev integer);
CREATE OR REPLACE FUNCTION all_docs_and_revs_for_tree (j json)
    RETURNS SETOF document_revision
    LANGUAGE plv8
    IMMUTABLE
AS
$$
    var q = [j];
    var acc = [];

    while (q.length > 0) {
        v = q.pop();
        acc.push({
            doc_id: v.d,
            doc_rev: v.r
        });
        v.c.forEach(function (k) {
            q.push(k)
        });
    }

    return acc;
$$;

CREATE TABLE users (
    id serial PRIMARY KEY,
    email varchar,
    pwhash varchar
);

CREATE UNIQUE INDEX users_email ON users (lower(email));

CREATE TABLE projects (
    id serial PRIMARY KEY,
    name varchar
);

CREATE TABLE project_acl (
    project_id integer REFERENCES projects (id) ON DELETE CASCADE ON UPDATE CASCADE,
    user_id integer REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    level integer NOT NULL,

    PRIMARY KEY (project_id, user_id)
);

CREATE TABLE tree_revisions (
    project_id integer REFERENCES projects (id) ON DELETE CASCADE ON UPDATE CASCADE,
    tree_rev integer NOT NULL,
    ts timestamp NOT NULL,
    tree json NOT NULL,

    PRIMARY KEY (project_id, tree_rev)
);

CREATE TABLE doc_revisions (
    project_id integer REFERENCES projects (id) ON DELETE CASCADE ON UPDATE CASCADE,
    doc_id integer NOT NULL,
    doc_rev integer NOT NULL,
    content text NOT NULL,

    PRIMARY KEY (project_id, doc_id, doc_rev)
);

/*
CREATE VIEW project_docs (
    project_id,
    tree_rev,
    doc_id,
    doc_rev
) AS
SELECT (q).project_id AS project_id,
       (q).tree_rev AS tree_rev,
       ((q).r).doc_id AS doc_id,
       ((q).r).doc_rev AS doc_rev
FROM (
    SELECT project_id,
           tree_rev,
           all_docs_and_revs_for_tree(tree) AS r
    FROM tree_revisions) AS q;
*/
