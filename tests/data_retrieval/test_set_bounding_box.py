from tradesman.utils import set_bbox


def test_set_bounding_boxes(nauru_no_pop):
    xmin = float(nauru_no_pop.about.xmin)
    xmax = float(nauru_no_pop.about.xmax)
    ymin = float(nauru_no_pop.about.ymin)
    ymax = float(nauru_no_pop.about.ymax)

    assert isinstance(set_bbox(xmin, ymin, xmax, ymax, box_side=25), list)
