"""The room layouts for ops/build_room_maps.py, one function per room.

Each takes the Labels object and returns (body_svg, aria_detail, height).
Canvas is 1000 wide: the plan sits in the middle, labels sit in the margins
(left ones start at LX, right ones end at RX) with a leader to what they name.
Label indices are 0-based content.json order, so L.add(0, ...) is the zone the
room page lists first.
"""
from room_map_draw import *          # noqa: F401,F403

LX, RX = 22, 978


def garage(L):
    X, Y, W, H = 250, 84, 500, 440
    b = [walls(X, Y, W, H, gaps=[("b", 120, 480), ("t", 420, 480)])]
    b.append(line(X + 120, Y + H, X + 480, Y + H, stroke=SOFT, sw=1.5,
                  dash="10 6"))
    b.append(note(X + 300, Y + H + 24, "garage door"))
    b.append(door(X + 480, Y, 60, (-1, 0), (0, 1)))
    b.append(note(X + 450, Y - 10, "into the house"))
    b.append(zone(X + 32, Y + 3, 226, 26))
    b.append(pegboard(X + 40, Y + 6, 210))
    b.append(zone(X + 32, Y + 34, 226, 72))
    b.append(bench(X + 46, Y + 40, 198, 58))
    b.append(zone(X + 266, Y + 3, 146, 98))
    b.append(shelf(X + 274, Y + 10, 130, 34, items="drawers", n=4))
    for i in range(3):
        cx = X + 282 + i * 42
        b.append(rect(cx, Y + 58, 28, 20, fill=STEEL, sw=1.4, rx=3))
        b.append(circle(cx + 14, Y + 68, 3, fill=SLATE, sw=0))
    b.append(car(X + 300, Y + 172, 140, 252))
    b.append(zone(X + 282, Y + 138, 200, 104))
    for i in range(3):
        b.append(rect(X + 294 + i * 62, Y + 150, 52, 36, fill="none",
                      stroke=SOFT, sw=1.5, rx=3,
                      extra=' stroke-dasharray="5 4"'))
    b.append(note(X + 382, Y + 130, "racks on the ceiling"))
    b.append(zone(X + 456, Y + 254, 40, 176))
    b.append(shelf(X + 462, Y + 262, 28, 160, items="bottles", n=6))
    b.append(zone(X + 6, Y + 116, 176, 150))
    b.append(rect(X + 6, Y + 126, 8, 128, fill=STEEL, sw=1.2))
    b.append(bike(X + 30, Y + 166))
    b.append(bike(X + 30, Y + 226))
    b.append(basket(X + 146, Y + 226, 22))
    b.append(ball(X + 140, Y + 220, 8))
    b.append(ball(X + 154, Y + 232, 7))
    b.append(zone(X + 6, Y + 280, 210, 154))
    b.append(long_tools(X + 24, Y + 296, n=5, length=92))
    b.append(mower(X + 128, Y + 316))

    L.add(1, LX, Y - 6, to=(X + 32, Y + 16))
    L.add(0, LX, Y + 56, to=(X + 46, Y + 70))
    L.add(4, LX, Y + 172, to=(X + 70, Y + 191))
    L.add(5, LX, Y + 340, to=(X + 50, Y + 357))
    L.add(2, RX, Y + 110, to=(X + 412, Y + 92), align="right")
    L.add(6, RX, Y + 200, to=(X + 482, Y + 190), align="right")
    L.add(3, RX, Y + 336, to=(X + 496, Y + 352), align="right")
    return ("".join(b),
            "The back wall carries the tool wall with the workbench under it, "
            "and the power tools and chargers beside them. The car parks nose "
            "to the back wall, with the overhead racks on the ceiling above "
            "its hood and the automotive shelf on the wall beside it. Bikes "
            "and the ball bin are on the left wall, and the rakes, shovels "
            "and mower stand by the big door.", 610)


def cabinet_front(x, y, w, parts):
    """The open edge of a vanity: a strip of doors and drawer banks.

    parts: list of (kind, width) with kind "doors" or "drawers".
    """
    out = [rect(x, y, w, 12, fill=WOOD, sw=1.6)]
    cx = x
    for kind, pw in parts:
        out.append(line(cx, y, cx, y + 12, sw=1.3))
        if kind == "doors":
            out.append(line(cx + pw / 2, y + 2, cx + pw / 2, y + 10, sw=1))
            out.append(line(cx + pw / 2 - 6, y + 6, cx + pw / 2 - 2, y + 6,
                            sw=2))
            out.append(line(cx + pw / 2 + 2, y + 6, cx + pw / 2 + 6, y + 6,
                            sw=2))
        else:
            for k in range(1, 4):
                out.append(line(cx + pw * k / 4, y + 3, cx + pw * k / 4,
                                y + 9, sw=2))
        cx += pw
    return "".join(out)


