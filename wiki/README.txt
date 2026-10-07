HOW TO ADD A PAGE TO THE STICKMAN FIGHT WIKI
============================================

Write a plain text file, save it in this folder with a .txt name, and start
the game. Your page is in the wiki. That is the whole process — no code, no
permission, nothing else to edit.

A page looks like this:

    section: lore
    title: The Long Match
    subtitle: nobody remembers who started it

    They have been at this since before the health bars were invented. Lines
    that run together like this become one paragraph.

    A blank line starts the next paragraph.

    ## Things everyone agrees on
    - Brawler was first
    - Nobody has beaten Impossible fairly
    Round length = 99 seconds

The top lines are the header. Only "title" really matters:

    section:   which tab the page lands in. One of
               basics, characters, maps, events, costumes, fuser, modes,
               powerups, achievements, lore.
               A section nobody has used yet gets made for you.
               Leave it out and the page goes to lore.
    title:     the name in the list. Leave it out and the filename is used.
    subtitle:  the grey line under the title. Optional.
    color:     three numbers, 0-255, like  color: 180, 90, 220. Optional.
    tags:      comma separated, shown as little chips. Optional.

Then the body. Four kinds of line:

    plain text          a paragraph. Consecutive lines join up; a blank
                        line ends it.
    ## Heading          a heading.
    - bullet            a bullet point.
    Key = Value         a two-column row, good for numbers.

That is everything.

Notes
-----
* One file is one page. Name the file whatever you like.
* A file that cannot be read is skipped quietly — a broken page never stops
  the wiki opening.
* readme.txt (this file) is ignored.
* The character, map, event, costume, power-up, fuser and achievement pages
  are generated from the game's own data and are not stored here. If one of
  them is wrong, the game's data is wrong, and fixing the data fixes the page.
* Pages written here show a "contributed" mark, so readers can tell what a
  person wrote from what the game generated.
