Use to skip all except every k-th time.
    e.g. EachK(5) will skip 4 out of 5 times in the loop.
```python
    each5 = EachK(5)
    for _ in range(100):
        if each5:
            # do something, it will be executed every 5th time
            print("Executed every 5th iteration")
            
```

Useful for logging, debugging, or any other operation that should be performed less often.