def guest_bathroom(L):
    X, Y, W, H = 280, 84, 440, 420
    b = [walls(X, Y, W, H, gaps=[("b", 30, 110)])]
    b.append(door(X + 30, Y + H, 80, (1, 0), (0, -1)))
    b.append(window(X + W, Y + 300, X + W, Y + 380))
    # 1 the counter and 2 the cabinet beneath it, on the left wall.
    b.append(zone(X + 3, Y + 96, 120, 180))
    b.append(vanity(X + 6, Y + 106, 96, 160, wall="l"))
    b.append(rect(X + 102, Y + 106, 12, 160, fill=WOOD, sw=1.6))
    for yy in (Y + 146, Y + 226):
        b.append(line(X + 104, yy - 6, X + 104, yy + 6, sw=2))
    b.append(line(X + 102, Y + 186, X + 114, Y + 186, sw=1.3))
    b.append(rect(X + 30, Y + 112, 22, 12, fill=FABRIC, sw=1.1, rx=2))
    # 4 the toilet on the back wall.
    b.append(zone(X + 140, Y + 3, 100, 100))
    b.append(toilet(X + 190, Y + 6, "t"))
    b.append(rect(X + 150, Y + 10, 16, 30, fill=PAPER, sw=1.2, rx=3))
    # 3 the tub along the right wall.
    b.append(zone(X + W - 128, Y + 3, 125, 270))
    b.append(tub(X + W - 120, Y + 8, 112, 256))
    # 5 guest linen by the door.
    b.append(zone(X + W - 186, Y + H - 66, 183, 62))
    b.append(towels(X + W - 176, Y + H - 58, 166, 48, n=4))

    L.add(3, LX, Y - 4, to=(X + 140, Y + 30))
    L.add(0, LX, Y + 102, to=(X + 50, Y + 160))
    L.add(1, LX, Y + 220, to=(X + 112, Y + 226))
    L.add(2, RX, Y + 120, to=(X + W - 64, Y + 136), align="right")
    L.add(4, RX, Y + 300, to=(X + W - 90, Y + H - 60), align="right")
    return ("".join(b),
            "The vanity runs along the left wall, its counter on top and its "
            "cabinet doors facing the room. The toilet sits on the back wall "
            "and the tub fills the right side. The guest linen is a short "
            "stack of towels by the door, where a guest finds it without "
            "asking.", 580)


def primary_bathroom(L):
    X, Y, W, H = 250, 84, 500, 440
    b = [walls(X, Y, W, H, gaps=[("b", 200, 290)])]
    b.append(door(X + 290, Y + H, 90, (-1, 0), (0, -1)))
    # 4 the mirrored wall cabinet behind the basins.
    b.append(zone(X + 14, Y + 2, 272, 18))
    b.append(rect(X + 24, Y + 5, 252, 10, fill="#E3E7E8", sw=1.5))
    b.append(line(X + 150, Y + 5, X + 150, Y + 15, sw=1.2))
    # 1 the double counter, 2 the drawer bank and 3 the doors under it.
    b.append(zone(X + 14, Y + 24, 272, 70))
    b.append(vanity(X + 20, Y + 28, 260, 60, basins=2, wall="t"))
    b.append(cabinet_front(X + 20, Y + 88, 260,
                           [("doors", 100), ("drawers", 60), ("doors", 100)]))
    b.append(zone(X + 116, Y + 96, 68, 22))
    b.append(zone(X + 14, Y + 96, 98, 22))
    # 5 shower and tub on the right.
    b.append(zone(X + W - 144, Y + 3, 141, 380))
    b.append(shower(X + W - 136, Y + 8, 128, 128))
    b.append(tub(X + W - 112, Y + 150, 104, 226))
    # 6 the toilet on the left wall.
    b.append(zone(X + 3, Y + 196, 100, 100))
    b.append(toilet(X + 6, Y + 246, "l"))
    # 7 the linen cabinet by the door.
    b.append(zone(X + 3, Y + H - 140, 80, 136))
    b.append(towels(X + 8, Y + H - 132, 64, 124, n=4))

    L.add(3, LX, Y - 14, to=(X + 24, Y + 10))
    L.add(0, LX, Y + 54, to=(X + 20, Y + 58))
    L.add(2, LX, Y + 108, to=(X + 14, Y + 108))
    L.add(1, LX, Y + 152, to=(X + 150, Y + 118))
    L.add(5, LX, Y + 230, to=(X + 3, Y + 246))
    L.add(6, LX, Y + H - 90, to=(X + 3, Y + H - 72))
    L.add(4, RX, Y + 180, to=(X + W - 144, Y + 220), align="right")
    return ("".join(b),
            "A double vanity runs along the back wall with the mirrored "
            "cabinet on the wall behind it, a bank of drawers in the middle "
            "of the counter and cabinet doors under each basin. The shower "
            "and tub fill the right side, the toilet sits on the left wall, "
            "and the linen cabinet stands beside the door.", 600)


