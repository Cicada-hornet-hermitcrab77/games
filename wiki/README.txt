HOW TO ADD A PAGE TO THE STICKMAN FIGHT WIKI
============================================

The quick way: open the wiki in the game and press F2. Type a title, pick a
section, write the page, press F2 again to save. It lands in this folder as
one of the files described below, and you can go on editing it either way.

The other way: write a plain text file, save it in this folder with a .txt
name, and start the game. Your page is in the wiki. No code, no permission,
nothing else to edit.

You can also write on a page that already exists, including one the game
generates itself. Open it in the wiki and press F3: what you type goes at
the bottom of that page under "Notes", and is saved here as a file whose
header is a single "attach:" line.

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

Writing on a page the game generates
------------------------------------

Instead of section/title, use one attach line naming the page:

    attach: characters/Brawler

    He walks straight into you. Let him.

    ## What works
    - block early, kick late

The body works exactly as above. It appears under "Notes" at the bottom of
Brawler's page rather than as a page of its own. The part before the slash
is the section, the part after is the page title, spelled as it appears in
the wiki. Name a page that does not exist and it simply becomes a page of
its own instead — nothing is lost.

In game this is just F3 on whatever page you are reading, and the file is
named for you.

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
