from yoyo import step
steps = [
    step('CREATE TABLE chalice_collectibles (id integer primary key asc, hash text, price text)',
        'DROP TABLE chalice_collectibles'),
    step('CREATE TABLE galactic_toys (id integer primary key asc, hash text, price text)',
        'DROP TABLE galactic_toys')
]