def laundry_room(L):
    X, Y, W, H = 270, 90, 460, 400
    b = [walls(X, Y, W, H, gaps=[("b", 180, 270)])]
    b.append(door(X + 180, Y + H, 90, (1, 0), (0, -1)))
    # 2 the detergent shelf on the wall above the machines.
    b.append(zone(X + 12, Y + 2, 160, 24))
    b.append(shelf(X + 18, Y + 5, 148, 16, items="bottles", n=7))
    # 1 washer and dryer.
    b.append(zone(X + 12, Y + 30, 160, 82))
    b.append(washer(X + 20, Y + 38, 68))
    b.append(washer(X + 96, Y + 38, 68))
    # 4 folding counter along the right wall.
    b.append(zone(X + W - 98, Y + 3, 95, 210))
    b.append(rect(X + W - 90, Y + 8, 82, 198, fill=WOOD))
    b.append(shelf(X + W - 82, Y + 22, 66, 120, items="stacks", n=4,
                   fill=WOOD))
    # 5 the air-dry rack and hanging rod, lower right.
    b.append(zone(X + W - 160, Y + 232, 157, 130))
    b.append(line(X + W - 12, Y + 240, X + W - 12, Y + 354, sw=3))
    for yy in range(Y + 250, Y + 350, 18):
        b.append(path("M%s %s l-24 -6 l0 12 z" % (f(X + W - 14), f(yy)),
                      fill=FABRIC, sw=1.2))
    b.append(drying_rack(X + W - 150, Y + 246, 96, 100))
    # 3 sorting hampers on the left wall.
    b.append(zone(X + 3, Y + 140, 70, 160))
    for k in range(3):
        b.append(basket(X + 38, Y + 168 + k * 52, 21))
    # 6 utility corner: a deep sink, a bucket and a broom.
    b.append(zone(X + 3, Y + H - 92, 150, 88))
    b.append(rect(X + 8, Y + H - 84, 70, 70, fill=CARD))
    b.append(rect(X + 16, Y + H - 76, 54, 54, fill=PAPER, sw=1.3, rx=6))
    b.append(circle(X + 43, Y + H - 49, 3.5, fill=INK, sw=0))
    b.append(bucket_top(X + 110, Y + H - 40, 16))

    L.add(1, LX, Y - 12, to=(X + 12, Y + 13))
    L.add(0, LX, Y + 62, to=(X + 20, Y + 74))
    L.add(2, LX, Y + 200, to=(X + 17, Y + 220))
    L.add(5, LX, Y + H - 66, to=(X + 8, Y + H - 50))
    L.add(3, RX, Y + 80, to=(X + W - 8, Y + 100), align="right")
    L.add(4, RX, Y + 280, to=(X + W - 3, Y + 300), align="right")
    return ("".join(b),
            "The washer and dryer stand side by side on the back wall with "
            "the detergent shelf above them. A folding counter runs down the "
            "right wall, with the drying rack and a hanging rod below it. "
            "Three hampers line the left wall, and the utility sink, bucket "
            "and broom share the corner by the door.", 560)


def home_office(L):
    X, Y, W, H = 270, 84, 460, 420
    b = [walls(X, Y, W, H, gaps=[("b", 150, 230)])]
    b.append(door(X + 150, Y + H, 80, (1, 0), (0, -1)))
    b.append(window(X + 100, Y, X + 240, Y))
    # 1 the desk under the window, 2 its drawer pedestal.
    b.append(zone(X + 52, Y + 3, 232, 160))
    b.append(desk(X + 60, Y + 8, 216, 90))
    b.append(chair(X + 168, Y + 130, 20, back="d"))
    b.append(zone(X + 290, Y + 3, 70, 100))
    b.append(shelf(X + 296, Y + 8, 58, 90, items="drawers", n=3,
                   vertical=True))
    # 3 the filing cabinet on the left wall.
    b.append(zone(X + 3, Y + 170, 76, 124))
    b.append(shelf(X + 6, Y + 178, 64, 108, items="drawers", n=3,
                   vertical=True))
    # 5 printer on its own small table.
    b.append(zone(X + 3, Y + 306, 110, 92))
    b.append(rect(X + 6, Y + 318, 96, 72, fill=WOOD))
    b.append(printer(X + 22, Y + 324, 64, 44))
    # 4 the bookshelf along the right wall.
    b.append(zone(X + W - 54, Y + 110, 51, 250))
    b.append(shelf(X + W - 48, Y + 118, 40, 236, items="books", n=26,
                   vertical=True))
    # 6 the supply cabinet by the door.
    b.append(zone(X + 250, Y + H - 66, 140, 62))
    b.append(shelf(X + 256, Y + H - 58, 128, 48, items="bins", n=4))

    L.add(0, LX, Y + 40, to=(X + 60, Y + 54))
    L.add(2, LX, Y + 190, to=(X + 6, Y + 214))
    L.add(4, LX, Y + 316, to=(X + 6, Y + 340))
    L.add(1, RX, Y - 10, to=(X + 354, Y + 40), align="right")
    L.add(3, RX, Y + 196, to=(X + W - 8, Y + 214), align="right")
    L.add(5, RX, Y + H - 50, to=(X + 384, Y + H - 34), align="right")
    return ("".join(b),
            "The desk sits under the window on the back wall with its drawer "
            "pedestal at the right end and the chair in front. The filing "
            "cabinet stands against the left wall, the printer has its own "
            "small table below it, the bookshelf runs along the right wall, "
            "and the supply cabinet sits by the door.", 580)


