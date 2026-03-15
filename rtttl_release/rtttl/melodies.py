"""
rtttl/melodies.py
~~~~~~~~~~~~~~~~~
Built-in RTTTL melody strings.

These melodies may have copyrights you are responsible for respecting.

The Nokia tune (Grande Valse, Francisco Tárrega, arr.) has been corrected:
the original library had wrong octave/note assignments.  The correct sequence
for the iconic 13-note motif is:

    8e6, 8d6, f#5, g#5, 8c#6, 8b5, d5, e5, 8b5, 8a5, c#5, e5, 2a5
"""

RTTTL_MELODIES = [
    # 0
    "StarWars:d=32,o=5,b=45,l=2,s=N:p,f#,f#,f#,8b.,8f#.6,e6,d#6,c#6,8b.6,16f#.6,e6,d#6,c#6,8b.6,16f#.6,e6,d#6,e6,8c#6",
    # 1
    "MahnaMahna:d=16,o=6,b=125:c#,c.,b5,8a#.5,8f.,4g#,a#,g.,4d#,8p,c#,c.,b5,8a#.5,8f.,g#.,8a#.,4g,8p,c#,c.,b5,8a#.5,8f.,4g#,f,g.,8d#.,f,g.,8d#.,f,8g,8d#.,f,8g,d#,8c,a#5,8d#.,8d#.,16d#.,16d#.,8d#.",
    # 2
    "LeisureSuit:d=16,o=6,b=56:f.5,f#.5,g.5,g#5,32a#5,f5,g#.5,a#.5,32f5,g#5,32a#5,g#5,8c#.,a#5,32c#,a5,a#.5,c#.,32a5,a#5,32c#,d#,8e,c#.,f.,f.,f.,f.,f,32e,d#,8d,a#.5,e,32f,e,32f,c#,d#.,c#",
    # 3
    "MissionImp:d=16,o=6,b=95:32d,32d#,32d,32d#,32d,32d#,32d,32d#,32d,32d,32d#,32e,32f,32f#,32g,g,8p,g,8p,a#,p,c7,p,g,8p,g,8p,f,p,f#,p,g,8p,g,8p,a#,p,c7,p,g,8p,g,8p,f,p,f#,p,a#,g,2d,32p,a#,g,2c#,32p,a#,g,2c,a#5,8c,2p,32p,a#5,g5,2f#,32p,a#5,g5,2f,32p,a#5,g5,2e,d#,8d",
    # 4
    "Entertainer:d=4,o=5,b=140:8d,8d#,8e,c6,8e,c6,8e,2c.6,8c6,8d6,8d#6,8e6,8c6,8d6,e6,8b,d6,2c6,p,8d,8d#,8e,c6,8e,c6,8e,2c.6,8p,8a,8g,8f#,8a,8c6,e6,8d6,8c6,8a,2d6",
    # 5
    "Muppets:d=4,o=5,b=250:c6,c6,a,b,8a,b,g,p,c6,c6,a,8b,8a,8p,g.,p,e,e,g,f,8e,f,8c6,8c,8d,e,8e,8e,8p,8e,g,2p,c6,c6,a,b,8a,b,g,p,c6,c6,a,8b,a,g.,p,e,e,g,f,8e,f,8c6,8c,8d,e,8e,d,8d,c",
    # 6
    "Flinstones:d=32,o=5,b=40:p,16f6,16a#,16a#6,g6,16f6,16a#.,16f6,d#6,d6,d6,d#6,f6,16a#,16c6,4d6,16f6,16a#.,16a#6,g6,16f6,16a#.,f6,f6,d#6,d6,d6,d#6,f6,16a#,16c6,4a#,16a6,16d.6,16a#6,a6,a6,g6,f#6,a6,8g6,16g6,16c.6,a6,a6,g6,g6,f6,e6,g6,8f6,16f6,16a#.,16a#6,g6,16f6,16a#.,16f6,d#6,d6,d6,d#6,f6,16a#,16c.6,d6,d#6,f6,16a#,16c.6,d6,d#6,f6,16a#6,16c7,8a#.6",
    # 7
    "YMCA:d=4,o=5,b=160:8c#6,8a#,2p,8a#,8g#,8f#,8g#,8a#,c#6,8a#,c#6,8d#6,8a#,2p,8a#,8g#,8f#,8g#,8a#,c#6,8a#,c#6,8d#6,8b,2p,8b,8a#,8g#,8a#,8b,d#6,8f#6,d#6,f.6,d#.6,c#.6,b.,a#,g#",
    # 8
    "TheSimpsons:d=4,o=5,b=160:c.6,e6,f#6,8a6,g.6,e6,c6,8a,8f#,8f#,8f#,2g,8p,8p,8f#,8f#,8f#,8g,a#.,8c6,8c6,8c6,c6",
    # 9
    "Indiana:d=4,o=5,b=250:e,8p,8f,8g,8p,1c6,8p.,d,8p,8e,1f,p.,g,8p,8a,8b,8p,1f6,p,a,8p,8b,2c6,2d6,2e6,e,8p,8f,8g,8p,1c6,p,d6,8p,8e6,1f.6,g,8p,8g,e.6,8p,d6,8p,8g,e.6,8p,d6,8p,8g,f.6,8p,e6,8p,8d6,2c6",
    # 10
    "TakeOnMe:d=8,o=4,b=160:f#5,f#5,f#5,d5,p,b,p,e5,p,e5,p,e5,g#5,g#5,a5,b5,a5,a5,a5,e5,p,d5,p,f#5,p,f#5,p,f#5,e5,e5,f#5,e5,f#5,f#5,f#5,d5,p,b,p,e5,p,e5,p,e5,g#5,g#5,a5,b5,a5,a5,a5,e5,p,d5,p,f#5,p,f#5,p,f#5,e5,e5",
    # 11
    "Looney:d=4,o=5,b=140:32p,c6,8f6,8e6,8d6,8c6,a.,8c6,8f6,8e6,8d6,8d#6,e.6,8e6,8e6,8c6,8d6,8c6,8e6,8c6,8d6,8a,8c6,8g,8a#,8a,8f",
    # 12
    "20thCenFox:d=16,o=5,b=140:b,8p,b,b,2b,p,c6,32p,b,32p,c6,32p,b,32p,c6,32p,b,8p,b,b,b,32p,b,32p,b,32p,b,32p,b,32p,b,32p,b,32p,g#,32p,a,32p,b,8p,b,b,2b,4p,8e,8g#,8b,1c#6,8f#,8a,8c#6,1e6,8a,8c#6,8e6,1e6,8b,8g#,8a,2b",
    # 13
    "Bond:d=16,o=5,b=80:p,c#6,32d#6,32d#6,d#6,8d#6,c#6,c#6,c#6,c#6,32e6,32e6,e6,8e6,d#6,d#6,d#6,c#6,32d#6,32d#6,d#6,8d#6,c#6,c#6,c#6,c#6,32e6,32e6,e6,8e6,d#6,d6,c#6,c#7,4c.7,g#6,f#6,4g#.6",
    # 14
    "GoodBad:d=4,o=5,b=56:32p,32a#,32d#6,32a#,32d#6,8a#.,16f#.,16g#.,d#,32a#,32d#6,32a#,32d#6,8a#.,16f#.,16g#.,c#6,32a#,32d#6,32a#,32d#6,8a#.,16f#.,32f.,32d#.,c#,32a#,32d#6,32a#,32d#6,8a#.,16g#.,d#",
    # 15
    "PinkPanther:d=16,o=5,b=160:8d#,8e,2p,8f#,8g,2p,8d#,8e,p,8f#,8g,p,8c6,8b,p,8d#,8e,p,8b,2a#,2p,a,g,e,d,2e",
    # 16
    "ATeam:d=8,o=5,b=125:4d#6,a#,2d#6,16p,g#,4a#,4d#.,p,16g,16a#,d#6,a#,f6,2d#6,16p,c#.6,16c6,16a#,g#.,2a#",
    # 17
    "Jeopardy:d=4,o=6,b=125:c,f,c,f5,c,f,2c,c,f,c,f,a.,8g,8f,8e,8d,8c#,c,f,c,f5,c,f,2c,f.,8d,c,a#5,a5,g5,f5,p,d#,g#,d#,g#5,d#,g#,2d#,d#,g#,d#,g#,c.7,8a#,8g#,8g,8f,8e,d#,g#,d#,g#5,d#,g#,2d#,g#.,8f,d#,c#,c,p,a#5,p,g#.5,d#,g#",
    # 18
    "Gadget:d=16,o=5,b=50:32d#,32f,32f#,32g#,a#,f#,a,f,g#,f#,32d#,32f,32f#,32g#,a#,d#6,4d6,32d#,32f,32f#,32g#,a#,f#,a,f,g#,f#,8d#",
    # 19
    "Smurfs:d=32,o=5,b=200:4c#6,16p,4f#6,p,16c#6,p,8d#6,p,8b,p,4g#,16p,4c#6,p,16a#,p,8f#,p,8a#,p,4g#,4p,g#,p,a#,p,b,p,c6,p,4c#6,16p,4f#6,p,16c#6,p,8d#6,p,8b,p,4g#,16p,4c#6,p,16a#,p,8b,p,8f,p,4f#",
    # 20
    "Toccata:d=4,o=5,b=160:16a4,16g4,1a4,16g4,16f4,16d4,16e4,2c#4,16p,d.4,2p,16a4,16g4,1a4,8e.4,8f.4,8c#.4,2d4",
    # 21  Nokia Grande Valse — corrected note sequence
    "Nokia:d=4,o=5,b=112:8e6,8d6,f#5,g#5,8c#6,8b5,d5,e5,8b5,8a5,c#5,e5,2a5",
]

# ---- curated subsets -------------------------------------------------------

RTTTL_MELODIES_SMALL = [
    RTTTL_MELODIES[0],   # StarWars
    RTTTL_MELODIES[1],   # MahnaMahna
    RTTTL_MELODIES[2],   # LeisureSuit
    RTTTL_MELODIES[3],   # MissionImp
    RTTTL_MELODIES[9],   # Indiana
    RTTTL_MELODIES[10],  # TakeOnMe
    RTTTL_MELODIES[5],   # Muppets
    RTTTL_MELODIES[12],  # 20thCenFox
    RTTTL_MELODIES[13],  # Bond
    RTTTL_MELODIES[14],  # GoodBad
    RTTTL_MELODIES[15],  # PinkPanther
]

RTTTL_MELODIES_TINY = [
    RTTTL_MELODIES[0],   # StarWars
    RTTTL_MELODIES[1],   # MahnaMahna
    RTTTL_MELODIES[2],   # LeisureSuit
    RTTTL_MELODIES[10],  # TakeOnMe
    RTTTL_MELODIES[5],   # Muppets
    RTTTL_MELODIES[14],  # GoodBad
]
