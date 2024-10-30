# Cpnits Check11

Check11 checks Python >= 3.10 code for cpnits.com students
How to use:

## How to use check11: 
With an **absolute path** to the dir containg the python code:
```
check11 /absolute/path/to/dir/with/assignment
```
or with a **relative path**: 
```
check11 relative/path/with/assignment
```

or in **current working directory**: 
```
check11 -c 
```

## For **help**: 
```
check11 -h 
```
or:
```
check11 -help 
```

## Additional arguments
Additional argument for **no traceback** in the testreport:  
```
check11 --t /some/dir 
```

Additional argument for **errors only** in the test report:  
```
check11 --e /some/dir 
```

Additional argument for **clearing the prompt** before printing the test report:  :
```
check11 --p /some/dir 
```

Combined arguments for **no traceback** and **errors only**: 
```
check11 --et /some/dir 
```

## Examples
Example (assignment in **current dir**, **errors only**, **no traceback**, **clear prompt**): 
```
check11 --etp -c
```

Example (assignment in **relative dir** assignment, **clear prompt**): 
```
check11 --p assignment/
```

[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)