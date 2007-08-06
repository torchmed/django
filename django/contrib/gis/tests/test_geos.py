import random, unittest
from django.contrib.gis.geos import \
    GEOSException, GEOSGeometryIndexError, \
    GEOSGeometry, Point, LineString, LinearRing, Polygon, \
    MultiPoint, MultiLineString, MultiPolygon, GeometryCollection, \
    fromstr, HAS_NUMPY
from geometries import *

if HAS_NUMPY: from numpy import array

class GEOSTest(unittest.TestCase):

    def test01a_wkt(self):
        "Testing WKT output."
        for g in wkt_out:
            geom = GEOSGeometry(g.wkt)
            self.assertEqual(g.ewkt, geom.wkt)

    def test01b_hex(self):
        "Testing HEX output."
        for g in hex_wkt:
            geom = GEOSGeometry(g.wkt)
            self.assertEqual(g.hex, geom.hex)

    def test01c_kml(self):
        "Testing KML output."
        for tg in wkt_out:
            geom = fromstr(tg.wkt)
            kml = getattr(tg, 'kml', False)
            if kml: self.assertEqual(kml, geom.kml)

    def test01d_errors(self):
        "Testing the Error handlers."
        print "\nBEGIN - expecting GEOS_ERROR; safe to ignore.\n"
        for err in errors:
            if err.hex:
                self.assertRaises(GEOSException, GEOSGeometry, err.wkt)
            else:
                self.assertRaises(GEOSException, GEOSGeometry, err.wkt)
        print "\nEND - expecting GEOS_ERROR; safe to ignore.\n"
                
    def test02a_points(self):
        "Testing Point objects."
        prev = GEOSGeometry('POINT(0 0)')
        for p in points:
            # Creating the point from the WKT
            pnt = GEOSGeometry(p.wkt)
            self.assertEqual(pnt.geom_type, 'Point')
            self.assertEqual(pnt.geom_typeid, 0)
            self.assertEqual(p.x, pnt.x)
            self.assertEqual(p.y, pnt.y)
            self.assertEqual(True, pnt == GEOSGeometry(p.wkt))
            self.assertEqual(False, pnt == prev)

            # Making sure that the point's X, Y components are what we expect
            self.assertAlmostEqual(p.x, pnt.tuple[0], 9)
            self.assertAlmostEqual(p.y, pnt.tuple[1], 9)

            # Testing the third dimension, and getting the tuple arguments
            if hasattr(p, 'z'):
                self.assertEqual(True, pnt.hasz)
                self.assertEqual(p.z, pnt.z)
                self.assertEqual(p.z, pnt.tuple[2], 9)
                tup_args = (p.x, p.y, p.z)
                set_tup1 = (2.71, 3.14, 5.23)
                set_tup2 = (5.23, 2.71, 3.14)
            else:
                self.assertEqual(False, pnt.hasz)
                self.assertEqual(None, pnt.z)
                tup_args = (p.x, p.y)
                set_tup1 = (2.71, 3.14)
                set_tup2 = (3.14, 2.71)

            # Centroid operation on point should be point itself
            self.assertEqual(p.centroid, pnt.centroid.tuple)

            # Now testing the different constructors
            pnt2 = Point(tup_args)  # e.g., Point((1, 2))
            pnt3 = Point(*tup_args) # e.g., Point(1, 2)
            self.assertEqual(True, pnt == pnt2)
            self.assertEqual(True, pnt == pnt3)

            # Now testing setting the x and y
            pnt.y = 3.14
            pnt.x = 2.71
            self.assertEqual(3.14, pnt.y)
            self.assertEqual(2.71, pnt.x)

            # Setting via the tuple/coords property
            pnt.tuple = set_tup1
            self.assertEqual(set_tup1, pnt.tuple)
            pnt.coords = set_tup2
            self.assertEqual(set_tup2, pnt.coords)
            
            prev = pnt # setting the previous geometry

    def test02b_multipoints(self):
        "Testing MultiPoint objects."
        for mp in multipoints:
            mpnt = GEOSGeometry(mp.wkt)
            self.assertEqual(mpnt.geom_type, 'MultiPoint')
            self.assertEqual(mpnt.geom_typeid, 4)

            self.assertAlmostEqual(mp.centroid[0], mpnt.centroid.tuple[0], 9)
            self.assertAlmostEqual(mp.centroid[1], mpnt.centroid.tuple[1], 9)

            self.assertRaises(GEOSGeometryIndexError, mpnt.__getitem__, len(mpnt))
            self.assertEqual(mp.centroid, mpnt.centroid.tuple)
            self.assertEqual(mp.points, tuple(m.tuple for m in mpnt))
            for p in mpnt:
                self.assertEqual(p.geom_type, 'Point')
                self.assertEqual(p.geom_typeid, 0)
                self.assertEqual(p.empty, False)
                self.assertEqual(p.valid, True)

    def test03a_linestring(self):
        "Testing LineString objects."
        prev = GEOSGeometry('POINT(0 0)')
        for l in linestrings:
            ls = GEOSGeometry(l.wkt)
            self.assertEqual(ls.geom_type, 'LineString')
            self.assertEqual(ls.geom_typeid, 1)
            self.assertEqual(ls.empty, False)
            self.assertEqual(ls.ring, False)
            if hasattr(l, 'centroid'):
                self.assertEqual(l.centroid, ls.centroid.tuple)
            if hasattr(l, 'tup'):
                self.assertEqual(l.tup, ls.tuple)
                
            self.assertEqual(True, ls == GEOSGeometry(l.wkt))
            self.assertEqual(False, ls == prev)
            self.assertRaises(GEOSGeometryIndexError, ls.__getitem__, len(ls))
            prev = ls

            # Creating a LineString from a tuple, list, and numpy array
            self.assertEqual(ls, LineString(ls.tuple))  # tuple
            self.assertEqual(ls, LineString(*ls.tuple)) # as individual arguments
            self.assertEqual(ls, LineString([list(tup) for tup in ls.tuple])) # as list
            self.assertEqual(ls.wkt, LineString(*tuple(Point(tup) for tup in ls.tuple)).wkt) # Point individual arguments
            if HAS_NUMPY: self.assertEqual(ls, LineString(array(ls.tuple))) # as numpy array

    def test03b_multilinestring(self):
        "Testing MultiLineString objects."
        prev = GEOSGeometry('POINT(0 0)')
        for l in multilinestrings:
            ml = GEOSGeometry(l.wkt)
            self.assertEqual(ml.geom_type, 'MultiLineString')
            self.assertEqual(ml.geom_typeid, 5)

            self.assertAlmostEqual(l.centroid[0], ml.centroid.x, 9)
            self.assertAlmostEqual(l.centroid[1], ml.centroid.y, 9)

            self.assertEqual(True, ml == GEOSGeometry(l.wkt))
            self.assertEqual(False, ml == prev)
            prev = ml

            for ls in ml:
                self.assertEqual(ls.geom_type, 'LineString')
                self.assertEqual(ls.geom_typeid, 1)
                self.assertEqual(ls.empty, False)

            self.assertRaises(GEOSGeometryIndexError, ml.__getitem__, len(ml))
            self.assertEqual(ml.wkt, MultiLineString(*tuple(s.clone() for s in ml)).wkt)
            self.assertEqual(ml, MultiLineString(*tuple(LineString(s.tuple) for s in ml)))

    def test04_linearring(self):
        "Testing LinearRing objects."
        for rr in linearrings:
            lr = GEOSGeometry(rr.wkt)
            self.assertEqual(lr.geom_type, 'LinearRing')
            self.assertEqual(lr.geom_typeid, 2)
            self.assertEqual(rr.n_p, len(lr))
            self.assertEqual(True, lr.valid)
            self.assertEqual(False, lr.empty)

            # Creating a LinearRing from a tuple, list, and numpy array
            self.assertEqual(lr, LinearRing(lr.tuple))
            self.assertEqual(lr, LinearRing(*lr.tuple))
            self.assertEqual(lr, LinearRing([list(tup) for tup in lr.tuple]))
            if HAS_NUMPY: self.assertEqual(lr, LinearRing(array(lr.tuple)))
    
    def test05a_polygons(self):
        "Testing Polygon objects."
        prev = GEOSGeometry('POINT(0 0)')
        for p in polygons:
            # Creating the Polygon, testing its properties.
            poly = GEOSGeometry(p.wkt)
            self.assertEqual(poly.geom_type, 'Polygon')
            self.assertEqual(poly.geom_typeid, 3)
            self.assertEqual(poly.empty, False)
            self.assertEqual(poly.ring, False)
            self.assertEqual(p.n_i, poly.num_interior_rings)
            self.assertEqual(p.n_i + 1, len(poly)) # Testing __len__
            self.assertEqual(p.n_p, poly.num_points)

            # Area & Centroid
            self.assertAlmostEqual(p.area, poly.area, 9)
            self.assertAlmostEqual(p.centroid[0], poly.centroid.tuple[0], 9)
            self.assertAlmostEqual(p.centroid[1], poly.centroid.tuple[1], 9)

            # Testing the geometry equivalence
            self.assertEqual(True, poly == GEOSGeometry(p.wkt))
            self.assertEqual(False, poly == prev) # Should not be equal to previous geometry
            self.assertEqual(True, poly != prev)

            # Testing the exterior ring
            ring = poly.exterior_ring
            self.assertEqual(ring.geom_type, 'LinearRing')
            self.assertEqual(ring.geom_typeid, 2)
            if p.ext_ring_cs:
                self.assertEqual(p.ext_ring_cs, ring.tuple)
                self.assertEqual(p.ext_ring_cs, poly[0].tuple) # Testing __getitem__

            # Testing __getitem__ and __setitem__ on invalid indices
            self.assertRaises(GEOSGeometryIndexError, poly.__getitem__, len(poly))
            self.assertRaises(GEOSGeometryIndexError, poly.__setitem__, len(poly), False)
            self.assertRaises(GEOSGeometryIndexError, poly.__getitem__, -1)

            # Testing __iter__ 
            for r in poly:
                self.assertEqual(r.geom_type, 'LinearRing')
                self.assertEqual(r.geom_typeid, 2)

            # Testing polygon construction.
            self.assertRaises(TypeError, Polygon, 0, [1, 2, 3])
            self.assertRaises(TypeError, Polygon, 'foo')

            rings = tuple(r.clone() for r in poly)
            self.assertEqual(poly, Polygon(rings[0], rings[1:]))
            self.assertEqual(poly.wkt, Polygon(*tuple(r.clone() for r in poly)).wkt)
            self.assertEqual(poly.wkt, Polygon(*tuple(LinearRing(r.tuple) for r in poly)).wkt)

            # Setting the second point of the first ring (which should set the
            #  first point of the polygon).
            prev = poly.clone() # Using clone() to get a copy of the current polygon
            self.assertEqual(True, poly == prev) # They clone should be equal to the first
            newval = (poly[0][1][0] + 5.0, poly[0][1][1] + 5.0) # really testing __getitem__ ([ring][point][tuple])
            try:
                poly[0][1] = ('cannot assign with', 'string values')
            except TypeError:
                pass
            poly[0][1] = newval # setting the second point in the polygon with the newvalue (based on the old)
            self.assertEqual(newval, poly[0][1]) # The point in the polygon should be the new value
            self.assertEqual(False, poly == prev) # Should be different from the clone we just made
            
    def test05b_multipolygons(self):
        "Testing MultiPolygon objects."
        print "\nBEGIN - expecting GEOS_NOTICE; safe to ignore.\n"
        prev = GEOSGeometry('POINT (0 0)')
        for mp in multipolygons:
            mpoly = GEOSGeometry(mp.wkt)
            self.assertEqual(mpoly.geom_type, 'MultiPolygon')
            self.assertEqual(mpoly.geom_typeid, 6)
            self.assertEqual(mp.valid, mpoly.valid)

            if mp.valid:
                self.assertEqual(mp.num_geom, mpoly.num_geom)
                self.assertEqual(mp.n_p, mpoly.num_coords)
                self.assertEqual(mp.num_geom, len(mpoly))
                self.assertRaises(GEOSGeometryIndexError, mpoly.__getitem__, len(mpoly))
                for p in mpoly:
                    self.assertEqual(p.geom_type, 'Polygon')
                    self.assertEqual(p.geom_typeid, 3)
                    self.assertEqual(p.valid, True)
                self.assertEqual(mpoly.wkt, MultiPolygon(*tuple(poly.clone() for poly in mpoly)).wkt)

        print "\nEND - expecting GEOS_NOTICE; safe to ignore.\n"  

    def test06_memory_hijinks(self):
        "Testing Geometry __del__() in different scenarios"
        #### Memory issues with rings and polygons

        # These tests are needed to ensure sanity with writable geometries.

        # Getting a polygon with interior rings, and pulling out the interior rings
        poly = GEOSGeometry(polygons[1].wkt)
        ring1 = poly[0]
        ring2 = poly[1]

        # These deletes should be 'harmless' since they are done on child geometries
        del ring1 
        del ring2
        ring1 = poly[0]
        ring2 = poly[1]

        # Deleting the polygon
        del poly

        # Ensuring that trying to access the deleted memory (by getting the string
        #  representation of the ring of a deleted polygon) raises a GEOSException
        #  instead of something worse..
        self.assertRaises(GEOSException, str, ring1)
        self.assertRaises(GEOSException, str, ring2)

        #### Memory issues with geometries from Geometry Collections
        mp = fromstr('MULTIPOINT(85 715, 235 1400, 4620 1711)')
        
        # Getting the points
        pts = [p for p in mp]

        # More 'harmless' child geometry deletes
        for p in pts: del p

        # Cloning for comparisons
        clones = [p.clone() for p in pts]

        for i in xrange(len(clones)):
            # Testing equivalence before & after modification
            self.assertEqual(True, pts[i] == clones[i]) # before
            pts[i].x = 3.14159
            pts[i].y = 2.71828
            self.assertEqual(False, pts[i] == clones[i]) # after
            self.assertEqual(3.14159, mp[i].x) # parent x,y should be modified
            self.assertEqual(2.71828, mp[i].y)

        # Should raise GEOSException when trying to get geometries from the multipoint
        #  after it has been deleted.
        del mp
        for p in pts:
            self.assertRaises(GEOSException, str, p) # tests p's geometry pointer
            self.assertRaises(GEOSException, p.get_coords) # tests p's coordseq pointer

        # Now doing this with a GeometryCollection
        polywkt = polygons[3].wkt # a 'real life' polygon.
        lrwkt = linearrings[0].wkt # a 'real life' linear ring
        poly = fromstr(polywkt)
        linring = fromstr(lrwkt)

        # Pulling out the shell and cloning our initial geometries for later comparison.
        shell = poly.shell
        polyc = poly.clone()
        linringc = linring.clone()

        gc = GeometryCollection(poly, linring, Point(5, 23))
        
        # Should no longer be able to access these variables
        self.assertRaises(GEOSException, str, poly)
        self.assertRaises(GEOSException, str, shell)
        self.assertRaises(GEOSException, str, linring)

        r1 = gc[1] # pulling out the ring
        pnt = gc[2] # pulling the point from the geometry collection

        # Now lets create a MultiPolygon from the geometry collection components
        mpoly = MultiPolygon(gc[0], Polygon(gc[1]))
        self.assertEqual(polyc.wkt, mpoly[0].wkt)

        # Should no longer be able to access the geometry collection directly
        self.assertRaises(GEOSException, len, gc)
        
        # BUT, should still be able to access the Point we obtained earlier, but
        #  not the linear ring (since it is now part of the MultiPolygon.
        self.assertEqual(5, pnt.x)
        self.assertEqual(23, pnt.y)

        # __len__ is called on the coordinate sequence pointer -- make sure its nullified as well
        self.assertRaises(GEOSException, len, r1)
        self.assertRaises(GEOSException, str, r1)

        # Can't access point after deletion of parent geometry.
        del gc
        self.assertRaises(GEOSException, str, pnt)

        # Cleaning up.
        del polyc
        del mpoly

        #### Memory issues with creating geometries from coordinate sequences within other geometries

        # Creating the initial polygon from the following tuples, and then pulling out
        #  the individual rings.
        ext_tup = ((0, 0), (0, 7), (7, 7), (7, 0), (0, 0))
        itup1 = ((1, 1), (1, 2), (2, 2), (2, 1), (1, 1))
        itup2 = ((4, 4), (4, 5), (5, 5), (5, 4), (4, 4))
        poly1 = Polygon(LinearRing(ext_tup), LinearRing(itup1), LinearRing(itup2))
        shell = poly1.shell
        hole1 = poly1[1]
        hole2 = poly1[2]

        # Creating a Polygon from the shell and one of the holes
        poly2 = Polygon(shell, hole1)

        # We should no longer be able to access the original Polygon, its
        #  shell or its first internal ring.
        self.assertRaises(GEOSException, str, poly1)
        self.assertRaises(GEOSException, str, shell)
        self.assertRaises(GEOSException, str, hole1)

        # BUT, the second hole is still accessible.
        self.assertEqual(itup2, hole2.tuple)
        
        # Deleting the first polygon, and ensuring that
        #  the second hole is now gone for good.
        del poly1
        self.assertRaises(GEOSException, str, hole2)
        
    def test08_coord_seq(self):
        "Testing Coordinate Sequence objects."
        for p in polygons:
            if p.ext_ring_cs:
                # Constructing the polygon and getting the coordinate sequence
                poly = GEOSGeometry(p.wkt)
                cs = poly.exterior_ring.coord_seq

                self.assertEqual(p.ext_ring_cs, cs.tuple) # done in the Polygon test too.
                self.assertEqual(len(p.ext_ring_cs), len(cs)) # Making sure __len__ works

                # Checks __getitem__ and __setitem__
                for i in xrange(len(p.ext_ring_cs)):
                    c1 = p.ext_ring_cs[i] # Expected value
                    c2 = cs[i] # Value from coordseq
                    self.assertEqual(c1, c2)

                    # Constructing the test value to set the coordinate sequence with
                    if len(c1) == 2: tset = (5, 23)
                    else: tset = (5, 23, 8)
                    cs[i] = tset
                    
                    # Making sure every set point matches what we expect
                    for j in range(len(tset)):
                        cs[i] = tset
                        self.assertEqual(tset[j], cs[i][j])

    def test09_relate_pattern(self):
        "Testing relate() and relate_pattern()."
        g = GEOSGeometry('POINT (0 0)')
        self.assertRaises(GEOSException, g.relate_pattern, 0, 'invalid pattern, yo')

        for i in xrange(len(relate_geoms)):
            g_tup = relate_geoms[i]
            a = GEOSGeometry(g_tup[0].wkt)
            b = GEOSGeometry(g_tup[1].wkt)
            pat = g_tup[2]
            result = g_tup[3]
            self.assertEqual(result, a.relate_pattern(b, pat))
            self.assertEqual(g_tup[2], a.relate(b))

    def test10_intersection(self):
        "Testing intersects() and intersection()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = GEOSGeometry(g_tup[0].wkt)
            b = GEOSGeometry(g_tup[1].wkt)
            i1 = GEOSGeometry(intersect_geoms[i].wkt) 
            self.assertEqual(True, a.intersects(b))
            i2 = a.intersection(b)
            self.assertEqual(i1, i2)
            self.assertEqual(i1, a & b) # __and__ is intersection operator
            a &= b # testing __iand__
            self.assertEqual(i1, a)

    def test11_union(self):
        "Testing union()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = GEOSGeometry(g_tup[0].wkt)
            b = GEOSGeometry(g_tup[1].wkt)
            u1 = GEOSGeometry(union_geoms[i].wkt)
            u2 = a.union(b)
            self.assertEqual(u1, u2)
            self.assertEqual(u1, a | b) # __or__ is union operator
            a |= b # testing __ior__
            self.assertEqual(u1, a) 

    def test12_difference(self):
        "Testing difference()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = GEOSGeometry(g_tup[0].wkt)
            b = GEOSGeometry(g_tup[1].wkt)
            d1 = GEOSGeometry(diff_geoms[i].wkt)
            d2 = a.difference(b)
            self.assertEqual(d1, d2)
            self.assertEqual(d1, a - b) # __sub__ is difference operator
            a -= b # testing __isub__
            self.assertEqual(d1, a)

    def test13_symdifference(self):
        "Testing sym_difference()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = GEOSGeometry(g_tup[0].wkt)
            b = GEOSGeometry(g_tup[1].wkt)
            d1 = GEOSGeometry(sdiff_geoms[i].wkt)
            d2 = a.sym_difference(b)
            self.assertEqual(d1, d2)
            self.assertEqual(d1, a ^ b) # __xor__ is symmetric difference operator
            a ^= b # testing __ixor__
            self.assertEqual(d1, a)

    def test14_buffer(self):
        "Testing buffer()."
        for i in xrange(len(buffer_geoms)):
            g_tup = buffer_geoms[i]
            g = GEOSGeometry(g_tup[0].wkt)

            # The buffer we expect
            exp_buf = GEOSGeometry(g_tup[1].wkt)

            # Can't use a floating-point for the number of quadsegs.
            self.assertRaises(TypeError, g.buffer, g_tup[2], float(g_tup[3]))

            # Constructing our buffer
            buf = g.buffer(g_tup[2], g_tup[3])
            self.assertEqual(exp_buf.num_coords, buf.num_coords)
            self.assertEqual(len(exp_buf), len(buf))

            # Now assuring that each point in the buffer is almost equal
            for j in xrange(len(exp_buf)):
                exp_ring = exp_buf[j]
                buf_ring = buf[j]
                self.assertEqual(len(exp_ring), len(buf_ring))
                for k in xrange(len(exp_ring)):
                    # Asserting the X, Y of each point are almost equal (due to floating point imprecision)
                    self.assertAlmostEqual(exp_ring[k][0], buf_ring[k][0], 9)
                    self.assertAlmostEqual(exp_ring[k][1], buf_ring[k][1], 9)

    def test15_srid(self):
        "Testing the SRID property and keyword."
        # Testing SRID keyword on Point
        pnt = Point(5, 23, srid=4326)
        self.assertEqual(4326, pnt.srid)
        pnt.srid = 3084
        self.assertEqual(3084, pnt.srid)
        self.assertRaises(TypeError, pnt.set_srid, '4326')

        # Testing SRID keyword on fromstr(), and on Polygon rings.
        poly = fromstr(polygons[1].wkt, srid=4269)
        self.assertEqual(4269, poly.srid)
        for ring in poly: self.assertEqual(4269, ring.srid)
        poly.srid = 4326
        self.assertEqual(4326, poly.shell.srid)

        # Testing SRID keyword on GeometryCollection
        gc = GeometryCollection(Point(5, 23), LineString((0, 0), (1.5, 1.5), (3, 3)), srid=32021)
        self.assertEqual(32021, gc.srid)
        for i in range(len(gc)): self.assertEqual(32021, gc[i].srid)

    def test16_mutable_geometries(self):
        "Testing the mutability of Polygons and Geometry Collections."
        ### Testing the mutability of Polygons ###
        for p in polygons:
            poly = fromstr(p.wkt)

            # Should only be able to use __setitem__ with LinearRing geometries.
            self.assertRaises(TypeError, poly.__setitem__, 0, LineString((1, 1), (2, 2)))

            # Constructing the new shell by adding 500 to every point in the old shell.
            shell_tup = poly.shell.tuple
            new_coords = []
            for point in shell_tup: new_coords.append((point[0] + 500., point[1] + 500.))
            shell1 = LinearRing(*tuple(new_coords))
            shell2 = shell1.clone() 

            # Assigning polygon's exterior ring w/the new shell
            poly.exterior_ring = shell1
            self.assertRaises(GEOSException, str, shell1) # shell1 should no longer be accessible
            self.assertEqual(poly.exterior_ring, shell2)
            self.assertEqual(poly[0], shell2)
            del poly, shell1, shell_tup # cleaning up

        ### Testing the mutability of Geometry Collections
        for tg in multipoints:
            mp = fromstr(tg.wkt)
            for i in range(len(mp)):
                # Creating a random point.
                pnt = mp[i].clone()
                new = Point(random.randint(1, 100), random.randint(1, 100))
                tmp = new.clone()
                # Testing the assignmen
                mp[i] = tmp
                self.assertRaises(GEOSException, len, tmp)
                self.assertEqual(mp[i], new)
                self.assertEqual(mp[i].wkt, new.wkt)
                self.assertNotEqual(pnt, mp[i])
            del mp

        # Multipolygons involve much more memory management because each
        #  polygon w/in the collection has its own rings.
        for tg in multipolygons:
            mpoly = fromstr(tg.wkt)
            for i in xrange(len(mpoly)):
                poly = mpoly[i].clone()
                # Offsetting the each ring in the polygon by 500.
                tmp = poly.clone()
                for r in tmp: 
                    for j in xrange(len(r)): r[j] = (r[j][0] + 500., r[j][1] + 500.)
                self.assertNotEqual(poly, tmp)
                new = tmp.clone() # a 'reference' copy of the geometry used in assignment
                # Testing the assignment
                mpoly[i] = tmp
                self.assertRaises(GEOSException, str, tmp)
                self.assertEqual(mpoly[i], new)
                self.assertNotEqual(poly, mpoly[i])
            del mpoly

def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(GEOSTest))
    return s

def run(verbosity=2):
    unittest.TextTestRunner(verbosity=verbosity).run(suite())
