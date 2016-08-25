# Now with Code Highlighting

Listicle crucifix 3 wolf moon, whatever sartorial gluten-free tousled Austin
meh seitan. Tousled twee seitan selvage Shoreditch. Skateboard blog lumbersexual
craft beer bicycle rights, narwhal yr iPhone gluten-free twee Bushwick XOXO +1
hella.

```python
def is_balanced(string):
    parens = []
    for char in string:
        if char == '(':
            parens.append('x')
        elif char == ')':
            if len(parens):
                parens.pop()
            else:
                return False

    if len(parens):
        return False

    return True

if __name__ == '__main__':
    assert is_balanced('()') is True
    assert is_balanced('((()))') is True
    assert is_balanced('(()(())())') is True
    assert is_balanced('(()))') is False
    assert is_balanced('((())') is False
    assert is_balanced(')(') is False
    assert is_balanced('(()))(') is False

    print 'All tests passed.'
```
