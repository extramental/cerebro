from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.sql.expression import *
from sqlalchemy.orm import *

from pyramid.security import Allow, Everyone

from . import *

DocRev = PGCompositeType({
    "doc_id": Integer,
    "doc_rev": Integer
})


class Project(Base, IdMixin):
    __tablename__ = "projects"

    name = Column(String, nullable=False)
    title = Column(String, nullable=False)

    public = Column(Boolean, nullable=False, default=True)

    owner_id = Column(Integer, ForeignKey("users.id",
                                          onupdate="cascade",
                                          ondelete="cascade"),
                      nullable=False)

    owner = relationship("User", backref="projects")

    __table_args__ = (
        Index("project_owner_id_lower_name", owner_id, func.lower(name),
              unique=True),
    )

    @property
    def __acl__(self):
        acl = []

        for entry in self.acl:
            acl.extend([(Allow, "user_id:{}".format(entry.user_id), perm)
                for perm in entry.permissions])

        if self.public:
            acl.append((Allow, Everyone, "read"))

        return acl


class ProjectACLEntry(Base):
    __tablename__ = "project_acl"

    READER = 0
    WRITER = 1

    project_id = Column(Integer, ForeignKey("projects.id",
                                            onupdate="cascade",
                                            ondelete="cascade"),
                        nullable=False)

    project = relationship("Project", backref=backref("acl", lazy="joined"))

    user_id = Column(Integer, ForeignKey("users.id",
                                         onupdate="cascade",
                                         ondelete="cascade"),
                     nullable=False)

    user = relationship("User", backref="project_acl")

    level = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(project_id, user_id),
    )

    @property
    def permissions(self):
        return {
            ProjectACLEntry.READER: ["read"],
            ProjectACLEntry.WRITER: ["read", "write"]
        }.get(self.level, [])


class TreeRevision(Base, TimestampMixin):
    """
    A tree revision is a snapshot of a project at a given moment in time.
    When a snapshot is taken by the user, these things occur:

     * The tree is rewritten entirely with the current revision information.

     * A new tree revision is created to replace the old tree.

     * The old tree is regarded as immutable.

    Old tree revisions are never modified. Upon reversion to any old tree
    revision, the contents of the tree are copied into the latest revision and
    mutated on any edits. Tree revisions are _only_ created during snapshots.

    Changing the tree is also expensive, so it should be avoided as much as
    possible. The update of document revisions does _not_ require tree updates.
    """

    __tablename__ = "tree_revisions"

    project_id = Column(Integer, ForeignKey("projects.id",
                                            onupdate="cascade",
                                            ondelete="cascade"),
                        nullable=False)

    project = relationship("Project", backref="tree_revisions")

    tree_rev = Column(Integer, nullable=False)

    tree = Column(PGJson, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(project_id, tree_rev),
    )

    def _get_subtree_at_path(self, path):
        """
        Create a query to get a subtree at a given path.
        """
        return DBSession.query(func.subtree_at_path(TreeRevision.tree,
                                                    cast(array(path, type_=Integer), ARRAY(Integer)),
                                                    type_=PGJson)) \
        .filter(and_(
            TreeRevision.project_id == self.project_id,
            TreeRevision.tree_rev == self.tree_rev
        ))

    def get_subtree_at_path(self, path=()):
        """
        Get the scalar value of a subtree at a path.
        """
        return self._get_subtree_at_path(path).scalar()

    def get_doc_revs(self, path=()):
        """
        Get all the document content at a given path for a given tree revision.
        If the tree revision is omitted, then the latest tree is retrieved.
        """
        q = DBSession.query(
            func.all_docs_and_revs_for_tree(self._get_subtree_at_path(path).as_scalar(),
                                            type_=DocRev).label("doc_revs")) \
        .subquery()

        return DBSession.query(DocRevision).select_from(q).filter(
            DocRevision.doc_id == q.c.doc_revs.doc_id,
            ((DocRevision.doc_rev == None) & not_(DocRevision.frozen)) |
                (DocRevision.doc_rev == q.c.doc_revs.doc_rev))


class Doc(Base, IdMixin):
    """
    A doc is just a table to map document IDs to projects for ACLs to be
    checked.

    Document IDs are global across the whole system, i.e. all document IDs are
    associated with exactly one project.
    """
    __tablename__ = "docs"

    name = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id",
                                            onupdate="cascade",
                                            ondelete="cascade"),
                        nullable=False)

    project = relationship("Project", backref="docs")

    @property
    def __acl__(self):
        return self.project.__acl__


class DocRevision(Base, TimestampMixin):
    """
    A doc revision is a snapshot of a document at a given moment in time.
    Similar to a tree revision, it is created when a snapshot is taken and made
    immutable. Document revisions are _not_ created when they are saved, _only_
    during snapshots -- it is also unnecessary as Neuron can play back history.

    It is stored by ID in the tree under doc_id. Its associated revision is
    stored under doc_rev. If the tree contains the latest document, doc_rev
    will be null. The doc_rev number corresponds to the operation sequence
    number in Neuron. The doc_rev number may be updated(!) if the document is
    not frozen.

    The commit protocol for a doc revision is as follows:

    1. If a document is found at the correct revision for snapshotting, freeze
       it immediately.

    1.1. If a client attempts to commit a revision from Neuron, it must create
         a new revision as the current one is now frozen.

    2. The JSON tree is retrieved from the database and updated for the
       snapshot.

    Upon reversion to any old doc revision, the doc_rev of the offending member
    of the tree is changed to the revision number of the document and a
    reversion operation is sent to Neuron.

    0. Call the revision number before the revert n.

    1. Update the current tree with the number of the revision to revert to.
       Call this revision m.

    2. Send a Neuron operation to reset to the revision. Neuron is now at
       revision n + 1 (not m).

    3. When committing from Neuron, a new revision will be created as revision
       m is frozen.
    """
    __tablename__ = "doc_revisions"

    doc_id = Column(Integer, ForeignKey("docs.id",
                                        onupdate="cascade",
                                        ondelete="cascade"),
                    nullable=False)

    doc = relationship("Doc", backref="doc_revisions")

    doc_rev = Column(Integer, nullable=True)

    content = Column(Text, nullable=False)

    frozen = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        PrimaryKeyConstraint(doc_id, doc_rev),
        Index("doc_revision_project_id_doc_id_not_frozen", doc_id,frozen,
              postgresql_where=not_(frozen), unique=True),
    )