def mudroom(L):
    X, Y, W, H = 270, 84, 460, 400
    b = [walls(X, Y, W, H, gaps=[("b", 330, 420), ("t", 20, 100)])]
    b.append(door(X + 420, Y + H, 90, (-1, 0), (0, -1)))
    b.append(note(X + 375, Y + H + 22, "outside"))
    b.append(door(X + 20, Y, 80, (1, 0), (0, 1)))
    b.append(note(X + 60, Y - 10, "into the house"))
    # 1 hooks on the back wall, 2 the bench beneath them.
    b.append(zone(X + 120, Y + 2, 290, 46))
    b.append(hooks_row(X + 130, X + 400, Y + 4, 8))
    b.append(zone(X + 130, Y + 52, 270, 56))
    b.append(bench_seat(X + 140, Y + 58, 250, 44))
    # 3 shoes along the right wall.
    b.append(zone(X + W - 62, Y + 112, 59, 188))
    b.append(shoe_pairs(X + W - 54, Y + 118, 46, 176, pairs=5))
    # 5 seasonal gear in bins on the left wall.
    b.append(zone(X + 3, Y + 120, 66, 176))
    b.append(shelf(X + 6, Y + 128, 54, 160, items="bins", n=4))
    # 4 the pet station.
    b.append(zone(X + 12, Y + H - 82, 104, 70))
    b.append(pet_station(X + 22, Y + H - 72))
    # 6 the cleaning corner by the outside door: mat, bucket, broom.
    b.append(zone(X + 226, Y + H - 82, 100, 78))
    b.append(bucket_top(X + 256, Y + H - 40, 16))
    b.append(line(X + 290, Y + H - 70, X + 316, Y + H - 14, sw=2.4))
    b.append(rect(X + 306, Y + H - 22, 20, 12, fill=WOOD, sw=1.4))
    b.append(mat(X + 340, Y + H - 52, 76, 44))

    L.add(0, LX, Y + 8, to=(X + 120, Y + 24))
    L.add(1, LX, Y + 76, to=(X + 140, Y + 80))
    L.add(4, LX, Y + 186, to=(X + 6, Y + 200))
    L.add(3, LX, Y + H - 64, to=(X + 22, Y + H - 50))
    L.add(2, RX, Y + 180, to=(X + W - 8, Y + 210), align="right")
    L.add(5, RX, Y + H - 100, to=(X + 326, Y + H - 60), align="right")
    return ("".join(b),
            "A row of family hooks runs along the back wall with the bench "
            "beneath them. Shoes and boots line the right wall, seasonal "
            "gear sits in bins on the left wall, the pet station is in the "
            "near corner, and the bucket, broom and boot mat wait by the "
            "outside door.", 560)


def nursery(L):
    X, Y, W, H = 270, 84, 460, 420
    b = [walls(X, Y, W, H, gaps=[("b", 170, 250)])]
    b.append(door(X + 250, Y + H, 80, (-1, 0), (0, -1)))
    b.append(window(X + W, Y + 290, X + W, Y + 370))
    # 1 the crib on an inside wall, away from the window and its cords.
    b.append(zone(X + 18, Y + 3, 196, 112))
    b.append(crib(X + 30, Y + 10, 172, 94))
    # 2 the changing station, 5 the backstock right beside it.
    b.append(zone(X + 226, Y + 3, 128, 74))
    b.append(rect(X + 232, Y + 8, 116, 62, fill=WOOD))
    b.append(rect(X + 244, Y + 14, 92, 44, fill=FABRIC, sw=1.4, rx=10))
    b.append(zone(X + 360, Y + 3, 97, 56))
    b.append(shelf(X + 366, Y + 8, 86, 44, items="bins", n=3))
    # 3 baby clothing in the dresser on the right wall.
    b.append(zone(X + W - 62, Y + 96, 59, 170))
    b.append(shelf(X + W - 56, Y + 104, 48, 154, items="drawers", n=4,
                   vertical=True))
    # 4 the feeding chair and its side table.
    b.append(zone(X + 18, Y + H - 170, 150, 120))
    b.append(glider(X + 78, Y + H - 116))
    b.append(circle(X + 140, Y + H - 132, 16, fill=WOOD))
    b.append(lamp(X + 140, Y + H - 132, 6))
    # 6 books and quiet play: a low shelf and a rug.
    b.append(zone(X + 190, Y + 170, 196, 160))
    b.append(rect(X + 206, Y + 186, 164, 100, fill=FABRIC, sw=1.4, rx=14))
    b.append(rect(X + 216, Y + 196, 144, 80, fill="none", stroke=SOFT,
                  sw=1, rx=10))
    b.append(shelf(X + 206, Y + 292, 164, 30, items="books", n=18))

    L.add(0, LX, Y + 40, to=(X + 30, Y + 56))
    L.add(3, LX, Y + H - 140, to=(X + 18, Y + H - 120))
    L.add(4, RX, Y - 18, to=(X + 452, Y + 10), align="right")
    L.add(1, RX, Y + 54, to=(X + 348, Y + 60), align="right")
    L.add(2, RX, Y + 160, to=(X + W - 8, Y + 180), align="right")
    L.add(5, RX, Y + 330, to=(X + 386, Y + 300), align="right")
    return ("".join(b),
            "The crib stands on an inside wall away from the window. The "
            "changing station sits beside it with the diaper backstock "
            "within reach on the same wall. Baby clothing is in the dresser "
            "on the right wall, the feeding chair and its side table are in "
            "the near corner, and a rug and a low bookshelf make the quiet "
            "play space in the middle.", 580)


