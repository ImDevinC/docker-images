from yoyo import step
steps = [
    step('CREATE TABLE hot_topic (id integer primary key asc, hash text, price text)',
        'DROP TABLE hot_topic'),
]