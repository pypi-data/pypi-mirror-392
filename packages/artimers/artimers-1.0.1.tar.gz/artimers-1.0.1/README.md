# artimers

A utility package for timing and managing timers by Alexander Rießbeck

The goal of this package is it to provide easy to use timers that can collect timing data across your project and make the collected times accessible.

```
$ python -m pip install artimers
```

# Usage
```python
from artimers import Timer
```

## Basics

`Timer` can be used in multiple ways


### Class

`Timer` can be used as a **class**
```python
timer = Timer()
timer.start()
...
final_time = timer.stop()
```

### Decorator

`Timer` can be used as a **decorator**
```python
@(timer:=Timer())
def foo():
    ...

print(timer)
```

### Context Manager

`Timer` can be used as a **context manager**
```python
with Timer() as timer:
    ...
    x = timer.time
```

## Pretty print
`Timer` also has a custom `__str__` method

```python
timer = Timer()
timer.start()
sleep(0.2)
print(timer)
sleep(0.2)
timer.stop()
print(timer)
```
```
Timer (Running): 0.2004s
Timer (Stopped): 0.4007s
```

If the timer is named (`Timer('Stopwatch 1')`) the name will be used instead of `Timer`.

### Printed decimals

The deciaml point used in the `__str__` function can also be set (default is 4 and timing seems to be accurate up to 2)
```python
timer = Timer(decimal=5)
print(timer)
```


## Naming

`Timer` can be named and easily accessed later by using the same name again

```python
Timer('Stopwatch 1')
```
```python
Timer(name='Stopwatch 2')
```

Named timers always return the same instance and therefore keep their time and status (Running/Stopped).

### Get timers

`Timer` can return a dict of all named timers

```python
named_timers = Timer.get_timers()
```

## Print results

The final time can be printed when exiting a decorator or context manager
```python
@(Timer(print_result=True))
def foo():
    ...
```
```python
with Timer(print_result=True):
    ...
```

## Return results

The final time can also be return from a decorated function

```python
@(Timer(return_result=True))
def foo():
    ...

time, _ = foo()
```