def patio_or_deck(L):
    X, Y, W, H = 250, 84, 500, 420
    b = [rect(X, Y, W, H, fill="#EDE1C6", stroke="none", sw=0),
         boards(X, Y, W, H, gap=16)]
    # 6 the boards and the rail, underneath everything else.
    b.append(zone(X - 10, Y + 14, W + 20, H + 4))
    b.append(line(X - 12, Y, X + W + 12, Y, sw=10))
    b.append(note(X + W / 2, Y - 10, "back of the house"))
    b.append(rect(X + 200, Y - 4, 100, 8, fill=PAPER, sw=1.6))
    b.append(line(X + 250, Y - 4, X + 250, Y + 4, sw=1.4))
    b.append(rail(X, Y + 6, X, Y + H, posts=7))
    b.append(rail(X + W, Y + 6, X + W, Y + H, posts=7))
    b.append(rail(X, Y + H, X + 190, Y + H, posts=3))
    b.append(rail(X + 310, Y + H, X + W, Y + H, posts=3))
    b.append(stairs(X + 196, Y + H, 108, 44, 4, "u"))
    b.append(note(X + 250, Y + H + 62, "steps down to the yard"))
    # 5 the storage box against the house wall.
    b.append(zone(X + 50, Y + 8, 136, 64))
    b.append(deck_box(X + 62, Y + 16, 112, 46))
    # 2 the grill, out in the open, clear of the wall and the rail.
    b.append(zone(X + W - 150, Y + 30, 128, 96))
    b.append(grill(X + W - 110, Y + 78, 26))
    b.append(rect(X + W - 72, Y + 58, 38, 42, fill=WOOD, sw=1.6, rx=3))
    # 1 seating.
    b.append(zone(X + 22, Y + 160, 210, 196))
    b.append(armchair(X + 66, Y + 200, 46))
    b.append(armchair(X + 186, Y + 200, 46))
    b.append(rect(X + 88, Y + 238, 76, 40, fill=WOOD, rx=4))
    b.append(sofa(X + 40, Y + 290, 172, 56))
    # 3 dining.
    b.append(zone(X + 270, Y + 168, 190, 180))
    b.append(round_table(X + 365, Y + 258, 46, chairs=4))
    # 4 plants along the rail corner.
    b.append(zone(X + 380, Y + H - 66, 112, 60))
    b.append(planter(X + 412, Y + H - 36, 20))
    b.append(planter(X + 460, Y + H - 34, 16))

    L.add(4, LX, Y + 6, to=(X + 62, Y + 40))
    L.add(0, LX, Y + 236, to=(X + 22, Y + 250))
    L.add(5, LX, Y + H - 40, to=(X - 10, Y + H - 24))
    L.add(1, RX, Y + 30, to=(X + W - 22, Y + 78), align="right")
    L.add(2, RX, Y + 210, to=(X + 460, Y + 258), align="right")
    L.add(3, RX, Y + H - 30, to=(X + 492, Y + H - 36), align="right")
    return ("".join(b),
            "The deck runs out from the back of the house to a rail on three "
            "sides, with steps down to the yard. The storage box sits "
            "against the house wall, the grill stands out in the open clear "
            "of the wall and the rail, the seating group takes the left "
            "side, the dining table the right, and the planters gather in "
            "the far corner. The boards and the rail under all of it are "
            "the sixth zone.", 620)


