# Installation

lxml, selenium, requests and chrome browser install required

# Usage

Collecting rewards of 2017 Activity:

    $ python -m ckminer.run --user <--username--> --pwd <--password--> --act2017

    Welcome to 2017 CK101's activity, check rules at this link:
    https://ck101.com/thread-4133697-1-1.html

    Collecting latest post from 鬍小編...
    Collecting latest post from 手殘星妹子...
    Collecting latest post from 廢柴小宅女...
    Collecting latest post from 電影兒童...
    Collecting latest post from 天菜御姊...
    Collecting latest post from 壓力少女手癢央...
    ...
    +5 topic rewards! Now you have 85...
    +5 topic rewards! Now you have 90...
    +5 topic rewards! Now you have 95...
    Post already drained...
    +5 topic rewards! Now you have 100...
    Pocket full today!

Collecting rewards from visiting user spaces:

    $ python -m ckminer.run --user <--username--> --pwd <--password--> --space <--limit-->

    Randomly visiting user spaces for collecting rewards.
    You can set the limit you want to browsing after
    "--space" argument.

    Visiting 達也郎...
    Visiting 王烏鴉...
    ...

Update writers from api

    >>import ckminer
    >>ckminer.update_writer()








