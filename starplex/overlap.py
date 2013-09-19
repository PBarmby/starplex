#!/usr/bin/env python
# encoding: utf-8
"""
Module for finding footprint overlaps.
"""

from sqlalchemy import func

from .database.models import Catalog


class CatalogOverlaps(object):
    """Queries catalogs that overlap a principle catalog.
    
    Parameters
    ----------
    session :
        The active SQLAlchemy session instance.
    catalog : :class:`starplex.database.models.Catalog` instance
        The :class:`Catalog` instance to find footprint overlaps against.
    telescope : str
        Value of ``telescope`` field in ``catalog`` table rows to query.
    """
    def __init__(self, session, catalog, telescope):
        super(CatalogOverlaps, self).__init__()
        self._s = session
        self.main_catalog = catalog
        self._main_footprint = self.main_catalog.footprint
        self.telescope = telescope
        self._overlapping_catalogs = self._query_from_catalog(self.main_catalog)
        self._clips = None  # overlapping polygons, will be list
    
    def _query_from_catalog(self, main_catalog):
        """Query for overlapping catalogs given a principle catalog.
        Returns a list of overlapping catalogs.
        """
        overlaps = self._s.query(Catalog)\
            .filter(func.ST_Intersects(
                Catalog.footprint, self._main_footprint))\
            .filter(Catalog.id != main_catalog.id)\
            .filter(Catalog.telescope == self.telescope)\
            .all()
        return overlaps

    @property
    def count(self):
        """Number of overlaps"""
        return len(self._overlapping_catalogs)

    @property
    def catalogs(self):
        """List of overlapping catalogs"""
        return self._overlapping_catalogs

    @property
    def clips(self):
        """Polygons representing the intersecting areas between the princpiple
        catalog and all overlapping catalogs.
        
        Returns a list of tuples of :class:``WKBElement`` for each
        intersection, corresponding to the list of overlapping catalogs.
        That is, each overlap has a tuple of :class:``WKBElement`` since
        an overlap can have multiple polygon parts.

        The clipping polygons are cached.

        To get the WKT representation of these::

        >> for clip in overlaps.clips:
        >>     for part in clip:
        >>         print session.query(func.ST_AsText(part)).one()
        """
        if self._clips is None:
            self._clips = []
            for catalog in self._overlapping_catalogs:
                clip = self._s.\
                        query(func.ST_Intersection(
                            catalog.footprint, self._main_footprint))\
                        .one()
                self._clips.append(clip)
        return self._clips


def main():
    pass


if __name__ == '__main__':
    main()