def stair_landing(L):
    X, Y, W, H = 290, 84, 420, 440
    b = [walls(X, Y, W, H, gaps=[("b", 20, 190)])]
    # 2 pictures on the landing wall.
    b.append(zone(X + 34, Y + 2, 260, 22))
    b.append(frames_on_wall(X + 44, X + 284, Y + 6, 4))
    # 3 the flight and the walking path across the landing.
    b.append(zone(X + 14, Y + 40, 186, H - 36))
    b.append(rect(X + 24, Y + 50, 166, 120, fill=FABRIC, sw=1.3, rx=4))
    b.append(stairs(X + 24, Y + 176, 166, H - 176, 10, "u"))
    b.append(lamp(X + 107, Y + 110, 12))
    b.append(note(X + 107, Y + H + 22, "down to the hall"))
    # The open side of the flight is guarded by a rail.
    b.append(rail(X + 200, Y + 176, X + 200, Y + H, posts=6))
    b.append(rail(X + 200, Y + 176, X + W, Y + 176, posts=5))
    b.append(note(X + 310, Y + 316, "open to the floor below"))
    # 1 the console on the landing.
    b.append(zone(X + W - 84, Y + 30, 81, 132))
    b.append(rect(X + W - 70, Y + 40, 60, 112, fill=WOOD))
    b.append(lamp(X + W - 40, Y + 66, 9))
    b.append(rect(X + W - 58, Y + 100, 36, 26, fill=CARD, sw=1.3, rx=3))

    L.add(1, LX, Y - 12, to=(X + 34, Y + 12))
    L.add(2, LX, Y + 300, to=(X + 14, Y + 320))
    L.add(0, RX, Y + 80, to=(X + W - 3, Y + 96), align="right")
    return ("".join(b),
            "The landing sits at the top of a straight flight with pictures "
            "along its wall and a console against the far wall. The path "
            "runs from the top tread across the landing under a ceiling "
            "light, and the open side of the flight is guarded by a rail.",
            620)


def workshop(L):
    X, Y, W, H = 250, 84, 500, 420
    b = [walls(X, Y, W, H, gaps=[("b", 30, 120)])]
    b.append(door(X + 30, Y + H, 90, (1, 0), (0, -1)))
    # 6 PPE on the wall just inside the door: the first thing you reach.
    b.append(zone(X + 3, Y + H - 206, 110, 104))
    b.append(rect(X + 5, Y + H - 196, 10, 84, fill=STEEL, sw=1.2))
    b.append(goggles(X + 42, Y + H - 180))
    b.append(earmuffs(X + 42, Y + H - 148))
    b.append(extinguisher(X + 84, Y + H - 150))
    # 2 power tools on the back wall.
    b.append(zone(X + 12, Y + 3, 176, 96))
    b.append(shelf(X + 20, Y + 8, 160, 40, items="drawers", n=4))
    for i in range(3):
        cx = X + 30 + i * 50
        b.append(rect(cx, Y + 60, 30, 20, fill=STEEL, sw=1.4, rx=3))
        b.append(circle(cx + 15, Y + 70, 3, fill=SLATE, sw=0))
    # 3 fasteners in small drawers.
    b.append(zone(X + 198, Y + 3, 130, 62))
    b.append(shelf(X + 204, Y + 8, 118, 24, items="drawers", n=6))
    b.append(shelf(X + 204, Y + 34, 118, 24, items="drawers", n=6))
    # 5 finishing and chemicals in a closed metal cabinet.
    b.append(zone(X + W - 86, Y + 3, 83, 132))
    b.append(rect(X + W - 78, Y + 8, 70, 120, fill=STEEL))
    b.append(shelf(X + W - 72, Y + 14, 58, 108, items="bottles", n=5,
                   vertical=True, fill=STEEL))
    # 1 the main bench, standing free so both sides can be worked.
    b.append(zone(X + 146, Y + 150, 214, 112))
    b.append(bench(X + 156, Y + 160, 194, 90))
    # 4 the material rack along the near wall.
    b.append(zone(X + 156, Y + H - 82, 340, 78))
    b.append(lumber(X + 166, Y + H - 74, 320, n=6, gap=12))

    L.add(1, LX, Y + 2, to=(X + 12, Y + 30))
    L.add(0, LX, Y + 140, to=(X + 156, Y + 190))
    L.add(5, LX, Y + H - 170, to=(X + 3, Y + H - 152))
    L.add(4, RX, Y + 30, to=(X + W - 8, Y + 60), align="right")
    L.add(2, RX, Y + 140, to=(X + 300, Y + 65), align="right")
    L.add(3, RX, Y + H - 50, to=(X + 496, Y + H - 40), align="right")
    return ("".join(b),
            "The PPE station is on the wall just inside the door, so the "
            "glasses, ear defenders and extinguisher are the first thing "
            "you reach. Power tools with their chargers and the small "
            "fastener drawers share the back wall, the finishing products "
            "are shut in a metal cabinet in the far corner, the main bench "
            "stands free in the middle, and lumber is racked along the near "
            "wall.", 580)


