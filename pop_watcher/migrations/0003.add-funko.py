from yoyo import step
steps = [
    step('CREATE TABLE funko (id integer primary key asc, hash text, price text)',
         'DROP TABLE funko'),
]
