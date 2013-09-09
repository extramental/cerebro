import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.config import Configurator

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    config = Configurator(settings)
    config.scan("cerebro.models")
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    conn = engine.connect()
    conn.execute("""
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
""")
    conn.execute("""
CREATE EXTENSION IF NOT EXISTS plv8;

CREATE TYPE doc_rev AS (doc_id integer, doc_rev integer);
CREATE FUNCTION all_docs_and_revs_for_tree (j json, path varchar)
    RETURNS SETOF doc_rev
    LANGUAGE plv8
    IMMUTABLE
AS
$$
    path = path.length == 0 ? [] : path.split("/");

    while (path.length > 0) {
        j = j.c[path.shift()];
    }

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
""")
    Base.metadata.create_all(engine)
    with transaction.manager:
        pass