def hall_closet(L):
    X, Y, W, H = 330, 76, 340, 480
    b = [rect(X, Y, W, H, fill="#E9DFCC", stroke="none", sw=0)]
    b.append(rect(X - 14, Y - 10, W + 28, H + 10, fill="none", sw=9))
    b.append(line(X - 40, Y + H, X + W + 40, Y + H, sw=3))
    b.append(note(X + W / 2, Y + H + 22, "the closet with its doors open"))
    for yy in (Y + 92, Y + 188, Y + 268, Y + 336):
        b.append(rect(X, yy, W, 8, fill=WOOD, sw=1.6))
    # 5 seasonal and guest bins up top.
    b.append(zone(X + 6, Y + 8, W - 12, 80))
    for k in range(3):
        b.append(rect(X + 22 + k * 102, Y + 30, 90, 62, fill=FABRIC, sw=1.6,
                      rx=4))
        b.append(line(X + 22 + k * 102, Y + 44, X + 112 + k * 102, Y + 44,
                      sw=1.2))
    # 1 linen: folded stacks, folds facing out.
    b.append(zone(X + 6, Y + 104, W - 12, 80))
    for k in range(4):
        for j in range(4):
            b.append(rect(X + 20 + k * 78, Y + 172 - (j + 1) * 16, 66, 15,
                          fill=CARD, sw=1.2, rx=4))
    # 4 paper backstock: rolls standing in a row.
    b.append(zone(X + 6, Y + 200, W - 12, 64))
    for k in range(8):
        b.append(rect(X + 18 + k * 38, Y + 214, 30, 54, fill=PAPER, sw=1.3,
                      rx=3))
    # 3 supplies in a carry caddy.
    b.append(zone(X + 6, Y + 278, W - 12, 56))
    b.append(rect(X + 40, Y + 308, 150, 28, fill=STEEL, rx=4))
    b.append(path(P((X + 80, Y + 308), (X + 80, Y + 290), (X + 150, Y + 290),
                    (X + 150, Y + 308)), sw=2.2))
    for k in range(4):
        b.append(rect(X + 48 + k * 34, Y + 284 + (k % 2) * 6, 22,
                      26 - (k % 2) * 6, fill=CARD, sw=1.3, rx=5))
    b.append(rect(X + 220, Y + 296, 70, 40, fill=CARD, sw=1.4, rx=4))
    # 2 equipment on the floor: vacuum, broom, mop bucket.
    b.append(zone(X + 6, Y + 350, W - 12, H - 354))
    b.append(rect(X + 40, Y + H - 40, 46, 38, fill=STEEL, rx=8))
    b.append(line(X + 63, Y + H - 40, X + 63, Y + 376, sw=2.6))
    b.append(rect(X + 52, Y + 364, 22, 14, fill=STEEL, sw=1.6, rx=3))
    b.append(line(X + 150, Y + H - 22, X + 150, Y + 362, sw=2.4))
    b.append(path(P((X + 138, Y + H - 2), (X + 162, Y + H - 2),
                    (X + 156, Y + H - 24), (X + 144, Y + H - 24), close=True),
                  fill=WOOD, sw=1.5))
    b.append(path(P((X + 220, Y + H - 2), (X + 270, Y + H - 2),
                    (X + 276, Y + H - 50), (X + 214, Y + H - 50), close=True),
                  fill=STEEL, sw=1.8))
    b.append(line(X + 260, Y + H - 50, X + 290, Y + 362, sw=2.4))

    L.add(4, LX, Y + 24, to=(X + 6, Y + 50))
    L.add(0, LX, Y + 130, to=(X + 6, Y + 146))
    L.add(3, LX, Y + 218, to=(X + 6, Y + 234))
    L.add(2, RX, Y + 290, to=(X + W - 6, Y + 306), align="right")
    L.add(1, RX, Y + 400, to=(X + W - 6, Y + 416), align="right")
    return ("".join(b),
            "Seen from the front with the doors open: seasonal and guest "
            "bins on the top shelf, folded linen below them, a row of paper "
            "backstock, a caddy of cleaning supplies, and the vacuum, broom "
            "and mop bucket standing on the floor.", 660)


