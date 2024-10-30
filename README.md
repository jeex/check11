# Cpnits Check11

Check11 checks Python >= 3.10 code for cpnits.com students. 
## You need a github account
Check11 relies on a working github in your computer. 

Your github alias needs to be added to [cpnits.com/check11](https://cpnits.com/check11). Ask your teacher to do that for you.

You can only check11 assignments that come with a check11 command. Your assignment should have a line somewhere mentioning: Use 
```
check11 assignmentname -c
``` 
to check your solution for proper structure and output.

## How to install check11
1. Make sure you have an activated **virtual environment**.
2. Pip install check11 with...
```
pip install check11
```

## How to use check11: 
Let's asume that your assignment is called **nerdy**.

Check11 needs a path to the directory containing the Python files that you want tested.

With an **absolute path** (starting with **/**) to the dir containg the python files:
```
check11 nerdy /absolute/path/to/dir/with/assignment
```

or with a **relative path** (a relative path never starts with **/**): 
```
check11 nerdy relative/path
```

or in **current working directory**: 
```
check11 nerdy -c 
```

## For **help**: 
```
check11 -h 
```

or:
```
check11 nerdy -help 
```

## Additional arguments
Additional argument for **no traceback** in the testreport:  
```
check11 nerdy --t /some/dir 
```

Additional argument for **errors only** in the test report:  
```
check11 nerdy --e /some/dir 
```

Additional argument for **clearing the prompt** before printing the test report:  :
```
check11 nerdy --p /some/dir 
```

Combined arguments for **no traceback** and **errors only**: 
```
check11 nerdy --et /some/dir 
```

## Examples
Example (assignment in **current dir**, **errors only**, **no traceback**, **clear prompt**): 
```
check11 nerdy --etp -c
```

Example (assignment in **relative dir**, **clear prompt**): 
```
check11 nerdy --p assignment/
```

# [GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)