from nanogen import utils


def test_slugify():
    assert utils.slugify('This is a test') == 'this-is-a-test'
    assert utils.slugify('this is ^&* a test') == 'this-is-----a-test'


def test_is_valid_post_file():
    assert not utils.is_valid_post_file('asldkjf')
    assert not utils.is_valid_post_file('asldkjf.md')
    assert not utils.is_valid_post_file('12-34-56-example.md')
    assert not utils.is_valid_post_file('_2018-01-01-example-file.md')
    assert not utils.is_valid_post_file('2018-01-01-example-file.html')
    assert utils.is_valid_post_file('2018-01-01-example-file.md')