def pantry(L):
    X, Y, W, H = 300, 84, 400, 420
    b = [walls(X, Y, W, H, gaps=[("b", 150, 250)])]
    b.append(door(X + 250, Y + H, 100, (-1, 0), (0, -1)))
    # 1 dry goods: deep shelves of clear jars along the left wall.
    b.append(zone(X + 3, Y + 60, 76, 250))
    b.append(shelf(X + 6, Y + 68, 64, 234, items="bins", n=8))
    # 2 canned and jarred goods on the back wall, labels forward.
    b.append(zone(X + 84, Y + 3, 232, 58))
    b.append(rect(X + 90, Y + 8, 220, 46, fill=CARD))
    for row in range(2):
        for k in range(10):
            b.append(circle(X + 102 + k * 21.5, Y + 20 + row * 22, 8.5,
                            fill=STEEL, sw=1.3))
    # 3 baking canisters on the right wall.
    b.append(zone(X + W - 79, Y + 60, 76, 150))
    b.append(shelf(X + W - 70, Y + 68, 64, 134, items="rolls", n=5))
    # 4 snack and lunch bins at child height, near the door.
    b.append(zone(X + W - 79, Y + 222, 76, 128))
    b.append(shelf(X + W - 70, Y + 230, 64, 112, items="bins", n=4))
    # 5 backstock and bulk on the floor, bottom left.
    b.append(zone(X + 3, Y + H - 98, 132, 94))
    b.append(rect(X + 10, Y + H - 88, 56, 76, fill=FABRIC, rx=6))
    b.append(rect(X + 72, Y + H - 88, 56, 76, fill=FABRIC, rx=6))
    b.append(line(X + 10, Y + H - 72, X + 66, Y + H - 72, sw=1.2))
    b.append(line(X + 72, Y + H - 72, X + 128, Y + H - 72, sw=1.2))

    L.add(1, LX, Y - 12, to=(X + 84, Y + 32))
    L.add(0, LX, Y + 160, to=(X + 3, Y + 180))
    L.add(4, LX, Y + H - 70, to=(X + 3, Y + H - 50))
    L.add(2, RX, Y + 110, to=(X + W - 3, Y + 130), align="right")
    L.add(3, RX, Y + 270, to=(X + W - 3, Y + 286), align="right")
    return ("".join(b),
            "A walk-in pantry with shelves on three walls: dry goods in clear "
            "jars down the left, canned and jarred goods in rows on the back "
            "wall, baking canisters on the right, snack and lunch bins at "
            "child height by the door, and bulk backstock in floor bins.",
            580)


def family_room(L):
    X, Y, W, H = 260, 84, 480, 430
    b = [walls(X, Y, W, H, gaps=[("b", 40, 120)])]
    b.append(door(X + 40, Y + H, 80, (1, 0), (0, -1)))
    b.append(window(X + W, Y + 230, X + W, Y + 330))
    # 1 media: the console and screen on the back wall.
    b.append(zone(X + 130, Y + 3, 220, 62))
    b.append(rect(X + 140, Y + 18, 200, 40, fill=WOOD))
    b.append(rect(X + 170, Y + 8, 140, 10, fill=INK, sw=0))
    b.append(rect(X + 160, Y + 28, 40, 20, fill=STEEL, sw=1.2, rx=2))
    b.append(rect(X + 280, Y + 28, 40, 20, fill=STEEL, sw=1.2, rx=2))
    # The sofa facing it, 4 the blanket basket at its end, 5 charging on
    # the side table at the other end.
    b.append(sofa(X + 140, Y + 220, 200, 62))
    b.append(rect(X + 205, Y + 140, 70, 44, fill=WOOD, rx=4))
    b.append(zone(X + 92, Y + 214, 46, 74))
    b.append(basket(X + 115, Y + 251, 18))
    b.append(zone(X + 342, Y + 214, 52, 74))
    b.append(rect(X + 348, Y + 230, 40, 40, fill=WOOD, sw=1.6))
    b.append(rect(X + 356, Y + 238, 12, 22, fill=INK, sw=0, rx=2))
    b.append(rect(X + 372, Y + 242, 10, 16, fill=STEEL, sw=1, rx=2))
    # 3 board games in a cabinet on the right wall.
    b.append(zone(X + W - 58, Y + 40, 55, 150))
    b.append(shelf(X + W - 50, Y + 48, 42, 134, items="stacks", n=5))
    # 2 toys and play: cube bins and a mat, left side.
    b.append(zone(X + 3, Y + 70, 120, 200))
    b.append(shelf(X + 6, Y + 80, 46, 180, items="bins", n=5))
    b.append(rect(X + 60, Y + 120, 56, 100, fill=FABRIC, sw=1.4, rx=10))
    # 6 crafts at a small table, near corner.
    b.append(zone(X + W - 190, Y + H - 120, 186, 116))
    b.append(rect(X + W - 150, Y + H - 92, 100, 60, fill=WOOD, rx=4))
    for cx in (X + W - 130, X + W - 70):
        b.append(rect(cx - 12, Y + H - 116, 24, 20, fill=FABRIC, sw=1.4,
                      rx=5))
        b.append(rect(cx - 12, Y + H - 28, 24, 20, fill=FABRIC, sw=1.4,
                      rx=5))
    b.append(shelf(X + W - 30, Y + H - 110, 24, 96, items="bottles", n=4))

    L.add(1, LX, Y + 110, to=(X + 3, Y + 140))
    L.add(3, LX, Y + 250, to=(X + 92, Y + 262))
    L.add(0, RX, Y - 6, to=(X + 350, Y + 30), align="right")
    L.add(2, RX, Y + 100, to=(X + W - 3, Y + 116), align="right")
    L.add(4, RX, Y + 210, to=(X + 394, Y + 250), align="right")
    L.add(5, RX, Y + H - 50, to=(X + W - 4, Y + H - 40), align="right")
    return ("".join(b),
            "The media console and screen sit on the back wall with the sofa "
            "facing them, a blanket basket at one end of the sofa and a side "
            "table with the chargers at the other. Toy bins and a play mat "
            "take the left side, the board games live in a cabinet on the "
            "right wall, and a small craft table sits in the near corner.",
            590)
